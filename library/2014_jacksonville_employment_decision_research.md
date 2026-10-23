# Library: how Jacksonville decides Stone's employment after 2014

**Hindsight boundary (read first):** The career diverged on January 15, 2013, when Alex Stone accepted Jacksonville's head-coach job. This file records the repository's own methods and rates, and Shad Khan's and David Caldwell's dated public record **before** that day. It uses nothing a real person did, said or was described as after January 15, 2013 as evidence of how he would decide: not the real Jaguars' later coaching decisions, not the real club's 2013 head-coach hire or his tenure, not Khan's later statements, not later profiles of either man. A fact dated before January 15, 2013 is taken from a later source only when that source states it as a dated fact (for example the year a group was created, in a current club biography), never when it is an opinion formed later. Real head-coach hires made on or after January 15, 2013 are not named here and their dates are not given, as in the [2014 hiring rules](2014_coaching_hiring_and_anti_tampering_rules.md); where a repository input depends on them, the dependency is flagged as a defect (section 1.8). Each pre-divergence decision below is a dated fact about one decision in its own circumstances. None is a rule about how Khan or Caldwell would weigh a 2014 season.

**Status:** Research only, October 23, 2026. Three research passes (the repository's methods and rates; Khan; Caldwell), each followed by a separate skeptical second pass that reopened every page it could reach rather than trusting the first pass's citations, and recomputed every repository number with its own code. This file changes no canon, roster, staff, contract, standings, calendar or state fact, and it adopts no employment method. How Jacksonville's 2014 decision is resolved was awaiting the user's decision when it was written. **Decided October 23, 2026:** the user chose "One draw for all 32 (Recommended)", the proposal of section 1.7 (Q1), with the readings settled in the choice: 2013 counts as a recent playoff season for column choice (section 1.4), 11 wins without the playoffs is treated like 9 or 10 wins (section 1.4), and the real post-divergence hires behind the rate table (section 1.8, item 5) are settled before the first draw. The adopted method is in [season end](../docs/season_end.md#how-the-club-decides), section C, and the user's words in the [rebuild plan's change log](../docs/rebuild_plan.md#change-log); the research below stays as written.

**Labels:**

- **Confirmed**: two independent reports agree (different publishers, or separate reports on different days), or a repository fact was re-read and, where it holds numbers, recomputed with separate code. Several Jaguars.com pages count as one source; so do two club sites repeating one release.
- **Confirmed (excerpt)**: as Confirmed, but the second report was seen only in search-result text.
- **Single source**: one publisher only; the page was reopened and its wording matches. The words are on record; nothing independent confirms them. "(club site)" marks the team's own site.
- **Unverified**: seen only in search-result text ("snippet-only"), not found, conflicting, or an inference.
- **Corrected**: a first pass, a source or an existing record was wrong; what changed and why is stated in the row and in section 5.2.
- **Removed**: breaks the January 15, 2013 boundary, or is an opinion formed later (section 5.3).
- **Dated opinion**: a writer's or colleague's characterization dated before the boundary. It is recorded as what was said, not as a fact about how the person decides.

**Access limits:** Pages reopened in the second passes: jaguars.com, www.nfl.com, nbcsports.com and profootballtalk.nbcsports.com (ProFootballTalk), atlantafalcons.com, espn.com (some pages, in the repository pass only), github.com and raw.githubusercontent.com (nflverse data), and en.wikipedia.org (context only, never evidence). Refused by the network proxy at least once: Forbes, Dawn, Jax Daily Record, Florida Trend, CBS News and CBS Sports, SI, the Washington Times, Fox News, Sports Business Daily, Grantland, WJXT (news4jax), the Florida Times-Union, ClickOrlando, heraldnet, WFAE, NBC Sports Boston, Bangor Daily News, FootballScoop, the illinois.edu sites, the Eagles media guide and the Wayback Machine; ESPN pages were refused in the Khan and Caldwell passes. **No block was routed around**: no mirror, archive or alternate host was tried. NFL.com wire pages show no visible date; their dates come from page metadata (`datePublished`), day-of-week references in the story, or dated companion pages, as each row states. Jaguars.com and Falcons.com migrated timestamps appear to run about eight hours early (an inference: the Mularkey release shows 3:04 AM while its text says 11:01 a.m.); no date in this file depends on a timestamp.

## 1. The repository's methods and rates

Read at merged `main` commit `f2989ce54f5b1c17abe134fa7f747af9092bafe6` (October 23, 2026), in a fresh detached worktree.

### 1.1 Who decides, and Stone's standing position

| # | Finding | Label and source |
|---|---|---|
| A1 | Hiring, retaining, suspending or firing the head coach is decided by Khan and Caldwell. Stone: "The user may negotiate, object, or resign, but cannot decide the employer's action." The row's `consultation` and `limits` fields are `[UNSET]`. | **Confirmed** ([job record](../state/current_job.json) `appointments[0].authority.domains`, row 1; [Document 3](../foundation/03_Head_Coach_Organization_and_Authority_Canon.md) authority row 1). **Corrected** path: every job field sits under `appointments[0]` |
| A2 | `employment_decided_by` is `["khan","caldwell"]`; `direct_supervisor`, `evaluator`, `cadence` and `escalation` are null. Document 3 §3.2: "Do not create a single job-security, prestige, reputation, owner-confidence, or locker-room score." | **Confirmed** (job record `appointments[0].reporting`; Document 3 §3.2) |
| A3 | Another club's request to contact or interview Stone is Khan's alone (row 1a, the user's decision of October 20, 2026). Standing instruction `stone-not-open-to-job-offers`: user date 2026-10-20, in-world date 2014-10-05. | **Confirmed** (job record rows 1a and `standing_instructions`) |
| A4 | The employment method is "frozen before Jacksonville's final game and before any My Season Response is read". Stone may rebut an error or give a substantive new plan; "rhetorical polish, word count and actor name cannot change the conclusion". | **Confirmed** ([season end](../docs/season_end.md) §C items 2 and 6) |
| A5 | "Do not invent arbitrary 'owner satisfaction' scores, secret fixed wins or guaranteed retention." An adjudication unable to distinguish possible outcomes must say its method is unresolved. | **Confirmed** (season end §C **item 2**; **Corrected** from a first-pass citation of "§C.2") |
| A6 | Document 1 §9.1: criteria are "fixed from the real, established evidence before the protagonist's specific case is evaluated". | **Confirmed** ([Document 1](../foundation/01_Project_Instructions.md) §9.1) |

### 1.2 The January 15, 2014 review (closed)

Source for every row: [owner and GM review](../career/2013/season_review/owner_and_gm_review.md).

| # | Finding | Label |
|---|---|---|
| B1 | Entry 1 (criteria freeze) was recorded September 28, 2026 "before the meeting was written"; freeze state CLOSED; event-record sequence 74, through 2014-02-02. | **Confirmed** |
| B2 | The contract at the time: four years, fully guaranteed, with no option, extension, buyout or termination terms. "Compensation is undetermined in the record." That was true when the review was written; the salary in 1.5 is a later reconstruction. | **Confirmed** |
| B3 | The review froze five hire criteria: a working relationship with a newly hired general manager; whole-program leadership for a 2-14 roster; a quarterback evaluation and development plan; a staff and operating structure from a near-clean reset; roster-development judgment under a high draft position. | **Corrected** on the source: [pre-hire market](2013_coaching_market_pre_hire.md) §3.4 lists **six** items; item 6, "No automatic bonus for prior head-coaching experience", was not carried into Entry 1 |
| B4 | Stone's own first-year standard ends "not a promised playoff appearance". | **Confirmed** |
| B5 | Record reviewed: 10-6, 356-346; three losses by 28 or more (11-41, 6-38, 16-45); Wild Card 38-14 at Kansas City; Divisional 13-20 at Tennessee; Cousins 3,981 passing yards, 23 touchdowns, 18 interceptions, 38 sacks taken. | **Confirmed** by separate sums over the 16 regular-season receipts in `career/2013/stats/game_receipts/` and the receipts in `career/2013/stats/postseason_receipts/` |
| B6 | Unknown private weighting: Khan's 2014 expectations and any appetite for an extension are not established. | **Confirmed** |
| B7 | Entry 3 retained Stone. The concerns raised are "measures for 2014, not grounds to end a fully guaranteed contract after one year". Its label-swap line: "Any club with this record, this evidence and a four-year fully guaranteed contract in its first year retains its head coach." | **Confirmed** |
| B8 | Entry 4: after the carousel, the decision was "re-checked, not re-made". | **Confirmed** |
| B9 | Follow-ups: Caldwell's first 2014 measures are the scoring margin, and the quarterback's ball security and protection. Khan asked for the London week (Dallas, November 9, 2014, Wembley) to be prepared on the 2013 Wembley plan. | **Confirmed** |

### 1.3 The January 2014 coaching carousel (closed)

Sources: [carousel method](../data/2014/Early_Offseason/staff_changes/carousel_method.json), [results](../data/2014/Early_Offseason/staff_changes/carousel_results.json) (ledger Entry 75), [deferred results](../data/2014/Early_Offseason/staff_changes/carousel_deferred_results.json) (Entry 83) and [`scripts/coaching_carousel.py`](../scripts/coaching_carousel.py).

| # | Finding | Label |
|---|---|---|
| K1 | Each club's head coach changes with the probability of his base-rate group: branch 2013 regular-season wins (ties half) and his tenure with the club, or the playoff group by tenure if the club reached the branch postseason. A coach past his first season whose club missed the branch postseason is split by whether the club reached the real 2011 or 2012 playoffs. One draw per club, clubs in alphabetical order; a vacancy opens the day after the club's last game. | **Confirmed** |
| K2 | Stage 1's scope was every club except Jacksonville, "whose head coach was retained by the January 15 review". Entry 75 drew 29 clubs. The two branch Super Bowl clubs, Buffalo and Minnesota, played February 2, 2014; their draws were deferred (`draw: null`) and made in Entry 83. | **Corrected**: a first pass said stage 1 drew every club but Jacksonville; it drew 29, and Buffalo's and Minnesota's draws come from Entry 83 |
| K3 | Tenure is read from the base-rate file's `tenure_2013`, with Sean Payton overridden to a seventh season; inputs digest `564af326…`. | **Confirmed** |
| K4 | Jacksonville's group was `playoffs|1st season` (0 changes in 20 club-seasons; smoothed rate 0.0416). The code sets Jacksonville's probability to None explicitly (`... if team != JAX else None`); the rate exists in the table. The code also overwrites the coach name in Jacksonville's base-rate row with "Alex Stone" (1.8, item 5). | **Confirmed** (dry run), with that clarification |
| K5 | Expected changes among the 29 drawn clubs: 4.6044. Changes in Entry 75: Atlanta (7-8 wins, 4th+ season, recent playoffs; rate 0.1101, draw 0.0024; hired Jacksonville's Alan Lowry on January 12, 2014), Cincinnati (5-6, 4th+, recent; 0.4727, 0.2981), Denver (7-8, 2nd-3rd, recent; 0.1548, 0.1027), Indianapolis (7-8, 2nd-3rd, recent; 0.1548, 0.0949) and San Francisco (0-4, 2nd-3rd, recent; 0.6778, 0.0235). Entry 83: Buffalo kept (playoffs, 1st season; 0.0416, draw 0.6475); Minnesota changed (playoffs, 2nd-3rd; 0.0254, draw 0.0048). Six of the 31 drawn clubs changed. | **Confirmed** against both results files |
| K6 | Hire timing is drawn from the January 2013 cycle's eight hires (3, 6, 7, 9, 14, 15, 15 and 16 days after the vacancy opened); a new head coach opens the offensive coordinator job with probability 1.0 and the defensive coordinator job with 0.875, from the same cycle. | **Confirmed** as what the method states; flagged as an input that crosses the boundary (1.8, item 8) |

### 1.4 The base-rate table

Source: [`2012_hc_change_base_rates.json`](data/2012_hc_change_base_rates.json), built by `scripts/research/build_hc_change_base_rates.py` from nflverse `games.csv` (D1).

| # | Finding | Label |
|---|---|---|
| R1 | "changed = a different head coach opened the club's next regular season (a firing during or after the season, a resignation or a retirement alike)". Club-seasons 2002-2012, keyed to the coach who opened the season; outcomes read from the 2003-2013 openers; New Orleans 2012 left out. Smoothing: rate = (changed + 5 x overall) / (seasons + 5); a split group is smoothed toward its parent group. Ties count half. Tenure groups: 1st season, 2nd-3rd, 4th+. "Recent" means a playoff game in either of the two seasons before (s-1 or s-2). Playoff seasons are pooled by tenure, with no recent split. | **Confirmed** (the file, and the builder's `wins_bucket`, `tenure_bucket` and `recent`) |
| R2 | 351 club-seasons, 73 changes, overall rate 0.208 (about 6.7 a year), 33 groups. | **Confirmed**: `games.csv` re-downloaded on October 23, 2026 (sha256 `618b9326…`; it matches neither the pinned `c14c7de…` nor the first pass's `18208704…`, because the upstream file keeps changing); separate grouping code reproduced all 33 groups exactly, in counts and in smoothed rates |
| R3 | Era corroboration. Len Pasquarelli, ESPN, about December 2001 (exact date not in the page text): "There have been, over the past 20 seasons, an average of nearly seven coaching changes per year." Pasquarelli, 2003: "In the 11 seasons of free agency, there has been an average of seven head coach changes per year." | **Confirmed** (E3, E4; both pages opened, both before the boundary, both agree with 6.7 a year) |
| R4 | The [coaching career path](nfl_coaching_career_path.md) §7 restatement (0.63, 0.41, 0.13, 0.12, 0.03; 0.19 against 0.54) equals the groups 0.6267, 0.4075, 0.1262, 0.12, 0.0254, 0.1852 and 0.5399. | **Confirmed** |
| R5 | FootballScoop's "68 changes 2004-2013" and its "38 months" average tenure, cited in career path §7. | **Removed**: search text shows the post at a 2014-dated address (the 2025 address looks like a re-hosting) counting "the 10 seasons from 2004 through 2013", so it includes changes after January 15, 2013. The page itself was refused. The career path file still cites it (section 5.5) |

**Rates for a coach in his second or third season** (Stone's group in 2014). Counts are real changed / club-seasons, 2002-2012.

| 2014 finish | Recent playoffs (counts branch 2013) | No recent playoffs (real 2011-2012 only) | Pooled parent |
|---|---|---|---|
| Reached the playoffs, any record | 0.0254 (0 of 36) | not split | 0.0254 |
| 11 or more wins, missed the playoffs | no group | no group | no group |
| 9-10 wins | 0.1231 (1 of 8) | 0.0667 (0 of 4) | 0.12 (1 of 12) |
| 7-8 wins | 0.1548 (2 of 12) | 0.0815 (1 of 15) | 0.1262 (3 of 27) |
| 5-6 wins | 0.1852 (0 of 6) | 0.5399 (12 of 21) | 0.4075 (12 of 27) |
| 0-4 wins | 0.6778 (5 of 7) | 0.7137 (9 of 12) | 0.6267 (14 of 19) |

- Every value: **Confirmed** by recomputation.
- **Which column applies to Stone is unstated (modelling choice).** The builder's definition (s-1 or s-2) counts the branch 2013 playoffs, which puts Stone in the first column. The January 2014 method's text names only the real 2011 or 2012 playoffs, which would put him in the second. Neither 2014 rule is written.
- **The 11-wins row. Corrected.** A first pass said no 11+ non-playoff group existed. One such club-season exists in 2002-2012 (New England 2008, 11-5, its coach's 9th season), so `11+|4th+` (0 of 1, 0.1733) and `11+|4th+|recent playoffs` (0.1444) exist. No 1st-season or 2nd-3rd group exists, so for `11+|2nd-3rd|recent playoffs` the lookup `rates["cells"][c["cell"]]` in `scripts/coaching_carousel.py` would raise a KeyError. A fallback rule would be a modelling choice.
- Stone stood at 3 wins on October 23, 2026, so every row remains reachable.

### 1.5 Stone's contract

| # | Finding | Label and source |
|---|---|---|
| S1 | Signed January 15, 2013: the 2013-2016 seasons, all four guaranteed, and the authority terms. Document 3 §3.1: "a negotiated partial-guarantee/performance-vesting alternative ... proposed by Stone and declined by Jacksonville". | **Confirmed** ([coach record](../data/people/coaches/alex_stone.json); Document 3 §3.1) |
| S2 | Reconstructed terms: end date the later of January 31, 2017 or the day after the last 2016 game (contracts library row C73); salary $2,800,000 a season (rows C35, C52); dollar-for-dollar offset (C54, C55); dismissed without cause, the remainder less the offset, with no buyout (C53); dismissed for cause, nothing further (C56); no signing bonus and no options. | **Confirmed** as recorded reconstructions. **Corrected** date: the coach record dates the user's delegation ("you can decide the rest") to `user_date` 2026-10-18 and the entry to `recorded` 2026-10-19 |
| S3 | Rivera's four years and $11.2 million (row C35), the comparable behind the salary. | **Unverified** (one origin, ESPN, relayed by AP reprints that were refused; [contracts library](nfl_head_coach_contracts_2005_2014.md) also labels it Unverified) |
| S4 | By the reconstruction, $5,600,000 for 2015-2016 remains after 2014. Whether any 2014 salary would be unpaid at a dismissal is not recorded. No grounds for cause are defined. | **Confirmed** (season end §D) |
| S5 | Assistants: Crennel 2015 $1,700,000 and Tice 2015 $1,200,000, both guaranteed subject to offset; Westhoff 2015 $750,000, non-guaranteed. Nine contracts run through 2014 (Bush, Yarno, Bates, Drake, Spencer, Oden, Pleasant, Zernhelt, Skalaski); their lapse date is not fixed. | **Confirmed** ([coaching staff](../career/2014/Team_Operations/Staff/coaching_staff.md); [milestones](../docs/season_cycle_milestones.md) §4 item 4) |
| S6 | Cost of a change: the remainder less the offset, plus the assistants not kept. | **Confirmed** as a Derived row (contracts library C61) |
| S7 | Real practice before the boundary: clubs dismissed head coaches with years left and paid the remainder less any offset, for example San Diego (February 12, 2007, after 14-2, one year left), Baltimore (December 31, 2007, three years left), Denver (December 30, 2008, three years left) and Seattle (January 8, 2010, after one season, three years left). | Repository record, with that file's labels (contracts library C53); not re-checked in this pass |

### 1.6 The 2014 record on file (October 23, 2026)

| # | Finding | Label and source |
|---|---|---|
| G1 | 3-2, 115-109 (+6), first in the AFC South on division record over Houston, two straight losses: 23-20 at Philadelphia in overtime, 24-7 at Washington, 38-34 against Indianapolis, 20-21 at San Diego, 10-27 against Pittsburgh. Week 17 is at Houston on December 28, 2014. | **Confirmed** (receipts in `data/2014/Regular_Season/Statistics/records/game_receipts/`; [standings](../career/2014/Regular_Season/standings.md); [calendar](../career/2014/Calendar.md)) |
| G2 | Cousins: 7 interceptions and 8 sacks taken in 5 games. | **Confirmed** (sum over the receipts) |
| G3 | `khan-london-week` is OPEN and is an organizational request. | **Confirmed** (season end §E item 2) |
| G4 | [Performance reviews](../career/Stone/Performance_Reviews.md), October 5, 2014, is headed "Ownership perspective" and written in an unsigned "we" ("We hired Alex …"); it never names Khan as its author. Its two sentences, in separate paragraphs: "Alex Stone is our head coach, and we support the direction of the club." and "... we do not treat one difficult Sunday as a referendum on the coach." Last rewritten in commit bb8f51c on October 19, 2026 (an earlier commit that day, adc6c7f, moved the file). It is not a decision and not a delivered concern. | **Corrected**: a first pass called it "in Khan's voice" and joined the two paragraphs into one quote. Not a decision: **Confirmed** (season end §B and §E item 2) |
| G5 | The page's football claims. Real 2012: 2-14, 255-444 (**Confirmed**, `games.csv`). Sacks allowed: real 2012 50, branch 2013 38 (**Confirmed**). Rushing yards: real 2012 1,369 by play-by-play sum (not an official total), branch 2013 2,043 (**Unverified** against the official 2012 total). Opponents' third-down conversions: real 2012 89 of 215 (41.4 percent), branch 2013 67 of 199 (33.7 percent) (**Confirmed**). | Own counts from nflverse 2012 play-by-play (D2) and the branch receipts |

### 1.7 The open question

| # | Finding | Label |
|---|---|---|
| Q1 | Season end §C, "How the club decides (awaiting the user's decision)": "Neither option below is adopted; the first is the proposal." Proposal: one base-rate draw for all 32 clubs keyed on wins, tenure and recent playoffs. Alternative: a review with frozen criteria for every club. "Two methods in one league fail the label-swap test." | **Confirmed** |
| Q2 | Under the proposal, My Season Response "can correct a factual input before the draw"; under the alternative it is read against the frozen criteria. | **Confirmed** (season end §C table) |
| Q3 | Milestones §4 item 3 restates the open question. Item 5: no `library/data/2014_postseason_slots.json` and no January 2015 carousel method exist (only the 2013 slots file). | **Confirmed** |
| Q4 | No frozen retention criteria exist for the other 31 clubs. A repository search found criteria freezes only in Jacksonville and protagonist files. | **Confirmed** |
| Q5 | The review method produces no rate. | **Confirmed** |

### 1.8 Problems found in the repository's inputs

1. **Thin groups change direction.** Within 2nd-3rd, recent playoffs raise the rate at 7-8 wins (0.1548 against 0.0815) and 9-10 (0.1231 against 0.0667) and lower it at 5-6 (0.1852 against 0.5399) and 0-4 (0.6778 against 0.7137). Within 4th+, they lower it at 0-4, 5-6 and 7-8 and raise it at 9-10 (0.2959 against 0.2211, on one no-recent season). The method's sentence "in the 2002-2012 data recent playoffs lowered the change rate" holds only for some groups. **Confirmed.**
2. **The draw ignores the contract.** `cell()` takes no contract input. **Confirmed.**
3. **No mid-season timing.** [Event inserts](../docs/event_inserts.md) §D says "a dismissal can happen on any date"; the draw happens once, at season end. **Confirmed.** No era count of mid-season firings was found (career path §7, Unverified).
4. **Some outcomes are read past the boundary.** The data counts 31 club-seasons for 2012 (New Orleans excluded), with 8 changes and **23** kept (**Corrected** from 24). Kept outcomes are read from the September 2013 openers, after the boundary. Dismissal dates of the 8 changes: Andy Reid and Lovie Smith on December 31, 2012 and Mike Mularkey on January 10, 2013 are **Confirmed** (contracts library rows D11 to D13; J25; P6). Pat Shurmur, Romeo Crennel, Chan Gailey, Ken Whisenhunt and Norv Turner on December 31, 2012 rest on search-result text from three outlets (S5, S6, S7) and an undated NFL.com gallery (S8): **Unverified** (snippet-only, consistent). [Pre-hire market](2013_coaching_market_pre_hire.md) §2.1 does not give these dates.
5. **Real 2013 hires used as identities.** `tenure_2013` names each club's real 2013 opening-day coach, including hires made on or after January 15, 2013 (names and dates withheld here). Jacksonville's row names the real club's 2013 hire; the carousel code overwrites the name with "Alex Stone". Every club's opening coach and tenure count is read from September 2013 games. The [hiring search](../career/2013/offseason/hiring_search.md) says "The ledger records no later result" for Arizona, Philadelphia and Chicago, and records San Diego as "outside Stone's pursued search", yet the January 2014 carousel results name real post-boundary hires as those clubs' coaches. **Confirmed** as a defect.
6. **The FootballScoop count.** **Removed** (1.4, R5).
7. **The October 5, 2014 page** could be read as private owner weighting. **Confirmed** as unsettled.
8. **Hire timing and coordinator openings come from the post-boundary January 2013 cycle.** The hire-day list and the 1.0 and 0.875 opening rates are taken from that cycle's archive; the rules file (§7.3, §7.4) labels them "archive" and "archive only", and five of the eight hires behind the list fell on or after January 15, 2013 (day-level dates Unverified there). **Confirmed** as a defect.
9. **An overstated pre-hire line.** Pre-hire market line 116 says Caldwell "publicly discussed Greg Roman, Brian Schottenheimer, Vic Fangio, and Jay Gruden" on January 10, 2013. J27 says those names "ha[ve] been mentioned as a possibility"; Caldwell commented only on Roman, as a friend, and otherwise declined specifics. **Confirmed** discrepancy; not corrected in this commit (section 5.5).

## 2. Shad Khan before January 15, 2013

### 2.1 Background and business

| # | Finding | Label and sources |
|---|---|---|
| KH1 | Born in Pakistan; J1 says "born in Lahore-Punjab". | Pakistan: **Confirmed** (J1; N1, "Pakistani-born"). Lahore: **Single source (club site)**, consistent with Wikipedia (W1) |
| KH2 | Moved to the United States at 16 to attend the University of Illinois (N1: "16 when he moved from Pakistan"); graduated in 1971 from its School of Mechanical and Industrial Engineering (J1). | **Confirmed** (J1, N1) |
| KH3 | Born July 18, 1950; arrived in 1967. | **Unverified** (W1, citing the 60 Minutes profile of October 28, 2012, not opened). The year fits AP's "61-year-old" in December 2011 (N1); PFT's "55-year-old" in February 2010 (P1) conflicts and is treated as the outlier |
| KH4 | Flex-N-Gate: "employs more than 12,450 people worldwide", "more than $3 billion in revenue last year" (J1, December 2011); "nearly 13,000 people at 48 manufacturing and nine product development and engineering facilities" in Canada, the United States, Mexico, Argentina and Spain, headquartered in Champaign-Urbana (J14, October 2012). | **Single source (club site)**. **Corrected** detail: J14 names those countries and gives facility counts; it does not say "North America, Argentina and Spain" |
| KH5 | "Upon graduating from college in 1971, Khan went to work at Flex-N-Gate as an engineering manager"; he left in 1978 to found Bumper Works and bought his former employer in 1980 (N1). J2: he "began working for Flex-N-Gate in 1970", "left the company in 1978, then purchased it in 1980". | **Confirmed** for 1978 and 1980 (**Corrected**: upgraded from Wikipedia only). Start year 1970 against 1971: **Unverified**, unresolved |
| KH6 | Net worth of $2.5 billion in 2012 (the March Forbes billionaires list, No. 164 in the United States, S1; the 2012 Forbes 400, No. 179, S2); Forbes's "$3.4 billion business" (S3). | **Unverified** (snippet-only; the two $2.5 billion snippets refer to two different Forbes lists) |
| KH7 | First job washing dishes for $1.20 an hour. | **Unverified** (W1, attributed to 60 Minutes; not in J1 or N1) |
| KH8 | Earlier Rams bid: a signed agreement to buy the 60 percent owned by Chip Rosenbloom and Lucia Rodriguez, closing expected in March (P1, February 11, 2010). Stan Kroenke used his matching right "late on a Monday", the deadline day, which fits April 12, 2010 (N2); Khan said he respected Kroenke's "right to try to purchase the Rosenbloom family's interest" and had told the majority owners he would "conclude the purchase if the opportunity presents itself" (N2). Owners approved Kroenke unanimously at a Wednesday meeting in Atlanta, which fits August 25, 2010 (N3). | **Confirmed** (P1; J1, "last year entered into an agreement"). **Corrected**: J1's "last year" means 2010, not "earlier in 2011" |

### 2.2 Buying the Jaguars

| # | Finding | Label and sources |
|---|---|---|
| KH9 | Wayne Weaver "signed the agreement with Khan on Tuesday morning", November 29, 2011, after "an endorsement from NFL Commissioner Roger Goodell"; terms not disclosed. | **Confirmed** (N4; J3) |
| KH10 | The same day Weaver, not Khan, fired Jack Del Rio, named Mel Tucker interim coach and offered general manager Gene Smith a three-year extension ("Weaver on Tuesday announced he had offered General Manager Gene Smith a three-year extension", J4). | **Confirmed** (N4; J3; J4) |
| KH11 | Khan was expected to keep current management. | **Single source** (N4; neither J3 nor J4 says it) |
| KH12 | The league finance committee "voted unanimously Tuesday to recommend Shahid Khan's bid" (N5); N4 places that meeting on December 6, 2011, a Tuesday. | **Single source (AP)**. **Corrected**: now dated |
| KH13 | Owners approved the sale unanimously on December 14, 2011 ("unanimously, 32-0", J2). | **Confirmed** (P2; J2; N1). **Corrected**: J2 is dated December 14, not December 15 |
| KH14 | At approval: "I'm totally committed to Jacksonville" (no plan to move); "This is a partnership, really, with the fans"; "Doing whatever it takes to put a winner on the field"; "Here I am, reporting for duty and ready to serve the fans. Let the fun begin"; "Accountability to the fans starts right now"; "Whatever it takes to get the fans engaged". | First three: **Confirmed** (P2 or N1 with J2). "Reporting for duty": **Single source** (N1). "Accountability to the fans": **Single source (club site)** (J2). "Fans engaged": **Single source** (P2) |
| KH15 | Ownership transferred on Wednesday, January 4, 2012 ("took place Wednesday afternoon", N7; Khan "officially takes over Wednesday", N6). Khan, partial quote: he "will do everything possible to build a consistent winner on the field and a model franchise off the field" (N7). | Date: **Confirmed** (two AP stories on different days; W1 agrees). Quote: **Single source** |
| KH16 | Price: AP used "an estimated $760 million" at approval (N1); at closing "$770 million. The deal included a $660 million sale price and $110 million in debt" (N7), repeated in N9. | **Corrected**: use $770 million as the closing figure; $760 million was a pre-closing estimate |

### 2.3 Decisions in 2012

| # | Finding | Label and sources |
|---|---|---|
| KH17 | Kept Gene Smith after the 2011 season. On *Jaguars This Week*: "I have tremendous respect for him and he's absolutely a huge asset to this organization." To Gene Frenette of the Florida Times-Union the next day: "The uninformed fan is the one who comes up with, 'Fire Gene Smith'." | **Single source (club site)** (J5, January 6, 2012). The exact days are not given |
| KH18 | December 2011, on Smith: lunch on Wednesday; "What I know about him is from his reputation." "Obviously Wayne speaks highly of him. That's the most important thing." | **Single source (club site)** (J1). **Corrected**: "the most important thing" refers to Weaver's regard for Smith, not to reputation in general |
| KH19 | Who ran the 2012 coaching search: "General manager Gene Smith is leading the coaching search" (N6, January 2, 2012), with Khan insisting money would not be a factor (paraphrase); "Owner Shahid Khan and general manager Gene Smith are handling the process" (N8, January 4, 2012); "conducted mostly by Smith" (J7). The club asked permission to interview Mularkey (P3, January 2, 2012, citing Jason La Canfora). | Smith led, with Khan involved: **Confirmed** (N6, N8, J7). Permission request: **Single source** (P3) |
| KH20 | January 4, 2012: "We know who our top three choices are. All three are excellent." "It's been proven to me, people want this job." | **Single source** (N8) |
| KH21 | Mularkey hired Tuesday night, January 10, 2012; introduced Wednesday, January 11. | **Confirmed** (J6; N9; J7; N10). A Jaguars.com article of January 10, 2013 saying Khan hired Mularkey "on January 11, 2012, six days after taking over ownership" was found by one pass and not located by the other: **Unverified**; the contemporaneous pages settle the two dates |
| KH22 | Mularkey's contract: three years, "tied to the hip with Gene", Smith being "also on a three-year deal". Financial terms not found. | Term: **Single source (club site)** (J8). Money: **Unverified** (not found) |
| KH23 | Khan sat in on the interview with Mularkey and Smith; per J7 "the two" left the room for what Mularkey called "a good while", and the job was offered soon after they returned; the offer came "about four and a half hours into the interview" (J8). Khan: "It was an easy call after I spent several hours with him." "You want to trust, but verify." "The issue was not splash. The issue was smart." "It's something sustainable and it's about building a winner for the long term." The process was "thorough, professional, confidential", with "no drama". | Quotes: **Single source (club site)** (J7). "Smart" over splash, and the line about big-name coaches "after the splash": **Confirmed** (N10). **Corrected**: the four-and-a-half-hours detail is from J8, not J7 |
| KH24 | January 12, 2012: "Mike is going to be putting together a staff." "we want to give him a meritocracy, where they are the most competent coaches…" "What you don't get is the culture and the values, the emotional page…" (in context: Smith had gathered background data on the candidates; culture, values and emotional commitment were what the data did not show). "Everybody looks great until the ball is snapped." The ability to "work with and develop young quarterbacks" was one of Khan's criteria (the writer's paraphrase). One or two candidates were "public figures" who wanted a public arrangement, which Khan treated as a non-starter. | **Single source (club site)** (J8) |
| KH25 | "This is a passing league. This is a quarterback league." | **Single source (AP)** (N9, January 10, 2012: "Khan said last month", that is December 2011). **Corrected** source |
| KH26 | "It's about balance, it's about taking shots at the right time." | **Removed** as a Khan view: it is Mularkey describing his offense (J7) |
| KH27 | Mark Lamping named president, effective February 27, 2012, responsible for all non-football areas and reporting to Khan; "Gene Smith will continue to report directly to Khan." | **Single source (club site)** (J9, February 13, 2012) |
| KH28 | Tim Tebow, March 2012: "Earlier this week, I asked Gene Smith and his staff to explore the potential of acquiring Tim Tebow." "I think we have a duty to consider all avenues of improving the Jaguars on and off the field." "Our commitment to developing Blaine Gabbert was, and still is, central to our goal." "We're looking ahead with zero regrets." Later, to Tania Ganguli of the Times-Union on a Monday: "He didn't want to come, obviously" (P4, March 26, 2012). | Statement: **Single source** (N11, the same text on two NFL.com pages). **Corrected**: the full text adds "on and off the field". Date of March 21, 2012: **Unverified** (snippet-only Jax Daily Record addresses dated March 21 and 22, S4; P4's "last week" is consistent). "Didn't want to come": **Single source** (P4). The fourth-round pick plus $3 million of a $5 million advance: **Unverified** (snippet-only; P4 says only that the club would have "blown through a draft pick") |
| KH29 | Maurice Jones-Drew's holdout: "There's no decision here… It's his choice." "There's more than 50 players under contract… Where do you draw the line?" (P5, July 25, 2012); the club "will not renegotiate", with two years left on a five-year deal (J11, August 1, 2012). On Tuesday, August 21, 2012: "The train's leaving the station. Run. Get on it." and "There's very little for me to add." (J12; N12 via the Times-Union, slightly different wording). Jones-Drew reported on a Sunday with no new deal (N13); Khan: "The Jaguars are a better football team today than we were yesterday," "and now our entire franchise can move forward together and as one," "Nothing more needs to be said." | Stance: **Confirmed** (P5, J11). "Train" quote: **Confirmed** (J12, N12); **Corrected** date. Report date of September 2, 2012: **Confirmed (excerpt)** (N13 plus an AP copy at a Washington Times address dated September 2, S9). Khan's statement: **Single source** (N13) |
| KH30 | Business moves: a $3 million locker-room renovation, for which players thanked Khan (J11). On Tuesday, August 21, 2012 Khan and Goodell announced one Jaguars home game at Wembley in each of 2013, 2014, 2015 and 2016; Khan: "The Jacksonville Jaguars will be a bold and ambitious NFL franchise." | Renovation: **Single source (club site)**. London: **Confirmed (excerpt)** (J13; a Wembley Stadium release address dated August 22, 2012, S10). **Corrected**: the announcement is now dated |
| KH31 | Analytics: "his 30-year-old son, Tony, will helm the team's new technology and analytics group" (Forbes, September 5, 2012, quoted on an Illinois page seen only in a snippet, S3). The current Tony Khan biography states the group was created in 2012 (J32; only that dated fact is used). No Shad Khan statement on analytics before the boundary was found. | **Unverified** (snippet-only) for the Forbes line; 2012 creation: **Single source (club site)**. Later characterizations of Shad Khan's analytics emphasis: **Removed** (section 5.3) |
| KH32 | Mid-season, November 7, 2012: "What I want to evaluate is really the organization… I think people are one part of it." "The simple fact is I really want to satisfy people in the short-term. But what's more important is the long-term." He would wait until the season ended to judge Mularkey and Smith, and would not evaluate them as a unit (paraphrase); "There's nobody here that's happy with the results." J15 also has "evaluation, not reaction"; "knee-jerk, emotional reaction"; three ingredients, "The right people in the right spots." "The correct processes to make decisions." "Support from ownership and customers."; "I'm going to go with my judgment."; a contrast with another owner, "that's not me"; "London is not a neutral site"; and a 2012 payroll of $135 million, sixth-highest (Khan's own claim). | Core stance: **Confirmed** (J15; N14 quoting the Times-Union). **Corrected** wording to the fuller Times-Union text. J15-only items: **Single source (club site)**. Payroll figure: **Unverified** (Khan's claim, not independently checked) |

### 2.4 The end of the 2012 season

| # | Finding | Label and sources |
|---|---|---|
| KH33 | Mularkey, December 31, 2012: "I report to Shad just as Gene reports to Shad just as (Jaguars President) Mark Lamping reports to Shad." "I always stayed in touch with Shad weekly to give him updates." | **Single source (club site)** (J16); fits J9 |
| KH34 | Khan dismissed Gene Smith on Monday, December 31, 2012, the day after the regular season ended. Release at 8:10 a.m. ET (N15, `datePublished` 2012-12-31, by Gregg Rosenthal); "Monday around 8:09 a.m." (J18). Khan: "I met with Gene Smith this morning to inform him of my decision to go in a new direction and thank him for his dedication to the Jaguars since the inception of the franchise." (the page spells the owner "Shah Khan"); Smith is "a good man with a long career ahead of him in football". ESPN, 8:20 a.m. ET: "The Jaguars fired general manager Gene Smith on Monday ..." | **Confirmed** (N15; E1; J18). **Corrected**: N15 does carry a date in its metadata. "Now it is time for the Jacksonville Jaguars to begin a new chapter" (WJXT) and a report that Weaver urged Khan to keep Smith: **Unverified** (snippet-only). The heraldnet AP copy: **Unverified** (refused) |
| KH35 | "Owner Shad Khan is waiting to decide Mularkey's fate until he hires a new general manager." | **Single source** (E1, December 31, 2012); the substance is **Confirmed** by KH45 |
| KH36 | Mularkey's status, three accounts that do not fully agree: his job was not discussed and he was coach "until I'm told otherwise" (J18, January 2, 2013); he told players he remained head coach after speaking with the owner "Thursday and Monday" (Jay Glazer, via the N15 update); he "met with owner Shad Khan last week" and "was told that the new GM would have final say" (P6, January 10, 2013). | First two: **Single source** each, wording confirmed. "Final say": **Single source** (P6, unsourced there) |
| KH37 | By January 5, 2013, "the coaching staff has been given permission to speak with other teams" (J20, relaying ESPN's Adam Schefter), which the columnist called "a fair and admirable move by Khan" (dated opinion). A reader's question in the same column says PFT reported Khan was "leaning toward keeping" Mularkey. | Permission: **Confirmed (excerpt)** (J20; the AP headline "Person familiar with situation: Jaguars owner Khan allows assistant coaches to pursue jobs", S11, search text only; contracts library C72 agrees). "Leaning toward keeping": **Unverified** (the PFT report was not located; J20 only paraphrases a reader) |
| KH38 | Mularkey dismissed Thursday, January 10, 2013 ("In a meeting this morning", J25); "Caldwell, in his first major move as general manager, met with and dismissed Mularkey around 10 a.m. Thursday" (J27). Khan: "Mike Mularkey is leaving our organization with my utmost respect." "Mike will land on his feet soon." | Date, and Caldwell making the call: **Confirmed** (J25; N16; P6). 10 a.m.: **Single source (club site)**. "Utmost respect": **Confirmed** (J25, N16) |
| KH39 | Khan's stated reasons, January 10, 2013: "the team has really gotten worse"; "we were a pretty good team, just a few players and a draft away from really competing for a playoff spot"; "we would need really a fresh start and a rebuild from the ground up"; "I think it's time for me to set a different course" (J26). "Our record was still 2-14 and regrettably this is a league that demands winning. What we have to do is win, obviously." (J27). "It was hard for both of us" (J27; the rest of that sentence not re-confirmed). | **Single source (club site)**, wording confirmed against the pages; "rebuild from the ground up" **Confirmed (excerpt)** (an AP snippet, S12). **Corrected**: the 2-14 quote now exact from J27 (a first pass had a paraphrase) |
| KH40 | "Mularkey became the 14th NFL coach since 1984 to be dismissed after one season" (a Jaguars.com article of January 10, 2013). He had two years left on a three-year contract. In the base-rate data his 2012 season sits in the "0-4 wins, 1st season" group, where 5 of 17 coaches were changed. | "14th": **Unverified** (one sentence, club site). Two years left: **Unverified** in this pass (W1 in search text; the CBS News and AP pages were refused); the contracts library (C39) labels it Confirmed through Wikipedia's cited AP and USA Today reports. Group count: **Confirmed** (1.4) |

### 2.5 The January 2013 search

| # | Finding | Label and sources |
|---|---|---|
| KH41 | General manager first. Khan interviewed Caldwell "a day after the regular season ended, hours after announcing" Smith's departure (J23); Caldwell was the first candidate Khan interviewed (J26); the interview was on Monday, with a second meeting on Wednesday (J19). Thomas Dimitroff passed on the opportunity ("Shad will be here at four"). | **Single source (club site)** (J19, J23, J26); Monday interview **Confirmed** with N21 (CA9). Dimitroff: **Single source (club site)** |
| KH42 | Khan "knew immediately in that meeting he wanted to hire Caldwell", but Caldwell wanted this to be his last job, so Khan "needed to be sure"; Khan "encouraged – even mandated" Caldwell's Jets interview (J26, the writer's paraphrases). The editorial called the nine-day search "extensive, not knee-jerk" (J23, dated opinion). | **Single source (club site)**, paraphrase. **Corrected**: a first pass's "Khan decided quickly" drops the need to be sure and the third interview (CA13) |
| KH43 | Candidates: the club reportedly interviewed Caldwell (Monday and Wednesday), Tom Gamble (Tuesday) and Marc Ross (Friday), and spoke with Steve Keim on Friday evening; Saturday reports had the search narrowed to Caldwell and Keim (J21, January 6, 2013). Keim was promoted to Arizona general manager on January 8, 2013. | Days: **Single source (club site)**; Gamble, Ross and the final two: **Confirmed** (CA12). Keim: **Confirmed** (N17; N26; J23). **Corrected**: J19 does not mention Ross and lists Keim only as a planned interview; a first pass's "Keim stayed in Arizona" had no source |
| KH44 | Caldwell hired Tuesday, January 8, 2013. Khan: "We got our man," and "the best days for the Jacksonville Jaguars are in front of us"; "Khan hired Caldwell after a nine-day search that began the day following the Jaguars' final regular season game" (J22); "I have a lot of faith in David Caldwell" (N17). | **Confirmed** (J22; N17; F4). Caldwell "on the top of his list": **Removed** (not found) |
| KH45 | The new general manager leads the coaching decision. Khan, January 10, 2013: "About the coach, we went through a coaching search which was led by Gene (Smith) at that point, and this time will be led by David (Caldwell)." "Circumstances are a little bit different." | Quote: **Single source (club site)** (J27). Substance: **Confirmed** (E1, December 31, 2012; J27; P6). Only P6 says "final say" |
| KH46 | "As Shad Khan laid it out, the Jaguars' new head coach will report to Caldwell", which the writer adds "presumably" gives Caldwell final say on personnel. | **Unverified** (J30, January 13, 2013: the writer's paraphrase and his own inference; no verbatim Khan statement on the reporting line was found) |
| KH47 | On Tebow, "It's not my decision"; Khan said he told the staff to look at Tebow and they chose "a different direction". | **Unverified** (snippet-only syndicated AP copy of January 10, 2013) |

### 2.6 What the dated record shows (a reading of the rows above)

- **Timing and patience.** He made no in-season change in 2012 and said he would judge the coach and general manager after the season, by "evaluation, not reaction" (KH32). He dismissed the general manager the day after the regular season ended (KH34), and the coach was dismissed ten days later by the general manager he had just hired (KH38).
- **Accountability** (J1, December 2011, **Single source (club site)**): "That's huge power, but with that comes responsibility and accountability." "I'd rather not have partners … That way I don't have accountability to them. It's mine alone and I would prefer that." "When you don't [succeed], you go back and start making a midcourse correction." In January 2013: "a league that demands winning" (KH39).
- **What he said he wanted in a coach, 2011-2012:** a quarterback league (KH25); smart over splash (KH23); culture and values (KH24); developing young quarterbacks (paraphrase, KH24); a meritocracy on the staff (KH24); no candidate who wanted a public arrangement (KH24).
- **Delegation.** In 2012 the general manager led the coaching search with Khan in the room (KH19, KH23). In January 2013 he left the coach decision to the new general manager (KH45).
- **Communication.** In 2012 the coach, the general manager and the president each reported to him, and the coach updated him weekly (KH33, **Single source (club site)**). The 2013 line to Caldwell is **Unverified** (KH46). He spoke bluntly in public ("The train's leaving the station", KH29) and defended his people in public ("uninformed fan", KH17).
- **Dated opinions** by the club's writer, not facts: "doesn't believe he has all the answers" and is "open-minded enough to ask the right questions – and to hear the real answers" (J5, January 6, 2012; **Corrected** from a first-pass paraphrase); "He chose substance over flash in hiring Mike Mularkey" (J10, February 16, 2012); "it has been Khan's approach to let football people make football decisions" and "He knows enough to know what he doesn't know" (J30, January 13, 2013).
- **What the record does not contain:** any case of Khan or Caldwell judging a head coach after a winning or middling season. The one coach Khan helped hire was judged after 2-14, and the dismissal was made by a general manager hired two days earlier.

## 3. David Caldwell before January 15, 2013

### 3.1 Career before Jacksonville

| # | Finding | Label and sources |
|---|---|---|
| CA1 | Carolina Panthers, 1996-97, scouting assistant, "with Polian" (J22). Context: a "17-year NFL veteran with Carolina, Indianapolis and Atlanta" (J26); on Greg Roman, "we worked together in Carolina" (J27). | **Single source (club site)** |
| CA2 | Indianapolis Colts, 1998-2007 (10 seasons), western regional scout in his last two: "the last 10 seasons with the Colts, including the last two as western regional scout" (N18); a "10-year term" (N21); "area and regional scout" (F1). | **Confirmed** (J22; N18; N21; F1). Territory (Pac 10, Big 10, Big 12): **Single source (club site)** (J22, J24). **Unverified, unresolved**: J24 says area scout "for seven seasons covering the Midwest and West Coast", and seven plus two is nine, not ten; a later media guide seen only in search text says "first eight years" |
| CA3 | Hired by Atlanta as director of college scouting in 2008; AP says only "on Wednesday", and the page's `datePublished` is 2008-04-30, a Wednesday. Dimitroff: "He comes to us from a highly respected and very successful team... great asset to the scouting department"; it was "the same position... that Dimitroff held in New England". | Likely April 30, 2008: **Corrected** date, resting on page metadata only (**Unverified**, no second source). Quotes: **Single source (AP)** (N18) |
| CA4 | Promoted to director of player personnel on February 14, 2012, replacing Les Snead, after four seasons as college director. | **Confirmed** (F1; N19). **Corrected**: J22's "director of college scouting from 2008-2012" is wrong; F1, N19 and N20 give 2008 to early 2012 |
| CA5 | Falcons duties. F1: he oversaw the college area and regional scouts, "assimilates the information he receives and presents it to General Manager Thomas Dimitroff with a goal to make the NFL Draft as effective as possible", and helped scout Julio Jones, Sean Weatherspoon, Corey Peters, William Moore and Joe Hawley. F4: in 2012 he "oversaw both the college and pro scouting efforts" and "played a day-to-day role in the analysis and evaluation of the Falcons' current roster while aiding in the research on how to acquire future free agents". He sat in on Combine interviews with Dimitroff, Mike Smith, the coordinators, Lionel Vital and a team psychologist (F2, a staff writer summarizing Dimitroff's podcast). Dimitroff, April 19, 2012: the personnel department was "led by Dave Caldwell, our new Director of Player Personnel and Lionel Vital" (F3). | F1 items: **Single source (club site)**. F4: the club's own description, quoted by J22 (**Single source**, two club sites repeating one release). F2: **Unverified** (summary of a podcast). F3: **Single source (club site)** |
| CA6 | Atlanta went 56-24 with four playoff appearances, 2008-2012 (J24); N20 has three earlier appearances plus the 2012 top seed. | **Confirmed** (J24; N20; W1's season list sums to 56-24). Only regular-season records and qualification are used; the January 2013 playoff results are not |
| CA7 | Age 38 (J22, J24, J26; an AP/ESPN January 8 excerpt, "the 38-year-old Caldwell"). John Carroll University, a Buffalo native, married to Joelle, a son David Michael II (J22). Played linebacker at John Carroll, 1992-96. Greg Roman was "Caldwell's roommate at John Carroll University" (J27), "his former college classmate" (P6), "old friends" (an NFL.com report of January 10, 2013). Chris Polian and Caldwell "attended college together" (J27). | Age: **Confirmed (excerpt)**. Family and hometown: **Single source (club site)**. Linebacker: **Unverified** (snippet-only). College link with Roman: **Confirmed**; "roommate": **Single source (club site)**. Polian: **Single source (club site)**, consistent with W1 |

### 3.2 The general-manager search and hire

| # | Finding | Label and sources |
|---|---|---|
| CA8 | December 30, 2012: "front-runner for projected openings in Buffalo and Jacksonville"; Dimitroff: "He's my right-hand guy..." | **Single source** (N20). **Corrected** author: Steve Wyche (named in the page metadata), not unbylined |
| CA9 | First interview with Khan on Monday, December 31, 2012. | **Confirmed** (N21, Glazer; J18; J19; Caldwell's account in J26) |
| CA10 | San Diego: Atlanta granted permission for the Jets and the Chargers (N21); "The Chargers also interviewed Steve Keim and Caldwell" (N26, January 8, 2013). | Interviewed: **Confirmed** (N26; an AP excerpt listing him as a Chargers candidate). **Corrected**: upgraded from permission only. Date of the interview: **Unverified** |
| CA11 | Second Jaguars interview on Wednesday, January 2. | **Single source (club site)** (J19) |
| CA12 | Other candidates: Tom Gamble (N21, Albert Breer on permission; J18); Marc Ross (N22, a scheduled Jaguars interview; J23); down to Keim and Caldwell by January 6 (N23; J23). | **Confirmed** as reported |
| CA13 | Third interview on Monday, January 7: "will have a third interview" (N24); "Monday" (J23); "already staged three" (N25, January 8); "a day after a third interview" (an AP excerpt). | **Confirmed** |
| CA14 | A second Jets interview scheduled for Tuesday, January 8, in New Jersey. | Reported as scheduled: **Single source** (N25). Whether it was held: **Unverified** |
| CA15 | Hired Tuesday, January 8, 2013; Keim was promoted in Arizona the same day. Caldwell: "There are no bad GM opportunities... This is where I wanted to be and I could not be happier." | **Confirmed** (J22; F4; N17; N26; the statement quotes match in J22 and N17) |
| CA16 | A five-year contract: an AP photo caption carried on P7 (January 14, 2013) and an ESPN excerpt of January 10, 2013 ("who signed a five-year deal", E2). Salary, guarantees and authority clauses not found. | Length: **Confirmed (excerpt)** as a media report; both may trace to AP, and the club stated no terms. Other terms: **Unverified** (not found) |
| CA17 | The Jets: "Shad made me go to New York to visit the Jets... that had a major role in me selecting the Jacksonville Jaguars" (J26, J28). The Jets prepared a $1 million housing allowance (P7, citing Peter King). P7's view that the Jets' cap, quarterback situation and inherited coach deterred him. | Quote: **Single source (club site)**. "encouraged – even mandated" and "his next job to be his last job" are the writer's paraphrases, **Corrected** from quotes. Housing: **Unverified** (secondhand). P7's view: a journalist's dated inference, not evidence of Caldwell's reasoning |

### 3.3 Authority and reporting

| # | Finding | Label and sources |
|---|---|---|
| CA18 | The new general manager would decide the coaching staff's future: "reports that Khan will leave the future of the coaching staff to the general manager" (J18, January 2); N23 (January 6); "will rest largely in Caldwell's hands" (N17, January 8); P6 (January 10). J19 (January 3): "Khan has not discussed that situation publicly." | **Confirmed** as reported. P6's "was told that the new GM would have final say": **Single source**, unsourced there; Mularkey had said his status was not discussed in his December 31 meeting (KH36) |
| CA19 | Khan, January 10: the coaching search "this time will be led by David (Caldwell)". | **Single source (club site)** (J27); see KH45 |
| CA20 | Assistants: the new head coach decides their fate; assistants may seek other jobs but "must clear the process through Caldwell". | **Single source (club site)** (J26; J27) |
| CA21 | Reporting line: "As Shad Khan laid it out, the Jaguars' new head coach will report to Caldwell, and presumably that will give Caldwell final say on personnel matters" (J30). | **Unverified**: the reporting line is the writer's paraphrase; "final say" is his own inference |
| CA22 | Tebow: an AP excerpt says Khan would make no Tebow demands of Caldwell, or that the decision was ultimately Caldwell's. Gregg Rosenthal on NFL.com (January 10, 2013): "the ultimate decision-maker was not in place yet. Caldwell is making those decisions." | AP: **Unverified** (snippet-only). Rosenthal: a dated analysis, not a sourced fact |

### 3.4 The Mularkey decision, January 10, 2013

| # | Finding | Label and sources |
|---|---|---|
| CA23 | Caldwell dismissed Mularkey on his first day in the building, in a meeting around 10 a.m.; the statement went out at 11:01 a.m. | Date: **Confirmed** (J25; N27, an opinion column used for the date only; P6; an AP excerpt). Times and "first day in the building": **Single source (club site)** |
| CA24 | Release statement: "I know Mike well... an immediate and clean restart." AP excerpts carry "I informed Mike today..." and "an immediate and clean restart". | **Confirmed (excerpt)** (J25) |
| CA25 | Press conference: "You've got to have a fresh start across the board" (J28; an ESPN excerpt). "I felt like we needed a fresh start here"; the conversation was "difficult"; "It was tough... the worst part of the business"; "I have a personal relationship over the last five years with Mike". | First: **Confirmed (excerpt)**. Others: **Single source (club site)** |
| CA26 | Caldwell and Mularkey overlapped in Atlanta from 2008 to 2011, four seasons ("Mularkey spent 2008-2011 as the Atlanta Falcons' offensive coordinator", J27; "four years together in Atlanta", an AP excerpt). | **Confirmed (excerpt)**. **Corrected**: J26's "2008 through 2012" contradicts itself |
| CA27 | Khan the same day: "rebuild from the ground up"; "I think it's time for me to set a different course." | See KH39 |

### 3.5 Introductory remarks, January 10, 2013

| # | Finding | Label and sources |
|---|---|---|
| CA28 | Head-coach criteria: "Not a prerequisite... In terms of previous head coaching experience, not necessary", citing Mike Smith (J26, J27, J28; a ClickOrlando excerpt of January 11, 2013). "I'm looking for the right person"; "We're not going to set a timetable..."; a list with "wheels" turning; on Roman, "Greg and I went to college together, we worked together in Carolina...". J28 also lists Mike Nolan among names mentioned. | First: **Confirmed (excerpt)**. Others: **Single source (club site)** |
| CA29 | "The common thread is the relationship between the head coach and the general manager and obviously the quarterback." | **Single source (club site)** (J28). The "trinity" framing around it is the writer's |
| CA30 | Quarterback: Tebow would not be on the roster (J26; N28; an AP excerpt); "There will be an open competition" (NFL.com) or "We're going to have open competition... let the best player win" (J28); Blaine Gabbert the "second-youngest" quarterback (an NFL.com paraphrase; repeated in a J30 reader question); "I have others in mind and I'm comfortable with what's here". | Tebow and open competition: **Confirmed** (wording varies). "Second-youngest": **Confirmed** as a paraphrase. Last quote: **Single source (club site)** |
| CA31 | Evaluating people: "I need to evaluate everybody here first to give everyone an equal opportunity to get on board" (J27 only), said about the front office and scouting in reply to a question about Chris Polian, not about the staff in general. "Right now I know we have a good scouting department..." (J27; J28). | **Single source (club site)**. **Corrected** scope |
| CA32 | Analytics: "I am a believer of analytics... It's not the whole part of the process." | **Single source (club site)** (J28) |
| CA33 | Draft-first building: no statement dated before the boundary was found. A February 22, 2013 club article says he had made the point "since Caldwell's hiring in early January", with no dated quote. | **Unverified** (not found). The February 22 characterization: **Removed** |
| CA34 | Patience and accountability: no direct statement found. The pre-boundary record leans toward urgency: "immediately explore every avenue", "as quickly as our fans deserve". | **Unverified** for patience; urgency phrases: **Single source (club site)** |

### 3.6 Working style: dated opinions only

| # | Finding | Label and sources |
|---|---|---|
| CA35 | Dimitroff, January 8, 2013: "very bright, adept and organized talent evaluator... very sound understanding of team building and player acquisition". December 30, 2012: "He's my right-hand guy". | First: dated opinion, on two club sites repeating one release (F4; J22). Second: **Single source** (N20) |
| CA36 | Bill Polian: "I had the pleasure of working with him for over 15 years..." | Dated opinion, **Single source (club site)** (J24). Their shared employment in the club biographies is 1996-2007, 12 seasons |
| CA37 | Anonymous: "If you get him, you guys will win... He's that good" (a scout who worked with him with the Colts, said "late Monday", January 7; J23); "The guy's a stud" (J26). | Dated opinions, **Single source (club site)**. **Corrected**: the first quote is in the J23 editorial, not J24 |
| CA38 | Club-site judgments: "decisive" (J26); "Caldwell has guts" (J28); "decisive and sure on the issue of Tim Tebow" (J29, O-Zone). | Dated opinions. **Corrected** attribution: the migrated pages show no bylines, so only the O-Zone pieces (J29, J30) can be attributed to John Oehser |
| CA39 | Coaching-search activity inside the window: a permission request for Brian Schottenheimer (N29, citing Ian Rapoport; J28); Mel Tucker scheduled for Monday, January 14 and Jay Gruden set to interview (N30; J30; J31); Mike Armstrong and Mike McCoy named in the O-Zone; "no prior relationship" with Tucker (J30, J31). | Schottenheimer, Tucker and Gruden: **Confirmed** as reported plans. Armstrong and McCoy: **Single source (club site)**. "No prior relationship": **Single source (club site)**. Whether the Tucker interview happened inside the window: **Unverified** (the first confirmation found is dated January 16 and is excluded) |

## 4. How this record may and may not be used

**May:**

- As dated facts about what Khan and Caldwell did and said before January 15, 2013, each with its label.
- As a **frozen, documented input applied the same way to every club for which a comparable dated pre-divergence record exists**, written into the 2014 employment method before Jacksonville's final 2014 game and before any My Season Response is read (season end §C; Document 1 §9.1). Example of the form, not a recommendation: "an owner on record as judging his coach only after the season is not drawn mid-season", applied to every club whose owner has such a dated statement.

**May not:**

- Set or adjust Jacksonville's chance alone, or any club's chance where the other clubs' comparable records have not been researched to the same depth. Jacksonville's record is far deeper than any other club's in this repository (1.7, Q4).
- Stand for how Khan would weigh a 2014 season. Each recorded decision was one decision in its own circumstances: a 2-14 season, an inherited coach, a general manager hired two days earlier (2.6).
- Supply a size. No source gives how much a stated attitude changes a dismissal rate. Any number attached to one is a modelling choice and must be labelled as such.
- Draw on anything after the boundary: the real club's later decisions, statements or profiles.
- Treat the October 5, 2014 "Ownership perspective" page as Khan's private weighting (1.6, G4).

## 5. Verification

### 5.1 How the second passes were run

- **Repository and rates.** A new detached worktree of merged `main` at `f2989ce`, removed afterwards. Own code, written separately from the repository's builder and from the first pass and kept outside the repository, recomputed the base rates from a fresh `games.csv` (D1) and counted the real 2012 Jaguars figures from nflverse play-by-play (D2). The carousel's stage 1 was dry-run from the committed inputs.
- **Khan and Caldwell.** Every page was reopened rather than trusting the first pass's citations; pages on refused hosts stay at their search-text label. Wikipedia was used only for context.
- **Label harmonization (this file).** The Khan pass counted a reopened single page, or two Jaguars.com pages, as Confirmed ("club-only"); the Caldwell pass counted several Jaguars.com pieces as one source. This file applies the Caldwell rule to both men: such claims are **Single source (club site)**.

### 5.2 Corrections

1. The January 2014 stage 1 drew 29 clubs; Buffalo's and Minnesota's draws come from Entry 83 (K2).
2. An 11+ non-playoff group exists for 4th+ tenure; none exists for a 1st-season or 2nd-3rd coach (1.4).
3. The review froze five of the pre-hire file's six criteria (B3).
4. The 2012 season had 23 kept club-seasons, not 24 (1.8, item 4).
5. The delegation for Stone's reconstructed terms is dated October 18, 2026; the entry October 19 (S2).
6. The October 5, 2014 page is unsigned, not "in Khan's voice", and the quote is two sentences from separate paragraphs (G4).
7. The ban on invented scores is season end §C item 2 (A5); the job fields sit under `appointments[0]` (A1).
8. The NFL.com Gene Smith page is dated in its metadata (KH34); the January 10, 2013 2-14 quote is now exact (KH39).
9. Khan's background: the countries in J14 (KH4); Flex-N-Gate dates upgraded from Wikipedia only (KH5); the Rams agreement dated to 2010 (KH8).
10. Purchase: the finance-committee vote dated December 6, 2011 (KH12); J2 dated December 14 (KH13); $770 million at closing (KH16).
11. 2012: "the most important thing" refers to Weaver's regard for Smith (KH18); the four-and-a-half-hours detail is from J8 (KH23); "passing league" sourced to AP, December 2011 (KH25); "balanced offense" is Mularkey's (KH26); the Tebow quote's full text (KH28); the "train" quote dated August 21, 2012 (KH29); the London announcement dated (KH30); the November 7, 2012 wording (KH32).
12. January 2013: "decided quickly" corrected (KH42); the candidate list and Keim's promotion (KH43).
13. Caldwell: his Falcons hire date from metadata (CA3); the college-director years (CA4); the Wyche byline (CA8); the Chargers interview upgraded (CA10); Jets paraphrases are the writer's (CA17); "equal opportunity" scope (CA31); the overlap with Mularkey is 2008-2011 (CA26); the scout quote's source (CA37); byline attribution (CA38).

### 5.3 Removed

- FootballScoop's "68 changes 2004-2013" and "38 months" average tenure (R5): the count includes changes after January 15, 2013, and the article dates to 2014.
- Later characterizations of Shad Khan's emphasis on analytics (TruMedia releases of 2013 and 2015), and the "under Khan's guidance" framing in the current Tony Khan biography; only its dated "2012" fact is kept (KH31).
- "Caldwell on the top of his list" (not found, KH44).
- "Balanced offense" as a Khan view (KH26).
- The February 22, 2013 draft-first characterization of Caldwell (CA33) and the January 16, 2013 confirmation of the Tucker interview (CA39).
- The real club's head-coach hire after the boundary, every article about it, all later profiles, and all later coaching-hire, playoff-result and tenure material that appeared in searches.
- Wikipedia's reading that Polian "was not at Carolina"; Wikipedia itself has him as Carolina's general manager in 1995-97.
- No first-pass claim about Khan or Caldwell used a post-boundary action as evidence of how either would decide. The post-boundary items in 1.8 (items 4, 5 and 8) remain only as flagged defects in the modelling inputs.

### 5.4 Still unverified or not found

- Mularkey's financial terms; Caldwell's salary, guarantees and authority clauses.
- Any statement by Shad Khan on analytics before January 15, 2013.
- Any explanation from Khan on December 31, 2012 beyond "new direction".
- Khan's birth day, arrival year and first job (KH3, KH7).
- The 60 Minutes transcript, the January 10, 2013 press-conference transcript and the full text of the Forbes story.
- The official 2012 Jaguars rushing total (G5).
- A rate for mid-season dismissals in the era.
- Whether the 2014 rule for "recent playoffs" counts the branch 2013 season (1.4), and what applies to an 11-win non-playoff second-season coach (1.4). These are modelling choices, not facts to be found.

### 5.5 Discrepancies in existing records (not corrected in this commit)

- [Coaching career path](nfl_coaching_career_path.md) §7 still cites the removed FootballScoop count and tenure.
- [Pre-hire market](2013_coaching_market_pre_hire.md) line 116 overstates what Caldwell discussed on January 10, 2013 (1.8, item 9).
- The base-rate file's `tenure_2013` and the January 2014 carousel results carry real post-boundary hires as identities (1.8, item 5); the hire-day list and coordinator-opening rates come from the post-boundary cycle (1.8, item 8).
- The carousel method's sentence that recent playoffs "lowered the change rate" holds only for some groups (1.8, item 1); its text names only the real 2011 or 2012 playoffs while the builder counts the two prior seasons (1.4).

## 6. What this file does not contain

- No adopted employment method, no probability for Stone, and no shift to any base rate.
- No real event after January 15, 2013 used as evidence, and no name or date of a real head-coach hire made on or after that day.
- No private weighting by Khan or Caldwell for 2014.
- No grounds for dismissal for cause, and no payment schedule beyond the recorded reconstruction.

## Sources

Repository files are linked where cited and were read at commit `f2989ce`.

**Jaguars.com (club site)**

- J1. Oehser, "Getting to know Shad Khan" (December 15, 2011): https://www.jaguars.com/news/getting-to-know-shad-khan-6615180
- J2. "An American dream come true" (December 14, 2011): https://www.jaguars.com/news/an-american-dream-come-true-6611651
- J3. "A surreal day" (November 29, 2011): https://www.jaguars.com/news/a-surreal-day-6384747
- J4. "Ten things" (December 3, 2011): https://www.jaguars.com/news/ten-things-6413202
- J5. Oehser, "Magnificent Seven" (January 6, 2012): https://www.jaguars.com/news/magnificent-seven-6761174
- J6. "Mike Mularkey new head coach" (January 10, 2012): https://www.jaguars.com/news/mike-mularkey-new-head-coach-6787942
- J7. "The best choice" (January 11, 2012): https://www.jaguars.com/news/the-best-choice-6793607
- J8. "A key factor" (January 12, 2012): https://www.jaguars.com/news/a-key-factor-6796393
- J9. "Lamping named new Jaguars president" (February 13, 2012): https://www.jaguars.com/news/lamping-named-new-jaguars-president-6937773
- J10. "Not quite that time" (February 16, 2012): https://www.jaguars.com/news/not-quite-that-time-6948040
- J11. "Khan: It's coming along very well" (August 1, 2012): https://www.jaguars.com/news/khan-it-s-coming-along-very-well-7755420
- J12. "Nothing to add on Maurice Jones-Drew" (August 21, 2012): https://www.jaguars.com/news/nothing-to-add-on-maurice-jones-drew-8004055
- J13. "Jaguars announce four London home games" (August 21, 2012): https://www.jaguars.com/news/jaguars-announce-four-london-home-games-8003196
- J14. "Khan on 60 Minutes" (October 25, 2012): https://www.jaguars.com/news/khan-on-60-minutes-8654330
- J15. "Shad Khan: Now's the time for evaluation" (November 7, 2012): https://www.jaguars.com/news/shad-khan-now-s-the-time-for-evaluation-8777485
- J16. "Full speed ahead" (December 31, 2012): https://www.jaguars.com/news/full-speed-ahead-9248145
- J17. "Part of the business" (December 31, 2012): https://www.jaguars.com/news/part-of-the-business-9246138
- J18. "The waiting game" (January 2, 2013): https://www.jaguars.com/news/the-waiting-game-9260361
- J19. "Looking back and looking ahead" (January 3, 2013): https://www.jaguars.com/news/looking-back-and-looking-ahead-9269405
- J20. O-Zone, "Getting on the radar" (January 5, 2013): https://www.jaguars.com/news/ozone-getting-on-the-radar-9287179
- J21. O-Zone, "Sometimes you get the bear" (January 6, 2013): https://www.jaguars.com/news/ozone-sometimes-you-get-the-bear-9291948
- J22. "Caldwell named Jaguars general manager" (January 8, 2013): https://www.jaguars.com/news/caldwell-named-jaguars-general-manager-9312875
- J23. Editorial, "The future begins" (January 9, 2013): https://www.jaguars.com/news/editorial-the-future-begins-9314139
- J24. "Dimitroff: I know that he will excel" (January 9, 2013): https://www.jaguars.com/news/dimitroff-i-know-that-he-will-excel-9318386
- J25. "Mularkey dismissed as Jaguars head coach" (January 10, 2013): https://www.jaguars.com/news/mularkey-dismissed-as-jaguars-head-coach-9321977
- J26. "The new leader" (January 10, 2013): https://www.jaguars.com/news/the-new-leader-9337107
- J27. "No timetable on coaching search" (January 10, 2013): https://www.jaguars.com/news/no-timetable-on-coaching-search-9337150
- J28. "What we learned" (January 11, 2013): https://www.jaguars.com/news/what-we-learned-9338759
- J29. O-Zone, "A memorable day" (January 11, 2013): https://www.jaguars.com/news/a-memorable-day-9338902
- J30. O-Zone, "Don't overthink it" (January 13, 2013): https://www.jaguars.com/news/don-t-overthink-it-9350736
- J31. "Wild weekend" (January 14, 2013): https://www.jaguars.com/news/wild-weekend-9359436
- J32. Tony Khan, front-office biography (current page; its dated "2012" fact only): https://www.jaguars.com/team/front-office-roster/tony-khan

**NFL.com** (wire pages show no visible date; the date given is the one the row derives)

- N1. AP, "Pakistani-born Khan approved as Jaguars new owner" (December 14, 2011; 2011 AP copyright): https://www.nfl.com/news/pakistani-born-khan-approved-as-jaguars-new-owner-09000d5d8250c180
- N2. AP, Kroenke exercises his matching right (a Monday deadline, fits April 12, 2010): https://www.nfl.com/news/kroenke-exercises-matching-right-to-try-to-buy-100-percent-of-r-09000d5d8177c7f3
- N3. AP, "NFL unanimously approves Kroenke as Rams majority owner" (a Wednesday meeting, fits August 25, 2010): https://www.nfl.com/news/nfl-unanimously-approves-kroenke-as-rams-majority-owner-09000d5d81a00a70
- N4. AP, Weaver selling the Jaguars (Tuesday, November 29, 2011): https://www.nfl.com/news/weaver-selling-jags-whom-he-believes-will-stay-in-jacksonville-09000d5d824946d5
- N5. AP, "NFL finance committee supports Khan as Jaguars owner" (Tuesday, December 6, 2011): https://www.nfl.com/news/nfl-finance-committee-supports-khan-as-jaguars-owner-09000d5d824cef5e
- N6. AP, "Jaguars eager to move on after tumultuous season" (January 2, 2012): https://www.nfl.com/news/jaguars-eager-to-move-on-after-tumultuous-season-09000d5d825a4b63
- N7. AP, "Jaguars ownership officially transfers from Weaver to Khan" (Wednesday, January 4, 2012): https://www.nfl.com/news/jaguars-ownership-officially-transfers-from-weaver-to-khan-09000d5d825b5e22
- N8. "New Jaguars owner hits ground running on coaching search" (January 4, 2012): https://www.nfl.com/news/new-jaguars-owner-hits-ground-running-on-coaching-search-09000d5d825b9e32
- N9. AP, "Jaguars hire Mularkey as head coach" (January 10, 2012): https://www.nfl.com/news/jaguars-hire-mularkey-as-head-coach-09000d5d825e4b49
- N10. AP, "Jaguars' Mularkey is a smart, not splashy hire" (January 11, 2012): https://www.nfl.com/news/jaguars-mularkey-is-a-smart-not-splashy-hire-09000d5d825e9b9b
- N11. Khan's Tebow statement (March 2012): https://www.nfl.com/news/khan-spins-positive-on-tebow-but-this-one-hurts-09000d5d827c711b and https://www.nfl.com/news/09000d5d827c664b
- N12. Rosenthal, "Shad Khan to Maurice Jones-Drew: Train is leaving" (Tuesday, August 21, 2012): https://www.nfl.com/news/shad-khan-to-maurice-jones-drew-train-is-leaving-0ap1000000052675
- N13. McIntyre, "Maurice Jones-Drew ends Jacksonville Jaguars holdout" (a Sunday; September 2, 2012 per S9): https://www.nfl.com/news/maurice-jones-drew-ends-jacksonville-jaguars-holdout-0ap1000000057581
- N14. Sessler, "Shad Khan to assess Jacksonville Jaguars after season" (November 7, 2012): https://www.nfl.com/news/shad-khan-to-assess-jacksonville-jaguars-after-season-0ap1000000091885
- N15. Rosenthal, "Gene Smith fired as Jacksonville Jaguars GM" (`datePublished` December 31, 2012): https://www.nfl.com/news/gene-smith-fired-as-jacksonville-jaguars-gm-0ap1000000119906
- N16. Sessler, "Mike Mularkey dismissed as Jacksonville Jaguars coach" (January 10, 2013): https://www.nfl.com/news/mike-mularkey-dismissed-as-jacksonville-jaguars-coach-0ap1000000124398
- N17. Hanzus, "David Caldwell hired as Jacksonville Jaguars GM" (January 8, 2013): https://www.nfl.com/news/david-caldwell-hired-as-jacksonville-jaguars-gm-0ap1000000123880
- N18. AP, "Falcons hire Caldwell to direct scouting" (`datePublished` April 30, 2008): https://www.nfl.com/news/falcons-hire-caldwell-to-direct-scouting-09000d5d80816a43
- N19. AP, "Caldwell, Polk move up in Falcons' plans after Snead departure" (February 14, 2012): https://www.nfl.com/news/caldwell-polk-move-up-in-falcons-plans-after-snead-departure-09000d5d826fb0b7
- N20. Wyche, "Atlanta Falcons' David Caldwell in demand for open GM spots" (December 30, 2012): https://www.nfl.com/news/atlanta-falcons-david-caldwell-in-demand-for-open-gm-spots-0ap1000000118646
- N21. Glazer, "Dave Caldwell interviews for Jacksonville Jaguars GM job" (December 31, 2012): https://www.nfl.com/news/dave-caldwell-interviews-for-jacksonville-jaguars-gm-job-0ap1000000120674
- N22. "Marc Ross of New York Giants to interview for vacant GM jobs" (January 3, 2013): https://www.nfl.com/news/marc-ross-of-new-york-giants-to-interview-for-vacant-gm-jobs-0ap1000000121570
- N23. Breer, "David Caldwell, Steve Keim leading Jaguars GM targets" (January 6, 2013): https://www.nfl.com/news/david-caldwell-steve-keim-leading-jaguars-gm-targets-0ap1000000123005
- N24. Breer, "David Caldwell lands third interview with Jacksonville Jaguars" (January 7, 2013): https://www.nfl.com/news/david-caldwell-lands-third-interview-with-jacksonville-jaguars-0ap1000000123349
- N25. Sessler citing Breer, "Caldwell, New York Jets set second GM interview" (January 8, 2013): https://www.nfl.com/news/caldwell-new-york-jets-set-second-gm-interview-0ap1000000123752
- N26. "San Diego Chargers done interviewing GM candidates" (January 8, 2013): https://www.nfl.com/news/san-diego-chargers-done-interviewing-gm-candidates-0ap1000000124054
- N27. Rosenthal, "Jacksonville Jaguars had to let Mike Mularkey go" (January 10, 2013; opinion column, date only): https://www.nfl.com/news/jacksonville-jaguars-had-to-let-mike-mularkey-go-0ap1000000124517
- N28. Rosenthal, "Tim Tebow won't be on Jacksonville Jaguars, GM says" (January 10, 2013): https://www.nfl.com/news/tim-tebow-won-t-be-on-jacksonville-jaguars-gm-says-0ap1000000124575
- N29. Rosenthal citing Rapoport, "Jaguars want to interview Brian Schottenheimer" (January 10, 2013): https://www.nfl.com/news/jaguars-want-to-interview-brian-schottenheimer-0ap1000000124723
- N30. "Jacksonville Jaguars to interview Mel Tucker" (January 12, 2013): https://www.nfl.com/news/jacksonville-jaguars-to-interview-mel-tucker-0ap1000000125146

**ProFootballTalk (NBC Sports)**

- P1. "Illinois businessman Shahid Khan set to buy Rams" (February 11, 2010): https://www.nbcsports.com/nfl/profootballtalk/rumor-mill/news/illinois-businessman-shahid-khan-set-to-buy-rams
- P2. Alper, "Owners unanimously approve Shahid Khan" (December 14, 2011): https://www.nbcsports.com/nfl/profootballtalk/rumor-mill/news/owners-unanimously-approve-shahid-khan
- P3. Rosenthal, "Jaguars ask for permission to interview Mularkey" (January 2, 2012): https://www.nbcsports.com/nfl/profootballtalk/rumor-mill/news/jaguars-ask-for-permission-to-interview-mularkey
- P4. "Jags owner says Tebow didn't want to come to Jacksonville" (March 26, 2012): https://www.nbcsports.com/nfl/profootballtalk/rumor-mill/news/jags-owners-says-tebow-didnt-want-to-come-to-jacksonville
- P5. Gantt, "Jags owner Shad Khan says no new deal for Maurice Jones-Drew" (July 25, 2012): https://www.nbcsports.com/nfl/profootballtalk/rumor-mill/news/jags-owner-shad-khan-says-no-new-deal-for-maurice-jones-drew
- P6. Gantt, "Jaguars fire Mike Mularkey after one season" (January 10, 2013): https://www.nbcsports.com/nfl/profootballtalk/rumor-mill/news/jaguars-fire-mike-mularkey-after-one-season (also https://profootballtalk.nbcsports.com/2013/01/10/jaguars-fire-mike-mularkey-after-one-season/)
- P7. "Jets were going to offer Caldwell the house, literally" (January 14, 2013): https://www.nbcsports.com/nfl/profootballtalk/rumor-mill/news/jets-were-going-to-offer-caldwell-the-house-literally

**ESPN**

- E1. ESPN.com news services, Gene Smith fired (December 31, 2012, 8:20 a.m. ET): https://www.espn.com/nfl/story/_/id/8795520/gene-smith-jacksonville-jaguars-fired
- E2. Mularkey fired after a 2-14 season (January 10, 2013; seen as an excerpt): https://www.espn.com/nfl/story/_/id/8831771/mike-mularkey-jacksonville-jaguars-fired-2-14-season
- E3. Pasquarelli column (about December 2001; exact date not in the page text): https://www.espn.com/nfl/columns/pasquarelli_len/1305634.html
- E4. Pasquarelli column (2003): https://www.espn.com/nfl/columns/pasquarelli_len/1532190.html

**Atlanta Falcons (club site)**

- F1. "Caldwell, Polk promoted" (February 14, 2012): https://www.atlantafalcons.com/news/caldwell-polk-promoted-7831918
- F2. "Rockin' and rollin'" (February 23, 2012): https://www.atlantafalcons.com/news/rockin-and-rollin-7831983
- F3. Transcript, Thomas Dimitroff pre-draft news conference (April 19, 2012): https://www.atlantafalcons.com/news/transcript-thomas-dimitroff-pre-draft-news-conference-7832141
- F4. "Caldwell hired as Jaguars GM" (January 8, 2013): https://www.atlantafalcons.com/news/caldwell-hired-as-jaguars-gm-9313095

**Seen in search-result text only**

- S1. Jax Daily Record (March 9, 2012), "Khan's $2.5 billion net worth No. 164 in U.S.": https://www.jaxdailyrecord.com/news/2012/mar/09/khans-25-billion-net-worth-no-164-us
- S2. Dawn (September 22, 2012), Lahore-born entrepreneur among U.S. richest: https://www.dawn.com/news/751089/lahore-born-entrepreneur-among-us-richest-people
- S3. Forbes (September 5, 2012), "Shahid Khan: the new face of the NFL and the American dream": https://www.forbes.com/sites/briansolomon/2012/09/05/shahid-khan-the-new-face-of-the-nfl-and-the-american-dream/
- S4. Jax Daily Record addresses dated March 21 and 22, 2012 (the Tebow trade; date only).
- S5. WFAE (December 31, 2012), seven clubs dismiss coaches: https://www.wfae.org/2012-12-31/nfls-bears-bills-browns-cards-chargers-chiefs-eagles-dismiss-coaches
- S6. The Vindicator (January 1, 2013), "Firing squad": https://vindyarchives.com/news/2013/jan/01/firing-squad
- S7. NBC Sports Boston (date not shown), "Black Monday in NFL: 7 coaches, 4 GMs fired": https://www.nbcsportsboston.com/news/black-monday-in-nfl-7-coaches-4-gms-fired/296291/
- S8. NFL.com gallery (undated), coaches and GMs fired on Black Monday: https://www.nfl.com/photos/coaches-and-gms-fired-on-black-monday-0ap1000000120466
- S9. AP via the Washington Times (address dated September 2, 2012), Jones-Drew reports (date only).
- S10. Wembley Stadium release (address dated August 22, 2012), the Jaguars' London games (date only).
- S11. AP via Fox News (January 2013), "Person familiar with situation: Jaguars owner Khan allows assistant coaches to pursue jobs": https://www.foxnews.com/sports/person-familiar-with-situation-jaguars-owner-khan-allows-assistant-coaches-to-pursue-jobs
- S12. AP excerpts of January 10, 2013 on Mularkey's dismissal and Caldwell's introduction (syndicated copies; pages refused).
- S13. NBC Sports Bay Area (January 11, 2011), Rivera hired by Carolina (for row S3 in section 1.5): https://www.nbcsportsbayarea.com/news/ex-cal-lb-rivera-hired-to-coach-carolina-panthers/1238955/
- S14. FootballScoop (2014), "There have been 68 NFL coaching changes in the last decade" (cited only for its removal): https://footballscoop.com/news/there-have-been-68-nfl-coaching-changes-in-the-last-decade
- Five search-result pages dated January 15 to 18, 2013 reporting real head-coach hires were seen; their addresses are withheld because they name post-boundary hires (hindsight boundary).

**Data and context**

- D1. nflverse nfldata `games.csv` (live file, downloaded October 23, 2026; sha256 `618b9326…`): https://raw.githubusercontent.com/nflverse/nfldata/master/data/games.csv
- D2. nflverse play-by-play 2012 (downloaded October 23, 2026; sha256 `ff1cda2e…`): https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_2012.csv.gz
- W1. Wikipedia, "Shahid Khan" (context only, never evidence): https://en.wikipedia.org/wiki/Shahid_Khan
