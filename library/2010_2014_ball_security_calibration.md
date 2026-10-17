# 2010-2014 ball-security calibration

[Pre-build specification](2014_6_pre_build_specification.md) · [League base](2010_2014_calibration_base.md) · [Engine decisions](../runtime/2014_engine_decisions.md) · [Defect register](../runtime/defect_register.md)

**What this is.** The league record behind kernel 2014.6's ball security (batch B10): the band centres the fumble, muff and kicking-team-recovery rows are graded against, and the sourced shares the engine's credit draws read. The artifact is `library/data/2010_2014w4_ball_security.json`, built by `scripts/research/build_2010_2014_ball_security.py` with a `--check` mode, under the rules of the pre-build specification (section 4, Ball security and penalties; section 5, the B10 rows). Nothing in it is typed by hand.

**Data window.** NFL regular seasons 2010-2013 and 2014 Weeks 1-4 (games through September 29, 2014), read only through the batch B2 source gate. 2013 and 2014 Weeks 1-4 are an anonymous post-divergence league population: they enter pooled counts only. No club's, game's or player's own row is stored; identifiers are read only to count games and team-games and to find a player's position group on that season's roster.

## What the engine models and what it draws from

The fumbles themselves are not drawn here. They come from the replayed real drives and kick records of the 2010-2014 league base (`library/data/2010_2014w4_nfl_field_position_model.json`): every drive carries its own fumbles (snap order, kind, outcome, forced, the forcer's and recoverer's position groups), and every kick record its muff or return fumble. This record supplies only what those annotations do not:

- **The band centres.** The real league's rates in the scope the engine draws, so a 2014.6 cohort can be graded.
- **Credit shares.** Who is named on a fumble the record describes only by group: the quarterback or the centre on an aborted snap, a kick-return fumble's forced share, a kept kick fumble or muff recovered by the player who lost it, and, for a lost fumble the replayed drive does not describe (a fourth-down attempt's fumble, batch B9F), the forced share and the forcer's and recoverer's groups by kind. Every name drawn from these shares is a group draw: it carries an `attribution` field and is never player evidence (`runtime/2014_engine_decisions.md`, E1).

## How each piece is counted

- **A fumble** is a play with the feed's fumble flag. A play a penalty nullified carries none. A punt muff carries the flag; most kickoff muffs do not (the receiving club never possessed the ball), so they are not fumbles here and the engine does not count them as fumbles either (it records them as muffs).
- **The modelled scope** is every fumble less the defense's own fumbles after a turnover, which the engine does not model. The kicking club's fumbles on its own kick plays and fumbles on field goals and tries are not modelled either; they are kept in the centre and listed (a handful in five seasons).
- **Kinds.** A scrimmage fumble is a run, a reception, a sack or an aborted snap (the committed annotation's kind). A kick fumble is the receiving club's muff or return fumble on a kickoff or a punt.
- **Outcomes.** Lost (the fumbling club lost the ball), out of bounds, or kept (the fumbling club recovered). The offense-kept share counts kept and out of bounds.
- **Kicking-team recoveries** are the retained kick records of the committed field-position artifact: punts in every season, kickoffs from the 35 from 2011, touchdowns and onside kicks left out (the onside kicks are batch B9's). That is exactly the scope the engine draws them in, so the centre is their count per team-game of their own seasons, punts and kickoffs added. A per-play count of the receiving club's lost kick fumbles is kept beside it as a cross-check; it is larger because it also holds 2010's kickoffs from the 30, return touchdowns and onside recoveries.
- **The muffer role share** is the share of muffed kick records whose muffer was the play's returner, among those whose muffer the feed records. No muffed record in the pool names another player, so the engine names the club's returner on every muff whose role is recorded; a muff with no recorded muffer names him by convention and is counted apart.
- **Muffs per punt** are punt plays whose counted description says MUFF and carry the fumble flag, over punt attempts. The receiving club's keep share of punt muffs (kept or out of bounds) is the definition behind the plan's 0.70.
- **Drift.** Each rate and share carries its per-season counts and a homogeneity test. Equal weight per event is the adopted weighting (default 1B.1); a drift is reported, never fitted.

## Two passes

The primary pass reads nflverse through the committed loader. The second pass reads nflscrapR's raw rows with separately written parsing: the kind from the description and the source's own flags, the outcome from the recovering team. Both files derive from the NFL GSIS feed, so the second pass checks the parse, not an independent observation of the seasons. Two readings are explained, never repaired: nflscrapR's 2014 Weeks 1-4 file leaves eight offense-retained fumbles without its fumble flag (lost fumbles agree), and nflscrapR does not separate a kept fumble that went out of bounds, so that split is single-pass. The official totals (Pro Football Reference) could not be fetched from this environment (403), so the gap the design measured between the official 2012 fumble count and play-by-play stays unresolved; the engine's events are play-by-play records, so the play-by-play definition is the one used.

## Honest limits

- Individual ball security, returner muffs and defender forcing are **not studied** (admissible 2010-2012 evidence exists): the engine carries them as named slope-0 terms, so no player's history moves a fumble, a muff or a forced fumble, and a real player's own 2013-2014 rows never set his value.
- Within a position group the forcer and the recoverer are drawn evenly from the players on the field. No sourced within-group share exists; it is a labelled convention.
- Overtime punts exclude retained records until a two-source rule amendment on muffs (the receiving club never possessed) against return fumbles (it possessed) is recorded. The named sources for it are the 2014 NFL rulebook's Rule 16 (operations.nfl.com) with the NFL.com overtime approved ruling, and Pro Football Talk (McKay, January 6, 2011) as corroboration; none of them was read for this record. The engine counts every overtime punt the exclusion touched (`ot_punt_retained_excluded`, and the retained records it set aside, `ot_punt_retained_records_excluded`). Overtime kickoffs keep their retained records: rule R4 already treats a kicking-club recovery of the opening kickoff as the receiving club's opportunity (batch B8).
- The fumble, muff, forced-fumble and recovery counters are stat-line credit. They are never player evidence or progression evidence (E1), and the lost-fumble observation the kernel wrote before batch B10 is withheld under the credit.

## Figures

<!-- generated:begin -->
Generated by `scripts/research/build_2010_2014_ball_security.py` from the artifact; do not edit.

| Centre | Count | Of | Value | Season drift p |
|---|---|---|---|---|
| fumbles per team game | 2831 | 2170 | 1.3046 | 0.238 |
| lost per team game | 1355 | 2170 | 0.6244 | 0.463 |
| offense kept share of scrimmage fumbles | 1152 | 2318 | 0.4970 | 0.972 |
| sack share of lost scrimmage fumbles | 369 | 1166 | 0.3165 | 0.012 |
| forced share of lost non aborted scrimmage fumbles | 1007 | 1064 | 0.9464 | 0.693 |
| forcer also recovers | 142 | 1006 | 0.1412 | 0.920 |
| muffs per punt | 264 | 10475 | 0.0252 | 0.608 |
| punt muff receiving keep share | 185 | 264 | 0.7008 | 0.795 |
| kicking-team recoveries per team-game (punts) | 105 | 2170 | 0.0484 | 0.541 |
| kicking-team recoveries per team-game (kickoffs from 2011) | 41 | 1658 | 0.0247 | 0.947 |
| muffer role share (returner) | 267 | 267 | 1.0000 | - |

Kicking-team recoveries per team-game, the centre (punts plus kickoffs): 0.0731. Team-game dispersion of fumbles (variance over mean): 1.105. Left out of the modelled scope: 19 defensive fumbles after a turnover; counted in the centre but not modelled: kicking_club 9, fg_xp 1, other 0.

| Season | Team-games | Fumbles | Lost | Scrimmage | Scrimmage lost | Pass 2 fumbles | Pass 2 lost |
|---|---|---|---|---|---|---|---|
| 2010 | 512 | 717 | 345 | 578 | 291 | 718 | 349 |
| 2011 | 512 | 641 | 302 | 538 | 267 | 636 | 303 |
| 2012 | 512 | 671 | 326 | 546 | 279 | 664 | 325 |
| 2013 | 512 | 645 | 309 | 523 | 265 | 638 | 310 |
| 2014w4 | 122 | 157 | 73 | 133 | 64 | 149 | 73 |

**Credit shares** (credit only; never player evidence):

Aborted-snap fumbler: quarterback 342, offensive line 72, other 35.

| Scrimmage kind | Lost forced | Forcer recovers | Forcer DL/LB/DB | Lost recoverer DL/LB/DB | Kept recoverer self/QB/OL/RB/WR/TE |
|---|---|---|---|---|---|
| run | 363/389 | 44/362 | 102/149/110 | 88/120/180 | 92/8/42/13/30/17 |
| reception | 282/306 | 46/282 | 23/96/163 | 39/83/177 | 69/7/28/13/21/7 |
| sack | 362/369 | 52/360 | 201/120/39 | 233/95/41 | 106/0/149/35/6/17 |
| aborted | 2/102 | 0/2 | 0/0/2 | 35/43/21 | 186/47/7/61/17/9 |

| Kick fumble | Forced | Kept, recovered by the fumbler | Lost, forcer recovers |
|---|---|---|---|
| muff | 9/281 | 134/166 | 0/4 |
| return | 190/222 | 34/100 | 5/88 |

**Second pass (nflscrapR)**

| Metric | nflverse | nflscrapR | Within 2 SE |
|---|---|---|---|
| fumbles per team-game (modelled scope) | 2831/2170 | 2805/2170 | yes |
| lost fumbles per team-game (modelled scope) | 1355/2170 | 1360/2170 | yes |
| offense-kept share of scrimmage fumbles | 1152/2318 | 1125/2294 | yes |
| sack share of lost scrimmage fumbles | 369/1166 | 366/1169 | yes |
| run fumbles lost per team-game | 389/2170 | 411/2170 | yes |
| reception fumbles lost per team-game | 306/2170 | 308/2170 | yes |
| sack fumbles lost per team-game | 369/2170 | 366/2170 | yes |
| aborted fumbles lost per team-game | 102/2170 | 84/2170 | yes |
| forced share of lost non-aborted scrimmage fumbles | 1007/1064 | 1004/1085 | yes |
| forcer also recovers | 142/1006 | 139/1006 | yes |
| muffs per punt | 264/10475 | 262/10426 | yes |
| punt muff receiving keep share | 185/264 | 184/262 | yes |
| receiving-club kick fumbles lost per team-game | 188/2170 | 190/2170 | yes |

Disagreements: none.
<!-- generated:end -->
