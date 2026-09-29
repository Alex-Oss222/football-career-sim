# 2012 NFL injury calibration (research input for proposed kernel 2014.4)

**Research date:** September 29, 2026. **Football information window:** 2012 regular season (weeks 1-17) and literature reporting 2012-or-earlier seasons. **Status: RESEARCH ARTIFACT.** No released kernel consumes it. It supplies sourced replacements for the unsourced constants in `runtime/injuries.py`, which is Tier 1 items 4-5 of `runtime/defect_register.md` and the "source class/severity/onset denominators" gate in `runtime/2014_engine_decisions.md` E2.

**Machine artifact:** [data/2012_nfl_injury_calibration.json](data/2012_nfl_injury_calibration.json). **Builder:** `scripts/research/build_2012_injury_calibration.py SOURCE_DIR` reproduces every Confirmed number offline from the three downloaded files.

**Information boundary.** Nothing from 2013 or later is an input. The one 2012-2014 study (L4) pools a post-divergence season, so it is cited only for method and ordering. None of its numbers is used.

**Labels.** *Confirmed* means computed directly from the 2012 files by the builder. *Pattern* means data combined with a stated assumption or a literature cross-check. *Unverified* means an assumption with no direct 2012 source.

## What the current model gets wrong

| Current constant | Problem | Replacement evidence |
|---|---|---|
| Flat 0.00072 x 20 exposures for every dressed player | Backups and specialists carry starter risk. About 0.7 onsets per team-game, against 4.1 report onsets and 1.1 in-game stoppages in 2012 | Per-snap hazard on actual participation, normalized to a per-team-game target |
| `POSITION_MULTIPLIER` keyed by group but read by raw position | OL, DL, DB and most LB fall through to 1.0 | Group relative risks from 2012 onset shares (below) |
| Uniform four-way class draw | Head/neck comes out near 25% | 2012 class mix: head/neck 11.1% of all report onsets and 22.9% of in-game stoppages that reached a report; about 18% of game onsets once between-game onsets are separated |
| Severity 57/22/16/5 with day bands 0-3/4-14/15-56/57-180 | No stored source. Multi-week plus long-term is 21%, two to three times the 2012 rate of 7-11%, and the bands do not match a weekly schedule | 2012 games-missed mix and game-cadence day bands |

## Sources

| Id | Source | Used for | Access |
|---|---|---|---|
| D1 | [nflverse injuries_2012.csv](https://github.com/nflverse/nflverse-data/releases/download/injuries/injuries_2012.csv): official weekly injury reports (5,533 rows) | Onsets, body part, status | Downloaded; sha256 in JSON |
| D2 | [nflverse play_by_play_2012.csv.gz](https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_2012.csv.gz): GSIS gamebook text | In-game "TEAM-##-Name was injured during the play" notes, play counts, player-id footprints | Downloaded |
| D3 | [nflverse roster_weekly_2012.csv](https://github.com/nflverse/nflverse-data/releases/download/weekly_rosters/roster_weekly_2012.csv) | Jersey to player to position map; club membership | Downloaded. Its ACT/RES status is back-filled (players show RES from Week 1; only 8 RES remain in Week 17), so it cannot date reserve placements and is not used for that |
| D4 | nflverse snap_counts_2012.csv | None: the file has a header and no rows (public snap counts start in 2013) | Checked |
| L1 | Feeley et al., "Epidemiology of NFL Training Camp Injuries from 1998 to 2007," *AJSM* 2008, [doi:10.1177/0363546508316021](https://doi.org/10.1177/0363546508316021) | Games 64.7 vs practices 12.7 injuries per 1,000 athlete-exposures; season-ending 5.4 vs 0.4 | Abstract via search index |
| L2 | Casson, Viano, Powell, Pellman, "Twelve Years of NFL Concussion Data," *Sports Health* 2010, [doi:10.1177/1941738110383963](https://doi.org/10.1177/1941738110383963) | 0.42 (1996-2001) and 0.38 (2002-2007) concussions per game | Abstract |
| L3 | Casson et al., "Concussions Involving 7 or More Days Out in the NFL," *Sports Health* 2011, [doi:10.1177/1941738110397876](https://doi.org/10.1177/1941738110397876) | 2002-07: 16.7% of concussions out 7+ days, 3.86% out 21+ days | Abstract |
| L4 | Lawrence, Hutchison, Comper, "Descriptive Epidemiology of Musculoskeletal Injuries and Concussions in the NFL, 2012-2014," *OJSM* 2015, [doi:10.1177/2325967115583653](https://doi.org/10.1177/2325967115583653) | Method only: official reports as surveillance; knee > ankle > hamstring > shoulder > head; WR/TE/DB highest per athlete at risk | Abstract. Pooled numbers not used |
| L5 | Elliott et al., "Hamstring Muscle Strains in Professional Football Players: A 10-Year Review," *AJSM* 2011, [doi:10.1177/0363546510394647](https://doi.org/10.1177/0363546510394647) | 1989-98: hamstring 13% of NFL injuries; regular-season practice 0.18 vs game 0.82 per 1,000 AE | Abstract |
| L6 | NFL/Quintiles health-and-safety data, [NFL.com, 2014](https://www.nfl.com/news/nfl-says-concussions-acl-injuries-decreased-this-season-0ap2000000320373) (2012 column only) | 2012 preseason plus regular season: 261 concussions; 63 ACL tears | Search summaries only; nfl.com blocked by proxy. Another summary gives 62 ACL. The 2012 regular-season-only figure of 173 concussions appears in one summary: **Unverified** |

The literature full texts (PubMed, PMC, Nature, arXiv and nfl.com) were blocked by the environment's egress proxy. Every literature value above comes from an abstract or search-index summary and is used only as a cross-check or bound, never as a sole parameter.

## Method

1. **Report onset (D1).** A report episode is a player and body part (side stripped, first element of compound entries) listed as primary on consecutive reports of his club. Illness, "Not Injury Related" and blank rows are excluded. An onset is an episode whose part was not listed, as primary or secondary, on the club's previous report. The onset is attributed to the one game between the two reports. Week-1 listings are camp carryovers and are excluded. Denominator: 480 consecutive report pairs (15 per club). A stricter rule, requiring absence from both prior reports, changes the rate by 3% (4.075 to 3.953).
2. **In-game stoppage (D2).** A gamebook note that a player "was injured during the play" marks an official injury stoppage. The injured player is the last "TEAM-##-Name" token before the note. Club and jersey map to a player and position through D3, with a surname check where a club-week lists a number twice. All 562 notes matched a player whose surname agrees with the note. Denominator: 512 team-games, 32,493 run/pass plays, 2,620 kickoffs and 2,469 punts. Exposure denominator: 41,758 plays that put 22 players at risk (run, pass, kicks, kneels, spikes and 1,478 snapped plays nullified by penalty; timeouts and pre-snap fouls excluded), or 1,794 player-plays per team-game.
3. **Games missed (D1+D2).** Only footprint players count here: those who recorded a play-by-play id in at least 75% (and at least 3) of their club's earlier games. The proxy is the number of later club games before the player's next footprint. Offensive linemen are excluded because they rarely get an id. A player not seen again is long-term when 9 or more club games remained, and censored otherwise.
4. **Unreported severe loss (D2+D3).** A footprint player may vanish from play-by-play while still on the club's roster, with 3 or more games left and no later report listing. This is an upper bound on severe injuries that skipped the Wednesday report, because it also catches benchings.

## Results (Confirmed unless noted)

### Onset rates

| Measure | Value |
|---|---|
| Report onsets, 2012 weeks 2-17 | 1,956 = **4.08 per team-game** |
| First listed status | Probable 1,063 (54%), Questionable 503, Doubtful 96, Out 294 |
| In-game injury stoppages | 562 = **1.10 per team-game** |
| Stoppages per 1,000 plays | run/pass 14.7; kickoff 11.8; punt 11.3 (per player on field: about 0.00067, 0.00054 and 0.00052) |
| Stoppages on the possession club vs the other club | 244 vs 318 |
| Footprint players who recorded a later play in the same game | 133 of 293 (45%, a lower bound on same-game return) |
| Unreported vanishes (upper bound) | 20 = 0.039 per team-game (6 with 9+ games left) |

### By position group

| Group | Report onsets / team-game | Report share | In-game stoppages / team-game | In-game share | RR report* | RR in-game* |
|---|---|---|---|---|---|---|
| QB | 0.108 | 2.7% | 0.037 | 3.4% | 0.59 | 0.74 |
| RB (incl. FB) | 0.394 | 9.7% | 0.088 | 8.0% | 1.70 | 1.41 |
| WR | 0.600 | 14.7% | 0.131 | 11.9% | 1.32 | 1.07 |
| TE | 0.254 | 6.2% | 0.039 | 3.6% | 1.06 | 0.60 |
| OL | 0.592 | 14.5% | 0.158 | 14.4% | 0.64 | 0.63 |
| DL | 0.579 | 14.2% | 0.148 | 13.5% | 0.84 | 0.80 |
| LB | 0.602 | 14.8% | 0.154 | 14.1% | 1.30 | 1.24 |
| DB | 0.881 | 21.6% | 0.338 | 30.8% | 0.99 | 1.41 |
| K/P/LS | 0.065 | 1.6% | 0.004 | 0.4% | n/a | n/a |

*Relative risk per on-field scrimmage slot uses an **Unverified** 2012 slot mix (QB 1, OL 5, RB 1.25, WR 2.45, TE 1.3; DL 3.7, LB 2.5, DB 4.8 of 22). 2012 has no public participation data (D4). RB, WR, LB and DB shares also include special-teams injuries.

### Body-part class mix (report onsets, n = 1,956)

| Class | Share | Main parts |
|---|---|---|
| Lower extremity | 61.7% | knee 334, ankle 244, hamstring 185, groin, foot, hip, calf, thigh |
| Upper extremity | 16.9% | shoulder 170, elbow, hand, wrist |
| Trunk/other | 10.3% | back 104, ribs, chest |
| Head/neck | 11.1% | concussion 102, head 55, neck 53 |

Hamstring is 9.5% of onsets (L5 gives 13% of all NFL injuries for 1989-98, including the preseason, where 53% of hamstring strains occur). That is consistent with regular-season-only data. Stoppages that reached the next report (n = 284) were 56.0% lower, 10.9% upper, 10.2% trunk/other and **22.9% head/neck**.

### Concussion cross-check (Pattern)

Report concussion onsets are 0.21 per team-game. L2 gives 0.19 per team-game for 2002-07, from team-physician surveillance. L6 gives 261 for the 2012 preseason and regular season combined; if the unverified regular-season figure of 173 holds, that is 0.34 per team-game. Reports therefore capture roughly 60-100% of concussions. Moving report concussions to the midpoint of the literature range (0.265) adds about 0.05 per team-game, taking head/neck onsets from 0.45 to about 0.50 per team-game.

### Severity (games missed; footprint report onsets n = 918, 63 censored)

| Band | All | Lower | Upper | Trunk/other | Head/neck | In-game stoppages (n = 262, 61 censored) |
|---|---|---|---|---|---|---|
| minor (0 games) | 77.5% | 76.0% | 83.8% | 83.7% | 68.9% | 75.2% |
| short (1-2) | 15.1% | 15.3% | 9.3% | 13.3% | 25.5% | 14.1% |
| multi_week (3-8) | 6.4% | 7.8% | 5.8% | 2.0% | 4.7% | 6.5% |
| long_term (9+) | 1.0% | 0.9% | 1.2% | 1.0% | 0.9% | 4.2% |

Head/neck has the largest short share. That agrees with L3's post-2002 conservative concussion management (16.7% of concussions out 7+ days, 3.9% out 21+). Censoring and the unreported vanishes both push the true long-term share above 1%.

## Recommended parameter set (for the 2014.4 candidate)

| Parameter | Value | Label | Evidence |
|---|---|---|---|
| Game onsets per team-game (the kernel normalizes on its own participation ledger) | **2.8** (band 2.4-3.3) | Pattern | 4.08 report onsets x 0.60-0.80 game-attributable share (L1, L5 game vs in-season practice exposure); floor 1.10 stoppages |
| Between-game onsets per club-week (optional; never removes anyone from a game) | 1.25 (0.8-1.7) | Pattern | Remainder of the report onsets |
| Mean hazard per player-snap | **0.00156** = 2.8 / 1,794 player-plays per team-game | Pattern | 1,794 = 11 x 41,758 exposure plays / 256 games, Confirmed from D2 (see Method 2) |
| Position RR per snap | QB 0.65, RB 1.50, WR 1.20, TE 0.80, OL 0.65, DL 0.80, LB 1.30, DB 1.20, K/P/LS 0.30 | Pattern | Rounded mean of the report and in-game RR above. Specialists: 0.2 in-game, about 1.0 on reports (includes practice kicking) |
| Class mix, game onsets | lower 0.57, upper 0.155, trunk/other 0.095, **head/neck 0.18** (0.14-0.21) | Pattern | Head/neck 0.50 per team-game (0.45 reported plus the concussion adjustment), assumed to be game injuries (**Unverified**), over 2.8 game onsets. The rest keeps the report ratio. Range: 80% game origin with no adjustment, up to full game origin at 0.34 concussions |
| Class mix, between-game onsets | lower 0.69, upper 0.19, trunk/other 0.12, head/neck 0 | Pattern | Report class totals minus game onsets; head/neck 0 follows from the same Unverified assumption |
| Head/neck share among in-game stoppages | about 0.23 | Confirmed (stoppages reaching the report, n = 284) | D1+D2 |
| Severity mix | minor 0.76, short 0.15, multi_week 0.07, long_term 0.02 | Pattern | D1+D2 footprint severity plus the censoring and vanish correction. Use the per-class columns above for class-conditional draws |
| Day bands | minor 0-6, short 7-20, multi_week 21-62, long_term 63-180 | Pattern | Weekly cadence: 0 / 1-2 / 3-8 / 9+ games missed. Uniform within a band is Unverified |
| Rest-of-game removals per team-game | **0.95** (band 0.6-1.1) | Pattern | Not measured. Stoppage-linked removals are at most about 0.60 (1.10 stoppages, at least 45% returned); removals without an injury timeout are unobserved. Time-loss game onsets (2.8 x 0.24 = 0.67) plus head/neck holds on minor injuries give about 0.9-1.0 |
| Removal probability by severity | minor 0.05, short 0.45, multi_week 1.0, long_term 1.0, any head/neck 1.0 | Pattern | Implied removals = 2.8 x [0.18 + 0.82 x (0.76 x 0.05 + 0.15 x 0.45 + 0.09)] = 0.95. Head/neck removal is the existing independent medical hold (canon), not a rate |

**Acceptance bands for a synthetic sample:** game onsets 2.4-3.3 per team-game; removals 0.6-1.1; head/neck 14-21% of game onsets and 0.40-0.58 per team-game; lower extremity 52-63% of game onsets; time-loss share (short or longer) 18-30%; long-term 1-4%; concussions 0.19-0.34 per team-game if the kernel labels concussions (the current kernel has only a head/neck class). Per-snap risk of RB, LB, DB and WR should exceed OL, QB and DL, with specialists lowest. These bands test aggregates. They never target any real player's injury.

## Limitations

- Official reports under-record minor knocks that do not affect practice and over-record Probable carryovers. A body part on a report is not a diagnosis.
- The report cannot tell a game injury from a practice injury. The game share (0.60-0.80) is an estimate from pre-2011-CBA exposure literature (L1 is training camp at a single club), so it is the least certain parameter.
- Players placed on reserve before the Wednesday report are invisible to it. The footprint check bounds these at about 0.04 per team-game among regular contributors, but it cannot see backups or linemen.
- The games-missed proxy needs a play-by-play id. A player who dresses and records nothing looks absent, which biases the proxy toward longer absences, and offensive linemen are excluded.
- The window excludes Week-1 listings and the Week-17 game. Postseason data were not used.
- A stoppage note needs an official injury timeout, so it undercounts in-game injuries. The same-game return rate (45%) is a lower bound.
- Group relative risks depend on an assumed 2012 slot mix. Recalibrate them from the kernel's own participation ledger rather than treating them as measured per-snap rates.
- The literature was reachable only as abstracts and search summaries, and the verification pass could not re-check it at all. The 2012 regular-season concussion split (173) and the ACL total (62 vs 63) are unresolved.
- The game-origin share of head/neck onsets is assumed, not measured. It moves the game head/neck share between 0.14 and 0.21.

## Verification pass (September 29, 2026)

A separate pass, run with fresh downloads and independent code.

**What was checked**
- **Source files.** D1-D4 were downloaded again. All sha256 hashes match the JSON, and D4 is still a header with no rows.
- **Reproduction.** The research-pass builder reproduced its own `data` block exactly from the fresh files.
- **Independent recomputation.** Separate code rebuilt the report onsets (1,956; 4.075 and 3.953 per team-game), first status, class and body-part counts, concussions (0.2125), footprint severity for report onsets (711/139/59/9, 63 censored, with the same by-class counts), unreported vanishes (20: 14 + 6) and play-type counts. All of these agree. Position groups agree within a few onsets when the report file's own position is used instead of the roster position (for example DL 284 vs 278, LB 282 vs 289). The builder keeps the roster position.
- **Roster status.** Weekly-roster RES counts fall from 208 in Week 1 to 8 in Week 17, which confirms the back-fill caveat.
- **Arithmetic.** The per-team-game rates, per-1,000-play rates, relative risks, slot sums (11 per side), concussion cross-check and implied-removal formula were recomputed by hand.
- **Information boundary.** The builder reads only 2012 regular-season rows; the 101-row 2012 postseason block in D1 is filtered out. No 2013 or later injury outcome is an input. L4 supplies no numbers. L6 is a 2014 publication, and only its 2012 column is cited.
- **JSON and markdown.** After the corrections below, every data value in this page matches the JSON `data` block, and every recommended value matches the JSON `recommended` block.

**What changed and why**
1. **In-game note attribution bug (fixed in the builder).** The note regex matched lazily from the first team-prefixed token in a play description. For a play such as "downed by IND-55-J.Hickman. CHI-33-C.Tillman was injured during the play", it credited the injury to the wrong club and player. 22 of 562 notes were misattributed. The builder now takes the last token before each note and checks the surname, and all 562 notes now agree with the matched player's surname. This changed the in-game position counts (DB 178 to 173, LB 82 to 79, WR 64 to 67, RB 42 to 45, QB 18 to 19, OL 80 to 81), possession/other (237/325 to 244/318), footprint same-game return (136/289 to 133/293, 47% to 45%), stoppages reaching the next report (277 to 284; head/neck 21.7% to 22.9%) and stoppage severity (n 261 to 262; long-term 3.8% to 4.2%). The stoppage total, rates per 1,000 plays and play-type split were unchanged.
2. **Player-snap denominator.** The research pass counted all 4,194 `no_play` rows as snaps. Only 1,478 are snapped plays nullified by a penalty; the rest are timeouts (about 1,800) and pre-snap fouls (about 920: false start, delay of game, neutral zone infraction, encroachment). Kneels and spikes were also left out. The corrected figure, now computed by the builder, is 1,794 player-plays per team-game, not 1,891, so the mean hazard moves from 0.00148 to 0.00156.
3. **Class mix applied to the wrong stream.** The research pass applied the all-report class mix (head/neck 0.135) to game onsets only. That gives 2.8 x 0.135 = 0.378 head/neck game onsets per team-game, fewer than the 0.452 the reports listed, even though the text said it raised head/neck for concussion under-listing. At the report concussion share of head/neck (47%), it would also give about 0.18 concussions per team-game, below the page's own 0.19-0.34 acceptance band. The pass also said the midpoint "adds about 0.1" concussions per team-game; the midpoint adds about 0.05. The fix is a separate game-onset mix (head/neck 0.18, range 0.14-0.21) and a between-game mix. It rests on an **Unverified** assumption that head/neck onsets are game injuries.
4. **Removal target.** "0.58 is a floor and 1.10 a ceiling" was not a valid bound. At least 45% of stoppage players returned, so about 0.60 is a ceiling on stoppage-linked removals, and removals without an injury timeout are unobserved. The target is now the value the recommended mix implies, 0.95, with a band of 0.6-1.1, and it is labeled as not measured.
5. **Position RR.** The corrected in-game shares move the WR blend from about 1.17 to 1.20, so WR is now 1.20. The other blends moved by less than 0.05 and are unchanged.
6. **Wording.** "About 9%" for the 2012 multi-week plus long-term share is now "7-11%" (7.4% report, 10.7% stoppage). The acceptance bands now match the corrected class mix.

**Not re-verified.** The literature (L1-L6) could not be checked again. The web-search budget for the session was exhausted, and Crossref, SAGE and Semantic Scholar are blocked by the proxy. Every literature value is still a single abstract or search summary, used only as a cross-check or bound, and is marked so in the JSON. The 173 and 62-vs-63 items remain unresolved.
