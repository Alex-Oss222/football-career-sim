#!/usr/bin/env python3
"""Create or check one annual NFL player sheet per season player."""
from __future__ import annotations
import argparse, json, re, unicodedata
from dataclasses import dataclass
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXIT_INDEX = ROOT / "career/2014/offseason/player_development/2013_exit_player_index.json"
ROSTER_PROFILES = ROOT / "career/2014/offseason/player_development/roster_profiles.md"
BIRTH_DATES = ROOT / "library/data/player_birth_dates.json"

POSITION_TRAITS = {
    "QB": ("Arm talent", "Ball placement", "Processing / decision-making"),
    "RB": ("Vision", "Contact balance", "Pass protection"),
    "FB": ("Lead blocking", "Receiving", "Pass protection"),
    "WR": ("Release / route running", "Hands / catch radius", "Ball tracking / separation"),
    "TE": ("Receiving / route detail", "Run blocking", "Pass protection"),
    "OT": ("Pass protection", "Run blocking", "Recognition / recovery"),
    "G": ("Pass protection", "Run blocking", "Recognition / communication"),
    "C": ("Pass protection", "Run blocking", "Calls / recognition"),
    "DE": ("Run defense", "Pass rush", "Block recognition"),
    "DT": ("Run defense", "Pass rush", "Block recognition"),
    "LB": ("Run fits", "Coverage", "Tackling / pressure"),
    "CB": ("Coverage", "Ball skills", "Tackling / run support"),
    "S": ("Range / coverage", "Processing / communication", "Tackling / run support"),
    "K": ("Accuracy", "Leg strength", "Operation consistency"),
    "P": ("Distance / hang time", "Directional control", "Operation consistency"),
    "LS": ("Snap accuracy / velocity", "Protection", "Coverage"),
}
COUNT_RE = re.compile(r"Canonical controlled-player count:\*\*\s*\*\*(\d+)\*\*")
AS_OF_RE = re.compile(r"^\*\*As of:\*\*\s*(.+?)(?:\s*\(|$)")

@dataclass(frozen=True)
class SheetPlayer:
    player: str
    pos: str
    age: int | None
    continuity: bool
    inherited_identity: str
    source_note: str

def slugify(name: str) -> str:
    ascii_name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "_", ascii_name.lower()).strip("_")
    if not slug:
        raise ValueError("player name cannot produce an empty slug")
    return slug

def _cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]

def parse_profile_syntheses(path: Path = ROSTER_PROFILES) -> dict[str, str]:
    syntheses = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| **"):
            continue
        cells = _cells(line)
        if len(cells) < 3:
            continue
        match = re.search(r"\*\*(.+?) \(([^()]+)\)\*\*", cells[0])
        if match:
            syntheses[match.group(1)] = cells[1]
    return syntheses

def completed_years(birth_date: str, on_date: date) -> int:
    born = date.fromisoformat(birth_date)
    return on_date.year - born.year - ((on_date.month, on_date.day) < (born.month, born.day))

def load_birth_dates() -> dict[str, str]:
    data = json.loads(BIRTH_DATES.read_text(encoding="utf-8"))
    return {name: row["birth_date"] for name, row in data["players"].items() if row.get("birth_date")}

def parse_current_roster(path: Path):
    text = path.read_text(encoding="utf-8")
    m = COUNT_RE.search(text)
    if not m:
        raise ValueError("roster is missing canonical controlled-player count")
    canonical_count = int(m.group(1))
    checkpoint = "Current roster checkpoint"
    in_current = False
    player_col = pos_col = age_col = None
    players, seen = [], set()
    for line in text.splitlines():
        dm = AS_OF_RE.match(line)
        if dm:
            checkpoint = dm.group(1).strip()
        if line.strip() == "## Current controlled players":
            in_current = True
            continue
        if in_current and line.startswith("## "):
            break
        if not in_current:
            continue
        if not line.startswith("|"):
            player_col = pos_col = age_col = None
            continue
        cells = _cells(line)
        if "Player" in cells:
            player_col = cells.index("Player")
            pos_col = cells.index("Pos") if "Pos" in cells else None
            age_col = cells.index("Age") if "Age" in cells else None
            continue
        if player_col is None or pos_col is None:
            continue
        if cells and all(set(cell) <= {"-", ":"} for cell in cells if cell):
            continue
        if max(player_col, pos_col) >= len(cells):
            continue
        player, pos = cells[player_col], cells[pos_col]
        if not player or player in seen:
            continue
        age = int(cells[age_col]) if age_col is not None and age_col < len(cells) and cells[age_col].isdigit() else None
        seen.add(player)
        players.append((player, pos, age))
    if len(players) != canonical_count:
        raise ValueError(f"parsed {len(players)} current players but roster declares {canonical_count}")
    return checkpoint, canonical_count, players

def load_season_players(season: int):
    syntheses, births = parse_profile_syntheses(), load_birth_dates()
    if season == 2013:
        data = json.loads(EXIT_INDEX.read_text(encoding="utf-8"))
        checkpoint_date = date(2014, 1, 13)
        players = []
        for row in data["players"]:
            name = row["player"]
            age = completed_years(births[name], checkpoint_date) if name in births else None
            synthesis = syntheses.get(name, "Annual-sheet synthesis not yet entered; use the 2013 exit-review evidence.")
            players.append(SheetPlayer(name, row["pos"], age, False, synthesis,
                "2013 exit-review baseline and the frozen 2014-entry roster synthesis."))
        return "January 13, 2014 season-close / exit-review baseline", players
    roster_path = ROOT / f"career/{season}/roster.md"
    checkpoint, _, rows = parse_current_roster(roster_path)
    exit_players = {row["player"] for row in json.loads(EXIT_INDEX.read_text(encoding="utf-8"))["players"]}
    players = []
    for name, pos, age in rows:
        continuity = season == 2014 and name in exit_players
        if continuity:
            inherited = syntheses.get(name, "2013 established identity exists but has not yet been summarized here.")
            source = "Inherited Jacksonville 2013 profile plus current 2014 roster facts."
        else:
            inherited = ("No prior Jacksonville annual sheet. Preserve permitted pre-Jacksonville "
                         "NFL capabilities; only Jacksonville system familiarity begins new.")
            source = "Current roster plus permitted pre-divergence player evidence."
        players.append(SheetPlayer(name, pos, age, continuity, inherited, source))
    return f"{checkpoint} working profile", players

def previous_profile_link(player: SheetPlayer, season: int) -> str:
    if season == 2014 and player.continuity:
        return f"[2013 Jacksonville profile](../../2013/player_profiles/{slugify(player.player)}.md)"
    return "None in the Jacksonville annual-sheet archive"

def render_player_sheet(player: SheetPlayer, season: int, checkpoint: str) -> str:
    traits = POSITION_TRAITS.get(player.pos, ("Position trait 1", "Position trait 2", "Position trait 3"))
    prior = previous_profile_link(player, season)
    age = str(player.age) if player.age is not None else "Unverified"
    if season == 2013:
        identity = established = player.inherited_identity
        change_row = "| Established identity | No prior annual sheet | 2013 season-close baseline | Baseline created | 2013 exit-review evidence |"
    elif player.continuity:
        identity = ("Carries forward the supported 2013 player at this checkpoint. "
                    "No 2014 on-field development evidence has displaced that baseline.")
        established = player.inherited_identity
        change_row = ("| Established identity | See 2013 profile | Carried forward | Retained pending new evidence | "
                      "A season rollover alone is not a football cause of change |")
    else:
        identity = ("New Jacksonville acquisition. Preserve established NFL ability from permitted evidence; "
                    "Jacksonville terminology, teammate timing and role access are new.")
        established = player.inherited_identity
        change_row = ("| Established identity | No Jacksonville prior profile | Baseline import required | Not a reset to zero | "
                      "Use only evidence permitted at this checkpoint |")
    rows = [("Overall","— /10"),("Athleticism","— /10"),("Speed","— /10"),("Strength / Power","— /10"),
            ("Agility / Change of direction","— /10"),("Technique","— /10"),("Football IQ","— /10"),
            (traits[0],"— /10"),(traits[1],"— /10"),(traits[2],"— /10")]
    grades = "\n".join(f"| {a} | {b} | Unassessed |" for a,b in rows)
    comparison = "\n".join(f"| {x} | Unassessed | Unassessed | Unassessed |"
                            for x in ("Speed","Size / Length","Strength","Explosiveness",traits[0],traits[1]))
    return f"""# {player.player} — {season} NFL Player Sheet

**Team:** Jacksonville Jaguars  
**Season:** {season}  
**Checkpoint:** {checkpoint}  
**Age:** {age}  
**Position:** {player.pos}  
**NFL standing:** Unassessed  
**Player identity:** {identity}  
**Previous annual profile:** {prior}  

> Personnel snapshot only. The /10 grades are human-facing summaries and do not feed the game resolver directly.
> Established capabilities carry forward unless causal evidence supports a change.

## Player grades

| Category | Grade | NFL standing |
| --- | ---: | --- |
{grades}

## League comparison

| Trait | vs. Average | vs. Best | vs. Worst |
| --- | --- | --- | --- |
{comparison}

## Established player state

- {established}

## Year-over-year change

| Area | Prior profile | Current checkpoint | Change | Evidence / football reason |
| --- | --- | --- | --- | --- |
{change_row}
| Physical | Unassessed | Unassessed | Unassessed | Do not infer change from age or calendar rollover |
| Technical | Unassessed | Unassessed | Unassessed | Requires position-specific evidence |
| Processing / Football IQ | Unassessed | Unassessed | Unassessed | Separate recognition from playbook knowledge |
| Consistency | Unassessed | Unassessed | Unassessed | Repeat rate is separate from peak capability |
| Role / system access | Unassessed | Unassessed | Unassessed | Role is not the same thing as talent |

## What makes him [NFL standing]

- Unassessed until the standing is supported by checkpoint evidence.

## Historical comparison

**Level historically:** Unassessed  
**Closest player comparison:** Unassessed  
**What is similar:** Unassessed  
**What is different:** Unassessed  

## Play style

Unassessed on the annual sheet.

## Best traits

- Not yet converted into an annual-sheet rank. Start with the established player state above.

## Main weaknesses

- Not yet converted into an annual-sheet rank. Do not manufacture a weakness to fill the field.

## Evidence and uncertainty

- **Primary evidence:** {player.source_note}
- **What is established:** See established player state.
- **What remains uncertain:** Numeric grades, league standing and unsupported year-over-year changes.
- **What would change the assessment:** New permitted practice, film, medical or game evidence tied to the relevant trait.

**One-line description:**  
{identity}
"""

def target_path(season: int, player_name: str) -> Path:
    return ROOT / f"career/{season}/player_profiles/{slugify(player_name)}.md"

def check_profiles(season: int, players: list[SheetPlayer]) -> list[str]:
    errors=[]
    for player in players:
        path=target_path(season, player.player)
        if not path.exists():
            errors.append(f"missing annual profile: {path.relative_to(ROOT)}")
            continue
        text=path.read_text(encoding="utf-8")
        for item in (f"# {player.player} — {season} NFL Player Sheet", f"**Position:** {player.pos}",
                     "## Established player state","## Year-over-year change","## Player grades"):
            if item not in text:
                errors.append(f"{path.relative_to(ROOT)} missing required content: {item}")
    return errors

def main() -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--season",type=int,required=True)
    p.add_argument("--check",action="store_true")
    p.add_argument("--force",action="store_true")
    args=p.parse_args()
    checkpoint,players=load_season_players(args.season)
    if args.check:
        errors=check_profiles(args.season,players)
        if errors:
            print("ANNUAL_PLAYER_SHEETS: STALE")
            for e in errors: print("- "+e)
            return 1
        print(f"ANNUAL_PLAYER_SHEETS: READY season {args.season}, {len(players)} required")
        return 0
    created=updated=kept=0
    for player in players:
        path=target_path(args.season,player.player)
        path.parent.mkdir(parents=True,exist_ok=True)
        if path.exists() and not args.force:
            kept+=1; continue
        existed=path.exists()
        path.write_text(render_player_sheet(player,args.season,checkpoint),encoding="utf-8")
        if existed: updated+=1
        else: created+=1
    print(f"ANNUAL_PLAYER_SHEETS: season {args.season}, created {created}, updated {updated}, kept {kept}")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
