#!/usr/bin/env python3
"""Build a season's contract and cap pages from the permanent contract records (rebuild step 5, B1).

  python scripts/render_contract_pages.py [--season YEAR] [--check] [--root PATH]

Every page is built and clean, and every figure on it comes from a record: the contract records
(data/people/contracts, runtime/player_contracts.py), the club-level facts of the contract inputs
(the league cap, the workout charge, the carryover estimate, the in-season terms method) and the
roster record's lists. The pages, under the season's Team_Operations/Finances folder:

- player_contracts/Player_Contracts.md: the contracts in force (the active roster and the reserve
  lists), the practice squad, the status register, the contracts that ended in the season, and
  the update log built from the dated contract entries;
- salary_cap/Salary_Cap.md: the working position under the full count, the reserve lists, the
  dead money, the later commitments and one dated reconciliation for every date from the full count
  on with a contract entry;
- history/cap_changes.md: its bytes as recorded before Week 6, then built dated entries for each
  contract change after the page history closes (the prefix rule; nothing is added while there is
  none);
- the player_contracts and salary_cap folder READMEs, the current pages first and the earlier
  pages (contracts.md, contract_status.md, cap_worksheet.md) listed as history: those keep their
  bytes, so every inbound anchor keeps resolving.

Write mode writes only what differs from its build and refuses a page that would break the
clean-page rule. ``--check`` writes nothing and exits 1 when a page is missing, stale or unclean.
"""
from __future__ import annotations

import argparse
import os
import sys
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime import player_contracts as pc  # noqa: E402
from runtime.season_layout import PAGE_HISTORY, repository_relative  # noqa: E402
from runtime.seasons import CLEAN_SEASON, SeasonPaths, active_season  # noqa: E402

DETAILS = "career/finances/player_contracts/contract_details.md"
TRACKER = "career/finances/salary_cap/cap_tracker.md"
COMPLETION = "library/2014_jaguars_contract_completion.md"
PAGES = {
    "contracts": "finances/player_contracts/Player_Contracts.md",
    "cap": "finances/salary_cap/Salary_Cap.md",
    "changes": "finances/history/cap_changes.md",
    "contracts_readme": "finances/player_contracts/README.md",
    "cap_readme": "finances/salary_cap/README.md",
    "finances": "finances/README.md",
    "decisions": "finances/upcoming_decisions/README.md",
    "contract_table": "finances/player_contracts/contracts.md",
    "status_register": "finances/player_contracts/contract_status.md",
    "worksheet": "finances/salary_cap/cap_worksheet.md",
}


# ------------------------------------------------------------------ words and links
def money(value):
    return "" if value is None else ("-$%s" % format(abs(value), ",") if value < 0 else "$%s" % format(value, ","))


def change(value):
    return "No change" if not value else ("+" + money(value) if value > 0 else money(value))


# The contract inputs' adopted contract table (``current_contract_table``), which the reader wording
# links where a stored note names the adoption; set by ``render`` from the inputs.
_TABLE = {}


def words(text):
    """A stored text in reader wording (the cap views' rules: no system words, entry numbers or raw
    paths); the figures and names stay as written."""
    from scripts.render_jaguars_cap_tracker import presentation_note
    if text is None:
        return ""
    return presentation_note(str(text), _TABLE.get("path") or pc.inputs(ROOT)["current_contract_table"])


def link(page, target, label):
    """A link from ``page`` (a repository path) to ``target`` (a repository path or a legacy one,
    with an optional anchor)."""
    path, _, anchor = str(target).partition("#")
    rel = os.path.relpath(repository_relative(path), os.path.dirname(page)).replace(os.sep, "/")
    return "[%s](%s%s)" % (label, rel, "#" + anchor if anchor else "")


_TITLES = {}


def page_label(target, root=ROOT):
    """The title of the page ``target`` names (its first heading, in reader wording)."""
    path = Path(root) / repository_relative(str(target).split("#")[0])
    if path not in _TITLES:
        title = next((line[2:].strip() for line in path.read_text(encoding="utf-8").splitlines()
                      if line.startswith("# ")), path.stem.replace("_", " "))
        _TITLES[path] = words(title.replace("Library: ", ""))
    return _TITLES[path]


def table(headers, rows, right=()):
    def cell(v):
        return str(v).replace("|", "/").replace("\n", " ")
    head = "| " + " | ".join(headers) + " |"
    rule = "|" + "|".join("---:" if i in right else "---" for i in range(len(headers))) + "|"
    return "\n".join([head, rule] + ["| " + " | ".join(cell(c) for c in r) + " |" for r in rows]) + "\n\n"


def charge(row_year):
    if row_year["status"] in ("known", "tender"):
        return row_year["cap"]
    if row_year["status"] == "approximate":
        return row_year["approximate_cap"]
    return None


def slug(name):
    from scripts.render_jaguars_cap_tracker import slug as tracker_slug
    return tracker_slug(name)


# ------------------------------------------------------------------ the position on a day
class Position:
    """The season's working position from the records in force on day ``on`` (None: all)."""

    def __init__(self, records, data, year, root, on=None):
        self.year, self.root = str(year), root
        self.years = pc.horizon(data)
        self.rows = pc.rows(root, on, records, self.years)
        self.kinds = {}
        for record in records.values():
            current = pc.contract_on(record, on, root)
            if current is not None:
                self.kinds[record["name"]] = current["kind"]
        self.current = [r for r in self.rows if r["name"] in self.kinds]
        self.groups = {kind: [r for r in self.current if self.kinds[r["name"]] == kind] for kind in pc.START_KINDS}
        self.dead = pc.dead_money(root, records, data.get("dead_money", []), on)
        self.data = data

    def total(self, kind, year=None):
        year = year or self.year
        return sum(charge(r["years"][year]) or 0 for r in self.groups[kind])

    def dead_total(self, year=None):
        year = year or self.year
        return sum(d["amount"] for d in self.dead if str(d["year"]) == year)

    def contracts(self, year=None):
        return sum(self.total(kind, year) for kind in pc.START_KINDS)

    def obligations(self, year=None):
        return self.contracts(year) + self.dead_total(year)

    def scheduled(self, year):
        """Every committed charge of the year (later years: the players still under contract)."""
        return sum(charge(r["years"][year]) or 0 for r in self.rows if r["years"][year]["status"] in pc.CHARGED)

    def later(self, year):
        return self.scheduled(year) + self.dead_total(year)

    @property
    def workout(self):
        return self.data["team_years"][self.year].get("opening_workout_charge") or 0

    @property
    def cap(self):
        return self.data["league_caps"].get(self.year)

    def working_total(self):
        return self.obligations() + self.workout

    def difference(self):
        return None if self.cap is None else self.cap - self.working_total()


def season_terms(data, year):
    return (data.get("in_season_terms") or {}).get("seasons", {}).get(str(year), {})


def full_count(data, year):
    found = season_terms(data, year).get("full_count_from")
    return pc.day(found["date"]) if found else None


# ------------------------------------------------------------------ describing entries
def entry_change(record, entry, records, root, data):
    """One update-log or reconciliation line for a contract entry, built from its fields."""
    name = record["name"]
    kind = entry["kind"]
    if kind == "contract_signed":
        years = pc.schedule(entry, [], root)
        charges = [(y, charge(r)) for y, r in sorted(years.items()) if charge(r) is not None]
        line = "Signed through %s" % entry["through"] if entry.get("through") else "Signed"
        if charges:
            line += ": " + ", ".join("%s in %s" % (money(v), y) for y, v in charges)
        spec = entry.get("method")
        if spec:
            season = pc.league_year(entry["date"])
            left, total = pc.pay_weeks_left(season, entry["date"], root)
            terms = pc.method(root, data)
            if spec["name"] == "in_season_minimum":
                rate = pc.minimum_salary(season, int(spec["credited_seasons"]), root, terms)
                line += " (the %s league minimum for his credited seasons, earned for %d of %d pay weeks)" % (
                    money(rate), left, total)
            elif spec["name"] == "promotion":
                rate = terms["promotion"]["schedule"][str(season)]
                weekly = pc.practice_squad_rate(season, root, terms)
                line += " (the %s rate for %d of %d pay weeks, %s, plus %d practice-squad week%s at %s)" % (
                    money(rate), left, total, money(pc.prorated(rate, left, total)), spec["squad_weeks"],
                    "" if spec["squad_weeks"] == 1 else "s", money(weekly))
        return line
    if kind == "practice_squad":
        return "Practice-squad contract at %s a week (%s for %d weeks, a working estimate)" % (
            money(entry["weekly_rate"]), money(entry["weekly_rate"] * entry["weeks"]), entry["weeks"])
    if kind == "tender":
        charges = [money(charge(r)) for _, r in sorted((entry.get("years") or {}).items()) if charge(r) is not None]
        return "Tendered" + (" at %s" % ", ".join(charges) if charges else "")
    if kind == "contract_amended":
        return words(entry["text"])
    if kind == "contract_ended":
        start = next(e for e in record["entries"] if e.get("contract") == entry["contract"] and e["kind"] in pc.START_KINDS)
        line = words(entry["text"])
        left = [(y, charge(r)) for y, r in sorted(pc.schedule(start, [], root).items())
                if charge(r) is not None and int(y) >= pc.league_year(entry["date"])]
        if left and start["kind"] == "practice_squad":
            line += "; the practice-squad working estimate leaves (%s)" % ", ".join(
                "%s in %s" % (money(v), y) for y, v in left)
        elif left and entry["how"] != "traded":
            line += "; the remaining charges leave (%s)" % ", ".join("%s in %s" % (money(v), y) for y, v in left)
        elif left:
            line += "; the contract leaves with him (%s)" % ", ".join("%s in %s" % (money(v), y) for y, v in left)
        dead = entry.get("dead_money") or []
        if dead:
            line += "; dead money " + ", ".join("%s in %s" % (money(d["amount"]), d["year"]) for d in dead)
        return line
    raise ValueError("no change line for a %s entry" % kind)


def dated_entries(records, start=None, end=None):
    """[(record, entry)] of every contract entry dated from ``start`` to ``end`` (days), in date
    order and then register order."""
    out = []
    for record in records.values():
        for e in pc.entries(record):
            if e["kind"] not in pc.CONTRACT_KINDS:
                continue
            d = pc.day(e["date"])
            if (start is None or d >= start) and (end is None or d <= end):
                out.append((record, e))
    return sorted(out, key=lambda item: (pc.day(item[1]["date"]), item[0]["listed"],
                                         item[0]["entries"].index(item[1])))


# ------------------------------------------------------------------ Player_Contracts.md
def contracts_page(records, data, year, root, paths):
    page = paths["contracts"]
    pos = Position(records, data, year, root)
    y = str(year)
    as_of = pc.as_of(root, records)
    out = ["# Player contracts\n\n",
           "%s · %s · %s\n\n" % (link(page, paths["finances"], "%s finances" % y), link(page, paths["cap"], "Salary cap"),
                                 link(page, DETAILS, "Every contract year by year")),
           "As of %s, the latest contract change. Whole US dollars. Each amount is the player's adopted contract "
           "schedule: a recorded schedule, or a labelled reconstruction where the original instrument is incomplete "
           "(%s). A blank year is outside his contract; an estimate is marked as one.\n\n" % (
               pc.date_words(as_of), link(page, COMPLETION, "completion research"))]
    order = {p: i for i, p in enumerate(pc.POSITIONS)}

    def ranked(rows):
        return sorted(rows, key=lambda r: (order[r["position"]], -(charge(r["years"][y]) or 0), r["name"]))

    signed = ranked(pos.groups["contract_signed"])
    out.append("## Under contract\n\n%d players: the active roster and the reserve lists.\n\n" % len(signed))
    rows = []
    for r in signed:
        cur = r["years"][y]
        other = (charge(cur) or 0) - (cur.get("base") or 0) - (cur.get("proration") or 0)
        rows.append([link(page, DETAILS + "#" + slug(r["name"]), r["name"]), r["position"], words(r["contract_type"]),
                     words(r["signed"]), r["contract_ends"] or "", money(charge(cur)), money(cur.get("base")),
                     money(cur.get("proration")), money(other), money(r["remaining_guarantees"])])
    out.append(table(["Player", "Pos", "Contract", "Signed", "Through", "%s cap" % y, "Base", "Bonus proration",
                      "Other", "Unpaid guaranteed salary"], rows, right=(5, 6, 7, 8, 9)))
    squad = ranked(pos.groups["practice_squad"])
    out.append("## Practice squad\n\n%d weekly contracts. Each is charged only for the weeks he is on the squad; "
               "the season figure is a working estimate for the full season.\n\n" % len(squad))
    rows = []
    for r in squad:
        record = next(rec for rec in records.values() if rec["name"] == r["name"])
        entry = pc.contract_on(record, None, root)["start"]
        rows.append([r["name"], r["position"], words(r["signed"]), money(entry["weekly_rate"]), entry["weeks"],
                     money(charge(r["years"][y]))])
    out.append(table(["Player", "Pos", "Signed", "Weekly pay", "Weeks", "%s working estimate" % y], rows,
                     right=(3, 4, 5)))
    tenders = ranked(pos.groups["tender"])
    if tenders:
        out.append("## Unsigned tenders\n\n")
        out.append(table(["Player", "Pos", "Tender", "%s charge" % y],
                         [[r["name"], r["position"], words(r["value"]), money(charge(r["years"][y]))] for r in tenders],
                         right=(3,)))
    out.append("## Status register\n\nHis status, credited seasons and accrued seasons as the register records "
               "them.\n\n")
    out.append(table(["Player", "Status", "Credited seasons", "Accrued seasons"],
                     [[r["name"], words(r["status"]), words(r["credited_seasons"]), words(r["accrued_seasons"])]
                      for r in ranked(pos.current)]))
    ended = [(rec, e) for rec, e in dated_entries(records, pc.day(y), pc.day(str(int(y) + 1)) - timedelta(days=1))
             if e["kind"] == "contract_ended"]
    out.append("## Contracts that ended in %s\n\n" % y)
    if ended:
        rows = []
        for rec, e in ended:
            start = next(s for s in rec["entries"] if s.get("contract") == e["contract"] and s["kind"] in pc.START_KINDS)
            dead = ", ".join("%s in %s" % (money(d["amount"]), d["year"]) for d in e.get("dead_money") or [])
            contract = (words(start.get("value_text")) if start["kind"] == "tender"
                        else words(start.get("type") or start.get("notes")))
            rows.append([rec["name"], rec["position"], contract,
                         pc.date_words(e["date"]), words(e["text"]), dead or "None"])
        out.append(table(["Player", "Pos", "Contract", "Ended", "How it ended", "Dead money"], rows))
    else:
        out.append("None.\n\n")
    out.append("## Update log\n\nEvery dated contract change of %s, from the contract records.\n\n" % y)
    log = dated_entries(records, pc.day(y))
    out.append(table(["Date", "Player", "Change", "Record"],
                     [[e.get("label") or pc.date_words(e["date"]), rec["name"], entry_change(rec, e, records, root, data),
                       link(page, e["source"], page_label(e["source"], root))] for rec, e in log]))
    out.append("## Earlier pages\n\nThe %s and the %s keep their dated changes as they were written; the contract "
               "records now hold every figure.\n" % (link(page, paths["contract_table"], "earlier contract table"),
                                                   link(page, paths["status_register"], "earlier status register")))
    return "".join(out)


# ------------------------------------------------------------------ Salary_Cap.md
def position_rows(pos, data):
    y = pos.year
    rows = [["Signed contracts: the active roster and the reserve lists (%d players)" % len(pos.groups["contract_signed"]),
             money(pos.total("contract_signed"))]]
    if pos.groups["practice_squad"]:
        rows.append(["Practice squad: %d weekly contracts, a full-season working estimate charged only for the weeks "
                     "on the squad" % len(pos.groups["practice_squad"]), money(pos.total("practice_squad"))])
    if pos.groups["tender"]:
        rows.append(["Unsigned tenders (%d)" % len(pos.groups["tender"]), money(pos.total("tender"))])
    rows += [["Player contracts", money(pos.contracts())], ["Dead money", money(pos.dead_total())],
             ["Recorded obligations", money(pos.obligations())]]
    if pos.workout:
        rows.append(["Offseason workout charge", money(pos.workout)])
    rows.append(["Working total", money(pos.working_total())])
    if pos.cap is not None:
        rows.append(["Difference against the %s league cap of %s, before the carryover estimate and reserves" % (
            y, money(pos.cap)), money(pos.difference())])
        estimate = data["team_years"][y].get("carryover_working_estimate")
        if estimate:
            rows.append(["With the carryover estimate from the year before (%s to %s), not certified" % (
                money(estimate["low"]), money(estimate["high"])),
                "%s to %s" % (money(pos.difference() + estimate["low"]), money(pos.difference() + estimate["high"]))])
    return rows


def cap_page(records, data, year, root, paths):
    page = paths["cap"]
    y = str(year)
    pos = Position(records, data, year, root)
    as_of = pc.as_of(root, records)
    counted = full_count(data, year)
    out = ["# Salary cap\n\n",
           "%s · %s · %s\n\n" % (link(page, paths["finances"], "%s finances" % y),
                                 link(page, paths["contracts"], "Player contracts"),
                                 link(page, TRACKER, "Twelve-year cap table")),
           "As of %s, the latest contract change. Whole US dollars. " % pc.date_words(as_of)]
    if pos.cap is not None:
        out.append("The %s league cap is %s. " % (y, money(pos.cap)))
    if counted:
        out.append("Every contract counts in full from the compliance deadline of %s, the practice squad weekly; "
                   "before it the offseason Top-51 count applied, and its balances are in the %s. " % (
                       pc.date_words(counted.isoformat()), link(page, paths["changes"], "dated cap changes")))
    out.append("No certified cap room exists: the carryover from the year before and the club's adjustments are not "
               "reconciled.\n\n")
    out.append("## Working position\n\n")
    out.append(table(["Component", y], position_rows(pos, data), right=(1,)))
    # The reserve lists, from the roster record (its lists as it stands).
    from runtime import roster as roster_record
    roster = roster_record.load(Path(root) / repository_relative(data["current_roster"]))
    reserve = [p for p in roster["players"] if p["list"] == "reserve"]
    by_name = {r["name"]: r for r in pos.current}
    if reserve:
        out.append("## On the reserve lists\n\nTheir contracts continue and count in full (the roster as of %s).\n\n"
                   % roster_record.as_of_label(roster))
        out.append(table(["Player", "Pos", "List", "%s charge" % y],
                         [[p["name"], by_name[p["name"]]["position"] if p["name"] in by_name else p["position"],
                           words(p["status"]), money(charge(by_name[p["name"]]["years"][y])) if p["name"] in by_name else ""]
                          for p in reserve], right=(3,)))
    dead = [d for d in pos.dead if str(d["year"]) == y]
    out.append("## Dead money in %s\n\n" % y)
    out.append(table(["Player", "Charge", "Basis"], [[d["player"], money(d["amount"]), words(d["basis"])] for d in dead]
                     + [["Total", money(pos.dead_total()), ""]], right=(1,)))
    out.append("## Later commitments\n\nThe contracts already signed and the dead money already carried into each "
               "later league year; not a forecast of team spending.\n\n")
    later = [[yr, money(pos.scheduled(yr)), money(pos.dead_total(yr)) if pos.dead_total(yr) else "",
              money(pos.later(yr))] for yr in pos.years[1:] if pos.later(yr)]
    out.append(table(["League year", "Scheduled player contracts", "Dead money", "Recorded obligations"], later,
                     right=(1, 2, 3)))
    out.append("## Dated reconciliations\n\n")
    dates = sorted({pc.day(e["date"]) for _, e in dated_entries(records, counted)}) if counted else []
    dates = [d for d in dates if d.year == int(y) or (d.year == int(y) + 1 and d.month < 3)]
    if not dates:
        out.append("No contract has changed since the compliance deadline.\n\n")
    for d in reversed(dates):
        out.append(reconciliation(records, data, year, root, page, d))
    out.append("## Earlier pages\n\nThe %s keeps its dated reconciliations as they were written; the contract records "
               "now hold every figure.\n" % link(page, paths["worksheet"], "earlier cap worksheet"))
    return "".join(out)


def reconciliation(records, data, year, root, page, d):
    y = str(year)
    before = Position(records, data, year, root, d - timedelta(days=1))
    after = Position(records, data, year, root, d)
    out = ["### %s\n\n" % pc.date_words(d.isoformat())]
    for record, e in dated_entries(records, d, d):
        what = entry_change(record, e, records, root, data)
        out.append("- %s: %s (%s).\n" % (record["name"], what[:1].lower() + what[1:],
                                          link(page, e["source"], page_label(e["source"], root))))
    out.append("\n")
    rows = [["Signed contracts", "%s (%d)" % (money(before.total("contract_signed")), len(before.groups["contract_signed"])),
             "%s (%d)" % (money(after.total("contract_signed")), len(after.groups["contract_signed"])),
             change(after.total("contract_signed") - before.total("contract_signed"))],
            ["Practice squad", "%s (%d)" % (money(before.total("practice_squad")), len(before.groups["practice_squad"])),
             "%s (%d)" % (money(after.total("practice_squad")), len(after.groups["practice_squad"])),
             change(after.total("practice_squad") - before.total("practice_squad"))]]
    if before.groups["tender"] or after.groups["tender"]:
        rows.append(["Unsigned tenders", money(before.total("tender")), money(after.total("tender")),
                     change(after.total("tender") - before.total("tender"))])
    for label, fn in (("Player contracts", "contracts"), ("Dead money", "dead_total"),
                      ("Recorded obligations", "obligations")):
        a, b = getattr(before, fn)(), getattr(after, fn)()
        rows.append([label, money(a), money(b), change(b - a)])
    rows.append(["Working total with the workout charge", money(before.working_total()), money(after.working_total()),
                 change(after.working_total() - before.working_total())])
    if after.cap is not None:
        rows.append(["Difference against the league cap", money(before.difference()), money(after.difference()),
                     change(after.difference() - before.difference())])
    for yr in after.years[1:4]:
        a, b = before.later(yr), after.later(yr)
        if a or b:
            label = "%s commitments" % yr
            if after.dead_total(yr):
                label += " (scheduled %s and dead money %s)" % (money(after.scheduled(yr)), money(after.dead_total(yr)))
            rows.append([label, money(a), money(b), change(b - a)])
    out.append(table(["Measure", "Before (%s)" % pc.date_words((d - timedelta(days=1)).isoformat()), "After", "Change"],
                     rows, right=(1, 2, 3)))
    return "".join(out)


# ------------------------------------------------------------------ cap_changes.md (prefix rule)
def history_prefix(root, rel):
    from runtime.clean_pages import history, history_lengths
    path = Path(root) / rel
    data = path.read_bytes() if path.is_file() else b""
    length = history_lengths(root).get(rel)
    recorded = history(root).get(rel)
    if recorded is None:
        return data.decode("utf-8")
    from runtime.clean_pages import digest
    if isinstance(length, int) and len(data) >= length and digest(data[:length]) == recorded:
        return data[:length].decode("utf-8")
    raise ValueError("%s no longer begins with its recorded bytes; restore them before building" % rel)


def changes_page(records, data, year, root, paths):
    rel = Path(paths["changes"]).as_posix()
    head = history_prefix(root, rel)
    since = pc.history_through(root) + timedelta(days=1)
    dates = sorted({pc.day(e["date"]) for _, e in dated_entries(records, since)})
    dates = [d for d in dates if d.year == int(year) or (d.year == int(year) + 1 and d.month < 3)]
    if not dates:
        return head
    y = str(year)
    nxt = str(int(year) + 1)
    rows = []
    for d in dates:
        after = Position(records, data, year, root, d)
        business = "; ".join("%s: %s" % (rec["name"], entry_change(rec, e, records, root, data))
                             for rec, e in dated_entries(records, d, d))
        rows.append(["%s: %s" % (pc.date_words(d.isoformat()).rsplit(",", 1)[0], business), money(after.contracts()),
                     money(after.dead_total()), money(after.obligations()), money(after.workout),
                     money(after.working_total()), money(after.difference()), money(after.later(nxt))])
    text = ("\n## Changes from %s\n\nBuilt from the contract records, one line for each date with a contract "
            "change, under the full count. None is certified cap room.\n\n" % pc.date_words(since.isoformat()))
    text += table(["Date and completed business", "Player contracts", "Dead money", "Recorded obligations",
                   "Workout charge", "Working total", "Difference before carryover and reserves",
                   "%s commitments" % nxt], rows, right=(1, 2, 3, 4, 5, 6, 7))
    return head + text.rstrip("\n") + "\n"


# ------------------------------------------------------------------ the folder READMEs
def contracts_readme(year, paths):
    page = paths["contracts_readme"]
    return ("# Player contracts\n\n%s\n\n" % link(page, paths["finances"], "%s finances" % year) +
            table(["Open", "What you will find"], [
                [link(page, paths["contracts"], "Player contracts"),
                 "Every contract in force, the practice squad, the status register, the contracts that ended and the "
                 "dated update log, built from the contract records."],
                [link(page, DETAILS, "Contract details, every year"),
                 "Each player's full salary, bonus, guarantee, cap and cash schedule."],
                [link(page, paths["decisions"], "Upcoming decisions"), "What needs attention and when."]]) +
            "## Earlier pages\n\nKept as they were written before the contract records replaced them.\n\n" +
            table(["Page", "What it holds"], [
                [link(page, paths["contract_table"], "Earlier contract table"),
                 "Current-year amounts, terms and dated changes as the table recorded them."],
                [link(page, paths["status_register"], "Earlier status register"),
                 "Signed, unsigned, tendered and expiring rights, with the accrued-service evidence."]]).rstrip("\n") + "\n")


def cap_readme(year, paths):
    page = paths["cap_readme"]
    return ("# Salary cap\n\n%s\n\n" % link(page, paths["finances"], "%s finances" % year) +
            table(["Open", "What you will find"], [
                [link(page, paths["cap"], "Salary cap"),
                 "The working position under the full count, the reserve lists, dead money, later commitments and "
                 "the dated reconciliations, built from the contract records."],
                [link(page, TRACKER, "Twelve-year cap table"),
                 "Charges by player and position, dead money and future years."],
                [link(page, paths["changes"], "Dated cap changes"), "The working balance after each completed transaction."]]) +
            "## Earlier pages\n\nKept as they were written before the contract records replaced them.\n\n" +
            table(["Page", "What it holds"], [
                [link(page, paths["worksheet"], "Earlier cap worksheet"),
                 "The current-year reconciliation, the carryover calculation, the workout charge and the open items "
                 "as the worksheet recorded them."]]).rstrip("\n") + "\n")


# ------------------------------------------------------------------ the build
def page_paths(year, root):
    season = SeasonPaths(int(year), Path(root))
    return {key: season.record(rel).relative_to(Path(root).resolve()).as_posix() for key, rel in PAGES.items()}


def render(root=ROOT, year=None):
    """{repository path: text} of every page this builder owns, and the contract inputs file."""
    root = Path(root).resolve()
    year = active_season(root) if year is None else int(year)
    if year < CLEAN_SEASON:
        raise ValueError("%d is a closed season; its pages are history and are not rebuilt" % year)
    records = pc.load_all(root)
    data = pc.inputs(root)
    _TABLE["path"] = data["current_contract_table"]
    paths = page_paths(year, root)
    out = {paths["contracts"]: contracts_page(records, data, year, root, paths),
           paths["cap"]: cap_page(records, data, year, root, paths),
           paths["changes"]: changes_page(records, data, year, root, paths),
           paths["contracts_readme"]: contracts_readme(year, paths),
           paths["cap_readme"]: cap_readme(year, paths)}
    return out


def problems(root, rel, text):
    from runtime.clean_pages import text_errors
    return [] if rel.endswith(".json") else text_errors(rel, text, root)


def check(root=ROOT, year=None):
    """Every page or file that is missing, stale or would be unclean (writes nothing)."""
    root = Path(root).resolve()
    out = []
    try:
        built = render(root, year)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return ["Contract pages cannot be built: %s" % exc]
    for rel, text in built.items():
        path = root / rel
        if not path.is_file() or path.read_text(encoding="utf-8") != text:
            out.append("Contract page missing or stale: %s; run the contract page builder" % rel)
        out += problems(root, rel, text)
    return out


def write(root=ROOT, year=None):
    """Write each page that differs from its build; refuses (writes nothing) when one is unclean."""
    root = Path(root).resolve()
    built = render(root, year)
    unclean = [p for rel, text in built.items() for p in problems(root, rel, text)]
    if unclean:
        raise ValueError("unclean contract pages, nothing written: " + "; ".join(unclean[:5]))
    written = []
    for rel, text in built.items():
        path = root / rel
        if path.is_file() and path.read_text(encoding="utf-8") == text:
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        written.append(rel)
    return written


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--season", type=int)
    parser.add_argument("--check", action="store_true", help="write nothing; exit 1 when a page is stale")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    if args.check:
        found = check(args.root, args.season)
        print("\n".join(found) if found else "CONTRACT PAGES CURRENT")
        return 1 if found else 0
    try:
        written = write(args.root, args.season)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print("CONTRACT PAGES NOT WRITTEN: %s" % exc)
        return 1
    print("\n".join("wrote %s" % p for p in written) if written else "contract pages: nothing to write")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
