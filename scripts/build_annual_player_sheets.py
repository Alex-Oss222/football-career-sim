#!/usr/bin/env python3
"""Create or check frozen end-of-season NFL player sheets."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from dataclasses import dataclass
from datetime import date
from pathlib import Path
import sys
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from runtime.seasons import SeasonPaths
EXIT_INDEX = SeasonPaths(2014, ROOT).record('offseason/player_development/2013_exit_player_index.json')
BIRTH_DATES = ROOT / "library/data/player_birth_dates.json"

POSITION_SHEET_TRAITS = {
    "QB": ("Arm strength / velocity","Short-intermediate ball placement","Deep-outside placement","Timing / anticipation","Coverage / protection processing","Pocket movement","Scramble speed / mobility","Mechanics / release","Pressure decision-making","Ball security / command"),
    "RB": ("Vision / decision","Burst / acceleration","Long speed","Cut efficiency / change of direction","Contact balance / power","Ball security","Receiving","Route detail","Pass protection","Short-yardage finishing"),
    "FB": ("Lead blocking","Pass protection","Short-yardage power","Receiving / hands","Route / flat utility","Ball security","Special-teams utility"),
    "WR": ("Release vs press","Route running","Separation / quickness","Long speed","Hands","Catch radius / contested catches","Ball tracking / deep receiving","YAC / contact balance","Coverage recognition / adjustments","Blocking"),
    "TE": ("Route running / separation","Hands / catch radius","Contested catch / ball tracking","YAC","Run blocking","Pass protection / chip","Alignment versatility","Speed / athleticism","Coverage recognition"),
    "OT": ("Pass-set / mirror","Anchor vs power","Hand usage / punch","Recovery / balance","Drive blocking","Reach / movement blocking","Second-level work","Twist / blitz recognition","Assignment / penalty consistency"),
    "G": ("Interior pass protection","Anchor / power","Hand usage","Recovery / balance","Drive blocking","Pull / movement blocking","Combination / second-level work","Stunt / blitz recognition","Leverage / consistency"),
    "C": ("Snap / operation","Protection identification / calls","Pass anchor","Hand usage","Run-fit / combination blocking","Reach / movement blocking","Second-level work","Leverage","Communication"),
    "DE": ("Get-off","Edge speed / bend","Power","Hand use / counters","Edge setting / run defense","Block shedding","Pursuit","Rush plan / recognition","Contain discipline"),
    "DT": ("Get-off","Anchor","Power","Hand use","Block shedding","Penetration","Pass-rush counters","Double-team play","Gap discipline / lateral pursuit"),
    "LB": ("Run diagnosis","Fit discipline","Block destruction","Range","Tackling","Zone coverage","Man coverage","Blitz / pressure","Communication","Pursuit angles"),
    "CB": ("Long / recovery speed","Short-area quickness / hips","Press coverage","Off-man coverage","Zone / pattern match","Route recognition / eyes","Ball skills","Catch-point play","Tackling / run support","Block defeat / penalty discipline"),
    "DB": ("Long / recovery speed","Short-area quickness / hips","Press coverage","Off-man coverage","Zone / pattern match","Route recognition / eyes","Ball skills","Catch-point play","Tackling / run support","Block defeat / penalty discipline"),
    "S": ("Range","Speed / change of direction","Route-combination recognition","Deep positioning","Man / slot coverage","Ball skills","Tackling","Run support / angles","Communication","Play-action discipline"),
    "K": ("Field-goal accuracy by distance","Leg strength / range","Kickoff distance / hang","Directional kickoff control","Snap-hold operation","Pressure consistency"),
    "P": ("Gross distance","Hang time","Net / location control","Directional punting","Plus-territory control","Catch-to-kick operation","Pressure consistency"),
    "LS": ("Snap accuracy","Snap velocity","Target consistency","Field-goal snap trajectory","Punt snap trajectory","Protection transition","Coverage / tackling"),
}

@dataclass(frozen=True)
class SheetPlayer:
    player: str
    pos: str
    age: int | None
    identity: str
    evidence: str

def slugify(name: str) -> str:
    ascii_name=unicodedata.normalize("NFKD",name).encode("ascii","ignore").decode()
    slug=re.sub(r"[^a-z0-9]+","_",ascii_name.lower()).strip("_")
    if not slug:
        raise ValueError("player name cannot produce an empty slug")
    return slug

def _cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]

def completed_years(birth_date: str,on_date: date) -> int:
    born=date.fromisoformat(birth_date)
    return on_date.year-born.year-((on_date.month,on_date.day)<(born.month,born.day))

def season_is_complete(season: int, root: Path = ROOT) -> bool:
    if season==2013:
        return True
    return any(path.is_file() for path in season_closeout_paths(season, root))


def season_closeout_paths(season: int, root: Path = ROOT) -> tuple[Path, ...]:
    paths = SeasonPaths(season, root)
    # The adopted season-review report is the owner. Keep the earlier name
    # readable for completed histories without requiring a duplicate report.
    return (paths.record('closeouts/season_review.md'),
            paths.record('closeouts/season_closeout.md'))

def load_season_players(season: int, root: Path = ROOT):
    if not season_is_complete(season, root):
        raise ValueError(f"{season} annual Player Sheets are final-season records; the season is not closed")
    if season!=2013:
        errors = final_closeout_errors(season, root)
        if errors:
            raise ValueError('; '.join(errors))
        from scripts.update_player_cards import profile_errors
        errors = profile_errors(season, root, require_complete=True)
        if errors:
            raise ValueError('; '.join(errors))
        players = []
        # Retained entry/opening cards define the annual cohort, including
        # departures. Receipts detect missing game participants below, but a
        # departed player with no game receipt cannot be recovered if his card
        # was deleted before the first review. Keep that archive intact and
        # reconcile it against the season's source history during exit review.
        for path in assessment_paths(SeasonPaths(season, root).record('player_profiles')):
            text = path.read_text(encoding='utf-8')
            name = re.search(r'^# (.+?) — ', text, re.M)[1]
            age = card_field(text, 'Age')
            players.append(SheetPlayer(name, card_field(text, 'Position'),
                                       int(age) if age.isdigit() else None,
                                       card_field(text, 'Player identity'),
                                       path.relative_to(root).as_posix()))
        from scripts.update_player_cards import period_data
        participants = set().union(*(period_data(season, post, root)['players']
                                     for post in (False, True)))
        missing = participants - {player.player for player in players}
        if missing:
            raise ValueError(f'{season}: recorded participants lack retained opening cards: '+', '.join(sorted(missing)))
        return f'{season} completed season; see each authored exit-review checkpoint', players
    data=json.loads((root/EXIT_INDEX.relative_to(ROOT)).read_text(encoding="utf-8"))
    births=json.loads((root/BIRTH_DATES.relative_to(ROOT)).read_text(encoding="utf-8"))["players"]
    checkpoint=date.fromisoformat(data["evidence_through"])
    if data["season"] != season or data["count"] != len(data["players"]):
        raise ValueError("annual-sheet exit index season/count mismatch")
    slugs=[slugify(row["player"]) for row in data["players"]]
    if len(set(slugs)) != len(slugs):
        raise ValueError("annual-sheet exit index has duplicate player paths")
    players=[]
    for row in data["players"]:
        name=row["player"]
        birth=births.get(name,{}).get("birth_date")
        age=completed_years(birth,checkpoint) if birth else None
        if row["pos"] not in POSITION_SHEET_TRAITS:
            raise ValueError(f"unsupported annual-sheet position: {row['pos']}")
        players.append(SheetPlayer(name,row["pos"],age,row["identity"],row["evidence"]))
    return f"2013 season complete; {checkpoint.strftime('%B')} {checkpoint.day}, {checkpoint.year} exit-review close",players

def render_player_sheet(player: SheetPlayer,season: int,checkpoint: str) -> str:
    if season != 2013:
        raise ValueError('2014-onward final assessments must be authored from reviewed season evidence; use --review')
    traits=POSITION_SHEET_TRAITS[player.pos]
    age=str(player.age) if player.age is not None else "Unverified"
    grade_rows=["| Overall at position | — /10 | Unassessed | Unassessed |"]
    grade_rows += [f"| {trait} | — /10 | Unassessed | Unassessed |" for trait in traits]
    comparison_rows=[f"| {trait} | Unassessed | Unassessed | Unassessed | Unassessed | Pending historical benchmark |" for trait in traits]
    return f"""# {player.player} — {season} NFL Player Sheet

**Team:** Jacksonville Jaguars  
**Season:** {season}  
**Season-close checkpoint:** {checkpoint}  
**Age at exit-review close:** {age}  
**Position:** {player.pos}  
**NFL standing:** Unassessed  
**Player identity:** {player.identity}  

> Final {season} season evaluation. This is not a {season+1} entry projection or offseason development plan.

## Position grades

| Position trait | Grade | NFL standing | Evidence quality |
| --- | ---: | --- | --- |
{chr(10).join(grade_rows)}

## Historical NFL benchmark

| Trait | Sim player | vs. {season} NFL average | vs. {season} top reference | vs. {season} low-end reference | Basis |
| --- | --- | --- | --- | --- | --- |
{chr(10).join(comparison_rows)}

## Season production in context

Use branch production only as context. Do not turn a box-score total into an arm, route, blocking, recognition or coverage grade without football evidence.

## Same-player real-world comparison

Optional, and only after the simulation evaluation is fixed. The real-world same-season player cannot set this branch grade or later development.

## What made him this player in {season}

- {player.identity}

## Play style

Unassessed beyond the supported identity above.

## Best traits

- Preserve only traits supported by the season evidence.

## Main weaknesses

- Preserve only weaknesses supported by the season evidence.

## Evidence and uncertainty

- **Branch evidence used:** [2013 exit-review record](../../../{player.evidence}) and its linked season evidence.
- **Historical benchmark method:** [position benchmarks](../../../library/annual_player_sheet_benchmark_method.md).
- **What is established:** See player identity and any filled grades.
- **What remains uncertain:** Any position trait still marked Unassessed.

**One-line description:**  
{player.identity}
"""

def target_path(season: int,player_name: str, root: Path = ROOT) -> Path:
    # The live opening card and the final review must never share a destination.
    directory = ('player_profiles' if season == 2013
                 else 'closeouts/player_assessments')
    return SeasonPaths(season, root).record(directory) / (slugify(player_name)+'.md')

GENERAL_TRAITS = ('Overall', 'Athleticism', 'Speed', 'Strength / Power',
                  'Agility / Change of direction', 'Technique', 'Football IQ')


def assessment_paths(directory: Path) -> list[Path]:
    return sorted(p for p in directory.glob('*.md')
                  if p.name.upper() not in {'README.MD', 'TEMPLATE.MD'})


def card_field(text: str, label: str) -> str:
    match = re.search(r'^\*\*'+re.escape(label)+r':\*\*[^\S\n]*(.*?)\s*$', text, re.M)
    return match[1].strip() if match else ''


def card_section(text: str, heading: str) -> str:
    match = re.search(r'^## '+re.escape(heading)+r'\n(.*?)(?=\n## |\Z)', text, re.M|re.S)
    return match[1].strip() if match else ''


def filled(value: str) -> bool:
    value = re.sub(r'<!--.*?-->', '', value, flags=re.S).strip(' \n\t-*')
    return bool(value) and not re.fullmatch(r'(?:—|TBD|TODO|Unassessed|Pending|\[[^\]]*\])', value, re.I)


def assessment_card_errors(path: Path, season: int, player: str, pos: str, *,
                           stage: str = 'opening', root: Path = ROOT) -> list[str]:
    """Validate authored personnel content, without generating any judgment.

    Position traits may use the author's football vocabulary (rookie cards do),
    but every named trait needs a grade and all three league comparisons.
    Source lineage and review hashes are checked separately by the handoff.
    """
    label = path.relative_to(root).as_posix()
    if not path.is_file():
        return [f'{label}: missing {stage} annual assessment']
    text = path.read_text(encoding='utf-8')
    errors = []
    expected = {'Season': str(season), 'Position': pos,
                'Assessment stage': 'Opening annual assessment' if stage == 'opening' else 'Final annual assessment',
                'Profile status': 'Working player card' if stage == 'opening' else 'Final annual assessment'}
    title = re.search(r'^# (.+?) — (\d{4})\b', text, re.M)
    if not title or title.groups() != (player, str(season)) or path.stem != slugify(player):
        errors.append(f'{label}: wrong player/season identity')
    for key, value in expected.items():
        if card_field(text, key) != value:
            errors.append(f'{label}: wrong {key.lower()}')
    for key in ('Team', 'Checkpoint', 'Age', 'NFL standing', 'Player identity', 'Evaluation policy', 'Previous annual profile'):
        if not filled(card_field(text, key)):
            errors.append(f'{label}: missing authored {key.lower()}')
    if pos not in POSITION_SHEET_TRAITS:
        errors.append(f'{label}: unsupported position {pos}')
    grades = _table_rows(text, 'Player grades')
    names = [row[0] for row in grades if row]
    if names[:7] != list(GENERAL_TRAITS) or len(names) < 10 or len(set(names[7:])) != len(names[7:]):
        errors.append(f'{label}: missing/duplicate general or position grade traits')
    for row in grades:
        if (len(row) != 3 or not re.fullmatch(r'(?:[1-9](?:\.\d+)?|10(?:\.0+)?) /10', row[1])
                or not filled(row[0]) or not filled(row[2])):
            errors.append(f'{label}: incomplete or invalid authored grade row')
            break
    comparisons = _table_rows(text, 'League comparison')
    if (sorted(row[0] for row in comparisons if row) != sorted(names[1:])
            or any(len(row) != 4 or not all(filled(v) for v in row) for row in comparisons)):
        errors.append(f'{label}: missing/duplicate trait comparisons or unfinished comparison rows')
    for heading in ('Established player state', 'Historical comparison', 'Play style',
                    'Best traits', 'Main weaknesses', 'Evidence and uncertainty'):
        if not filled(card_section(text, heading)):
            errors.append(f'{label}: missing authored {heading}')
    support = card_section(text, 'What supports this assessment')
    if not support:
        headings = re.findall(r'^## (What makes him .+)$', text, re.M)
        support = card_section(text, headings[0]) if headings else ''
    if not filled(support):
        errors.append(f'{label}: missing authored assessment support')
    changes = _table_rows(text, 'Year-over-year change')
    if ((stage == 'final' and not changes)
            or not filled(card_section(text, 'Year-over-year change'))
            or any(len(row) != 5 or not all(filled(v) for v in row) for row in changes)):
        errors.append(f'{label}: incomplete year-over-year change table')
    description = card_field(text, 'One-line description')
    if not description:
        match = re.search(r'^\*\*One-line description:\*\*\s*\n([^\n]+)', text, re.M)
        description = match[1] if match else ''
    if not filled(description):
        errors.append(f'{label}: missing one-line description')
    if stage == 'final' and not filled(card_section(text, 'Change from the opening assessment')):
        errors.append(f'{label}: missing authored change from the opening assessment')
    return errors


def _source_path(root: Path, relative: str) -> Path:
    from runtime.events import resolve_path
    return resolve_path(root, relative, mapping=None if (root/'docs/repository_map.json').is_file() else {})


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _handoff_path(season: int, root: Path) -> Path:
    return SeasonPaths(season, root).record('closeouts/season_handoff.json')


def final_closeout_errors(season: int, root: Path = ROOT) -> list[str]:
    """A filename alone cannot authorize completed-season judgments."""
    if not season_is_complete(season, root):
        return [f'{season} final player assessments require a completed season close']
    path = _handoff_path(season, root)
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return [f'{season}: missing or invalid season handoff for final assessments']
    if data.get('season') != season:
        return [f'{season}: wrong season handoff identity']
    errors = []
    closeouts = {path.resolve() for path in season_closeout_paths(season, root)}
    for name in ('team_season_closed', 'exit_interviews'):
        gate = data.get('gates', {}).get(name, {})
        evidence = gate.get('evidence', [])
        if gate.get('status') != 'COMPLETE' or not evidence:
            errors.append(f'{season}: final assessments require reviewed {name}')
            continue
        paths = set()
        for item in evidence:
            try:
                source = _source_path(root, item['path'])
                paths.add(source.resolve())
                if not source.is_file() or item.get('sha256') != _digest(source):
                    raise ValueError('stale evidence')
            except (KeyError, TypeError, ValueError, OSError):
                errors.append(f'{season}: missing or changed {name} evidence')
        if name == 'team_season_closed' and not closeouts & paths:
            errors.append(f'{season}: season closeout must be reviewed as team_season_closed evidence')
    return errors


def local_card_sources(path: Path, root: Path) -> set[Path]:
    """Resolve local Markdown citations and reject missing/escaping evidence."""
    sources = set()
    for target in re.findall(r'\]\(([^\s)]+)\)', path.read_text(encoding='utf-8')):
        if ':' in target or target.startswith('#'):
            continue
        source = (path.parent/unquote(target.split('#')[0].strip('<>'))).resolve()
        try:
            relative = source.relative_to(root.resolve()).as_posix()
        except ValueError:
            raise ValueError(f'{path.relative_to(root)}: evidence escapes the repository')
        source = _source_path(root, relative)
        if not source.is_file():
            raise ValueError(f'{path.relative_to(root)}: missing assessment evidence: {relative}')
        sources.add(source.resolve())
    return sources


def _final_review_receipt(season: int, players: list[SheetPlayer], root: Path) -> dict:
    manifest = json.loads(_handoff_path(season, root).read_text(encoding='utf-8'))
    sources = set()
    for name in ('team_season_closed', 'exit_interviews'):
        sources.update(_source_path(root, row['path']).resolve()
                       for row in manifest['gates'][name]['evidence'])
    cards = {}
    for player in players:
        path = target_path(season, player.player, root)
        cards[path.relative_to(root).as_posix()] = _digest(path)
        sources.add((root/player.evidence).resolve())
        sources.update(local_card_sources(path, root))
    paths = SeasonPaths(season, root)
    for directory in (paths.receipts, paths.postseason_receipts):
        # Other clubs can finish their league closeout after Jacksonville's
        # review. Only the receipts used in these player tables are sources.
        sources.update(path.resolve() for path in directory.glob('*.json')
                       if 'Jacksonville Jaguars' in json.loads(path.read_text(encoding='utf-8')).get('team_stats', {}))
    return {'season': season, 'cards': cards,
            'source_sha256': {p.relative_to(root.resolve()).as_posix(): _digest(p) for p in sorted(sources)}}


def final_assessment_errors(season: int, root: Path = ROOT, *,
                            require_complete: bool = False, require_reviewed: bool | None = None) -> list[str]:
    """Readiness is explicit: an unfinished future season may have no finals."""
    if season < 2014:
        return []
    if require_reviewed is None:
        manifest_path = _handoff_path(season, root)
        try:
            prior = json.loads(manifest_path.read_text(encoding='utf-8')) if manifest_path.is_file() else {}
        except (OSError, ValueError):
            return [f'{season}: missing or invalid season handoff for final assessments']
        # Once reviewed, the final set is frozen history even when someone
        # removes every card. An unfinished future year has no such receipt.
        require_reviewed = 'final_assessment_review' in prior
    finals = assessment_paths(target_path(season, 'example', root).parent)
    if not finals and not (require_complete or require_reviewed):
        return []
    if finals and not season_is_complete(season, root):
        return [f'{season} final player assessments exist before season close']
    errors = final_closeout_errors(season, root)
    if errors:
        return errors
    try:
        _, players = load_season_players(season, root)
    except (ValueError, OSError) as error:
        return [str(error)]
    expected = {target_path(season, p.player, root) for p in players}
    errors.extend(f'unexpected annual profile: {p.relative_to(root)}' for p in finals if p not in expected)
    manifest = json.loads(_handoff_path(season, root).read_text(encoding='utf-8'))
    exit_sources = {_source_path(root, item['path']).resolve()
                    for item in manifest['gates']['exit_interviews']['evidence']}
    from scripts.update_player_cards import START, END, refresh_text, period_data, section
    try:
        periods = {post: period_data(season, post, root) for post in (False, True)}
    except (ValueError, OSError, KeyError) as error:
        return errors+[f'{season}: invalid final statistics evidence: {error}']
    for player in players:
        path = target_path(season, player.player, root)
        errors.extend(assessment_card_errors(path, season, player.player, player.pos, stage='final', root=root))
        if not path.is_file():
            continue
        text = path.read_text(encoding='utf-8')
        opening = (root/player.evidence).resolve()
        try:
            sources = local_card_sources(path, root)
        except ValueError as error:
            errors.append(str(error))
            sources = set()
        if opening not in sources:
            errors.append(f'{path.relative_to(root)}: must link the same-year opening assessment')
        if not sources & exit_sources:
            errors.append(f'{path.relative_to(root)}: must link reviewed exit-interview evidence')
        old = opening.read_text(encoding='utf-8')
        if text.count(START) != 1 or text.count(END) != 1 or not text.rstrip().endswith(END):
            errors.append(f'{path.relative_to(root)}: final statistics require a single block at the bottom')
            continue
        try:
            if refresh_text(text, season, player.player, player.pos, periods, root) != text:
                errors.append(f'{path.relative_to(root)}: final statistics differ from season receipts')
        except ValueError as error:
            errors.append(f'{path.relative_to(root)}: {error}')
        for heading in ('Regular-season statistics by year', 'Playoff statistics by year'):
            prior = lambda value: [line for line in section(value, heading).splitlines()
                                   if re.match(r'^\| \d{4} \|', line) and not line.startswith(f'| {season} |')]
            if prior(text) != prior(old):
                errors.append(f'{path.relative_to(root)}: final assessment changed earlier-year statistics')
    if require_reviewed and not errors:
        if manifest.get('final_assessment_review') != _final_review_receipt(season, players, root):
            errors.append(f'{season}: final assessment review is missing or stale; review authored cards with --review')
    return errors


def review_final_assessments(season: int, root: Path = ROOT) -> int:
    """Stamp reviewed authored cards only; never write a grade or a final card."""
    if season < 2014:
        raise ValueError('--review applies to authored 2014-onward final assessments')
    errors = final_assessment_errors(season, root, require_complete=True, require_reviewed=False)
    if errors:
        raise ValueError('\n'.join(errors))
    _, players = load_season_players(season, root)
    path = _handoff_path(season, root)
    manifest = json.loads(path.read_text(encoding='utf-8'))
    manifest['final_assessment_review'] = _final_review_receipt(season, players, root)
    path.write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
    return len(players)

def _table_rows(text: str, section: str) -> list[list[str]]:
    body=text.split(f"## {section}\n",1)[-1].split("\n## ",1)[0]
    rows=[_cells(line) for line in body.splitlines() if line.startswith("|")]
    return rows[2:]

def check_profiles(season: int,players: list[SheetPlayer], root: Path = ROOT) -> list[str]:
    if season >= 2014:
        return final_assessment_errors(season, root, require_complete=True, require_reviewed=True)
    errors=[]
    checkpoint,_=load_season_players(season,root)
    for player in players:
        path=target_path(season,player.player,root)
        if not path.exists():
            errors.append(f"missing annual profile: {path.relative_to(root)}")
            continue
        text=path.read_text(encoding="utf-8")
        age=str(player.age) if player.age is not None else "Unverified"
        for required in (f"# {player.player} — {season} NFL Player Sheet",f"**Season:** {season}",f"**Position:** {player.pos}",f"**Season-close checkpoint:** {checkpoint}",f"**Age at exit-review close:** {age}","## Position grades","## Historical NFL benchmark","## Same-player real-world comparison"):
            if required not in text:
                errors.append(f"{path.relative_to(root)} missing required content: {required}")
        traits=POSITION_SHEET_TRAITS[player.pos]
        grades=_table_rows(text,"Position grades")
        if [row[0] for row in grades] != ["Overall at position",*traits]:
            errors.append(f"{path.relative_to(root)}: position grade traits differ from {player.pos}")
        for row in grades:
            if len(row) != 4 or not re.fullmatch(r"(?:—|(?:[1-9](?:\.0|\.5)?|10(?:\.0)?)) /10",row[1]):
                errors.append(f"{path.relative_to(root)}: invalid position grade row")
            elif row[1] == "— /10" and row[2:] != ["Unassessed","Unassessed"]:
                errors.append(f"{path.relative_to(root)}: unassessed grade has assessed standing/evidence")
        benchmarks=_table_rows(text,"Historical NFL benchmark")
        names=[row[0] for row in benchmarks]
        if any(names.count(trait) != 1 for trait in traits) or any(len(row) != 6 for row in benchmarks):
            errors.append(f"{path.relative_to(root)}: missing/duplicate position benchmarks or malformed rows")
        if not (root/player.evidence).is_file():
            errors.append(f"{path.relative_to(root)}: missing frozen branch evidence")
    expected={target_path(season,p.player,root) for p in players}
    for path in target_path(season, 'example', root).parent.glob("*.md"):
        if path.name != "README.md" and path not in expected:
            errors.append(f"unexpected annual profile: {path.relative_to(root)}")
    return errors

def repository_profile_errors(root: Path = ROOT) -> list[str]:
    _,players=load_season_players(2013,root)
    errors=check_profiles(2013,players,root)
    mapping = root/'docs/repository_map.json'
    active = json.loads(mapping.read_text(encoding='utf-8')).get('active_season') if mapping.is_file() else None
    for season_dir in (root/"career").glob("[0-9][0-9][0-9][0-9]"):
        season=int(season_dir.name)
        directory=SeasonPaths(season, root).record('player_profiles')
        if not season_is_complete(season,root) and any(
            p.name not in {"README.md","TEMPLATE.md"} and not all(marker in p.read_text(encoding="utf-8") for marker in ("**Profile status:** Working player card", "<!-- yearly-statistics:start -->", "<!-- yearly-statistics:end -->"))
            for p in directory.glob("*.md")
        ):
            errors.append(f"{season} annual Player Sheets exist before season close")
        if season >= 2014:
            from scripts.update_player_cards import profile_errors
            errors += profile_errors(season,root,require_complete=(season == active))
            errors += final_assessment_errors(season,root)
    return errors

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--season",type=int,required=True)
    parser.add_argument("--check",action="store_true")
    parser.add_argument("--force",action="store_true")
    parser.add_argument("--review", action="store_true",
                        help="2014+: review already-authored final cards and freeze their evidence hashes in the existing handoff")
    args=parser.parse_args()
    if args.season >= 2014:
        if args.force:
            parser.error('--force cannot overwrite authored 2014-onward final assessments')
        try:
            if args.review:
                count = review_final_assessments(args.season)
                print(f'ANNUAL_PLAYER_SHEETS: REVIEWED season {args.season}, {count} authored final sheets')
                return 0
            if not args.check:
                parser.error('Author final cards with foundation/templates/player_sheet_2014_onward_template.md, then use --review; this command never invents final assessments')
            errors = final_assessment_errors(args.season, require_complete=True, require_reviewed=True)
        except (ValueError, OSError) as error:
            errors = [str(error)]
        for error in errors:
            print('ERROR: '+error)
        if not errors:
            print(f'ANNUAL_PLAYER_SHEETS: READY season {args.season}')
        return int(bool(errors))
    if args.review:
        parser.error('--review applies to 2014-onward authored assessments; the 2013 builder is unchanged')
    checkpoint,players=load_season_players(args.season)
    if args.check:
        errors=check_profiles(args.season,players)
        if errors:
            print("ANNUAL_PLAYER_SHEETS: STALE")
            for error in errors:
                print("- "+error)
            return 1
        print(f"ANNUAL_PLAYER_SHEETS: READY season {args.season}, {len(players)} final sheets")
        return 0
    created=updated=kept=0
    for player in players:
        path=target_path(args.season,player.player)
        path.parent.mkdir(parents=True,exist_ok=True)
        if path.exists() and not args.force:
            kept+=1
            continue
        existed=path.exists()
        path.write_text(render_player_sheet(player,args.season,checkpoint),encoding="utf-8")
        updated+=int(existed)
        created+=int(not existed)
    print(f"ANNUAL_PLAYER_SHEETS: season {args.season}, created {created}, updated {updated}, kept {kept}")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
