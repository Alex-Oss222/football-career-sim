#!/usr/bin/env python3
"""Build the coach side's pages from the stored facts.

  python scripts/render_coach_pages.py [--check] [--root PATH]

Three pages, each built whole and never edited by hand (rebuild step 3):

- the Coach page, career/Stone/README.md: his job and employer, his contract
  and remaining term, his record by season (built from the closed games and
  runtime/standings.py), his career before Jacksonville, his philosophy (the
  opening of the coaching profile the user wrote, when it reads cleanly),
  the reviews he has received and any open opportunities;
- Contract and jobs, career/Stone/Contract_and_Jobs.md: the terms, salary by
  season, what is owed from today, which terms are signed and which were
  completed and from what (the same line sits under the Coach page's
  contract table), and every contact from another club with its stage;
- the active season's Staff page: who coaches what, who calls what, the
  contract status a head coach knows, departures and open jobs.

The facts come from the coach records (data/people/coaches, runtime/coaches.py),
the current-job record (state/current_job.json: the appointment, its history,
the delegation of who calls each phase), the closed game records and award
results, and the master date. --check writes nothing and fails on a coach
record that breaks its schema, a page that differs from its rebuild and a page
that breaks the clean-page rule. Run after a coach record, the job record, a
closed game or the master date changes (docs/update_workflow.md).
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime import coaches, current_job  # noqa: E402
from runtime.clean_pages import page_errors  # noqa: E402
from runtime.events import repository_map  # noqa: E402
from runtime.league import DIVISION_OF  # noqa: E402
from runtime.player_bios import master_date  # noqa: E402
from runtime.postseason import ROUNDS  # noqa: E402
from runtime.season_layout import PAGE_HISTORY, STONE_PAGES  # noqa: E402
from runtime.seasons import SeasonPaths  # noqa: E402
from runtime.standings import compute, pct_text  # noqa: E402

COACH_PAGE = STONE_PAGES + "/README.md"
CONTRACT_PAGE = STONE_PAGES + "/Contract_and_Jobs.md"
PROFILE = "career/coaching_profiles/alex_stone_coaching_profile.md"
PHOTO = "career/coaching_profiles/photos/alex_stone.webp"
PROFILES = "career/coaching_profiles/README.md"
PAYROLL = "career/finances/coaching_and_organization/coaching_payroll.md"
HIRING_RULES = "library/2014_coaching_hiring_and_anti_tampering_rules.md"
HIRING_RULES_ANCHOR = "13-head-coaches-under-contract-to-another-club"
CONTRACTS_RESEARCH = "library/nfl_head_coach_contracts_2005_2014.md"
ROUND_NAMES = {"wild_card": "Wild Card game", "divisional": "Divisional game",
               "conference": "Conference Championship", "super_bowl": "Super Bowl"}
ORDINAL = ("First", "Second", "Third", "Fourth", "Fifth", "Sixth", "Seventh", "Eighth")
UNIT_NAMES = {"team": "Team", "offense": "Offense", "defense": "Defense", "special_teams": "Special teams"}
PHASE_NAMES = {"offense": "the offense", "defense": "the defense", "special_teams": "special teams"}
TERM_NAMES = {"seasons": "the length", "end": "the end date", "salary": "the salary", "guaranteed": "the guarantee",
              "offset": "the offset", "dismissal": "the dismissal terms", "signing_bonus": "the signing bonus",
              "options": "the options", "terms": "the authority terms"}
SOURCE_LABELS = {CONTRACTS_RESEARCH: "head-coach contracts, 2005 to 2014"}
# An anchor carrying a code (an entry, row, document or section number) is not linked from a
# football page; the link goes to the page itself.
CODED_ANCHOR = re.compile(r"(?:^|-)(?:entry|row|document|section|item)-\d")


def long_date(value):
    when = date.fromisoformat(value) if isinstance(value, str) else value
    return "%s %d, %d" % (when.strftime("%B"), when.day, when.year)


def dollars(value):
    return "$%s" % format(value, ",")


def join(items, word="and"):
    items = [str(i) for i in items]
    return "".join(items) if len(items) < 2 else ", ".join(items[:-1]) + " " + word + " " + items[-1]


def table(headers, rows, align=None):
    align = align or ["---"] * len(headers)
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join(align) + "|"]
    return lines + ["| " + " | ".join(str(c).replace("|", "/") for c in row) + " |" for row in rows]


def place(club):
    return club.rsplit(" ", 1)[0]


def football_anchor(anchor, today):
    """``anchor`` when a football page may link it, else None: an anchor carrying a code or a
    real-world date (a year after the season the clock is in) sends the reader to the page."""
    if not anchor or CODED_ANCHOR.search(anchor):
        return None
    if any(int(y) > today.year + 1 for y in re.findall(r"(?<!\d)(\d{4})(?!\d)", anchor)):
        return None
    return anchor


# ---- the closed games -------------------------------------------------------

def _receipts(folder):
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(folder.glob("*.json"))] if folder.is_dir() else []


def club_fixtures(root, season, club):
    return sorted((g for g in SeasonPaths(season, root).regular_games() if club in (g["away"], g["home"])),
                  key=lambda g: g["date"])


def club_season(root, season, club):
    """The club's season from its closed games: the regular-season record and division place
    (runtime/standings.py over every closed game), whether its regular season is complete, the
    last week played and its postseason games."""
    paths = SeasonPaths(season, root)
    regular = [r for r in _receipts(paths.receipts) if r.get("game_type", "regular") != "preseason"]
    ours = [r for r in regular if club in (r["home"], r["away"])]
    if not ours:
        return None
    result = compute(regular)
    division = DIVISION_OF[club]
    line = result["lines"][club]
    post = []
    for receipt in sorted(_receipts(paths.postseason_receipts), key=lambda r: int(r["week"])):
        if club in (receipt["home"], receipt["away"]):
            other = receipt["away"] if receipt["home"] == club else receipt["home"]
            mine, theirs = receipt["final_score"][club], receipt["final_score"][other]
            post.append({"week": int(receipt["week"]), "round": ROUNDS.get(int(receipt["week"])), "opponent": other,
                         "home": receipt["home"] == club, "for": mine, "against": theirs, "won": mine > theirs})
    weeks = [int(r["week"]) for r in ours]
    return {"season": season, "record": line.overall, "division": division,
            "place": result["division_ranks"][division].index(club),
            "complete": len(ours) >= len(club_fixtures(root, season, club)), "last_week": max(weeks),
            "post": post, "receipts": ours}


def last_game(root, season, club, today):
    """(fixture, our points, their points) of the club's latest closed game on or before today."""
    paths = SeasonPaths(season, root)
    by_week = {int(r["week"]): r for r in _receipts(paths.receipts) if club in (r["home"], r["away"])}
    played = [g for g in club_fixtures(root, season, club)
              if g["week"] in by_week and date.fromisoformat(g["date"]) <= today]
    if not played:
        return None
    game = played[-1]
    receipt = by_week[game["week"]]
    other = receipt["away"] if receipt["home"] == club else receipt["home"]
    return game, receipt["final_score"][club], receipt["final_score"][other]


def club_record(root, season, club, through_week):
    """The club's regular-season record, W-L or W-L-T, from its own closed games through a week."""
    wins = losses = ties = 0
    for receipt in _receipts(SeasonPaths(season, root).receipts):
        if club in (receipt["home"], receipt["away"]) and int(receipt["week"]) <= through_week:
            other = receipt["away"] if receipt["home"] == club else receipt["home"]
            mine, theirs = receipt["final_score"][club], receipt["final_score"][other]
            wins, losses, ties = wins + (mine > theirs), losses + (mine < theirs), ties + (mine == theirs)
    return "%d-%d" % (wins, losses) + ("-%d" % ties if ties else "")


def record_text(record):
    return "%d-%d" % (record.wins, record.losses) + ("-%d" % record.ties if record.ties else "")


def postseason_text(post, club):
    parts = []
    for game in post:
        where = ("against %s" % place(game["opponent"]) if game["round"] == "super_bowl" else
                 ("at home against %s" if game["home"] else "at %s") % place(game["opponent"]))
        parts.append("%s the %s %s, %d-%d" % ("won" if game["won"] else "lost",
                                             ROUND_NAMES.get(game["round"], "playoff game"), where,
                                             max(game["for"], game["against"]), min(game["for"], game["against"])))
    text = "; ".join(parts)
    return text[:1].upper() + text[1:]


# ---- context ----------------------------------------------------------------

@dataclass
class Context:
    root: Path
    job: dict
    current: dict
    records: dict
    holder: str            # the coach record of the job's holder
    season: int
    paths: SeasonPaths
    today: date
    club: str

    def page(self, rel):
        return self.root / rel


def context(root=ROOT):
    root = Path(root).resolve()
    job = current_job.load(root)
    current = current_job.appointment(job) or {}
    records = coaches.load_all(root)
    holder = next((slug for slug, r in records.items() if r.get("party") == job.get("holder")), None)
    if holder is None:
        raise ValueError("no coach record for the job holder %s" % job.get("holder"))
    season = int(repository_map(root)["active_season"])
    return Context(root, job, current, records, holder, season, SeasonPaths(season, root), master_date(root),
                   (current.get("employer") or {}).get("club"))


def link(ctx, page, target, label, anchor=None):
    """A Markdown link from ``page`` to the repository file ``target``; the target must exist."""
    path = ctx.root / target if isinstance(target, str) else Path(target)
    if not path.exists() and path not in own_pages(ctx):
        raise ValueError("coach page link target missing: %s" % target)
    rel = os.path.relpath(path, (ctx.root / page).parent).replace(os.sep, "/")
    return "[%s](%s%s)" % (label, quote(rel, safe="/._-"), "#" + anchor if anchor else "")


def own_pages(ctx):
    """The pages this builder writes, which may link to each other before they first exist."""
    return {ctx.root / COACH_PAGE, ctx.root / CONTRACT_PAGE, ctx.paths.staff_page}


def rel(ctx, path):
    return Path(path).relative_to(ctx.root).as_posix()


def as_of(ctx):
    last = last_game(ctx.root, ctx.season, ctx.club, ctx.today)
    return "As of %s%s." % (long_date(ctx.today), ", after Week %d" % last[0]["week"] if last else "")


def party_name(ctx, pid):
    return current_job.party_name(ctx.job, pid)


def intervals(ctx, phase):
    rows = [r for r in (ctx.current.get("delegation") or {}).get("play_calling") or () if r.get("phase") == phase]
    return sorted(rows, key=lambda r: r.get("from") or "")


def since_text(interval):
    if interval.get("from"):
        return "since %s" % long_date(interval["from"])
    return "since %s" % (interval.get("from_label") or "the start")


def calls_text(ctx):
    """The phases the holder calls now, with since when."""
    out = []
    for phase in current_job.PHASES:
        now = next((r for r in intervals(ctx, phase) if r.get("to") is None), None)
        if now and now["caller"] == ctx.job["holder"]:
            out.append("%s (%s)" % (PHASE_NAMES[phase], since_text(now)))
    return join(out)


# ---- the coach page ---------------------------------------------------------

def terms_line(ctx, terms, page):
    """Which terms are signed and which were completed, and from what: the signed terms, each
    later signed amendment, then the completed terms grouped by their basis, with the research."""
    signed = terms["signed"]
    kept = [k for k in coaches.TERMS + ("terms",) if signed.get(k) is not None and signed.get(k) != []]
    parts = ["Signed on %s: %s." % (long_date(signed["date"]), join(TERM_NAMES[k] for k in kept))]
    for amendment in terms["amended"]:
        if not amendment.get("reconstruction"):
            parts.append("Amended on %s: %s." % (coaches.date_text(amendment),
                                                 join(TERM_NAMES[k] for k in coaches.TERMS
                                                      if k in (amendment.get("terms") or {}))))
    for source, keys in coaches.completed(terms):
        parts.append("Completed from %s: %s." % (source, join(TERM_NAMES[k] for k in keys)))
    research = [link(ctx, page, s, SOURCE_LABELS.get(s) or heading(ctx.root / s)) for s in coaches.completed_sources(terms)]
    if research:
        parts.append("The research behind them: %s." % join(research))
    return " ".join(parts)


def heading(path):
    """A page's first heading, as a link label."""
    first = next((l for l in path.read_text(encoding="utf-8").split("\n") if l.startswith("# ")), "# " + path.stem)
    return first[2:].strip()


def contract_rows(ctx, terms, page):
    seasons = terms.get("seasons") or []
    salary = coaches.scheduled(terms)
    amounts = sorted(set(salary.values()))
    remaining = [s for s in seasons if s >= ctx.season]
    rows = [("Seasons", "%d to %d" % (seasons[0], seasons[-1]) if len(seasons) > 1 else str(seasons[0])),
            ("Ends", (terms.get("end") or {}).get("text") or "Not recorded")]
    if remaining:
        rows.append(("Remaining", join(["%d (in progress)" % s if s == ctx.season else str(s) for s in remaining])))
    rows.append(("Salary", "%s a season" % dollars(amounts[0]) if len(amounts) == 1 else
                 "; ".join("%d: %s" % (s, dollars(v)) for s, v in salary.items()) or "Not recorded"))
    rows.append(("Guarantee", "Every season guaranteed" if coaches.guarantee_text(terms) == "Guaranteed"
                 else coaches.guarantee_text(terms)))
    return rows


def season_rows(ctx, record):
    """Rows of the record-by-season table, newest first, and the career totals."""
    rows, totals = [], {"w": 0, "l": 0, "t": 0, "pw": 0, "pl": 0}
    hire = coaches.hired(record, ctx.club)
    first = coaches.day(hire["date"]).year if hire else ctx.season
    for season in range(ctx.season, first - 1, -1):
        line = club_season(ctx.root, season, ctx.club)
        if line is None:
            continue
        r = line["record"]
        division = line["division"]
        finish = "%s in the %s" % (ORDINAL[line["place"]], division)
        label = str(season)
        if not line["complete"]:
            label += " (through Week %d)" % line["last_week"]
            finish += " after Week %d" % line["last_week"]
            playoffs = "Season in progress"
        else:
            playoffs = postseason_text(line["post"], ctx.club) or "Did not reach the playoffs"
        totals["w"] += r.wins; totals["l"] += r.losses; totals["t"] += r.ties
        totals["pw"] += sum(g["won"] for g in line["post"]); totals["pl"] += sum(not g["won"] for g in line["post"])
        rows.append((label, place(ctx.club), "Head coach", record_text(r), pct_text(r.pct), finish, playoffs))
    for before in sorted(record.get("head_coaching_before") or (), key=lambda b: -b["season"]):
        reg, post = before["regular"], before.get("postseason") or {"wins": 0, "losses": 0}
        games = reg["wins"] + reg["losses"] + reg.get("ties", 0)
        pct = (reg["wins"] + 0.5 * reg.get("ties", 0)) / games if games else 0.0
        text = "%d-%d" % (reg["wins"], reg["losses"]) + ("-%d" % reg["ties"] if reg.get("ties") else "")
        totals["w"] += reg["wins"]; totals["l"] += reg["losses"]; totals["t"] += reg.get("ties", 0)
        totals["pw"] += post["wins"]; totals["pl"] += post["losses"]
        rows.append((str(before["season"]), place(before["club"]), before["job"], text, pct_text(pct),
                     before.get("finish", ""), before.get("playoffs", "")))
    games = totals["w"] + totals["l"] + totals["t"]
    career = "%d-%d" % (totals["w"], totals["l"]) + ("-%d" % totals["t"] if totals["t"] else "")
    pct = pct_text((totals["w"] + 0.5 * totals["t"]) / games) if games else ""
    rows.append(("Career", "", "", career, pct, "", "%d-%d in the playoffs" % (totals["pw"], totals["pl"])))
    return rows


def award_lines(ctx, record):
    """Coach of the Year results naming him, from each season's award results."""
    hire = coaches.hired(record, ctx.club)
    first = coaches.day(hire["date"]).year if hire else ctx.season
    lines = []
    for season in range(ctx.season, first - 1, -1):
        path = SeasonPaths(season, ctx.root).awards_data / "season_honours_results.json"
        if not path.is_file():
            continue
        award = (json.loads(path.read_text(encoding="utf-8")).get("ap_awards") or {}).get("COY") or {}
        shortlist, won = award.get("shortlist") or [], award.get("winner_index")
        names = [c.get("coach") for c in shortlist]
        if record["name"] not in names or won is None:
            continue
        winner = shortlist[won]
        if names.index(record["name"]) == won:
            lines.append("- %d: Coach of the Year." % season)
        else:
            lines.append("- %d: Coach of the Year finalist; %s of the %s won." % (season, winner["coach"], winner["team"]))
    return lines


def philosophy(ctx):
    """The opening paragraphs of the user's coaching profile, when they read cleanly."""
    path = ctx.root / PROFILE
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    try:
        start = next(i for i, l in enumerate(lines) if l.startswith("[")) + 1
        stop = next(i for i, l in enumerate(lines) if l.startswith("## "))
    except StopIteration:
        return []
    body = "\n".join(lines[start:stop]).strip()
    if not body or page_errors(COACH_PAGE, body, (), ctx.root):
        return []
    return body.split("\n")


def coach_page(ctx):
    record = ctx.records[ctx.holder]
    page = COACH_PAGE
    current = ctx.current
    title = current.get("title") or "Not employed"
    born = record.get("born") or {}
    age = None
    if born.get("date"):
        b = date.fromisoformat(born["date"])
        age = ctx.today.year - b.year - ((ctx.today.month, ctx.today.day) < (b.month, b.day))
    header = " · ".join(x for x in (title, ctx.club, "Age %d" % age if age is not None else None) if x)
    out = ["# %s" % record["name"], "", "**%s**" % header, ""]
    facts = []
    if born.get("date"):
        facts.append("Born %s, %s" % (long_date(born["date"]), born.get("place")))
    for item in record.get("playing") or ():
        facts.append("%s, %s, %s" % (item["position"], item["team"], item["years"].replace("-", " to ")))
    if facts:
        out += [" · ".join(facts), ""]
    out += [as_of(ctx), ""]
    if (ctx.root / PHOTO).is_file():
        out += ["![%s](%s)" % (record["name"], os.path.relpath(ctx.root / PHOTO, (ctx.root / page).parent)), ""]
    # Job.
    rows = [("Job", "%s, %s" % (title, ctx.club)), ("Since", long_date(current["start"]))]
    for entry in current.get("history") or ():
        if entry.get("kind") == "retained":
            note = (entry.get("note") or "").split(";")[0].strip()
            rows.append(("Retained", long_date(entry["date"]) + (", " + note if note else "")))
    decided = (current.get("reporting") or {}).get("employment_decided_by") or []
    if decided:
        rows.append(("Employment decided by", join(party_name(ctx, p) for p in decided)))
    calls = calls_text(ctx)
    if calls:
        rows.append(("Calls", calls[:1].upper() + calls[1:]))
    # The contract and its remaining term, in the same short table.
    terms = current_job.contract_terms(ctx.job, ctx.root)
    if terms:
        rows += [("Contract" if label == "Seasons" else label, value) for label, value in contract_rows(ctx, terms, page)]
    else:
        rows.append(("Contract", "Not recorded"))
    out += ["## Job and contract", ""] + table([rows[0][0], rows[0][1]], rows[1:])
    if terms:
        out += ["", terms_line(ctx, terms, page)]
    out += ["", "Every term, what is owed and any contact from another club: %s."
            % link(ctx, page, CONTRACT_PAGE, "Contract and jobs"), ""]
    # Record by season.
    out += ["## Record by season", "", "Regular season and playoffs; preseason games are not counted.", ""]
    out += table(["Season", "Team", "Job", "Regular season", "Pct", "Division finish", "Playoffs"],
                 season_rows(ctx, record), ["---", "---", "---", "---:", "---:", "---", "---"])
    out += [""]
    awards = award_lines(ctx, record)
    if awards:
        out += ["## Awards", ""] + awards + [""]
    # Career history.
    out += ["## Career history", "", "### Coaching", ""]
    history = [(h["years"].replace("-", " to "), h["club"], h["job"], h.get("work", ""))
               for h in record.get("coaching_history") or ()]
    work = "Calls %s" % calls if calls else ""
    history.append(("%d to present" % date.fromisoformat(current["start"]).year, ctx.club, title, work))
    out += table(["Years", "Club", "Job", "Work"], history) + [""]
    if record.get("playing"):
        out += ["### Playing", ""]
        out += table(["Years", "Team", "Position", "Note"],
                     [(p["years"].replace("-", " to "), p["team"], p["position"], p.get("note", ""))
                      for p in record["playing"]]) + [""]
        pr = record.get("playing_record")
        if pr:
            out += table(["NFL seasons", "Games", "Receptions", "Yards", "Touchdowns", "Pro Bowls",
                          "First-team All-Pro"],
                         [(pr["seasons"], pr["games"], pr["receptions"], format(pr["yards"], ","), pr["touchdowns"],
                           pr["pro_bowls"], pr["all_pro_first_team"])], ["---:"] * 7) + [""]
    if record.get("education"):
        out += ["### Education", "", " · ".join("%s, %s, %d" % (e["degree"], e["school"], e["year"])
                                               for e in record["education"]), ""]
    # Philosophy.
    out += ["## Coaching philosophy", ""]
    words = philosophy(ctx)
    if words:
        out += words + [""]
    out += ["The full approach, in his own terms: %s." % link(ctx, page, PROFILE, "coaching profile"), ""]
    # Reviews.
    out += ["## Reviews", ""] + review_lines(ctx, page) + [""]
    # Opportunities.
    out += ["## Opportunities", ""]
    open_contacts = [c for c in record.get("contacts") or () if c.get("stage") not in ("declined",)]
    if open_contacts:
        out += ["- %s: %s, %s (%s)." % (coaches.date_text(c), c["club"], c.get("job", ""),
                                       coaches.STAGE_NAMES[c["stage"]]) for c in open_contacts]
    else:
        out += ["None recorded: no rumor, call, permission request, interview request or offer from another club."]
    out += ["", "Every contact, and the rules on approaching a head coach under contract: %s."
            % link(ctx, page, CONTRACT_PAGE, "Contract and jobs"), ""]
    return "\n".join(out).rstrip() + "\n"


def review_lines(ctx, page):
    current = ctx.current
    decided = (current.get("reporting") or {}).get("employment_decided_by") or []
    lines = []
    for entry in current.get("history") or ():
        if entry.get("kind") != "retained":
            continue
        when = date.fromisoformat(entry["date"])
        season = when.year - 1 if when.month <= 2 else when.year
        note = (entry.get("note") or "").split(";")[0].strip()
        text = "**%s.** %s reviewed the %d season with him and retained him%s." % (
            long_date(when), join(party_name(ctx, p) for p in decided), season, " " + note if note else "")
        for item in current.get("evaluation") or ():
            if item.get("by") != "contract" and item.get("season") == when.year and item.get("measures"):
                text += " %s's %s: %s." % (party_name(ctx, item["by"]), item.get("label") or "measures",
                                           "; ".join(item["measures"]))
        record = entry.get("record") or {}
        if record.get("path"):
            text += " " + link(ctx, page, record["path"], "Season review",
                               football_anchor(record.get("anchor"), ctx.today))
        lines.append("- " + text)
    return lines or ["None recorded."]


# ---- contract and jobs --------------------------------------------------------

def salary_text(salary):
    """'$X a season, $Y in all' when every season pays the same, else season by season."""
    if not salary:
        return "Not recorded"
    amounts = set(salary.values())
    each = ("%s a season" % dollars(amounts.pop()) if len(amounts) == 1
            else "; ".join("%d: %s" % (s, dollars(v)) for s, v in salary.items()))
    return "%s, %s in all" % (each, dollars(sum(salary.values())))


def contract_page(ctx):
    record = ctx.records[ctx.holder]
    page = CONTRACT_PAGE
    terms = current_job.contract_terms(ctx.job, ctx.root)
    out = ["# Contract and jobs", "", "**%s · %s, %s**" % (record["name"], ctx.current.get("title"), ctx.club), "",
           as_of(ctx), "", link(ctx, page, COACH_PAGE, "Coach page"), ""]
    if terms is None:
        out += ["No contract is recorded.", ""]
    else:
        signed = terms["signed"]
        seasons = terms["seasons"]
        salary = coaches.scheduled(terms)
        dismissal = terms.get("dismissal") or {}
        bonus = terms.get("signing_bonus")
        rows = [("Signed", long_date(signed["date"])),
                ("Seasons", "%d to %d" % (seasons[0], seasons[-1])),
                ("Ends", (terms.get("end") or {}).get("text") or "Not recorded"),
                ("Salary", salary_text(salary)),
                ("Guarantee", "Every season guaranteed" if coaches.guarantee_text(terms) == "Guaranteed"
                 else coaches.guarantee_text(terms)),
                ("Offset", terms.get("offset") or "Not recorded"),
                ("Dismissal without cause", dismissal.get("without_cause") or "Not recorded"),
                ("Dismissal for cause", dismissal.get("for_cause") or "Not recorded"),
                ("Signing bonus", "None" if bonus == 0 else dollars(bonus) if bonus else "Not recorded"),
                ("Options", terms.get("options") or "Not recorded")]
        out += ["## Terms", ""] + table(["Term", "Detail"], rows) + [""]
        if terms.get("terms"):
            out += ["Signed authority and standards:", ""] + ["- %s." % t.rstrip(".") for t in terms["terms"]] + [""]
        out += [terms_line(ctx, terms, page), ""]
        out += ["## Salary by season", ""]
        rows = []
        for season in seasons:
            status = ("Season complete" if season < ctx.season else "Current season" if season == ctx.season
                      else "To come")
            rows.append((season, dollars(salary[season]) if season in salary else "Not recorded",
                         "Yes" if season in (terms.get("guaranteed") or ()) else "No", status))
        if salary:
            rows.append(("Total", dollars(sum(salary.values())), "", ""))
        out += table(["Season", "Salary", "Guaranteed", "Status"], rows, ["---", "---:", "---", "---"]) + [""]
        owed = {s: v for s, v in salary.items() if s >= ctx.season}
        out += ["## Owed from today", ""]
        if owed:
            out += table(["Season", "Salary"], [(s, dollars(v)) for s, v in owed.items()]
                         + [("Total", dollars(sum(owed.values())))], ["---", "---:"])
            if ctx.season in owed:
                out += ["", "The %d figure is the whole season's salary; how it is paid through the year is not "
                        "recorded." % ctx.season]
            out += ["", "If he were dismissed without cause today, the unpaid part of this would be owed, less pay "
                    "from another coaching job through the end of the term; dismissed for cause, nothing further.", ""]
        else:
            out += ["Nothing remains owed under this contract.", ""]
    out += ["## Contacts from other clubs", ""]
    contacts = record.get("contacts") or []
    if contacts:
        out += table(["Date", "Club", "Job", "Stage", "Deadline"],
                     [(coaches.date_text(c), c["club"], c.get("job", ""), coaches.STAGE_NAMES[c["stage"]],
                       long_date(c["deadline"]) if c.get("deadline") else "") for c in contacts]) + [""]
    else:
        out += ["None recorded: no rumor, call, permission request, interview request, offer or accepted job.", ""]
    out += ["A club may not approach a head coach under contract without his club's permission. During "
            "Jacksonville's season, playoffs included, no club may ask to speak with him, and he may not discuss "
            "another job unless he is dismissed. After the season, a move to another club's head-coaching job "
            "needs Jacksonville's consent, which it may refuse (%s)."
            % link(ctx, page, HIRING_RULES, "the league's coaching hiring rules", HIRING_RULES_ANCHOR), ""]
    return "\n".join(line for line in out if line is not None).rstrip() + "\n"


# ---- the staff page -----------------------------------------------------------

def staff_members(ctx):
    """[(slug, record)] of the club's staff today: unit order, coordinators first, then by surname."""
    order = {u: i for i, u in enumerate(coaches.UNITS)}
    members = []
    for slug, record in ctx.records.items():
        if coaches.on_staff(record, ctx.club, ctx.today):
            title, unit = coaches.job(record, ctx.club)
            head = 0 if unit == "team" else 1 if "coordinator" in title.lower() else 2
            members.append(((order.get(unit, 9), head, record["name"].split()[-1]), slug, record))
    return [(slug, record) for _, slug, record in sorted(members)]


def contract_status(terms):
    if terms is None:
        return "Not recorded"
    through = coaches.through_season(terms)
    return "Through %d; %s" % (through, coaches.guarantee_text(terms).lower())


def staff_page(ctx):
    page = rel(ctx, ctx.paths.staff_page)
    out = ["# Coaching staff", "", "**%s · %d**" % (ctx.club, ctx.season), "", as_of(ctx), ""]
    rows = []
    for slug, record in staff_members(ctx):
        title, unit = coaches.job(record, ctx.club)
        hire = coaches.hired(record, ctx.club)
        terms = coaches.current_contract(record, ctx.club)
        name = link(ctx, page, COACH_PAGE, record["name"]) if slug == ctx.holder else record["name"]
        rows.append((name, title, UNIT_NAMES.get(unit, unit), coaches.date_text(hire), contract_status(terms)))
    out += ["## Who coaches what", ""] + table(["Coach", "Job", "Unit", "Since", "Contract"], rows)
    out += ["", "Salaries are on the %s." % link(ctx, page, PAYROLL, "coaching payroll"), ""]
    # Who calls what.
    out += ["## Who calls what", ""]
    rows, before = [], []
    for phase in current_job.PHASES:
        spans = intervals(ctx, phase)
        now = next((r for r in spans if r.get("to") is None), None)
        if now is None:
            continue
        also = []
        if now.get("transmits"):
            also.append("%s sends in %s" % (party_name(ctx, now["transmits"]), now.get("transmits_what") or "the call"))
        if now.get("front_declaration"):
            also.append("%s declares the front" % party_name(ctx, now["front_declaration"]))
        rows.append((UNIT_NAMES[phase],
                     "%s%s, %s" % (party_name(ctx, now["caller"]), ", interim" if now.get("interim") else "",
                                   since_text(now)),
                     party_name(ctx, now["prepares"]) if now.get("prepares") else "Not recorded",
                     "; ".join(also)[:1].upper() + "; ".join(also)[1:] if also else ""))
        for earlier in reversed([r for r in spans if r is not now]):
            start = long_date(earlier["from"]) if earlier.get("from") else (earlier.get("from_label") or "the start")
            before.append("%s called %s%s from %s until %s." % (
                party_name(ctx, earlier["caller"]), PHASE_NAMES[phase], " on an interim basis" if earlier.get("interim")
                else "", start, long_date(earlier["to"])))
    out += table(["Phase", "Calls on game day", "Prepares", "Also"], rows) + [""]
    if before:
        out += ["Before: " + " ".join(before), ""]
    delegation = ctx.current.get("delegation") or {}
    carriers = (delegation.get("relay") or {}).get("carriers") or []
    if carriers:
        out += ["Information to the caller on game day: %s." % "; ".join(
            "%s, %s" % (party_name(ctx, c["party"]), c["carries"]) for c in carriers), ""]
    retained = []
    for phase in current_job.PHASES:
        now = next((r for r in intervals(ctx, phase) if r.get("to") is None), None)
        if now and now.get("stone_retains"):
            retained.append("- %s: %s." % (UNIT_NAMES[phase], now["stone_retains"][:1].lower() + now["stone_retains"][1:]))
    if retained:
        out += ["What %s keeps in each phase, whoever calls it:" % party_name(ctx, ctx.job["holder"]), ""]
        out += retained + [""]
    emergency = delegation.get("emergency") or {}
    if emergency.get("practice_lead"):
        out += ["If %s is out: %s runs practice%s. Game-day caller: %s." % (
            party_name(ctx, ctx.job["holder"]).split()[-1], ", then ".join(party_name(ctx, p) for p in emergency["practice_lead"]),
            " (%s)" % emergency["limits"] if emergency.get("limits") else "",
            party_name(ctx, emergency["game_day_caller"]) if emergency.get("game_day_caller") else "not appointed"), ""]
    # Departures and open jobs.
    gone, open_jobs = [], []
    for slug, record in ctx.records.items():
        leave = coaches.departed(record, ctx.club)
        if leave is None or coaches.day(leave["date"]).year != ctx.season:
            continue
        title, _ = coaches.job(record, ctx.club)
        gone.append((record["name"], title, coaches.date_text(leave), leave.get("to", "")))
        filled = any(coaches.on_staff(other, ctx.club, ctx.today) and coaches.job(other, ctx.club)[0] == title
                     for other in ctx.records.values())
        if not filled:
            open_jobs.append(title)
    out += ["## Departures in %d" % ctx.season, ""]
    out += (table(["Coach", "Job", "Left", "Went to"], gone) if gone else ["None."]) + [""]
    out += ["## Open jobs", "", ("- " + "\n- ".join(open_jobs)) if open_jobs else "None.", ""]
    # History.
    history = json.loads((ctx.root / PAGE_HISTORY).read_text(encoding="utf-8")) if (ctx.root / PAGE_HISTORY).is_file() else {}
    register = ctx.paths.staff_register
    links = []
    if register.is_file():
        through = history.get("through")
        links.append(link(ctx, page, register, "Staff register%s" % (", through " + long_date(through) if through else "")))
    changes = ctx.paths.record("offseason/staff_changes/README.md")
    if changes.is_file():
        links.append(link(ctx, page, changes, "Staff changes in %d" % ctx.season))
    links.append(link(ctx, page, PROFILES, "Coaching profiles"))
    out += ["## Records", "", " · ".join(links), ""]
    return "\n".join(out).rstrip() + "\n"


# ---- build, check, write --------------------------------------------------------

def build(root=ROOT):
    """{repository path: text} of every page this builder writes."""
    ctx = context(root)
    return {COACH_PAGE: coach_page(ctx), CONTRACT_PAGE: contract_page(ctx),
            rel(ctx, ctx.paths.staff_page): staff_page(ctx)}


def check(root=ROOT):
    root = Path(root).resolve()
    errors = coaches.all_errors(root)
    try:
        pages = build(root)
    except (OSError, ValueError, KeyError, IndexError, TypeError) as exc:
        return errors + ["Coach pages cannot be built: %s" % exc]
    for page, text in pages.items():
        path = root / page
        if not path.is_file() or path.read_text(encoding="utf-8") != text:
            errors.append("Coach page stale or hand-edited: %s; run scripts/render_coach_pages.py" % page)
        errors += page_errors(page, text, (), root)
    return errors


def write(root=ROOT):
    root = Path(root).resolve()
    errors = coaches.all_errors(root)
    if errors:
        raise ValueError("; ".join(errors))
    written = []
    for page, text in build(root).items():
        path = root / page
        if not path.is_file() or path.read_text(encoding="utf-8") != text:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            written.append(page)
    return written


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    if args.check:
        errors = check(args.root)
        print("\n".join(errors) if errors else "COACH PAGES CURRENT")
        return 1 if errors else 0
    try:
        written = write(args.root)
    except (OSError, ValueError, KeyError, IndexError, TypeError) as exc:
        print("Coach pages cannot be built: %s" % exc)
        return 1
    print("\n".join("wrote " + p for p in written) or "COACH PAGES CURRENT")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
