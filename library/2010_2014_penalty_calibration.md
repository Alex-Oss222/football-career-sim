# 2010-2014 penalty calibration

[Pre-build specification](2014_6_pre_build_specification.md) · [League base](2010_2014_calibration_base.md) · [Engine decisions](../runtime/2014_engine_decisions.md) · [Defect register](../runtime/defect_register.md)

**What this is.** The league record behind kernel 2014.6's per-play penalty records (batch B11, R11): the band centres the penalty rows are graded against, and the sourced rules and shares the engine reads when it replays a real drive's own penalties. The artifact is `library/data/2010_2014w4_penalties.json`, built by `scripts/research/build_2010_2014_penalties.py` with a `--check` mode, under the rules of the pre-build specification (section 4, Ball security and penalties; section 5, the B11 rows). Nothing in it is typed by hand.

**Data window.** NFL regular seasons 2010-2013 and 2014 Weeks 1-4 (games through September 29, 2014), read only through the batch B2 source gate. 2013 and 2014 Weeks 1-4 are an anonymous post-divergence league population: they enter pooled counts only. No club's, game's or player's own row is stored; identifiers are read only to count team-games and fouling clubs and to find a fouler's position group on that season's roster.

## What the engine models and what it draws from

Before kernel 2014.6 a penalty was a counter only: one draw per scrimmage play at an unsourced factor, every flag charged to the offense, one `randint(5, 10)` yardage per drive, while the replayed drive's own penalty yards stayed folded into its passing and rushing yards (defect register item 11). The penalties are still not drawn here. They come from the replayed real drives and kick records of the 2010-2014 league base (`library/data/2010_2014w4_nfl_field_position_model.json`, field `pen`): every drive carries its own clauses (the hosting row, the type, the fouling side, the accepted yards, accepted, declined or offsetting, the enforcement on a no-play row, after a counted snap or on the drive's kick row, the source's first-down-by-penalty flag and the type's nominal yards), and every kick record its kick row's clauses. Under the profile flag `penalty_records` the engine replays them (`runtime/penalties.py`, `runtime/chains.py` ledger-walk-v2). This record supplies only what those annotations do not:

- **The band centres.** The real league's rates in the scope the engine replays, so a 2014.6 cohort can be graded.
- **The automatic-first-down classes.** Whether an accepted defensive foul of each type is a first down by rule or only by its yards.
- **The half-distance rule's evidence.** Which records are half-distance enforcements, so the engine places each record only where its real yards are legal.
- **Fouler shares.** The position group of the fouler by type and side. Every fouler the engine names from these shares is a group draw (`fouler_basis` `group_draw`, `group_fallback` when the group is not on the field, `team` for the source's unnamed share, `unit_draw` on a kick play) and is never player evidence (`runtime/2014_engine_decisions.md`, E1).

## How each piece is counted

- **The modelled scope** is every clause on a drive's own rows except those after or on the terminal snap of a touchdown, turnover, safety or downs drive (enforced on the kickoff, the try or the next possession, which the kernel draws from its own transition pools) and those on the drive's punt or field-goal row (the punt row carries the punt record's own clauses; a field-goal row's are not modelled). Both are counted and listed below the centres, and the engine counts them per game (`penalty_post_terminal_excluded`, `penalty_kick_row_excluded`). The kick plays' own clauses (punts; kickoffs from the 35 from 2011 and free kicks; onside kicks and return touchdowns left out) are in the scope: the engine publishes them on the kick rows it draws. The classification is `runtime.penalties.classify` run on the same records, so the centre and the engine count the same kinds of rows, with one exception in the denominator (corrected by the review of October 16, 2026, which found this sentence overstated it): the 2010 kickoffs (from the 30) are outside the scope, but the centres still divide every season's records by all 2,170 team-games, 2010's 512 included, while the engine draws every kickoff from the 2011-and-later pool. The accepted kickoff clauses are 319 over the 1,658 team-games of 2011 to 2014 Week 4 (about 0.192 per team-game), so the accepted-penalties centre (5.8949) sits about 0.045 per team-game below the engine's own scope (about 5.940), the penalty-yards centre (49.65) about 0.4 below it, and the informational kick-play row's centre (0.6548) below its engine-scope value (about 0.700). On the standard 250-game sample that is about 0.12 of the accepted row's tolerance, and every graded row reads WITHIN. The artifact is unchanged; whether to rebuild the centres with the kickoff component taken over 2011 and later only is for Stone at the release check, with the U8 rows.
- **Accepted penalties and yards** are charged to the fouling club, accepted records only (the NFL convention); declined and offsetting records are counted apart.
- **First downs by penalty** are the rows the source flags `first_down_penalty`. On a scrimmage play the source flags both the play's own first down and the penalty's (482 of the 1,136 drive plays flagged `first_down_penalty` also carry the rushing or passing flag; nflscrapR 482 of 1,076; the first-down convention line below), so an automatic foul on a play that made its own first down is still a first down by penalty in the engine's walk; the play's third- or fourth-down conversion is its own gain, as the source's `third_down_converted` is.
- **The automatic-first-down class** of each defensive type comes from the accepted defensive clauses on single-clause no-play drive rows whose yards fall short of the line to gain: automatic when the two passes' pooled share carrying the flag is at least one half, yardage only below it, and replay (the record's own real flag) when no such clause exists or the two passes fall on opposite sides of one half (one type, illegal block above the waist). This majority rule was written after the design phase's table was seen (an earlier 0.95/0.05 cut left two types on the edge); it is disclosed in the decisions record.
- **Half distance.** An accepted record two or more yards below its type's nominal yards is a half-distance enforcement, legal only where half the distance to the goal it moves toward, floor or ceiling in whole yards, equals its yards. Of the 417 such no-play clauses (nflverse), 404 sit at half the distance at their own real spot, and the full nominal yards would have been legal at only 6 of them. A record one yard short keeps the full rule: the feed's whole-yard spots make half of those half distances and half full enforcements. A type with no nominal yards (defensive pass interference, intentional grounding) is a spot foul and needs only its new spot in the field; every other record moves the ball at most half the distance to the goal it moves toward.
- **Fouler groups** are the fouler's position group on that season's roster, single-clause scrimmage and no-play rows, by type and side (pass 1 only). `unknown` is the source's unnamed share (the feed names no player, or the roster holds none): a twelve-men or team delay foul, mostly; the engine charges such a foul to the club alone.
- **Drift.** Each rate carries its per-season counts and a homogeneity test. Equal weight per event is the adopted weighting (default 1B.1); a drift is reported, never fitted.

## Two passes

The primary pass reads nflverse through the committed loader and the committed annotation (`league_base_2010_2014.penalties_of`), so its clauses are exactly the tuples' `pen` records. The second pass reads nflscrapR's raw rows with separately written parsing of its own penalty columns (one accepted penalty per row). Both files derive from the NFL GSIS feed, so the second pass checks the parse, not an independent observation of the seasons. Every compared metric agrees within two standard errors (the table below); declined and offsetting clauses and the fouler group shares are single-pass, since nflscrapR flags accepted penalties only.

## Honest limits

- Individual and club penalty tendencies are **not studied** (no admissible persistence evidence was examined): the engine carries them as named slope-0 terms (`runtime.penalties.TERMS`), so no player's or club's history moves a penalty, and a real player's own 2013-2014 rows never set his value.
- The penalties are the replayed real drives' own. Accept or decline is the real record's (`decision_source` `replayed`), never a coaching choice, and no review credits it to a coach.
- Within a position group the fouler is drawn evenly from the players on the field. No sourced within-group share exists; it is a labelled convention.
- A replayed drive's records keep their real yards but not their real spots: the engine seats each where its yards are legal. A drive whose records admit no legal layout from its start is resampled or, as the last fallback, laid out without its records (their yards back in its scrimmage split); the engine counts every such drive (`penalty_layout_dropped`, `penalty_records_dropped`).
- 1.6% of the real drives do not satisfy the identity of their own net (scrimmage yards plus accepted penalty yards); they keep the remainder in their scrimmage split, as before kernel 2014.6.

## Figures

<!-- generated:begin -->
Generated by `scripts/research/build_2010_2014_penalties.py` from the artifact; do not edit.

| Centre | Count | Of | Value | Dispersion | SD | Season drift p |
|---|---|---|---|---|---|---|
| accepted penalties per team game | 12792 | 2170 | 5.8949 | 1.239 | 2.703 | 0.000 |
| penalty yards per team game | 107732 | 2170 | 49.6461 | 13.397 | 25.790 | 0.000 |
| penalty first downs per team game | 3715 | 2170 | 1.7120 | 1.206 | 1.437 | 0.000 |
| defense share of accepted drive penalties (informational) | 4946 | 11371 | 0.4350 | - | - | 0.000 |
| declined per team game (informational) | 1421 | 2170 | 0.6548 | - | - | 0.001 |
| offsetting per team game (informational) | 479 | 2170 | 0.2207 | - | - | 0.000 |
| kick play penalties per team game (informational) | 1421 | 2170 | 0.6548 | - | - | 0.000 |

Left out of the scope (per team-game): clauses after or on the terminal snap of a touchdown, turnover, safety or downs drive 614/2170 = 0.2829; clauses on a drive's own punt or field-goal row 1258/2170 = 0.5797. Kick-play accepted clauses by site: free_kick 4, kickoff 319, punt 1098.

| Season | Team-games | Accepted | Yards | First downs | Declined | Offsetting |
|---|---|---|---|---|---|---|
| 2010 | 512 | 2802 | 23210 | 737 | 307 | 108 |
| 2011 | 512 | 3125 | 26076 | 865 | 360 | 118 |
| 2012 | 512 | 3090 | 26008 | 916 | 346 | 113 |
| 2013 | 512 | 2985 | 25716 | 929 | 299 | 91 |
| 2014w4 | 122 | 790 | 6722 | 268 | 109 | 49 |

**Automatic first downs** (defensive no-play clauses short of the line to gain):

| Type | nflverse | nflscrapR | Class |
|---|---|---|---|
| Clipping | 0/0 | 1/1 | automatic |
| Defensive 12 On-field | 1/93 | 0/0 | yardage |
| Defensive Delay of Game | 0/4 | 0/5 | yardage |
| Defensive Holding | 421/421 | 420/421 | automatic |
| Defensive Offside | 0/544 | 0/535 | yardage |
| Defensive Pass Interference | 195/195 | 190/191 | automatic |
| Delay of Game | 0/3 | 0/7 | yardage |
| Disqualification | 0/0 | 1/2 | automatic |
| Encroachment | 0/206 | 0/214 | yardage |
| Face Mask | 4/4 | 0/0 | automatic |
| False Start | 0/0 | 0/1 | yardage |
| Horse Collar Tackle | 2/2 | 1/1 | automatic |
| Illegal Bat | 1/1 | 1/1 | automatic |
| Illegal Blindside Block | 0/0 | 0/1 | yardage |
| Illegal Block Above the Waist | 1/1 | 0/6 | replay (the passes fall on opposite sides of one half) |
| Illegal Contact | 211/211 | 218/218 | automatic |
| Illegal Formation | 0/1 | 0/1 | yardage |
| Illegal Kick | 0/0 | 0/1 | yardage |
| Illegal Substitution | 0/4 | 0/15 | yardage |
| Illegal Touch Kick | 0/0 | 0/1 | yardage |
| Illegal Use of Hands | 96/96 | 95/96 | automatic |
| Leaping | 1/1 | 1/1 | automatic |
| Leverage | 2/2 | 2/2 | automatic |
| NA | 0/0 | 24/120 | yardage |
| Neutral Zone Infraction | 0/341 | 0/337 | yardage |
| Offensive Holding | 0/0 | 0/3 | yardage |
| Personal Foul | 5/5 | 13/14 | automatic |
| Roughing the Kicker | 5/5 | 4/4 | automatic |
| Roughing the Passer | 24/24 | 25/25 | automatic |
| Running Into the Kicker | 0/18 | 0/18 | yardage |
| Taunting | 0/0 | 4/5 | automatic |
| Unnecessary Roughness | 14/14 | 15/18 | automatic |
| Unsportsmanlike Conduct | 1/1 | 3/6 | automatic |

**Half-distance enforcement** (single-clause accepted no-play clauses below nominal yards, at their own real spot): records / at half the distance (floor or ceiling) / full nominal legal there.

| Records | nflverse | nflscrapR |
|---|---|---|
| 2 or more below nominal (half-distance records) | 417/404/6 | 438/371/47 |
| one yard below nominal (full rule) | 175/86/89 | 176/87/88 |

**First-down convention**: scrimmage plays flagged first_down_penalty that also carry the rushing or passing first-down flag: nflverse 482 of 1136, nflscrapR 482 of 1076.

**Second pass (nflscrapR)**

| Metric | nflverse | nflscrapR | Within 2 SE |
|---|---|---|---|
| accepted penalties per team-game | 12792/2170 | 13054/2170 | yes |
| penalty first downs per team-game | 3715/2170 | 3747/2170 | yes |
| penalty yards per team-game (mean, team-game SD) | 107732/2170 | 110325/2170 | yes |
| defense share of accepted drive penalties | 4946/11371 | 5123/11693 | yes |
| kick-play penalties per team-game | 1421/2170 | 1361/2170 | yes |

Disagreements: none. Single pass: declined and offsetting clauses (nflscrapR flags accepted penalties only); the fouler group shares (pass 1 only; the design's pass 2 read multi-clause rows differently).
<!-- generated:end -->
