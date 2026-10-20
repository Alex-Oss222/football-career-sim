"""The Game Report's layout and its agreement with the closed game (game week version 2, Phase A).

From 2014 Week 6 every played game's result page, playoff games included, is
the Game Report (runtime.seasons.SeasonPaths.game_report), written from the
Game Report template (``TEMPLATE``; docs/game_week_v2.md, section 6). The
guidance for writing it is docs/game_output_workflow.md, and for its media
docs/head_coach_media_method.md. 2014 Weeks 1 to 5 keep their output.md as
written, in the layout of foundation/templates/regular_season_output_template.md.

Layout. The report's sections are the template's level-two headings, in the
template's order: Coach record, sections 1 to 7, Full game statistics. A
report opened before the game carries some of them in that order (its
preparation and pregame media); once the game has closed it carries every one.
No other level-two heading appears and none twice.

The statistics last. Once the game has closed, the report holds exactly one
box-score block (the two markers scripts/render_box_score.py fills, ``BLOCK``),
for the game's own event and Jacksonville, under "Full game statistics", and
nothing but blank lines follows its closing marker. The template's markers name
no game yet (``EVENT_PLACEHOLDER`` and ``TEAM_PLACEHOLDER``); once the game has
closed, render_box_score.py --write and the rebuild name it (``place_markers``)
and fill the block. Before the game closes, the page carries no filled box score
and no final score.

Reconciled with the closed game. The header's round line names the game
("Regular-season Week 6", or the playoff round), the header's "Final:" line is
the final score with the winner first (each club by its full name, its place or
its nickname), the "Final score by quarter" table is the game book's line score
(the periods scored in, as render_box_score.py --line-score prints it), an
Overtime subheading appears exactly when overtime was played, and section 7's
"Record after game" names Jacksonville's record after the game (a playoff
game's may add the postseason record). The box score itself is checked against
the closed game by scripts/render_box_score.stale_blocks. The football account
is not parsed: whether each told play matches the game book is the editorial
review's to establish (docs/game_output_workflow.md, section 5).
"""
from __future__ import annotations

import re
from pathlib import Path

from .seasons import GAME_REPORT_FROM, SeasonPaths

ROOT = Path(__file__).resolve().parents[1]
JAX = "Jacksonville Jaguars"
TEMPLATE = "foundation/templates/game_week/game_report_template.md"
EVENT_PLACEHOLDER, TEAM_PLACEHOLDER = "{{EVENT_ID}}", "{{TEAM_NAME}}"
STATISTICS = "Full game statistics"
QUARTERS = "Final score by quarter"
OVERTIME = "Overtime"
RECORD = "**Record after game:**"
# The box-score block of a result page: its opening marker names the game and the club listed first.
BLOCK = re.compile(
    r"(<!-- box-score event=(?P<event>[^ ]+) team=(?P<team>.+?) -->\n)(?P<body>.*?)(<!-- /box-score -->)",
    re.S,
)
H2 = re.compile(r"^## (.+?)\s*$", re.M)
FINAL = re.compile(r"^\*\*Final: (.+?) (\d+), (.+?) (\d+)\*\*\s*$")
RECORD_TOKEN = re.compile(r"(?<![\d-])\d{1,2}-\d{1,2}(?:-\d{1,2})?(?![\d-])")


def sections(root=ROOT):
    """The report's level-two headings, in the template's order."""
    text = (Path(root) / TEMPLATE).read_text(encoding="utf-8")
    return [h.strip() for h in H2.findall(text)]


def is_placeholder(match):
    return match.group("event") == EVENT_PLACEHOLDER or match.group("team") == TEAM_PLACEHOLDER


def place_markers(text, event_id, team=JAX):
    """``text`` with the template's unnamed box-score markers naming the game and the club."""
    marker = "<!-- box-score event=%s team=%s -->" % (EVENT_PLACEHOLDER, TEAM_PLACEHOLDER)
    return text.replace(marker, "<!-- box-score event=%s team=%s -->" % (event_id, team))


def names(club):
    """The words a report may name a club by: its full name, its place and its nickname."""
    return {club, club.rsplit(" ", 1)[0], club.split()[-1]}


def overtime_played(receipt):
    from .play_detail import DRIVE_SUMMARY_FIELDS
    half = DRIVE_SUMMARY_FIELDS.index("half")
    return any(str(row[half]).startswith("OT") for row in receipt.get("drives") or ())


def outcome(receipt, club):
    other = receipt["home"] if receipt["away"] == club else receipt["away"]
    mine, theirs = receipt["final_score"][club], receipt["final_score"][other]
    return (mine > theirs) - (mine < theirs)


def record_forms(receipts, club):
    """The club's record over ``receipts`` as a report may write it: W-L-T, and W-L when untied."""
    results = [outcome(r, club) for r in receipts]
    w, l, t = results.count(1), results.count(-1), results.count(0)
    forms = {"%d-%d-%d" % (w, l, t)}
    if not t:
        forms.add("%d-%d" % (w, l))
    return forms


def _section(text, heading, level=3):
    """The lines under a heading of ``level`` until the next heading of that level or higher."""
    lines, out, inside = text.splitlines(), [], False
    for line in lines:
        m = re.match(r"^(#{1,6}) (.+?)\s*$", line)
        if m and inside and len(m.group(1)) <= level:
            break
        if m and len(m.group(1)) == level and m.group(2).strip() == heading:
            inside = True
            continue
        if inside:
            out.append(line)
    return out if inside else None


def _table(lines):
    rows = [[c.strip() for c in line.strip().strip("|").split("|")] for line in lines if line.strip().startswith("|")]
    return [r for r in rows if not all(re.fullmatch(r":?-{3,}:?", c) for c in r)]


def report_errors(text, receipt=None, game=None, club=JAX, root=ROOT, label="Game Report"):
    """The Game Report's problems: its layout, and once the game has closed (``receipt``, with
    ``game`` its fixture) the statistics last and the result reconciled with the game book."""
    errors = []
    order = sections(root)
    found = [h.strip() for h in H2.findall(text)]
    for heading in found:
        if heading not in order:
            errors.append("%s: '## %s' is not a section of the Game Report (%s)" % (label, heading, "; ".join(order)))
    known = [h for h in found if h in order]
    for heading in sorted({h for h in known if known.count(h) > 1}):
        errors.append("%s: '## %s' appears twice" % (label, heading))
    if [order.index(h) for h in known] != sorted(order.index(h) for h in known):
        errors.append("%s: the sections are not in the template's order (%s)" % (label, "; ".join(order)))
    blocks = list(BLOCK.finditer(text))
    filled = [b for b in blocks if not is_placeholder(b)]
    head = text.split("\n## ", 1)[0]
    finals = [m for m in (FINAL.match(line) for line in head.splitlines()) if m]
    if receipt is None:
        if filled:
            errors.append("%s: a box score is filled before the game has been played" % label)
        if finals:
            errors.append("%s: the header gives a final score before the game has been played" % label)
        return errors
    for heading in order:
        if heading not in found:
            errors.append("%s: the game has been played; '## %s' is missing" % (label, heading))
    errors += _statistics_errors(text, receipt, club, blocks, label)
    errors += _header_errors(head, finals, receipt, game, label)
    errors += _line_score_errors(text, receipt, label)
    played_ot = overtime_played(receipt)
    has_ot = _section(text, OVERTIME) is not None
    if played_ot and not has_ot:
        errors.append("%s: the game went to overtime; '### %s' is missing" % (label, OVERTIME))
    if has_ot and not played_ot:
        errors.append("%s: '### %s' is written, but the game ended in regulation" % (label, OVERTIME))
    errors += _record_errors(text, receipt, game, club, root, label)
    return errors


def _statistics_errors(text, receipt, club, blocks, label):
    errors = []
    if len(blocks) != 1:
        return ["%s: the page needs exactly one box score under '## %s' (%d found)" % (label, STATISTICS, len(blocks))]
    block = blocks[0]
    if is_placeholder(block):
        return ["%s: the box score does not name the game yet; fill it from the closed game (python "
                "scripts/render_box_score.py --season %d --write the page, or the rebuild)" % (label, receipt["season"])]
    if block.group("event") != receipt["event_id"] or block.group("team") != club:
        errors.append("%s: the box score names %s for %s; it is the game's own, %s for %s"
                      % (label, block.group("event"), block.group("team"), receipt["event_id"], club))
    statistics = re.search(r"^## %s\s*$" % re.escape(STATISTICS), text, re.M)
    if statistics is None or statistics.start() > block.start():
        errors.append("%s: the box score sits outside '## %s'" % (label, STATISTICS))
    if text[block.end():].strip():
        errors.append("%s: the box score is not last; nothing follows the full game statistics" % label)
    return errors


def _header_errors(head, finals, receipt, game, label):
    errors = []
    away, home = receipt["away"], receipt["home"]
    title = next((line for line in head.splitlines() if line.startswith("# ")), "")
    m = re.match(r"^# (.+?) at (.+?)\s*$", title)
    if not m or m.group(1) not in names(away) or m.group(2) not in names(home):
        errors.append("%s: the title names the clubs away first (%s at %s)" % (label, away, home))
    if game is not None:
        lines = [l.strip() for l in head.splitlines()]
        if game.get("game_type") == "postseason":
            wanted = game["round_name"]
            ok = any(l.startswith("**") and wanted in l and not l.startswith("**Final") for l in lines)
        else:
            wanted = "Regular-season Week %d" % int(game["week"])
            ok = any(re.fullmatch(r"\*\*%s\*\*\s*" % re.escape(wanted), l) for l in lines)
        if not ok:
            errors.append("%s: the header's round line is '**%s**'" % (label, wanted))
    if len(finals) != 1:
        return errors + ["%s: the header needs one '**Final: winner score, loser score**' line" % label]
    f = finals[0]
    score = receipt["final_score"]
    first = next((c for c in (away, home) if f.group(1) in names(c)), None)
    second = next((c for c in (away, home) if f.group(3) in names(c)), None)
    if first is None or second is None or first == second:
        return errors + ["%s: the Final line names %s and %s, not the two clubs" % (label, f.group(1), f.group(3))]
    if (int(f.group(2)), int(f.group(4))) != (score[first], score[second]):
        errors.append("%s: the Final line reads %s %s, %s %s; the game ended %s %d, %s %d" % (
            label, f.group(1), f.group(2), f.group(3), f.group(4), first, score[first], second, score[second]))
    elif score[first] < score[second]:
        errors.append("%s: the Final line names the winner first" % label)
    return errors


def _line_score_errors(text, receipt, label):
    from .gamebook import line_score_table
    lines = _section(text, QUARTERS)
    if lines is None:
        return ["%s: '### %s' is missing" % (label, QUARTERS)]
    expected = _table(line_score_table(receipt).splitlines())
    written = _table(lines)
    clubs = [receipt["away"], receipt["home"]]
    if len(written) != 3 or [c.lower() for c in written[0]] != [c.lower() for c in expected[0]]:
        return ["%s: the line score's columns are %s, the periods scored in" % (label, ", ".join(expected[0]))]
    for row, want, club in zip(written[1:], expected[1:], clubs):
        if row[0] not in names(club) or row[1:] != want[1:]:
            return ["%s: the line score differs from the game book (%s: %s)" % (label, club, ", ".join(want[1:]))]
    return []


def _record_errors(text, receipt, game, club, root, label):
    if game is None:
        return []
    line = next((l for l in text.splitlines() if l.strip().startswith(RECORD)), None)
    if line is None:
        return ["%s: section 7 needs its '%s' line" % (label, RECORD)]
    from . import game_weeks
    paths = SeasonPaths(int(receipt["season"]), root)
    week = int(game["week"])
    postseason = game.get("game_type") == "postseason"
    regular = [r for r in game_weeks.regular_receipts(paths) if club in (r["away"], r["home"])
               and (postseason or int(r["week"]) <= week)]
    allowed = record_forms(regular, club)
    if postseason:
        post = [r for r in game_weeks.postseason_receipts(paths) if club in (r["away"], r["home"])
                and int(r["week"]) <= week]
        allowed |= record_forms(post, club)
    tokens = RECORD_TOKEN.findall(line)
    wanted = sorted(record_forms(regular, club), key=len)[0]
    if not tokens or tokens[0] not in record_forms(regular, club) or any(t not in allowed for t in tokens):
        return ["%s: the record after the game is %s" % (label, wanted)]
    return []


def report_games(paths, club=JAX):
    """[(game, report path, closed record or None)] of the season's games written as a Game Report."""
    from . import game_weeks
    year, first = GAME_REPORT_FROM
    regular = game_weeks.regular_receipts(paths)
    post = game_weeks.postseason_receipts(paths)
    out = []
    for game in game_weeks.club_games(paths, club):
        postseason = game.get("game_type") == "postseason"
        if paths.year < year or (paths.year == year and not postseason and int(game["week"]) < first):
            continue
        path = paths.game_report(int(game["week"]), postseason)
        out.append((game, path, game_weeks.closed_receipt(post if postseason else regular, game)))
    return out


def validation_errors(root=ROOT, seasons=None):
    """Every Game Report on file against its layout and, once its game has closed, the game."""
    from .seasons import active_season
    root = Path(root).resolve()
    years = sorted(set(seasons or ()) | {GAME_REPORT_FROM[0], active_season(root)})
    errors = []
    for year in years:
        paths = SeasonPaths(year, root)
        if not paths.schedule.is_file():
            continue
        for game, path, receipt in report_games(paths):
            if path.is_file():
                rel = path.relative_to(root).as_posix()
                errors += report_errors(path.read_text(encoding="utf-8"), receipt, game, root=root, label=rel)
    return errors
