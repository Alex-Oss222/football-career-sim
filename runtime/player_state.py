"""Kernel 2014.6 (batch B7): the player-state model at runtime.

Policy: runtime/2014_engine_decisions.md (Stone's player policy, October 2,
2026) and the frozen rules in library/2014_6_pre_build_specification.md
(section 4, Player states). Data (batch B4b, data only until this batch):

* library/data/2010_2014_player_state_model.json: the fitted model (families,
  adopted swing parameters sb2, su2, rho, tau; feedback weights);
* library/data/2014_player_state_public.json: the public table, one row per
  gsis id of the branch identity table, with the record family, basis, the
  expectation (m_b persistent, m_u swing) and its covariance P = [Pbb, Pbu,
  Puu] for the 2014 league year, built from each player's 2010-2012 lines
  only (no club field; 2013 and 2014 rows never set a player's own value);
* library/data/2014_player_state_manifest.json: pins the two files above by
  sha256 (this module fails closed when either file differs);
* library/data/2014_player_state_binding.json: written by
  scripts/bind_latent_season.py from the private service's reply when the
  league year is bound: the manifest digest the service drew against and the
  public commitment over the drawn rows. Absent until the bind; a kernel on
  the player-state model refuses to run without it.

Hidden state. The public table holds expectations only. The once-per-season
draw is made by the private Engine State service, which holds the season
reference R_Y (an HMAC of the store seed by league year that never leaves the
service) and records z for every public row at bind (runtime.private_service).
Each z is a pure function of (R_Y, key) with key
['player-state-z-v1', Y, gsis_id, slot]: no club, no family, no event, so a
relabelled club or a position change cannot move a value, and a rebuilt or
resumed game fetches the same draws. uniform = ((x >> 11) + 0.5) / 2^53 from
the first eight digest bytes; z = the AS241 inverse normal (vendored below).
The latent deviation is a PSD-safe factorization of P: with L11 = sqrt(Pbb),
L21 = Pbu / L11 and L22 = sqrt(Puu - L21^2) (each clipped at 0), the base
slots are b and u, drawn from R_2014 for the base season; a later league year
adds its own innovation slot e drawn from R_Y where tau > 0 (the swing
carries with rho and renews with tau). A slot whose factor is 0 is not drawn
(sigma 0 consumes nothing). The latent value a lineup slot reads is
(m_b + m_u + deviation) / sqrt(sb2 + su2), the family's true-state SD units,
the same unit the strength v4 fit used for its E-value composites
(library/data/2014_strength_calibration_v4.json). A held family (LB under U5),
a family with no spread and a no-state row (offensive linemen, long snappers)
read 0 and draw nothing.

Boundary. These values are hidden-state statistical priors for the engine
only: never scouting evidence, never a staff-facing grade, and no staff
assessment, grade or E2 advice reads them or their tiers. Nothing here reads a
club name or which side is the protagonist.
"""
from __future__ import annotations

import copy
import hashlib
import hmac
import json
import math
from dataclasses import replace
from functools import lru_cache
from pathlib import Path

from .packets import canonical

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "library/data"
MODEL_PATH = DATA / "2010_2014_player_state_model.json"
PUBLIC_PATH = DATA / "2014_player_state_public.json"
MANIFEST_PATH = DATA / "2014_player_state_manifest.json"

DERIVATION = "player-state-v1"
KEY_DOMAIN = "player-state-z-v1"
REFERENCE_DOMAIN = b"player-state-reference-v1"
MANIFEST_SCHEMA = "2014-player-state-manifest-v1"
PUBLIC_SCHEMA = "2014-player-state-public-v1"
BINDING_SCHEMA = "player-state-binding-v1"
BASE_SLOTS = ("b", "u")
INNOVATION_SLOT = "e"
POSITION_FAMILIES = ("QB", "RB", "WR", "TE", "DL", "LB", "DB", "K", "P")
FAMILY_SIDE = {"QB": "offense", "RB": "offense", "WR": "offense", "TE": "offense",
               "DL": "defense", "LB": "defense", "DB": "defense", "K": "special", "P": "special",
               "KR": "special", "PR": "special"}


class PlayerStateError(ValueError):
    pass


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def binding_path(league_year, root=ROOT):
    return Path(root) / "library/data" / ("%d_player_state_binding.json" % int(league_year))


@lru_cache(maxsize=1)
def manifest():
    """The pinned manifest; the model and public table must match its digests."""
    data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if data.get("schema") != MANIFEST_SCHEMA or data.get("derivation") != DERIVATION:
        raise PlayerStateError("player-state manifest schema or derivation unknown")
    if sha256_file(MODEL_PATH) != data.get("model_sha256"):
        raise PlayerStateError("player-state model differs from its manifest digest")
    if sha256_file(PUBLIC_PATH) != data.get("public_table_sha256"):
        raise PlayerStateError("player-state public table differs from its manifest digest")
    return data


def manifest_sha256():
    manifest()
    return sha256_file(MANIFEST_PATH)


@lru_cache(maxsize=1)
def model():
    manifest()
    return json.loads(MODEL_PATH.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def public_table():
    """{gsis: row} of the pinned public table."""
    manifest()
    data = json.loads(PUBLIC_PATH.read_text(encoding="utf-8"))
    if data.get("schema") != PUBLIC_SCHEMA or data.get("derivation") != DERIVATION:
        raise PlayerStateError("player-state public table schema or derivation unknown")
    return data["players"]


def league_year():
    return int(manifest()["league_year"])


def family_params(family):
    """{sb2, su2, rho, tau, held} of a family, or None for no family."""
    fam = (model()["families"].get(family) or {}).get("adopted")
    if not fam:
        return None
    return {"sb2": float(fam["sb2"]), "su2": float(fam["su2"]), "rho": float(fam["rho"]),
            "tau": float(fam.get("tau", 0.0)), "held": bool(fam.get("held"))}


def family_scale(family):
    """sqrt(sb2 + su2), the family's true-state SD; 0 for a held family or no spread."""
    p = family_params(family)
    if p is None or p["held"]:
        return 0.0
    return math.sqrt(max(p["sb2"] + p["su2"], 0.0))


def has_state(row):
    """Whether a public row carries a drawable state (record, draft,
    undrafted or population basis in a family with spread)."""
    if not row or row.get("basis") in (None, "held", "no_state") or "P" not in row:
        return False
    return family_scale(row.get("record_family")) > 0


def factor(P):
    """(L11, L21, L22): the PSD-safe lower factor of [[Pbb, Pbu], [Pbu, Puu]]."""
    pbb, pbu, puu = (float(v) for v in P)
    l11 = math.sqrt(max(pbb, 0.0))
    l21 = pbu / l11 if l11 > 0 else 0.0
    l22 = math.sqrt(max(puu - l21 * l21, 0.0))
    return l11, l21, l22


def key(year, gsis_id, slot):
    """The draw key; no club and no family."""
    return [KEY_DOMAIN, int(year), str(gsis_id), str(slot)]


def key_text(k):
    """The pinned wire form of a key: 'Y:gsis:slot'."""
    return "%d:%s:%s" % (int(k[1]), k[2], k[3])


def parse_key_text(text):
    year, gsis, slot = str(text).split(":")
    return key(int(year), gsis, slot)


def row_keys(gsis_id, row, year, base_year):
    """The draw keys one public row needs for league year `year` (base
    slots from the base year; one innovation slot per later year where
    tau > 0). Empty for a row without a drawable state."""
    if not has_state(row):
        return []
    l11, _, l22 = factor(row["P"])
    keys = []
    if l11 > 0:
        keys.append(key(base_year, gsis_id, "b"))
    if l22 > 0:
        keys.append(key(base_year, gsis_id, "u"))
    p = family_params(row["record_family"])
    if p and p["tau"] > 0:
        for y in range(int(base_year) + 1, int(year) + 1):
            keys.append(key(y, gsis_id, INNOVATION_SLOT))
    return keys


def expected_value(row):
    """The public expectation in the family's SD units (0 without a state)."""
    if not has_state(row):
        return 0.0
    return (float(row["m_b"]) + float(row["m_u"])) / family_scale(row["record_family"])


def latent_value(gsis_id, row, z, year, base_year):
    """The drawn value in SD units. `z` maps key text to z; a missing key
    for a drawable row raises (the binding is incomplete)."""
    if not has_state(row):
        return 0.0
    l11, l21, l22 = factor(row["P"])
    p = family_params(row["record_family"])

    def need(k):
        text = key_text(k)
        if text not in z:
            raise PlayerStateError("latent draw missing for %s" % text)
        return float(z[text])

    zb = need(key(base_year, gsis_id, "b")) if l11 > 0 else 0.0
    zu = need(key(base_year, gsis_id, "u")) if l22 > 0 else 0.0
    dev_b = l11 * zb
    dev_u = l21 * zb + l22 * zu
    mb, mu = float(row["m_b"]), float(row["m_u"])
    swing = mu + dev_u
    for y in range(int(base_year) + 1, int(year) + 1):
        swing = p["rho"] * swing
        if p["tau"] > 0:
            swing += p["tau"] * need(key(y, gsis_id, INNOVATION_SLOT))
    return (mb + dev_b + swing) / family_scale(row["record_family"])


# ---- the draw -----------------------------------------------------------------

def season_reference(seed, year):
    """R_Y for a store seed: never leaves the private service."""
    return hmac.new(seed, REFERENCE_DOMAIN + b":" + str(int(year)).encode(), hashlib.sha256).digest()


def uniform_from_digest(digest):
    """((x >> 11) + 0.5) / 2^53 from the first eight digest bytes: in (0, 1)
    exactly, except that the one 53-bit value 2^53 - 1 rounds to 1.0 in a
    double; it is held at the largest double below 1 (probability 2^-53)."""
    x = int.from_bytes(digest[:8], "big")
    return min(((x >> 11) + 0.5) / 2.0 ** 53, 1.0 - 2.0 ** -53)


def draw_z(reference, k):
    """z for one key under one season reference (a pure function)."""
    digest = hmac.new(reference, canonical(k), hashlib.sha256).digest()
    return inverse_normal(uniform_from_digest(digest))


def z_text(z):
    """The pinned byte encoding of a drawn z (IEEE double, hex)."""
    return float(z).hex()


def z_from_text(text):
    return float.fromhex(text)


def commitment(rows):
    """sha256 over the sorted drawn rows [key text, z hex]."""
    return hashlib.sha256(canonical(sorted([t, zt] for t, zt in rows))).hexdigest()


# AS241 (Wichura, 1988, algorithm PPND16): the inverse of the standard normal
# distribution to about 1e-16 relative accuracy. Vendored so the draw depends
# on no library version.
_A = (3.3871328727963666080e0, 1.3314166789178437745e2, 1.9715909503065514427e3, 1.3731693765509461125e4,
      4.5921953931549871457e4, 6.7265770927008700853e4, 3.3430575583588128105e4, 2.5090809287301226727e3)
_B = (1.0, 4.2313330701600911252e1, 6.8718700749205790830e2, 5.3941960214247511077e3, 2.1213794301586595867e4,
      3.9307895800092710610e4, 2.8729085735721942674e4, 5.2264952788528545610e3)
_C = (1.42343711074968357734e0, 4.63033784615654529590e0, 5.76949722146069140550e0, 3.64784832476320460504e0,
      1.27045825245236838258e0, 2.41780725177450611770e-1, 2.27238449892691845833e-2, 7.74545014278341407640e-4)
_D = (1.0, 2.05319162663775882187e0, 1.67638483018380384940e0, 6.89767334985100004550e-1,
      1.48103976427480074590e-1, 1.51986665636164571966e-2, 5.47593808499534494600e-4, 1.05075007164441684324e-9)
_E = (6.65790464350110377720e0, 5.46378491116411436990e0, 1.78482653991729133580e0, 2.96560571828504891230e-1,
      2.65321895265761230930e-2, 1.24266094738807843860e-3, 2.71155556874348757815e-5, 2.01033439929228813265e-7)
_F = (1.0, 5.99832206555887937690e-1, 1.36929880922735805310e-1, 1.48753612908506148525e-2,
      7.86869131145613259100e-4, 1.84631831751005468180e-5, 1.42151175831644588870e-7, 2.04426310338993978564e-15)


def _poly(coefficients, x):
    total = 0.0
    for c in reversed(coefficients):
        total = total * x + c
    return total


def inverse_normal(p):
    """Phi^-1(p) for 0 < p < 1 (AS241 PPND16)."""
    if not 0.0 < p < 1.0:
        raise ValueError("inverse normal requires 0 < p < 1")
    q = p - 0.5
    if abs(q) <= 0.425:
        r = 0.180625 - q * q
        return q * _poly(_A, r) / _poly(_B, r)
    r = p if q < 0 else 1.0 - p
    r = math.sqrt(-math.log(r))
    if r <= 5.0:
        r -= 1.6
        value = _poly(_C, r) / _poly(_D, r)
    else:
        r -= 5.0
        value = _poly(_E, r) / _poly(_F, r)
    return -value if q < 0 else value


# ---- the binding --------------------------------------------------------------

def binding(year, root=ROOT):
    """The committed binding of a league year, or None before the bind."""
    path = binding_path(year, root)
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != BINDING_SCHEMA or int(data.get("league_year", -1)) != int(year):
        raise PlayerStateError("player-state binding file is not a %d binding" % int(year))
    for field in ("manifest_sha256", "commitment"):
        if not isinstance(data.get(field), str) or len(data[field]) != 64:
            raise PlayerStateError("player-state binding lacks its %s" % field)
    return data


def require_binding(year, root=ROOT):
    """The binding, which must name the pinned manifest; absent fails closed."""
    data = binding(year, root)
    if data is None:
        raise PlayerStateError("league year %d is not bound: run scripts/bind_latent_season.py %d from merged "
                               "main before any game on the player-state model" % (int(year), int(year)))
    if data["manifest_sha256"] != manifest_sha256():
        raise PlayerStateError("the %d binding names manifest %s; the pinned manifest is %s"
                               % (int(year), data["manifest_sha256"][:12], manifest_sha256()[:12]))
    return data


# ---- TeamInput strength records ----------------------------------------------

def public_state(gsis_id, year=None):
    """The public fields a strength record carries for one gsis id:
    {family, basis, expected} (expected in SD units), or None when the table
    has no row. Family side rules read `family`."""
    row = public_table().get(gsis_id)
    if row is None:
        return None
    return {"family": row.get("record_family"), "basis": row.get("basis"),
            "expected": float("%.10g" % expected_value(row)) if has_state(row) else 0.0,
            "drawn": has_state(row)}


def record_keys(gsis_ids, year):
    """Sorted draw keys for a club's gsis ids in a league year."""
    base = league_year()
    out = []
    for gsis in gsis_ids:
        row = public_table().get(gsis)
        if row is not None:
            out += row_keys(gsis, row, year, base)
    return sorted(out, key=key_text)


def keys_of_inputs(*teams):
    """The union of the latent keys of the given TeamInputs' records."""
    keys = {}
    for team in teams:
        record = getattr(team, "strength", None) or {}
        if record.get("model") != DERIVATION:
            continue
        for k in record.get("latent_keys", ()):
            keys[key_text(k)] = list(k)
    return [keys[t] for t in sorted(keys)]


def roster_sha256(keys):
    return hashlib.sha256(canonical(sorted(key_text(k) for k in keys))).hexdigest()


def requires_draws(*teams):
    return bool(keys_of_inputs(*teams))


def apply_latent(team, draws):
    """A deep copy of a TeamInput whose player-state record carries each
    drawn player's latent value (`latent_value`, SD units). `draws` maps key
    text to z hex. A TeamInput without a player-state record is returned
    unchanged (no copy)."""
    record = getattr(team, "strength", None)
    if not record or record.get("model") != DERIVATION:
        return team
    record = copy.deepcopy(record)
    year = int(record["league_year"])
    base = league_year()
    z = {t: z_from_text(v) for t, v in draws.items()}
    for pid, player in record.get("players", {}).items():
        state = player.get("state")
        if not state or not state.get("drawn"):
            continue
        row = public_table().get(player.get("gsis_id"))
        if not row:
            raise PlayerStateError("public state missing for %s" % pid)
        player["latent_value"] = latent_value(player["gsis_id"], row, z, year, base)
    return replace(team, strength=record)


def latent_errors(record):
    """Why a player-state record cannot resolve: a drawable player without
    his latent value (the binding was not applied). Empty for other models."""
    if not record or record.get("model") != DERIVATION:
        return []
    return ["%s has no latent value" % pid for pid, p in sorted(record.get("players", {}).items())
            if (p.get("state") or {}).get("drawn") and "latent_value" not in p]
