"""The Game Report's layout and its agreement with the closed game (game week version 2, Phase A).

From 2014 Week 6 every played game's result page, playoff games included, is
the Game Report (runtime.seasons.SeasonPaths.game_report). The guidance for
writing it is docs/game_output_workflow.md. 2014 Weeks 1 to 5 keep their
output.md as written, in the layout of
foundation/templates/regular_season_output_template.md.

Layout, chosen per game (``layout``). From 2014 Week 7, every postseason game
included, the report is written from the Game Report template (``TEMPLATE``;
docs/game_week_v2.md, section 6) and its sections are the template's
level-two headings in its order: Coach record, sections 1 to 5, Full game
statistics, with no media sections and a short football review, by the user's
decision of October 24, 2026, verbatim: "Dropping the researched media sections
i like the full stats so trimming the unit review". 2014 Week 6's report, the
one Game Report before Week 7 (runtime.seasons.GAME_REPORT_FROM), keeps the
layout it was written in, frozen here (``WEEK_6_LAYOUT``): Coach record,
sections 1 to 7 with the pregame media in section 2 and the postgame media in
section 4 (docs/head_coach_media_method.md), Full game statistics. A report
opened before the game carries some of its layout's sections in that order (its
pregame sections); once the game has closed it carries every one. No other
level-two heading appears and none twice.

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
Overtime subheading appears exactly when overtime was played, and the final
record section's "Record after game" names Jacksonville's record after the game
(a playoff game's may add the postseason record). The box score itself is
checked against the closed game by scripts/render_box_score.stale_blocks.

The story's figures (``story_errors``). Every score written in the game story
(the layout's "The game" section, ``Layout.story``) is one the game actually
stood at, either way round, from 0-0 through the scoring summary to the final
(a touchdown's score before its try included), or a club's record before or
after the game; and wherever the report says a club of the game won, beat,
defeated, lost or fell by a score, that is the final score and that club the
winner or the loser. The rest of the football account (whether each told play
matches the game book) is the editorial review's to establish
(docs/game_output_workflow.md, section 5).

No figures twice (``table_errors``). The only tables before the full game
statistics are the coach record's, the line score and the after-action
injuries table in the template's columns: a statistics table in the story is
refused, as the statistics are the appendix's.

Pregame frozen (``pregame_errors``). At the game-day commit, before kickoff,
scripts/freeze_pregame.py records the sha256 of the layout's pregame sections,
the numbered sections before the game story (``Layout.pregame``: section 1, the
preparation, from 2014 Week 7; sections 1 and 2, the preparation and the
pregame media, in Week 6), in the week's data folder
(runtime/decisions.WeekPages.pregame). Once the game has closed the record must
exist and hold the layout's pregame sections, each as it froze it: the pregame
sections are never rewritten with the result known.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
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
# The Game Report's layout as 2014 Week 6's report was written, frozen: the template's layout until the
# user's decision of October 24, 2026 shortened the template from Week 7 (``TEMPLATE_FROM``).
WEEK_6_LAYOUT = ("Coach record", "1. Preparation and final game-day decisions", "2. Pregame media", "3. The game",
                 "4. Postgame media", "5. Football review and next week's work", "6. After-action report",
                 "7. Final record and next game", STATISTICS)
# The first regular-season game in the template's layout, (season, week); every postseason game is in it.
TEMPLATE_FROM = (2014, 7)
MEDIA = ("pregame media", "postgame media")
# The tables a report carries before its statistics: the coach record's (any), the line score and the
# after-action injuries table in the template's columns.
INJURIES = "Injuries and availability changes"
INJURY_COLUMNS = ["Player", "What was reported", "Effect now", "Next medical decision"]
WIN_WORDS, LOSS_WORDS = ("won", "beat", "defeated"), ("lost", "fell")
RESULT = re.compile(r"\b(?P<verb>won|beat|defeated|lost|fell)\b(?: to)?(?P<object>(?: the)?(?: [A-Z][\w.'-]*)+)?,? "
                    r"(?P<a>\d{1,2})-(?P<b>\d{1,2})(?![\d-])")


def sections(root=ROOT):
    """The template's level-two headings, in its order."""
    text = (Path(root) / TEMPLATE).read_text(encoding="utf-8")
    return [h.strip() for h in H2.findall(text)]


@dataclass(frozen=True)
class Layout:
    """A Game Report layout: its level-two headings, in order."""
    sections: tuple

    @property
    def story(self):
        """The game story's heading ("2. The game", or "3. The game" in Week 6's layout)."""
        return next(h for h in self.sections if h.endswith(". The game"))

    @property
    def pregame(self):
        """The pregame sections, frozen before kickoff: the numbered sections before the story."""
        return tuple(h for h in self.sections[:self.sections.index(self.story)] if re.match(r"\d+\. ", h))

    @property
    def final_record(self):
        """The section that carries the "Record after game" line."""
        return next(h for h in self.sections if h.endswith(". Final record and next game"))


def season_of(game):
    """The game's season: the first part of its id (runtime/week_inputs.event_id)."""
    return int(game.get("season") or str(game["game_id"]).split("-", 1)[0])


def layout(game=None, root=ROOT):
    """The Game Report's layout for ``game`` (a fixture): the template's from 2014 Week 7
    (``TEMPLATE_FROM``), every postseason game included; ``WEEK_6_LAYOUT`` for a regular-season game
    before it. With no game, the template's."""
    if game is not None and game.get("game_type") != "postseason" and \
            (season_of(game), int(game["week"])) < TEMPLATE_FROM:
        return Layout(WEEK_6_LAYOUT)
    return Layout(tuple(sections(root)))


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
    """The Game Report's problems: its layout (``game``'s, ``layout``), and once the game has closed
    (``receipt``) the statistics last and the result reconciled with the game book."""
    errors = []
    order = list(layout(game, root).sections)
    found = [h.strip() for h in H2.findall(text)]
    for heading in found:
        if heading not in order:
            why = ""
            if tuple(order) != WEEK_6_LAYOUT and re.sub(r"^\d+\.\s*", "", heading).lower() in MEDIA:
                why = "; from 2014 Week 7 the Game Report has no media sections (the user's decision of October 24, 2026)"
            errors.append("%s: '## %s' is not a section of the Game Report (%s)%s"
                          % (label, heading, "; ".join(order), why))
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
        return errors + table_errors(text, label)
    for heading in order:
        if heading not in found:
            errors.append("%s: the game has been played; '## %s' is missing" % (label, heading))
    errors += table_errors(text, label)
    errors += story_errors(text, receipt, game, root, label)
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
        return ["%s: '## %s' needs its '%s' line" % (label, layout(game, root).final_record, RECORD)]
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


# ---------------------------------------------------------------- tables, the story's figures
def _headed_lines(text):
    """[(level-two heading, level-three heading, line)] of the page before its full game statistics."""
    out, h2, h3 = [], None, None
    for line in text.splitlines():
        m = re.match(r"^(#{2,3}) (.+?)\s*$", line)
        if m and len(m.group(1)) == 2:
            h2, h3 = m.group(2).strip(), None
            if h2 == STATISTICS:
                break
            continue
        if m:
            h3 = m.group(2).strip()
            continue
        out.append((h2, h3, line))
    return out


def table_errors(text, label="Game Report"):
    """The tables before the full game statistics: only the coach record's, the line score and the
    after-action injuries table in the template's columns. Any other table repeats figures the game
    book at the end holds, or is a roster inventory the after-action report does not carry."""
    errors, previous = [], None
    for h2, h3, line in _headed_lines(text):
        is_row = line.strip().startswith("|")
        if is_row and previous is None:
            head = [c.strip() for c in line.strip().strip("|").split("|")]
            where = h3 or h2 or "the header"
            allowed = h2 == "Coach record" or h3 == QUARTERS or (h3 == INJURIES and head == INJURY_COLUMNS)
            if not allowed:
                errors.append("%s: a table under '%s' (%s); the only tables before the full game statistics are the "
                              "coach record, the line score and the after-action injuries, in the template's columns: "
                              "tell the rest in words and leave the figures to the statistics at the end"
                              % (label, where, " | ".join(head)[:60]))
        previous = line if is_row else None
    return errors


def scores_stood(receipt):
    """Every score the game stood at, as unordered pairs: 0-0, each score after a scoring play (and a
    touchdown's before its try) and the final."""
    from .gamebook import GameView
    view = GameView(receipt, receipt["home"])
    clubs = [receipt["away"], receipt["home"]]
    out = {(0, 0)}
    before = {c: 0 for c in clubs}
    for event in view.events:
        after = event["score"]
        if event["points"] > 6:
            mid = dict(before, **{event["club"]: before[event["club"]] + 6})
            out.add(tuple(sorted(mid[c] for c in clubs)))
        out.add(tuple(sorted(after[c] for c in clubs)))
        before = dict(after)
    out.add(tuple(sorted(receipt["final_score"][c] for c in clubs)))
    return out


def _records(receipt, game, root):
    """Each club's record before and after the game, in every form a report may write it."""
    if game is None:
        return set()
    from . import game_weeks
    paths = SeasonPaths(int(receipt["season"]), root)
    week = int(game["week"])
    postseason = game.get("game_type") == "postseason"
    out = set()
    for club in (receipt["away"], receipt["home"]):
        regular = [r for r in game_weeks.regular_receipts(paths) if club in (r["away"], r["home"])]
        for upto in (week - 1, week):
            out |= record_forms([r for r in regular if postseason or int(r["week"]) <= upto], club)
        if postseason:
            post = [r for r in game_weeks.postseason_receipts(paths) if club in (r["away"], r["home"])]
            for upto in (week - 1, week):
                out |= record_forms([r for r in post if int(r["week"]) <= upto], club)
    return out


def _section_lines(text, heading):
    return [line for h2, _, line in _headed_lines(text) if h2 == heading]


def story_errors(text, receipt, game=None, root=ROOT, label="Game Report"):
    """The story's figures against the game book: every score in the game story (``game``'s layout)
    one the game stood at (or a club's record), and every "won/beat/defeated/lost/fell" by a score,
    anywhere in the report's prose, the final score with the right club as winner or loser."""
    errors = []
    stood = scores_stood(receipt)
    records = _records(receipt, game, root)
    final = receipt["final_score"]
    clubs = [receipt["away"], receipt["home"]]
    story = [l for l in _section_lines(text, layout(game, root).story) if not l.strip().startswith("|")]
    for token in RECORD_TOKEN.findall("\n".join(story)):
        parts = tuple(int(p) for p in token.split("-"))
        if token in records:
            continue
        if len(parts) == 2 and tuple(sorted(parts)) in stood:
            continue
        errors.append("%s: the game story gives %s, a score the game never stood at (the scoring summary runs from "
                      "0-0 to %s %d, %s %d)" % (label, token, clubs[0], final[clubs[0]], clubs[1], final[clubs[1]]))
    winner = max(clubs, key=lambda c: final[c]) if final[clubs[0]] != final[clubs[1]] else None
    prose = [line for h2, _, line in _headed_lines(text) if h2 and h2 != "Coach record"
             and not line.strip().startswith(("|", "<!--"))]
    for line in prose:
        for sentence in re.split(r"(?<=[.!?])\s+", line):
            for m in RESULT.finditer(sentence):
                said = (int(m["a"]), int(m["b"]))
                subject = _last_club(sentence[:m.start()], clubs)
                if subject is None:
                    continue
                won = m["verb"] in WIN_WORDS
                if tuple(sorted(said)) != tuple(sorted(final.values())) or winner is None or \
                        (subject == winner) != won:
                    errors.append("%s: '%s' does not match the game book: the game ended %s %d, %s %d"
                                  % (label, sentence.strip()[:100], clubs[0], final[clubs[0]], clubs[1],
                                     final[clubs[1]]))
    return errors


def _last_club(text, clubs):
    """The club of the game named last in ``text`` (its full name, place or nickname), or None."""
    best, at = None, -1
    for club in clubs:
        for name in names(club):
            for m in re.finditer(r"\b%s\b" % re.escape(name), text):
                if m.start() > at:
                    best, at = club, m.start()
    return best


# ---------------------------------------------------------------- the pregame sections, frozen
def pregame_sections(text, headings):
    """{heading: its text} of the report's sections named in ``headings``, each from its heading to the
    next."""
    out, current, lines = {}, None, []
    for line in text.splitlines():
        m = re.match(r"^## (.+?)\s*$", line)
        if m:
            if current in headings:
                out[current] = "\n".join(lines).rstrip("\n")
            current, lines = m.group(1).strip(), [line]
            continue
        lines.append(line)
    if current in headings:
        out[current] = "\n".join(lines).rstrip("\n")
    return out


def pregame_digests(text, headings):
    return {h: hashlib.sha256(body.encode("utf-8")).hexdigest() for h, body in pregame_sections(text, headings).items()}


PREGAME_ABOUT = ("The Game Report's pregame sections (the numbered sections before the game story) as they stood "
                 "before kickoff: each section's heading and the sha256 of its text, frozen at the game-day commit by "
                 "scripts/freeze_pregame.py. Validation holds the report's pregame sections to it once the game has "
                 "closed.")


def pregame_record(text, day, game=None, root=ROOT):
    """The pregame freeze record of a report opened before ``game``: its layout's pregame sections
    (``Layout.pregame``)."""
    headings = layout(game, root).pregame
    digests = pregame_digests(text, headings)
    missing = [h for h in headings if h not in digests]
    if missing:
        raise ValueError("the Game Report has no '## %s' to freeze" % missing[0])
    return {"about": PREGAME_ABOUT, "frozen": day.isoformat(), "sections": {h: digests[h] for h in headings}}


def pregame_errors(text, record, closed, label="Game Report", hint="", game=None, root=ROOT):
    """The pregame sections against the pregame freeze record; once the game has closed the record
    must exist. With ``game``, the record holds exactly its layout's pregame sections."""
    if record is None:
        return (["%s: the game has been played, but its pregame sections were never frozen before kickoff%s"
                 % (label, hint)] if closed else [])
    frozen = record.get("sections") or {}
    errors = []
    if game is not None:
        wanted = layout(game, root).pregame
        if sorted(frozen) != sorted(wanted):
            errors.append("%s: the pregame freeze record holds %s; this game's pregame sections are %s"
                          % (label, "; ".join("'## %s'" % h for h in frozen) or "no section",
                             "; ".join("'## %s'" % h for h in wanted)))
    digests = pregame_digests(text, tuple(frozen))
    for heading, digest in frozen.items():
        if digests.get(heading) != digest:
            errors.append("%s: '## %s' differs from the section frozen before kickoff on %s; the pregame sections "
                          "stay as they stood before the game" % (label, heading, record.get("frozen")))
    return errors


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
                text = path.read_text(encoding="utf-8")
                errors += report_errors(text, receipt, game, root=root, label=rel)
                from .decisions import week_pages
                week = int(game["week"])
                frozen = week_pages(year, week, root, postseason=game.get("game_type") == "postseason").pregame
                record = json.loads(frozen.read_text(encoding="utf-8")) if frozen.is_file() else None
                errors += pregame_errors(text, record, receipt is not None, rel,
                                         " (python scripts/freeze_pregame.py %d --season %d at the game-day commit)"
                                         % (week, year), game=game, root=root)
    return errors


# ------------------------------------------------------------------ the week's results (rebuild step 5)
REPORT_LINK = re.compile(r"\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
# A stored text shorter than this many words is too common to call a copy when it recurs.
COPIED_WORDS = 6


def _plain(text):
    return re.sub(r"\s+", " ", str(text)).strip().lower()


def result_link_errors(report_text, results, report_rel=None, label="Game Report"):
    """F15 (docs/event_inserts.md, section A.5): the week's report links each separate result and
    never pastes one. ``results`` are the period's resolved event records, passed in (the lead's
    validation passes runtime/open_events.period_events; this module reads no event store): each
    names its page (``resolution.result_page``), which the report must link, and its "What happened"
    texts (the summary, each process entry and the decision), none of which the report may copy.
    With ``report_rel`` (the report's repository path) a link must resolve to the result page itself;
    without it, a link to a page of the same file name counts. Every result stays its own page: a
    combined summary is not a substitute."""
    import posixpath
    from urllib.parse import unquote
    errors = []
    targets = set()
    for dest in REPORT_LINK.findall(report_text):
        path = unquote(dest.split("#", 1)[0])
        if not path or "://" in path:
            continue
        if report_rel is not None:
            targets.add(posixpath.normpath(posixpath.join(posixpath.dirname(report_rel), path)))
        else:
            targets.add(posixpath.basename(path))
    plain = _plain(report_text)
    for record in results or ():
        res = record.get("resolution") or {}
        page = res.get("result_page")
        if not page:
            continue
        wanted = posixpath.normpath(page) if report_rel is not None else posixpath.basename(page)
        if wanted not in targets:
            errors.append("%s: the result for %s (%s) is not linked; the report links each result, never "
                          "replaces it" % (label, record.get("subject"), page))
        texts = [(record.get("summary") or {}).get("text"), (res.get("decision") or {}).get("text")]
        texts += [e.get("what") for e in record.get("process") or ()]
        for text in texts:
            if text and len(str(text).split()) >= COPIED_WORDS and _plain(text).rstrip(".") in plain:
                errors.append("%s: copies the result for %s (%r); link the result page instead of pasting it"
                              % (label, record.get("subject"), str(text)))
                break
    return errors
