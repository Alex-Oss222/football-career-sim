"""The clean-page rule (docs/rebuild_plan.md, rule 4) and the folder-map rule
(stored-facts rule 2), as checks for scripts/validate_repository.py.

Clean pages. A page the user reads is football only. ``page_errors`` fails a
page that shows an internal code or identifier (1C, 5A, E1, U5, gsis ids,
register keys, snake_case names, code spans, entry numbers), links to a system
file (.json, .py, .csv and the like) or into the data area or the code,
names a script or module, carries HTML markup other than the page builder's
own invisible markers (runtime/player_pages.MARKERS) and the event-record
marker an event owner carries on a line of its own (runtime/events.EVENT_META,
the whole line), a policy note, a disclaimer or a version label, or uses the
words engine, branch, receipt,
kernel, ledger, snapshot, checkpoint or simulation. A player's full name
that contains one of the words (Andre Branch, Tyvon Branch) is allowed by
name, from the birth-date registry and the permanent player records; any
other use of the word is caught. Every link form is checked: inline links,
links with a title ([x](path "t")) and reference definitions ([x]: path).

The page history map is pinned: ``history_pin_errors`` fails when the map's
bytes no longer match the digest the folder map records beside it
(runtime/season_layout.PAGE_HISTORY_SHA256), so an entry cannot be added or
changed (which would exempt a page) unless the pin changes in the same commit.

Which pages: every page the player page builder writes, and every Markdown
page under career/ written from 2014 Week 6 on. The pages written before
Week 6 are history (rule 1): the folder map's PAGE_HISTORY file holds each
one's path and the sha256 digest of its bytes as they stood before Week 6
("pages"), with the length of those bytes beside it ("lengths"). A page is
exempt while its bytes still match that digest. An append-only history page
(the medical history, the annual record, the roster decisions), whose
current bytes begin with its exact pre-Week-6 bytes (the first "length"
bytes match the digest), is checked only on what follows them: an appended
entry is a page written from Week 6 on. Any other change (an edited old
line, a page rewritten by hand or by its generator: the standings, the desk)
makes the whole page a new one, so a generator must be cleaned before it
rewrites a page after Week 5 (docs/rebuild_plan.md names the build step that
cleans each such view). A page the player page builder writes is checked by
its marker.

Folder map. ``folder_map_errors`` fails when a script or runtime module,
other than the folder map itself (runtime/season_layout.py, runtime/seasons.py)
and the frozen research builders (scripts/research/), writes a season folder
name or a year into a path: a path-like string constant with a year segment
(career/2014/..., data/2013) or a season folder segment (Regular_Season,
05_Regular_Season, ...); a season folder, a logical season folder name (the
top-level names of LEGACY_MOVES: stats, regular_season, trades, ...) or a
year used as a path part, an operand of "/" or a string argument of Path(),
PurePosixPath(), os.path.join() or joinpath(); or a formatted path that
starts with career/ or data/ followed by a slot (an f-string, a %-format, a
.format() call or a + concatenation). A year passed to the map
(SeasonPaths(2014), logical_path(year, "stats/...")) is the map's to place. Named research and
playbook files whose names carry their year (library/data/2012_..., the
playbook iterations) are fixed artifacts, not season folders, and are not
season paths.
"""
from __future__ import annotations

import ast
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

from .events import EVENT_META
from .season_layout import LEGACY_MOVES, NUMBERED_FOLDERS, PAGE_HISTORY, PAGE_HISTORY_SHA256

ROOT = Path(__file__).resolve().parents[1]
WORDS = re.compile(r"\b(engines?|branch(?:es)?|receipts?|kernels?|ledgers?|snapshots?|checkpoints?|"
                   r"simulat(?:e|es|ed|ing|ion|ions|or|ors))\b", re.I)
# Licence names that contain a checked code: the Creative Commons licences of the photo credits.
# A player's name that contains a checked word (Andre Branch) is allowed by name (proper_names).
ALLOWED = (re.compile(r"\bCC BY(?:-[A-Z]{2})*(?: \d\.\d)?"), re.compile(r"\bCC0\b"))
CODES = (
    (re.compile(r"(?<![\w'-])\d{1,2}[A-Z](?![\w'-])"), "internal code"),
    (re.compile(r"(?<![\w'-])[A-Z]\d{1,3}[a-z]?(?![\w'-])"), "internal code"),
    (re.compile(r"\b[A-Z]{2,}(?:-[0-9A-Z]+)+\b"), "internal identifier"),
    (re.compile(r"\b\d{2}-\d{7}\b"), "player identifier"),
    (re.compile(r"\b[a-z][a-z0-9]*(?:_[a-z0-9]+)+\b"), "system name"),
    (re.compile(r"`"), "code span"),
    (re.compile(r"\bEntr(?:y|ies) \d+"), "entry number"),
    (re.compile(r"\b[0-9a-f]{12,}\b"), "digest"),
)
SCRIPTS = re.compile(r"(\b[\w/.-]+\.(?:py|sh)\b|\bpython3?\b|(?<![\w.])(?:scripts|runtime|tests)/|\bruntime\.)")
POLICY = re.compile(r"(\bdisclaimer|\bpolicy note|\b(?:evaluation|assessment|recording|privacy) policy\b|"
                    r"\banswer key\b|\bgenerated by\b|\bauto-?generated\b|\bdo not edit\b|\bhand-edit|"
                    r"\btheoretical\b|\bnot an? (?:game|rating|probability|measurement|prediction)\b|"
                    r"\bplaceholder\b|\bTODO\b|\bTBD\b)", re.I)
VERSION = re.compile(r"(\bv\d+(?:\.\d+)*\b|\bversion \d|\bschema\b|\b20\d\d\.\d\b|\bsha-?256\b)", re.I)
HTML = re.compile(r"<[A-Za-z!/][^>]*>")
# A link destination may hold one level of parentheses (photo source pages do).
LINK = re.compile(r"(!?)\[([^\]\n]*)\]\(((?:[^()\s]|\([^()\s]*\))+)\)")
# A link with a title ([x](path "t")) and a reference definition ([x]: path "t"), checked like a link.
TITLE = r"(?:\"[^\"\n]*\"|'[^'\n]*'|\([^()\n]*\))"
TITLED_LINK = re.compile(r"(!?)\[([^\]\n]*)\]\(\s*<?([^\s<>()]+)>?\s+" + TITLE + r"\s*\)")
REFERENCE = re.compile(r"^ {0,3}\[([^\]\n^][^\]\n]*)\]:\s*<?([^\s<>]+)>?(?:\s+" + TITLE + r")?\s*$")
SYSTEM_SUFFIXES = (".json", ".jsonl", ".py", ".csv", ".gz", ".sqlite", ".db", ".yml", ".yaml", ".toml", ".sh",
                   ".txt", ".pkl", ".log")
SYSTEM_DIRS = ("data", "runtime", "scripts", "tests", ".sim_cache")


def proper_names(root=ROOT):
    """The pattern of the players' full names that contain a checked word (Alan Branch, Andre
    Branch, Tyvon Branch): the names in the birth-date registry and the permanent player records.
    Only these names let the word through; any other use of it is caught."""
    root = Path(root).resolve()
    if root not in _NAMES:
        from . import people, player_bios
        names = set()
        try:
            names |= set(player_bios.load(root, overrides=False))
        except (OSError, ValueError):
            pass
        names |= {r["name"] for r in people.load_all(root).values()}
        found = sorted((n for n in names if WORDS.search(n)), key=lambda n: (-len(n), n))
        _NAMES[root] = re.compile(r"\b(?:%s)\b" % "|".join(map(re.escape, found))) if found else None
    return _NAMES[root]


_NAMES = {}


def page_errors(rel, text, markers=(), root=ROOT, first_line=1):
    """The clean-page problems of one page (``rel`` is its repository path; ``first_line`` numbers
    the first line of ``text`` when it is the appended part of a history page); a player's name
    from ``root``'s registry and records that contains a checked word is allowed."""
    problems = []
    names = proper_names(root)
    lines = text.splitlines()
    for number, line in enumerate(lines, first_line):
        if line.strip() in markers or EVENT_META.fullmatch(line.strip()):
            continue
        found = []
        reference = REFERENCE.match(line)
        dests = [m.group(3) for m in LINK.finditer(line)] + [m.group(3) for m in TITLED_LINK.finditer(line)]
        dests += [reference.group(2)] if reference else []
        for dest in dests:
            parts = urlsplit(dest)
            if parts.scheme or parts.netloc:
                continue
            path = parts.path.lower()
            target = (Path(rel).parent / parts.path).as_posix()
            segments = [s for s in re.split(r"/+", _normalise(target)) if s]
            if path.endswith(SYSTEM_SUFFIXES) or (segments and segments[0] in SYSTEM_DIRS):
                found.append("link to a system file: %s" % dest)
        prose = reference.group(1) if reference else TITLED_LINK.sub(lambda m: m.group(2), line)
        prose = LINK.sub(lambda m: m.group(2), prose)
        prose = re.sub(r"https?://\S+", "", prose)
        for pattern in ALLOWED + ((names,) if names else ()):
            prose = pattern.sub(" ", prose)
        for m in WORDS.finditer(prose):
            found.append("system word: %s" % m.group(1))
        # A photo credit is quoted as its licence requires (a photographer's user name may
        # look like a code); only the words, markup and links are checked on it.
        codes = () if line.startswith("*Photo: ") else CODES
        for pattern, label in codes:
            for m in pattern.finditer(prose):
                found.append("%s: %s" % (label, m.group(0)))
        for m in SCRIPTS.finditer(prose):
            found.append("script or module name: %s" % m.group(0))
        for m in POLICY.finditer(prose):
            found.append("policy note or disclaimer: %s" % m.group(0))
        for m in VERSION.finditer(prose):
            found.append("version label: %s" % m.group(0))
        for m in HTML.finditer(prose):
            found.append("markup: %s" % m.group(0))
        problems += ["%s:%d: %s" % (rel, number, f) for f in found]
    return problems


def _normalise(path):
    out = []
    for part in path.split("/"):
        if part == "..":
            if out:
                out.pop()
        elif part not in ("", "."):
            out.append(part)
    return "/".join(out)


def digest(data):
    """The digest the page history records for a page's bytes."""
    return hashlib.sha256(data).hexdigest()


def _history_data(root):
    path = Path(root) / PAGE_HISTORY
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def history(root=ROOT):
    """{repository path: digest} of the pages written before 2014 Week 6."""
    return dict(_history_data(root).get("pages", {}))


def history_lengths(root=ROOT):
    """{repository path: length in bytes} of the same pages as they stood before Week 6."""
    return dict(_history_data(root).get("lengths", {}))


def unchecked_prefix(data, recorded, length):
    """How many leading bytes of a history page are exempt: all of them while the page matches its
    digest; the original ``length`` bytes when the page begins with them exactly (an append-only
    page with entries added after Week 5); none once an old byte has changed."""
    if recorded is None:
        return 0
    if digest(data) == recorded:
        return len(data)
    if isinstance(length, int) and 0 < length < len(data) and digest(data[:length]) == recorded:
        return length
    return 0


def history_pin_errors(root=ROOT):
    """The page history map against its pin (runtime/season_layout.PAGE_HISTORY_SHA256)."""
    path = Path(root) / PAGE_HISTORY
    if not path.is_file():
        return ["Page history map missing: %s" % PAGE_HISTORY]
    found = digest(path.read_bytes())
    if found != PAGE_HISTORY_SHA256:
        return ["Page history map changed without its pin: %s is %s, the folder map pins %s; a page written "
                "before Week 6 is never added or changed after the fact" % (PAGE_HISTORY, found, PAGE_HISTORY_SHA256)]
    return []


def checked_parts(root=ROOT):
    """(path, text, first line) for every page or part of a page the rule covers: built pages,
    pages newer than the history, the entries appended to a history page after its pre-Week-6
    bytes, and history pages whose old bytes changed (the whole page)."""
    from .player_pages import built_page
    root = Path(root)
    old, lengths = history(root), history_lengths(root)
    out = []
    for path in sorted((root / "career").rglob("*.md")):
        rel = path.relative_to(root).as_posix()
        data = path.read_bytes()
        text = data.decode("utf-8")
        if built_page(text):
            out.append((rel, text, 1))
            continue
        cut = unchecked_prefix(data, old.get(rel), lengths.get(rel))
        if cut == len(data):
            continue
        head = data[:cut].decode("utf-8")
        out.append((rel, data[cut:].decode("utf-8"), head.count("\n") + 1))
    return out


def checked_pages(root=ROOT):
    """(path, text) for every page or appended part the rule covers (``checked_parts``)."""
    return [(rel, text) for rel, text, _ in checked_parts(root)]


def clean_errors(root=ROOT):
    from .player_pages import MARKERS
    errors = []
    for rel, text, first in checked_parts(root):
        errors += page_errors(rel, text, MARKERS, root, first_line=first)
    return errors


# ------------------------------------------------------------------ folder map
SEASON_FOLDERS = frozenset(set(NUMBERED_FOLDERS) | set(NUMBERED_FOLDERS.values()) | {"League", "Supporting_Records"})
# The logical season folder names code passes to the map (SeasonPaths(year).record("stats/...")):
# the top-level folder names of LEGACY_MOVES. Written as a path part of their own (ROOT / "career" /
# str(year) / "stats"), they place a season record without the map. A file name (depth_chart.json)
# inside a folder the map gave is not a season path.
LOGICAL_NAMES = frozenset(key.split("/")[0] for key in LEGACY_MOVES if "." not in key.split("/")[0])
PART_NAMES = SEASON_FOLDERS | LOGICAL_NAMES
MAP_MODULES = ("runtime/season_layout.py", "runtime/seasons.py")
YEAR = re.compile(r"^(19|20)\d{2}$")
PATH_TOKEN = re.compile(r"[^\s()\[\]<>\"'`,;|]+")
PATH_START = ("career/", "data/", "library/", "state/", "docs/", "../", "./")
# Calls whose string arguments are path parts, like the operands of "/".
PATH_CALLS = frozenset({"Path", "PurePath", "PurePosixPath", "PureWindowsPath"})
PATH_METHODS = frozenset({"join", "joinpath"})
# A formatted path into a season: career/ or data/ at the start of a path (the start of the text,
# after a space, quote or bracket, after ../, or after a slot and /), followed by a slot ({year},
# %d, {}). A research file named by its year inside library/data/ is not a season path.
_START = r"(?:^/?|[\s(\[\"'`=]|\.\./)"
FORMATTED_ROOT = re.compile(_START + r"(?:career|data)/$")
PERCENT_ROOT = re.compile(r"(?:" + _START + r"|%[sd]/)(?:career|data)/%")
FORMAT_ROOT = re.compile(r"(?:" + _START + r"|\}/)(?:career|data)/\{")


def _docstrings(tree):
    out = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            first = node.body[0] if node.body else None
            if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) and isinstance(first.value.value, str):
                out.add(id(first.value))
    return out


def _path_like(token):
    return "/" in token and (token.startswith(PATH_START) or re.search(r"\.(md|json|csv|gz)\b", token)
                             or any(seg in SEASON_FOLDERS for seg in token.split("/")))


def string_errors(value):
    """Why a string constant writes a season path itself, or None."""
    for token in PATH_TOKEN.findall(value):
        if "://" in token or not _path_like(token):
            continue
        segments = token.split("/")
        if any(YEAR.match(s) for s in segments):
            return "a year in a path (%s)" % token
        if any(s in SEASON_FOLDERS for s in segments):
            return "a season folder in a path (%s)" % token
    return None


def part_errors(value):
    """Why a string used as a path part (an operand of "/", an argument of Path() or
    os.path.join()) places a season record itself, or None."""
    for segment in value.split("/"):
        if segment in PART_NAMES or YEAR.match(segment):
            return "a season folder, logical season name or year as a path part (%r)" % value
    return None


def _is_str(node):
    return isinstance(node, ast.Constant) and isinstance(node.value, str)


def _path_call(node):
    """Whether a call joins path parts: Path(...), PurePosixPath(...), os.path.join(...),
    posixpath.join(...) or path.joinpath(...); a string's own join ("/".join) is not one."""
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    if isinstance(func, ast.Name):
        return func.id in PATH_CALLS
    if isinstance(func, ast.Attribute):
        if func.attr in PATH_CALLS:
            return True
        return func.attr in PATH_METHODS and not _is_str(func.value)
    return False


def formatted_errors(node):
    """Why a formatted string (f-string, %-format, .format(), +) builds a season path, or None."""
    if isinstance(node, ast.JoinedStr):
        for piece, after in zip(node.values, node.values[1:]):
            if _is_str(piece) and isinstance(after, ast.FormattedValue) and FORMATTED_ROOT.search(piece.value):
                return "a formatted season path (%s{...})" % piece.value
    elif isinstance(node, ast.BinOp) and _is_str(node.left):
        if isinstance(node.op, ast.Mod) and PERCENT_ROOT.search(node.left.value):
            return "a formatted season path (%r %% ...)" % node.left.value
        if (isinstance(node.op, ast.Add) and not _is_str(node.right)
                and FORMATTED_ROOT.search(node.left.value)):
            return "a season path built by + (%r + ...)" % node.left.value
    elif (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "format"
          and _is_str(node.func.value) and FORMAT_ROOT.search(node.func.value.value)):
        return "a formatted season path (%r.format(...))" % node.func.value.value
    return None


def module_errors(rel, source):
    tree = ast.parse(source)
    docs = _docstrings(tree)
    parents = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parents[id(child)] = node
    errors = []
    for node in ast.walk(tree):
        why = formatted_errors(node)
        if why is None and _is_str(node) and id(node) not in docs:
            why = string_errors(node.value)
            parent = parents.get(id(node))
            if why is None and isinstance(parent, ast.BinOp) and isinstance(parent.op, ast.Div):
                why = part_errors(node.value)
            if why is None and _path_call(parent) and node in parent.args:
                why = part_errors(node.value)
        if why:
            errors.append((node.lineno, "%s:%d: writes %s itself; find it through the folder map "
                           "(runtime/season_layout.py)" % (rel, node.lineno, why)))
    return [e for _, e in sorted(errors)]


def folder_map_errors(root=ROOT):
    root = Path(root)
    errors = []
    for path in sorted(list((root / "scripts").glob("*.py")) + list((root / "runtime").glob("*.py"))):
        rel = path.relative_to(root).as_posix()
        if rel in MAP_MODULES:
            continue
        errors += module_errors(rel, path.read_text(encoding="utf-8"))
    return errors
