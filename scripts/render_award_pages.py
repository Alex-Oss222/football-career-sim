"""Readable weekly and monthly award pages. Presentation only: never select a winner.

From 2014 the pages read like the league's announcements (docs/rebuild_plan.md,
rule 4): the winner, his position and club, and his game or month from the
closed game records, then the other nominees with their photos. The winners,
nominees and their order are exactly the recorded results. How the nominees
are found and the winner drawn (the formulas, their scores and the weights)
is the season's method record (``methodology.json``, in the data area) and
the recorded results; it is never on a page, and from 2014 the award cards
(the .svg images) carry no score. Earlier seasons' pages keep their layout.
"""
from html import escape
import json
import os
from pathlib import Path
import re
import textwrap
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from runtime.seasons import CLEAN_SEASON
from scripts.player_photos import Photos, credit_short


CLEAN_FROM = CLEAN_SEASON      # the first season whose award pages read as the league's announcements


def award_cards(award, shortlist, winner_index, scores=True):
    if not 0 <= winner_index < len(shortlist) <= 3:
        raise ValueError('Award requires its recorded winner and at most three finalists')
    others = [row for i, row in enumerate(shortlist) if i != winner_index]
    slots = [others[0] if others else None, shortlist[winner_index], others[1] if len(others) > 1 else None]
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 255" role="img">',
             '<title>'+escape(award)+': recorded winner in the center</title>',
             '<rect width="960" height="255" fill="#f3f6f5"/>']
    for index, row in enumerate(slots):
        if row is None:
            continue
        x, winner = 16 + index * 315, index == 1
        parts.append(f'<rect x="{x}" y="16" width="298" height="220" rx="12" fill="white" stroke="{ "#b38b31" if winner else "#d4dddb" }" stroke-width="{4 if winner else 1}"/>')
        def line(y, value, size=17, color='#173f3c', weight='normal'):
            parts.append(f'<text x="{x+149}" y="{y}" text-anchor="middle" font-family="Arial, sans-serif" font-size="{size}" fill="{color}" font-weight="{weight}">{escape(str(value))}</text>')
        line(48, 'WINNER' if winner else ('FINALIST' if scores else 'NOMINEE'), 13, '#80601b' if winner else '#526c68', 'bold')
        for n, value in enumerate(textwrap.wrap(row['player'], 22)):
            line(94+n*25, value, 22, weight='bold')
        for n, value in enumerate(textwrap.wrap(row['team'], 29)):
            line(157+n*21, value, 16)
        if scores:
            line(213, f"Shortlist score: {row['score']:.1f}", 15, '#526c68')
    return '\n'.join(parts+['</svg>'])+'\n'


ROOT = Path(__file__).resolve().parents[1]
POSITION_WORDS = {
    "QB": "quarterback", "RB": "running back", "HB": "running back", "FB": "fullback", "WR": "wide receiver",
    "TE": "tight end", "OT": "tackle", "T": "tackle", "LT": "tackle", "RT": "tackle", "OG": "guard", "G": "guard",
    "LG": "guard", "RG": "guard", "C": "center", "OL": "offensive lineman", "DE": "defensive end",
    "DT": "defensive tackle", "NT": "nose tackle", "DL": "defensive lineman", "OLB": "linebacker",
    "ILB": "linebacker", "MLB": "linebacker", "LB": "linebacker", "CB": "cornerback", "S": "safety",
    "FS": "safety", "SS": "safety", "DB": "defensive back", "K": "kicker", "PK": "kicker", "P": "punter",
    "LS": "long snapper",
}
SPAN = {"week": "of the Week", "month": "of the Month"}
NUMBER_WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five"}


def award_title(name, kind):
    """The league's name for an award: "AFC Offensive Player of the Week"."""
    return "%s %s" % (name, SPAN[kind])


def sized(url, width):
    """A photo's address at a display width, where the image server takes one (?width=)."""
    parts = urlsplit(url)
    query = dict(parse_qsl(parts.query))
    if "width" not in query:
        return url
    query["width"] = str(width)
    return urlunsplit(parts._replace(query=urlencode(query)))


def nickname(team):
    return team.split()[-1]


def long_date(value):
    from datetime import date
    day = date.fromisoformat(value)
    return day.strftime("%B ") + str(day.day) + day.strftime(", %Y")


def month_day(value):
    from datetime import date
    day = date.fromisoformat(value)
    return day.strftime("%B ") + str(day.day)


def plural(count, one, many=None, none=False):
    """"1 yard", "3 yards"; with ``none``, "no touchdowns" for zero."""
    if none and not count:
        return "no " + (many or one + "s")
    return "%d %s" % (count, one if count == 1 else (many or one + "s"))


def stat_line(category, line):
    """The award's statistics for a player's line, in the league's words."""
    from runtime.stat_tables import g, thrown
    parts = []
    if category == "offense":
        # Passing, rushing and receiving, each a clause of its own.
        if g(line, "pass_attempts"):
            parts.append("%d of %d passing for %s, %s and %s" % (
                g(line, "completions"), g(line, "pass_attempts"), plural(g(line, "passing_yards"), "yard"),
                plural(g(line, "passing_touchdowns"), "touchdown", none=True),
                plural(thrown(line), "interception", none=True)))
        if g(line, "rushing_attempts"):
            parts.append("%s for %s" % (plural(g(line, "rushing_attempts"), "carry", "carries"),
                                        plural(g(line, "rushing_yards"), "yard"))
                         + (" and %s" % plural(g(line, "rushing_touchdowns"), "touchdown")
                            if g(line, "rushing_touchdowns") else ""))
        if g(line, "receptions"):
            parts.append("%s for %s" % (plural(g(line, "receptions"), "catch", "catches"),
                                        plural(g(line, "receiving_yards"), "yard"))
                         + (" and %s" % plural(g(line, "receiving_touchdowns"), "touchdown")
                            if g(line, "receiving_touchdowns") else ""))
    elif category == "defense":
        for field, one, many in (("tackles", "tackle", None), ("sacks", "sack", None),
                                 ("tackles_for_loss", "tackle for loss", "tackles for loss"),
                                 ("defensive_interceptions", "interception", None),
                                 ("passes_defended", "pass defended", "passes defended"),
                                 ("forced_fumbles", "forced fumble", None),
                                 ("fumble_recoveries", "fumble recovery", "fumble recoveries")):
            value = g(line, field)
            if value:
                parts.append(("%g %s" % (value, one if value == 1 else (many or one + "s"))) if field == "sacks"
                             else plural(value, one, many))
        return ", ".join(parts)
    else:
        if g(line, "field_goals_attempted"):
            parts.append("%d of %d field goals" % (g(line, "field_goals_made"), g(line, "field_goals_attempted")))
        if g(line, "extra_points_attempted"):
            parts.append("%d of %d extra points" % (g(line, "extra_points_made"), g(line, "extra_points_attempted")))
        if g(line, "punts"):
            parts.append("%s for a %.1f-yard average, %d inside the 20" % (
                plural(g(line, "punts"), "punt"), g(line, "punt_yards") / g(line, "punts"), g(line, "punts_inside_20")))
        if g(line, "kick_returns"):
            parts.append("%s for %s" % (plural(g(line, "kick_returns"), "kickoff return"),
                                        plural(g(line, "kick_return_yards"), "yard")))
        if g(line, "punt_returns"):
            parts.append("%s for %s" % (plural(g(line, "punt_returns"), "punt return"),
                                        plural(g(line, "punt_return_yards"), "yard")))
        if g(line, "special_teams_tackles"):
            parts.append(plural(g(line, "special_teams_tackles"), "coverage tackle"))
    return "; ".join(parts)


class Games:
    """The closed regular-season games of a season, read from the game records and fixtures."""

    def __init__(self, season, root=ROOT):
        from runtime.seasons import SeasonPaths
        from scripts.render_season_stats import load_receipts
        paths = SeasonPaths(season, root)
        self.receipts = load_receipts(paths.receipts)
        try:
            self.dates = {(g["week"], g["away"], g["home"]): g["date"] for g in paths.regular_games()}
        except (OSError, ValueError, KeyError):
            self.dates = {}

    def week_dates(self, weeks):
        days = sorted(d for (w, _, _), d in self.dates.items() if w in weeks)
        return (days[0], days[-1]) if days else None

    def lines(self, player, team, weeks):
        out = []
        for receipt in self.receipts:
            if int(receipt["week"]) in weeks and team in receipt.get("team_stats", {}):
                line = receipt["team_stats"][team]["players"].get(player)
                if line is not None:
                    out.append((receipt, line))
        return sorted(out, key=lambda item: int(item[0]["week"]))


def _combine(lines):
    from runtime.stat_tables import combine
    total = combine(lines)
    positions = [l.get("position") for l in lines if l.get("position")]
    if positions:
        total["position"] = positions[-1]
    return total


def winner_text(kind, category, row, games, weeks):
    """The announcement line for a winner: name, position, club, then his game or month."""
    played = games.lines(row["player"], row["team"], weeks)
    if not played:
        return "**%s, %s.**" % (row["player"], row["team"])
    line = _combine([l for _, l in played])
    position = POSITION_WORDS.get(line.get("position", ""), line.get("position", ""))
    name = "**%s, %s, %s.**" % (row["player"], position, row["team"]) if position else "**%s, %s.**" % (row["player"], row["team"])
    stats = stat_line(category, line)
    if kind == "week" and len(played) == 1:
        receipt = played[0][0]
        team = row["team"]
        opponent = next(t for t in receipt["final_score"] if t != team)
        us, them = receipt["final_score"][team], receipt["final_score"][opponent]
        result = "win over" if us > them else "loss to" if us < them else "tie with"
        day = games.dates.get((int(receipt["week"]), receipt.get("away"), receipt.get("home")))
        when = (" on " + month_day(day)) if day else ""
        place = "In the %s' %d-%d %s the %s%s" % (nickname(team), max(us, them), min(us, them), result, opponent, when)
        return "%s %s%s" % (name, place, (": %s." % stats) if stats else ".")
    count = NUMBER_WORDS.get(len(played), str(len(played)))
    span = "In %s %s" % (count, "game" if len(played) == 1 else "games")
    return "%s %s%s" % (name, span, (": %s." % stats) if stats else ".")


def _methodology_link(season):
    """The awards method beside the README (2013), or in the data area (2014 onward)."""
    if season < 2014:
        return 'methodology.json'
    from runtime.seasons import data_link
    return data_link(season, 'awards/methodology.json', 4)


def _postseason_link(season, root=ROOT):
    """The season's postseason page, from the awards README, placed by the folder map."""
    from runtime.seasons import SeasonPaths
    paths = SeasonPaths(season, root)
    return Path(os.path.relpath(paths.record('postseason/README.md'), paths.awards)).as_posix()


def _same_as_mirror(method, root):
    """Whether the method keeps the formulas, shortlist size and panel weights of the method it
    mirrors (the earlier season's file it names)."""
    mirror = (method.get('frozen') or {}).get('mirrors')
    path = Path(root) / mirror if mirror else None
    if not path or not path.is_file():
        return None
    earlier = json.loads(path.read_text(encoding='utf-8'))
    if not all(earlier.get(k) == method.get(k) for k in ('formulas', 'shortlist_size', 'panel_weights', 'award_names')):
        return None
    year = re.search(r'(20\d\d)', mirror)
    return earlier.get('season') or (year.group(1) if year else 'the earlier season')


def _winner_cell(entry, key):
    if not entry or key not in entry['awards']:
        return ''
    award = entry['awards'][key]
    row = award['shortlist'][award['winner_index']]
    return '%s (%s)' % (row['player'], nickname(row['team']))


def month_spans(method):
    """"September (Weeks 1-4, September 4 to September 29)": each award month's weeks and dates."""
    spans = []
    for month, data in (method.get('months') or {}).items():
        weeks = data.get('weeks') or []
        dates = re.findall(r'\d{4}-\d{2}-\d{2}', data.get('fixture_dates', ''))
        span = 'Weeks %d-%d' % (weeks[0], weeks[-1]) if len(weeks) > 1 else 'Week %d' % weeks[0]
        if len(dates) == 2:
            span += ', %s to %s' % (month_day(dates[0]), month_day(dates[1]))
        spans.append('%s (%s)' % (month, span))
    return spans


def render_pages(season, results, method=None, root=ROOT):
    if results and method is None:
        raise ValueError('Recorded awards require their season methodology')
    out = {}
    entries = {(v['kind'], str(v['key'])): v for v in results.values()}
    keys = list(method['award_names']) if method else []
    head = ['| %s | ' + ' | '.join(method['award_names'][k].replace(' Player', '') for k in keys) + ' |',
            '|---|' + '---|' * len(keys)] if keys else []
    index = [f'# {season} regular-season awards', '',
             '[Regular season](../README.md) · [Season](../../README.md)', '',
             "The league's players of the week and players of the month. Open a week or a month for each "
             "winner's game or month and %s." % ("the other nominees" if season >= CLEAN_FROM
                                                 else "the three finalists"), '']
    if not results:
        index += [f'No {season} award has been named yet; awards follow the closed games of each week and month.', '']
    games = Games(season, root) if results else None
    photos = Photos()
    index += ['## Players of the Week', '']
    weekly = []
    for week in range(1, 19 if season >= 2021 else 18):
        rel = f'week_{week:02d}/README.md'
        entry = entries.get(('week', str(week)))
        label = f'[Week {week}]({rel})' if entry else f'Week {week}'
        if keys:
            cells = [_winner_cell(entry, k) for k in keys] if entry else ['Awarded after the week’s games'] + [''] * (len(keys) - 1)
            weekly.append('| %s | %s |' % (label, ' | '.join(cells)))
        else:
            weekly.append(f'| {label} | {"Recorded" if entry else "Awarded after the week’s games"} |')
        if entry:
            out.update(period_page(f'Week {week}', rel, entry, method, photos=photos, games=games,
                                   clean=season >= CLEAN_FROM))
    index += [head[0] % 'Week'] + head[1:] if keys else ['| Week | Awards |', '|---|---|']
    index += weekly + ['', '## Players of the Month', '']
    months = (list(method['months']) if method and method.get('months') else
              ['September', 'October', 'November', 'December'])
    index += [head[0] % 'Month'] + head[1:] if keys else ['| Month | Awards |', '|---|---|']
    for month in months:
        rel = f'monthly/{month.lower()}/README.md'
        entry = next((v for (kind, key), v in entries.items() if kind == 'month' and key.lower() == month.lower()), None)
        label = f'[{month}]({rel})' if entry else month
        if keys:
            cells = [_winner_cell(entry, k) for k in keys] if entry else ['Awarded after the month’s games'] + [''] * (len(keys) - 1)
            index.append('| %s | %s |' % (label, ' | '.join(cells)))
        else:
            index.append(f'| {label} | {"Recorded" if entry else "Awarded after the month’s games"} |')
        if entry:
            out.update(period_page(month, rel, entry, method, back='../../README.md', photos=photos, games=games,
                                   clean=season >= CLEAN_FROM))
    if season >= CLEAN_FROM:
        index += ['', '## The awards', '']
        text = ("After each week's games the league names an offensive, a defensive and a special teams player "
                "of the week in each conference, and after each month its players of the month.")
        spans = month_spans(method) if method and method.get('frozen') else []
        if spans:
            text += " Each month covers whole weeks: " + '; '.join(spans) + "."
        index += [text, '']
    elif method and method.get('frozen'):
        index += ['', '## How the winners are chosen', '']
        weights = method.get('panel_weights') or []
        size = method.get('shortlist_size') or len(weights)
        text = ("One formula for each award scores every player from the game statistics of the week or the month. "
                "The %s best scores in each conference are the finalists, and a panel picks the winner, weighing "
                "the finalists %s by rank." % (NUMBER_WORDS.get(size, str(size)), ', '.join(str(w) for w in weights[:-1]) + ' and ' + str(weights[-1])
                                               if len(weights) > 1 else ', '.join(map(str, weights))))
        earlier = _same_as_mirror(method, root)
        text += " The method was fixed on %s, before the first award%s." % (
            long_date(method['frozen']['date']),
            (", with the same formulas, finalists and panel weights as in %s" % earlier) if earlier else '')
        spans = month_spans(method)
        if spans:
            text += " Each month covers whole NFL weeks: " + '; '.join(spans) + "."
        index += [text, '']
    else:
        index += ['', '## How the winners are chosen', '',
                  'Before the first award, the season’s method and its months are fixed from the actual schedule. '
                  'Earlier winners and monthly windows do not carry forward.', '']
    index += ['## Season honours', '',
              'Season awards and the Pro Bowl use their own dates and selection processes. Follow [postseason and Pro Bowl]('
              + _postseason_link(season, root) + ').', '']
    out['README.md'] = '\n'.join(index)
    return out


def period_page(label, relative, entry, method, back='../README.md', photos=None, games=None, clean=False):
    kind = entry.get('kind', 'week') if entry else 'week'
    heading = ('%s Players of the Week' % label) if kind == 'week' else ('%s Players of the Month' % label)
    lines = [f'# {heading}', '', f'[All regular-season awards]({back})', '']
    out = {}
    photos = photos or Photos()
    if not entry:
        lines += ['Not awarded yet. The winner and the finalists appear here after the games and the award close.', '']
        out[relative] = '\n'.join(lines)
        return out
    weeks = [int(entry['key'])] if kind == 'week' else list((method.get('months') or {}).get(entry['key'], {}).get('weeks') or [])
    span = games.week_dates(weeks) if games else None
    when = ('the games of %s to %s' % (month_day(span[0]), long_date(span[1])) if span and span[0] != span[1]
            else 'the games of %s' % long_date(span[0]) if span else 'the period’s games')
    lines += ['The league’s %s %s, for %s.' % ('players of the week for' if kind == 'week' else 'players of the month for',
                                                   label, when), '',
              '| Award | Player | Club |', '|---|---|---|']
    for key, award in entry['awards'].items():
        row = award['shortlist'][award['winner_index']]
        lines.append('| %s | %s | %s |' % (award_title(method['award_names'][key], kind), row['player'], row['team']))
    lines.append('')
    for key, award in entry['awards'].items():
        name = method['award_names'][key]
        title = award_title(name, kind)
        category = key.split('-', 1)[1] if '-' in key else key
        asset = re.sub(r'[^a-z0-9]+', '_', key.lower()) + '.svg'
        # The card keeps the award's recorded name, so the image is unchanged.
        out[(Path(relative).parent / asset).as_posix()] = award_cards(name, award['shortlist'], award['winner_index'],
                                                                      scores=not clean)
        row = award['shortlist'][award['winner_index']]
        winner = row['player']
        found = {r['player']: photos.lookup(r['player'], team=r['team']) for r in award['shortlist']}
        lines += [f'## {title}', '']
        if found[winner]:
            lines += [f'![{winner}]({sized(found[winner]["url"], 160)})', '']
        lines += [winner_text(kind, category, row, games, set(weeks)) if games else f'**{winner}, {row["team"]}.**', '',
                  f'![{name}: {winner} wins; winner centered with a gold border]({asset})', '']
        if clean:
            # The nominees as the league names them: no formula score, no selection weights.
            lines += ['| Photo | Player | Team | Result |', '|---|---|---|---|']
            for i, r in enumerate(award['shortlist']):
                thumb = found[r['player']]
                cell = f'![{r["player"]}]({sized(thumb["url"], 60)})' if thumb else ''
                lines.append(f"| {cell} | {r['player']} | {r['team']} | {'Winner' if i == award['winner_index'] else 'Nominee'} |")
            lines.append('')
        else:
            lines += ['| Photo | Player | Team | Shortlist score | Result |', '|---|---|---|---:|---|']
            for i, r in enumerate(award['shortlist']):
                thumb = found[r['player']]
                cell = f'![{r["player"]}]({sized(thumb["url"], 60)})' if thumb else ''
                lines.append(f"| {cell} | {r['player']} | {r['team']} | {r['score']:.1f} | {'Winner' if i == award['winner_index'] else 'Finalist'} |")
            lines += ['', 'The shortlist score is the award formula’s score for the %s; the panel picked the winner '
                      'from the three finalists.' % ('week' if kind == 'week' else 'month'), '']
        for n, r in found.items():
            if r:
                lines += [f'*Photo: {n}, {credit_short(r)}.*', '']
    if entry.get('note'):
        lines += [entry['note'], '']
    out[relative] = '\n'.join(lines)
    return out
