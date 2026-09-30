#!/usr/bin/env python3
"""Create or check frozen end-of-season NFL player sheets."""
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from dataclasses import dataclass
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXIT_INDEX = ROOT / "career/2014/offseason/player_development/2013_exit_player_index.json"
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
    return (root/f"career/{season}/closeouts/season_closeout.md").exists()

def load_season_players(season: int, root: Path = ROOT):
    if not season_is_complete(season, root):
        raise ValueError(f"{season} annual Player Sheets are final-season records; the season is not closed")
    if season!=2013:
        raise ValueError(f"{season} closeout-backed annual-sheet population is not implemented yet")
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
    return root/f"career/{season}/player_profiles/{slugify(player_name)}.md"

def _table_rows(text: str, section: str) -> list[list[str]]:
    body=text.split(f"## {section}\n",1)[-1].split("\n## ",1)[0]
    rows=[_cells(line) for line in body.splitlines() if line.startswith("|")]
    return rows[2:]

def check_profiles(season: int,players: list[SheetPlayer], root: Path = ROOT) -> list[str]:
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
    for path in (root/f"career/{season}/player_profiles").glob("*.md"):
        if path.name != "README.md" and path not in expected:
            errors.append(f"unexpected annual profile: {path.relative_to(root)}")
    return errors

def repository_profile_errors(root: Path = ROOT) -> list[str]:
    _,players=load_season_players(2013,root)
    errors=check_profiles(2013,players,root)
    for directory in (root/"career").glob("[0-9][0-9][0-9][0-9]/player_profiles"):
        season=int(directory.parent.name)
        if not season_is_complete(season,root) and any(p.name != "README.md" for p in directory.glob("*.md")):
            errors.append(f"{season} annual Player Sheets exist before season close")
    return errors

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--season",type=int,required=True)
    parser.add_argument("--check",action="store_true")
    parser.add_argument("--force",action="store_true")
    args=parser.parse_args()
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
