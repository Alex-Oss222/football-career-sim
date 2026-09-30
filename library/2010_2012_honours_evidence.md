# 2010-2012 public honours evidence (AP All-Pro and Pro Bowl)

**Research date:** September 29, 2026. **Information window:** honours announced for the 2010, 2011 and 2012 NFL seasons, all before the January 15, 2013 Jacksonville divergence (Document 2). **Status:** research evidence for kernel 2014.4 item 1 (team strength); not yet consumed by any kernel. **Policy:** `runtime/2014_engine_decisions.md` E1, user choice "Honours + role" for the first league-wide pass.

Machine record: [`data/2010_2012_honours_evidence.json`](data/2010_2012_honours_evidence.json), built by `scripts/research/build_2010_2012_honours_evidence.py` from the verified honours research file plus pinned nflverse identity files (`players.csv`, `roster_2010.csv`, `roster_2011.csv`, `roster_weekly_2012.csv`; URLs and sha256 in the JSON). The JSON carries each season's verification-pass notes verbatim, because those notes define the second-pass source keys.

## What these receipts are, and are not

- Every entry is an **expert/selector judgement**, not a direct observation. AP All-Pro is a 50-member media panel. Pro Bowl selection combines fan, player and coach votes. Neither observes a specific skill or job.
- Each receipt carries the E1 fields: stable gsis `player_id`, source locator(s), public (announcement) date, observation scope (the whole regular season named), observation type `expert_judgement`, confidence, contamination notes, branch cutoff 2013-01-15 and an admissibility flag.
- No 2013-or-later honour, result, statistic or career outcome was read. Later-season search hits were used by the research passes only to reject misdated claims (see the season notes).
- A missing honour is **not** evidence of anything. Players without an honour stay Average and low-confidence under the tier rule.

## Identity matching

All 480 entries matched a single gsis `player_id` (0 unmatched, 0 ambiguous). 478 matched on the same-season nflverse roster of the club named in the entry; Matthew Slater (2011 and 2012, NE special teamer) matched through `players.csv` by name because the season roster lists him under another first-name form. "Michael Vick" matches nflverse "Mike Vick" (PHI, 2010) on the club roster.

## Verification labels

Labels are carried from the research and verification passes, not re-judged here:

| Block | Label | Basis in the season notes |
|---|---|---|
| 2010 AP All-Pro | Confirmed two-pass | Re-searched in the verification pass (vote counts V2, release texts V1). 23 of 61 entries have no second-pass key attached; they are labelled two-pass on the verifier's block treatment and the per-entry `verification_basis` says so. |
| 2011 AP All-Pro | Confirmed two-pass, except 11 entries | Notes: all 57 re-checked, none changed; but 1st-team G Nicks/Evans, T Peters/Thomas, P Lee, FB Leach and 2nd-team FB Kuhn, TE Graham, G Yanda/Mankins, P Lechler were not independently re-checked: those 11 are **Single-pass**. |
| 2012 AP All-Pro | Confirmed two-pass | Notes: "Treat the AP All-Pro entries as verified" (PR-slot question still open; no PR entry exists). |
| 2010 / 2011 Pro Bowl originals | Two-pass only where a verification key (V*) is attached or the notes name the player as corroborated | Otherwise Single-pass. |
| 2012 Pro Bowl originals and replacements | Single-pass | Notes: not re-checked (search budget exhausted). |
| Alternates/replacements (all seasons) | as above | No tier effect in any use (see the calibration note). |

Counts (Confirmed two-pass / Single-pass):

| Season | AP 1st team | AP 2nd team | Pro Bowl original | Alternate/replacement |
|---|---|---|---|---|
| 2010 | 27 / 0 | 34 / 0 | 32 / 52 | 2 / 16 |
| 2011 | 22 / 6 | 24 / 5 | 15 / 69 | 20 / 5 |
| 2012 | 27 / 0 | 29 / 0 | 0 / 84 | 0 / 11 |

Entry-level weakness flags carried from the research text: Tyson Clabo 2010 replacement (reason/date not verified), Ryan Mathews 2011 replacement (single search summary), LaRon Landry 2012 Pro Bowl (UNCONFIRMED), Thomas Morstead and Leon Washington 2012 Pro Bowl (thinly sourced), Marcel Reece 2012 replacement (weakly sourced). These receipts carry confidence `low`.

## Public dates

| List | Public date | Locator | Confidence |
|---|---|---|---|
| 2010 AP All-Pro | 2011-01-24 | boston.com 'Tom Brady unanimous selection to AP NFL All-Pro team' (/2011/01/24/) and Deseret News 2011-01-24; earliest dated article found, single search | medium |
| 2011 AP All-Pro | 2012-01-06 | Victoria Advocate '2011 All-Pro Team' dated 2012-01-06 ('announced Friday'); single search | medium |
| 2012 AP All-Pro | 2013-01-12 | NFL.com 'All-Pro Team headlined by Adrian Peterson, J.J. Watt' / Wikipedia '2012 All-Pro Team' search summary; single search | medium |
| 2010 Pro Bowl original selections | 2010-12-28 | PFT/NBC 'Tom Brady, Michael Vick lead 2011 Pro Bowl rosters' search summary | medium |
| 2011 Pro Bowl original selections | 2011-12-27 | honours verification notes 2011 V10 ('announced 2011-12-27') | medium |
| 2012 Pro Bowl original selections | 2012-12-26 | House of Sparky 'AFC Pro Bowl roster 2013' (/2012/12/26/) search result | medium |

Each date was located in one search on September 29, 2026 and has not had a second independent pass. The 2010 AP date is the earliest dated article found and could be later than the actual release. All six dates precede the divergence. Replacement/alternate announcements are **not** individually dated: they fall between the original announcement and the game (January 30, 2011; January 29, 2012; January 27, 2013). The 2012-season replacements may post-date the January 15, 2013 divergence, so every replacement receipt is marked inadmissible (`admissible_pre_divergence: false`, 54 receipts).

## Known gaps a human must close

1. **Research-pass source keys are undefined in the input.** Keys A1-A7, P1-P9, R1-R8 (2010, 2012) and AP1-AP6, PB1-PB9, R1-R7 (2011) are referenced by entries, but the verified file carries only the verification-pass definitions (V*, and 2011 R8). Those receipts' `source_locator` says "research-pass key; definition not carried in the verified input". The research-pass key table must be recovered or re-derived before these locators are complete.
2. **2012 Pro Bowl list: second pass done (September 30, 2026).** 82 of the 84 originals were named in the same conference and position by search summaries of a second source set (Bleacher Report's AFC/NFC "Complete Selections" articles, NFL.com's roster analyses, CBS Sports' announcement; page fetches are blocked by the session proxy, so these are search-result summaries) and move to Confirmed two-pass (weight 1.0), LaRon Landry's UNCONFIRMED flag cleared (listed as the AFC reserve strong safety). Two are **contradicted**: the file's AFC kicker (Sebastian Janikowski) and punter (Shane Lechler) entries for the 2012 season, where the second-pass sources name Phil Dawson (CLE) and Dustin Colquitt (KC). Those two entries are flagged `CONTRADICTED second pass`, left Single-pass at low confidence and not removed; they are specialist honours and never enter a composite. Andrew Luck, Demaryius Thomas, Jermaine Gresham, Owen Daniels, Drew Brees, Eli Manning and Russell Wilson appear in the second-pass sources only as replacements, consistent with the file. Counts after the pass: 314 Confirmed two-pass, 166 Single-pass.
3. **Replacement lists are incomplete** (per the notes) — irrelevant to tiers, since replacements carry no effect.
4. **Public dates: second pass done (September 30, 2026).** All six announcement dates were confirmed by a second source set in search summaries (ESPN, CBS Boston and patriots.com for the 2010 AP list; Bleacher Report and patriots.com for 2011 AP; Behind the Steel Curtain and ESPN for 2012 AP; ESPN and PFT for the 2010 Pro Bowl; Bleacher Report and WTHR for 2011; CBS Sports, Arrowhead Addict and NFL.com for 2012). The `public_dates` block in the JSON carries each second-pass locator.

## Entries

Honour kinds: AP1 = AP All-Pro 1st team, AP2 = 2nd team, PB = original Pro Bowl selection, ALT = alternate/replacement. Verification: 2P = Confirmed two-pass, 1P = Single-pass.

### 2010 season

| Player | gsis player_id | Club | Pos | Honour | Ver. | Sources |
|---|---|---|---|---|---|---|
| Tom Brady | 00-0019596 | NE | QB | AP1 | 2P | A1, A3, V1 |
| Arian Foster | 00-0026796 | HOU | RB | AP1 | 2P | A1, A4, V2 |
| Jamaal Charles | 00-0026213 | KC | RB | AP1 | 2P | A1, A4, V2 |
| Vonta Leach | 00-0022397 | HOU | FB | AP1 | 2P | A1, A5 |
| Roddy White | 00-0023462 | ATL | WR | AP1 | 2P | A1, A4 |
| Reggie Wayne | 00-0020498 | IND | WR | AP1 | 2P | A1, A4 |
| Jason Witten | 00-0022127 | DAL | TE | AP1 | 2P | A1, A4, V1 |
| Jake Long | 00-0025820 | MIA | T | AP1 | 2P | A1, A4 |
| Joe Thomas | 00-0025390 | CLE | T | AP1 | 2P | A1, A4 |
| Logan Mankins | 00-0023467 | NE | G | AP1 | 2P | A1, A3 |
| Jahri Evans | 00-0024323 | NO | G | AP1 | 2P | A1, A6 |
| Nick Mangold | 00-0024244 | NYJ | C | AP1 | 2P | A1, A4 |
| Julius Peppers | 00-0021140 | CHI | DE | AP1 | 2P | A1, A2, V2 |
| John Abraham | 00-0019546 | ATL | DE | AP1 | 2P | A1, A2, V2 |
| Haloti Ngata | 00-0024227 | BAL | DT | AP1 | 2P | A1, A4 |
| Ndamukong Suh | 00-0027855 | DET | DT | AP1 | 2P | A1, A4 |
| Clay Matthews | 00-0027002 | GB | OLB | AP1 | 2P | A1, A2, V2 |
| James Harrison | 00-0020712 | PIT | OLB | AP1 | 2P | A1, A2, A7, V2 |
| Patrick Willis | 00-0025398 | SF | ILB | AP1 | 2P | A1, A2, V2 |
| Jerod Mayo | 00-0026150 | NE | ILB | AP1 | 2P | A3, V2 |
| Nnamdi Asomugha | 00-0022077 | OAK | CB | AP1 | 2P | A1, A2 |
| Darrelle Revis | 00-0025401 | NYJ | CB | AP1 | 2P | A1, A2 |
| Troy Polamalu | 00-0022119 | PIT | S | AP1 | 2P | A1, A2, A7, V2 |
| Ed Reed | 00-0021377 | BAL | S | AP1 | 2P | A1, A2, V2 |
| Billy Cundiff | 00-0020972 | BAL | K | AP1 | 2P | A1, A4, V1 |
| Shane Lechler | 00-0019714 | OAK | P | AP1 | 2P | A1, A4, V1 |
| Devin Hester | 00-0024272 | CHI | KR | AP1 | 2P | A1, A4, V1 |
| Michael Turner | 00-0022821 | ATL | RB | AP2 | 2P | A1, A4, V2 |
| Adrian Peterson | 00-0025394 | MIN | RB | AP2 | 2P | A1, A4, V2 |
| Ovie Mughelli | 00-0022143 | ATL | FB | AP2 | 2P | A1, A4 |
| Brandon Lloyd | 00-0022097 | DEN | WR | AP2 | 2P | A1, A4 |
| Calvin Johnson | 00-0025389 | DET | WR | AP2 | 2P | A1, A4 |
| Dwayne Bowe | 00-0025410 | KC | WR | AP2 | 2P | A1, A4 |
| Antonio Gates | 00-0021547 | SD | TE | AP2 | 2P | A1, A4, V1 |
| Jason Peters | 00-0022531 | PHI | T | AP2 | 2P | A1, A4 |
| Sebastian Vollmer | 00-0027034 | NE | T | AP2 | 2P | A1, A4 |
| Chris Snee | 00-0022838 | NYG | G | AP2 | 2P | A1, A4 |
| Carl Nicks | 00-0026304 | NO | G | AP2 | 2P | A1, A6 |
| Maurkice Pouncey | 00-0027870 | PIT | C | AP2 | 2P | A1, A7 |
| Justin Tuck | 00-0023509 | NYG | DE | AP2 | 2P | A1, A4, V2 |
| Osi Umenyiora | 00-0021977 | NYG | DE | AP2 | 2P | A1, A4, V2 |
| Kyle Williams | 00-0024348 | BUF | DT | AP2 | 2P | A1, A4 |
| Vince Wilfork | 00-0022712 | NE | DT | AP2 | 2P | A1, A4, V2 |
| DeMarcus Ware | 00-0023445 | DAL | OLB | AP2 | 2P | A1, A2, V2 |
| Cameron Wake | 00-0023368 | MIA | OLB | AP2 | 2P | A1, A4, V2 |
| Brian Urlacher | 00-0019456 | CHI | ILB | AP2 | 2P | A1, A4, V2 |
| Ray Lewis | 00-0009889 | BAL | ILB | AP2 | 2P | A1, A4, V2 |
| Devin McCourty | 00-0027647 | NE | CB | AP2 | 2P | A1, A4 |
| Charles Woodson | 00-0018227 | GB | CB | AP2 | 2P | A1, A4, V2 |
| Nick Collins | 00-0023486 | GB | S | AP2 | 2P | A1, A2, V2 |
| Antrel Rolle | 00-0023443 | NYG | S | AP2 | 2P | A2, A4, V2 |
| Eric Weddle | 00-0025424 | SD | S | AP2 | 2P | A2, A4, V2 |
| Malcolm Jenkins | 00-0026990 | NO | S | AP2 | 2P | A2, A6, V2 |
| Quintin Mikell | 00-0021512 | PHI | S | AP2 | 2P | A2, A4, V2 |
| Chris Harris | 00-0023614 | CHI | S | AP2 | 2P | A2, A4, V2 |
| Michael Huff | 00-0024222 | OAK | S | AP2 | 2P | A2, A4, V2 |
| Michael Griffin | 00-0025406 | TEN | S | AP2 | 2P | A2, A4, V2 |
| Darren Sharper | 00-0014724 | NO | S | AP2 | 2P | A2, A6, V2 |
| David Akers | 00-0000108 | PHI | K | AP2 | 2P | A1, A4, V2 |
| Mat McBriar | 00-0021488 | DAL | P | AP2 | 2P | A1, A4, V1 |
| Leon Washington | 00-0024332 | SEA | KR | AP2 | 2P | A1, A4, V1 |
| Tom Brady | 00-0019596 | NE | QB | PB | 1P | P1, P2, P3 |
| Philip Rivers | 00-0022942 | SD | QB | PB | 1P | P1, P2 |
| Peyton Manning | 00-0010346 | IND | QB | PB | 1P | P1, P2 |
| Maurice Jones-Drew | 00-0024275 | JAX | RB | PB | 1P | P1, P2 |
| Arian Foster | 00-0026796 | HOU | RB | PB | 1P | P1 |
| Jamaal Charles | 00-0026213 | KC | RB | PB | 1P | P1 |
| Vonta Leach | 00-0022397 | HOU | FB | PB | 1P | P1 |
| Andre Johnson | 00-0022044 | HOU | WR | PB | 1P | P1, P2 |
| Reggie Wayne | 00-0020498 | IND | WR | PB | 1P | P1, P2 |
| Brandon Lloyd | 00-0022097 | DEN | WR | PB | 1P | P1 |
| Dwayne Bowe | 00-0025410 | KC | WR | PB | 1P | P1 |
| Antonio Gates | 00-0021547 | SD | TE | PB | 1P | P1 |
| Marcedes Lewis | 00-0024243 | JAX | TE | PB | 1P | P1 |
| Nick Mangold | 00-0024244 | NYJ | C | PB | 1P | P1 |
| Maurkice Pouncey | 00-0027870 | PIT | C | PB | 2P | P1, V5 |
| Kris Dielman | 00-0021546 | SD | G | PB | 1P | P1 |
| Logan Mankins | 00-0023467 | NE | G | PB | 1P | P1 |
| Brian Waters | 00-0018584 | KC | G | PB | 1P | P1 |
| Jake Long | 00-0025820 | MIA | T | PB | 1P | P1 |
| Joe Thomas | 00-0025390 | CLE | T | PB | 1P | P1 |
| D'Brickashaw Ferguson | 00-0024219 | NYJ | T | PB | 1P | P1 |
| Dwight Freeney | 00-0021146 | IND | DE | PB | 1P | P1, R1 |
| Robert Mathis | 00-0022059 | IND | DE | PB | 1P | P1 |
| Jason Babin | 00-0022695 | TEN | DE | PB | 1P | P1 |
| Haloti Ngata | 00-0024227 | BAL | DT | PB | 1P | P1 |
| Vince Wilfork | 00-0022712 | NE | DT | PB | 1P | P1 |
| Richard Seymour | 00-0020442 | OAK | DT | PB | 1P | P1, R2 |
| Ray Lewis | 00-0009889 | BAL | ILB | PB | 1P | P1 |
| Jerod Mayo | 00-0026150 | NE | ILB | PB | 1P | P1 |
| James Harrison | 00-0020712 | PIT | OLB | PB | 2P | P1, V5 |
| Cameron Wake | 00-0023368 | MIA | OLB | PB | 1P | P1 |
| Terrell Suggs | 00-0022161 | BAL | OLB | PB | 1P | P1 |
| Nnamdi Asomugha | 00-0022077 | OAK | CB | PB | 1P | P1 |
| Darrelle Revis | 00-0025401 | NYJ | CB | PB | 1P | P1 |
| Devin McCourty | 00-0027647 | NE | CB | PB | 1P | P1 |
| Troy Polamalu | 00-0022119 | PIT | SS | PB | 2P | P1, V5 |
| Ed Reed | 00-0021377 | BAL | FS | PB | 1P | P1 |
| Brandon Meriweather | 00-0025411 | NE | FS | PB | 1P | P1 |
| Shane Lechler | 00-0019714 | OAK | P | PB | 1P | P1 |
| Marc Mariani | 00-0027816 | TEN | KR | PB | 1P | P1 |
| Billy Cundiff | 00-0020972 | BAL | K | PB | 1P | P1 |
| Montell Owens | 00-0024103 | JAX | ST | PB | 1P | P1 |
| Michael Vick | 00-0020245 | PHI | QB | PB | 2P | P2, P4, V3 |
| Matt Ryan | 00-0026143 | ATL | QB | PB | 2P | P2, P4, V3 |
| Drew Brees | 00-0020531 | NO | QB | PB | 2P | P2, P4, V3 |
| Michael Turner | 00-0022821 | ATL | RB | PB | 2P | P2, P4, V3 |
| Adrian Peterson | 00-0025394 | MIN | RB | PB | 1P | P2, P4 |
| Steven Jackson | 00-0022736 | STL | RB | PB | 1P | P2, P4 |
| Ovie Mughelli | 00-0022143 | ATL | FB | PB | 1P | P4, P5 |
| Roddy White | 00-0023462 | ATL | WR | PB | 2P | P2, P4, V3 |
| Calvin Johnson | 00-0025389 | DET | WR | PB | 2P | P2, P4, V3 |
| Greg Jennings | 00-0024267 | GB | WR | PB | 1P | P2, R3 |
| DeSean Jackson | 00-0026189 | PHI | WR | PB | 1P | P2 |
| Jason Witten | 00-0022127 | DAL | TE | PB | 1P | P2, P4 |
| Tony Gonzalez | 00-0006101 | ATL | TE | PB | 1P | P2, P4, P5 |
| Andre Gurode | 00-0021385 | DAL | C | PB | 2P | P2, P4, V4 |
| Shaun O'Hara | 00-0019276 | NYG | C | PB | 2P | P2, V6 |
| Jahri Evans | 00-0024323 | NO | G | PB | 2P | P2, V4 |
| Chris Snee | 00-0022838 | NYG | G | PB | 2P | P2, V4 |
| Carl Nicks | 00-0026304 | NO | G | PB | 1P | P2 |
| Jason Peters | 00-0022531 | PHI | T | PB | 2P | P2, R6, V4 |
| Chad Clifton | 00-0019702 | GB | T | PB | 1P | P2, R3 |
| Jordan Gross | 00-0022117 | CAR | T | PB | 2P | P2, V4 |
| Julius Peppers | 00-0021140 | CHI | DE | PB | 2P | P2, V7 |
| John Abraham | 00-0019546 | ATL | DE | PB | 2P | P2, P5, V7 |
| Justin Tuck | 00-0023509 | NYG | DE | PB | 2P | P2, V7 |
| Ndamukong Suh | 00-0027855 | DET | DT | PB | 2P | P2, V3, V7 |
| Jay Ratliff | 00-0023656 | DAL | DT | PB | 2P | P2, V7 |
| Justin Smith | 00-0020535 | SF | DT | PB | 2P | P2, V7 |
| Clay Matthews | 00-0027002 | GB | OLB | PB | 2P | P2, R3, V7 |
| DeMarcus Ware | 00-0023445 | DAL | OLB | PB | 2P | P2, V7 |
| Lance Briggs | 00-0022128 | CHI | OLB | PB | 2P | P2, R4, V7 |
| Patrick Willis | 00-0025398 | SF | ILB | PB | 2P | P2, V7 |
| Brian Urlacher | 00-0019456 | CHI | ILB | PB | 2P | P2, R4, V7 |
| Asante Samuel | 00-0021956 | PHI | CB | PB | 2P | P6, V7 |
| Charles Woodson | 00-0018227 | GB | CB | PB | 2P | P6, R3, V7 |
| DeAngelo Hall | 00-0022923 | WAS | CB | PB | 2P | P6, V7 |
| Adrian Wilson | 00-0020505 | ARI | SS | PB | 2P | P6, V7 |
| Nick Collins | 00-0023486 | GB | FS | PB | 2P | P6, R3, V7 |
| Antrel Rolle | 00-0023443 | NYG | FS | PB | 2P | P6, V7 |
| David Akers | 00-0000108 | PHI | K | PB | 1P | P6 |
| Mat McBriar | 00-0021488 | DAL | P | PB | 1P | P6 |
| Devin Hester | 00-0024272 | CHI | KR | PB | 1P | P6 |
| Eric Weems | 00-0024535 | ATL | ST | PB | 1P | P5, P6 |
| Brett Keisel | 00-0021344 | PIT | DE | ALT | 2P | R1, V5 |
| Kyle Williams | 00-0024348 | BUF | DT | ALT | 1P | R2 |
| Matt Cassel | 00-0023662 | KC | QB | ALT | 1P | R5 |
| Tamba Hali | 00-0024235 | KC | OLB | ALT | 1P | R3 |
| Eric Berry | 00-0027858 | KC | S | ALT | 1P | R3 |
| Randy Starks | 00-0022805 | MIA | DL | ALT | 1P | R3 |
| Alex Mack | 00-0026997 | CLE | C | ALT | 1P | R4 |
| Jeff Saturday | 00-0014375 | IND | C | ALT | 2P | R7, V8 |
| Tramon Williams | 00-0024061 | GB | CB | ALT | 1P | R8 |
| Antoine Winfield | 00-0018093 | MIN | CB | ALT | 1P | R3 |
| Brent Grimes | 00-0024183 | ATL | CB | ALT | 1P | R3, P5 |
| Roman Harper | 00-0024258 | NO | S | ALT | 1P | R3 |
| Brian Orakpo | 00-0026989 | WAS | OLB | ALT | 1P | R3, R4 |
| Donald Penn | 00-0023894 | TB | T | ALT | 1P | R3 |
| Larry Fitzgerald | 00-0022921 | ARI | WR | ALT | 1P | R3 |
| London Fletcher | 00-0005322 | WAS | ILB | ALT | 1P | R3, R4 |
| Jon Beason | 00-0025412 | CAR | LB | ALT | 1P | R3, R4 |
| Tyson Clabo | 00-0022245 | ATL | T | ALT | 1P | R6, P5 |

### 2011 season

| Player | gsis player_id | Club | Pos | Honour | Ver. | Sources |
|---|---|---|---|---|---|---|
| Aaron Rodgers | 00-0023459 | GB | QB | AP1 | 2P | AP1, AP3 |
| Maurice Jones-Drew | 00-0024275 | JAX | RB | AP1 | 2P | AP1, AP3, AP5, V2 |
| LeSean McCoy | 00-0027029 | PHI | RB | AP1 | 2P | AP1, AP3, V2 |
| Vonta Leach | 00-0022397 | BAL | FB | AP1 | 1P | AP1, AP3 |
| Wes Welker | 00-0022427 | NE | WR | AP1 | 2P | AP1, AP3 |
| Calvin Johnson | 00-0025389 | DET | WR | AP1 | 2P | AP2, AP3 |
| Rob Gronkowski | 00-0027656 | NE | TE | AP1 | 2P | AP1, AP3 |
| Jason Peters | 00-0022531 | PHI | T | AP1 | 1P | AP4, AP1 |
| Joe Thomas | 00-0025390 | CLE | T | AP1 | 1P | AP4, AP1 |
| Carl Nicks | 00-0026304 | NO | G | AP1 | 1P | AP4 |
| Jahri Evans | 00-0024323 | NO | G | AP1 | 1P | AP4 |
| Maurkice Pouncey | 00-0027870 | PIT | C | AP1 | 2P | AP4, AP1, V1 |
| Jared Allen | 00-0022740 | MIN | DE | AP1 | 2P | AP2, AP3 |
| Jason Pierre-Paul | 00-0027867 | NYG | DE | AP1 | 2P | AP1, AP3 |
| Justin Smith | 00-0020535 | SF | DT | AP1 | 2P | AP1, AP6 |
| Haloti Ngata | 00-0024227 | BAL | DT | AP1 | 2P | AP1, AP3 |
| DeMarcus Ware | 00-0023445 | DAL | OLB | AP1 | 2P | AP2, AP1 |
| Terrell Suggs | 00-0022161 | BAL | OLB | AP1 | 2P | AP2, AP1 |
| Patrick Willis | 00-0025398 | SF | ILB | AP1 | 2P | AP2, AP1 |
| NaVorro Bowman | 00-0027894 | SF | ILB | AP1 | 2P | AP2 |
| Derrick Johnson | 00-0023449 | KC | ILB | AP1 | 2P | AP2 |
| Charles Woodson | 00-0018227 | GB | CB | AP1 | 2P | AP1, AP3 |
| Darrelle Revis | 00-0025401 | NYJ | CB | AP1 | 2P | AP1, AP3 |
| Troy Polamalu | 00-0022119 | PIT | S | AP1 | 2P | AP1, AP3 |
| Eric Weddle | 00-0025424 | SD | S | AP1 | 2P | AP5, AP1 |
| David Akers | 00-0000108 | SF | K | AP1 | 2P | AP1, V1 |
| Andy Lee | 00-0022824 | SF | P | AP1 | 1P | AP1 |
| Patrick Peterson | 00-0027943 | ARI | KR | AP1 | 2P | AP1, AP3 |
| Drew Brees | 00-0020531 | NO | QB | AP2 | 2P | AP4, AP1 |
| Arian Foster | 00-0026796 | HOU | RB | AP2 | 2P | AP1, AP3, V2, V4 |
| Ray Rice | 00-0026195 | BAL | RB | AP2 | 2P | AP1, AP3, V2 |
| John Kuhn | 00-0022999 | GB | FB | AP2 | 1P | AP1, AP3 |
| Larry Fitzgerald | 00-0022921 | ARI | WR | AP2 | 2P | AP1, AP3, V3 |
| Victor Cruz | 00-0027265 | NYG | WR | AP2 | 2P | AP1, AP3, V3 |
| Jimmy Graham | 00-0027696 | NO | TE | AP2 | 1P | AP4, AP1 |
| Duane Brown | 00-0026166 | HOU | T | AP2 | 2P | AP4, AP1, V4 |
| Joe Staley | 00-0025415 | SF | T | AP2 | 2P | AP4, AP1, V4 |
| Marshal Yanda | 00-0025473 | BAL | G | AP2 | 1P | AP4, AP1 |
| Logan Mankins | 00-0023467 | NE | G | AP2 | 1P | AP4, AP1 |
| Ryan Kalil | 00-0025446 | CAR | C | AP2 | 2P | AP4, AP1, V1 |
| Nick Mangold | 00-0024244 | NYJ | C | AP2 | 2P | AP4, AP1, V1 |
| Jason Babin | 00-0022695 | PHI | DE | AP2 | 2P | AP1, AP3, V3 |
| Justin Smith | 00-0020535 | SF | DE | AP2 | 2P | AP1, AP6 |
| Geno Atkins | 00-0027720 | CIN | DT | AP2 | 2P | AP1, AP3, V4 |
| Richard Seymour | 00-0020442 | OAK | DT | AP2 | 2P | AP1, AP3, V4 |
| Vince Wilfork | 00-0022712 | NE | DT | AP2 | 2P | AP1, AP3, V4 |
| Tamba Hali | 00-0024235 | KC | OLB | AP2 | 2P | AP1, V5 |
| Von Miller | 00-0027940 | DEN | OLB | AP2 | 2P | AP1, V5 |
| Brian Cushing | 00-0026991 | HOU | ILB | AP2 | 2P | AP1, AP3, V5, V4 |
| London Fletcher | 00-0005322 | WAS | ILB | AP2 | 2P | AP1, AP3, V5 |
| Johnathan Joseph | 00-0024239 | HOU | CB | AP2 | 2P | AP1, AP3, V3, V4 |
| Carlos Rogers | 00-0023444 | SF | CB | AP2 | 2P | AP1, AP3, V3 |
| Ed Reed | 00-0021377 | BAL | S | AP2 | 2P | AP1, AP3, V4 |
| Earl Thomas | 00-0027866 | SEA | S | AP2 | 2P | AP1, AP3, V4 |
| Sebastian Janikowski | 00-0019646 | OAK | K | AP2 | 2P | AP1, V1 |
| Shane Lechler | 00-0019714 | OAK | P | AP2 | 1P | AP1 |
| Devin Hester | 00-0024272 | CHI | KR | AP2 | 2P | AP1, AP3, V3 |
| Tom Brady | 00-0019596 | NE | QB | PB | 1P | PB1, PB2, PB3 |
| Ben Roethlisberger | 00-0022924 | PIT | QB | PB | 2P | PB1, PB4, V6 |
| Philip Rivers | 00-0022942 | SD | QB | PB | 2P | PB1, V6 |
| Ray Rice | 00-0026195 | BAL | RB | PB | 1P | PB1 |
| Maurice Jones-Drew | 00-0024275 | JAX | RB | PB | 1P | PB1 |
| Arian Foster | 00-0026796 | HOU | RB | PB | 1P | PB1, PB8 |
| Vonta Leach | 00-0022397 | BAL | FB | PB | 1P | PB5 |
| Wes Welker | 00-0022427 | NE | WR | PB | 1P | PB3, PB5 |
| Mike Wallace | 00-0026901 | PIT | WR | PB | 1P | PB3, PB4 |
| A.J. Green | 00-0027942 | CIN | WR | PB | 1P | PB3, PB5 |
| Brandon Marshall | 00-0024334 | MIA | WR | PB | 2P | PB3, PB5, V7 |
| Rob Gronkowski | 00-0027656 | NE | TE | PB | 1P | PB5, PB2 |
| Antonio Gates | 00-0021547 | SD | TE | PB | 1P | PB5 |
| Joe Thomas | 00-0025390 | CLE | T | PB | 1P | PB5 |
| Jake Long | 00-0025820 | MIA | T | PB | 1P | PB5, PB3 |
| D'Brickashaw Ferguson | 00-0024219 | NYJ | T | PB | 1P | PB5 |
| Logan Mankins | 00-0023467 | NE | G | PB | 1P | PB5, PB2 |
| Brian Waters | 00-0018584 | NE | G | PB | 1P | PB5, PB2 |
| Marshal Yanda | 00-0025473 | BAL | G | PB | 1P | PB5 |
| Maurkice Pouncey | 00-0027870 | PIT | C | PB | 1P | PB5, PB4 |
| Nick Mangold | 00-0024244 | NYJ | C | PB | 1P | PB5 |
| Dwight Freeney | 00-0021146 | IND | DE | PB | 1P | PB3, PB5 |
| Andre Carter | 00-0020489 | NE | DE | PB | 1P | PB3, PB5, PB2 |
| Elvis Dumervil | 00-0024341 | DEN | DE | PB | 1P | PB3, PB5 |
| Haloti Ngata | 00-0024227 | BAL | DT | PB | 1P | PB5 |
| Vince Wilfork | 00-0022712 | NE | DT | PB | 1P | PB5, PB2 |
| Richard Seymour | 00-0020442 | OAK | DT | PB | 1P | PB5, PB9 |
| Terrell Suggs | 00-0022161 | BAL | OLB | PB | 1P | PB5 |
| Von Miller | 00-0027940 | DEN | OLB | PB | 1P | PB5 |
| Tamba Hali | 00-0024235 | KC | OLB | PB | 1P | PB5 |
| Ray Lewis | 00-0009889 | BAL | ILB | PB | 2P | PB5, V8 |
| Derrick Johnson | 00-0023449 | KC | ILB | PB | 2P | PB5, V8 |
| Darrelle Revis | 00-0025401 | NYJ | CB | PB | 1P | PB5 |
| Champ Bailey | 00-0000585 | DEN | CB | PB | 2P | PB5, V8 |
| Johnathan Joseph | 00-0024239 | HOU | CB | PB | 1P | PB5, PB8, R4 |
| Ed Reed | 00-0021377 | BAL | FS | PB | 1P | PB5, R3 |
| Eric Weddle | 00-0025424 | SD | FS | PB | 1P | PB5 |
| Troy Polamalu | 00-0022119 | PIT | SS | PB | 1P | PB5, PB4 |
| Shane Lechler | 00-0019714 | OAK | P | PB | 1P | PB5, PB9 |
| Sebastian Janikowski | 00-0019646 | OAK | K | PB | 1P | PB5, PB9 |
| Antonio Brown | 00-0027793 | PIT | KR | PB | 1P | PB5, PB4 |
| Matthew Slater | 00-0026293 | NE | ST | PB | 1P | PB5, PB2 |
| Aaron Rodgers | 00-0023459 | GB | QB | PB | 2P | PB1, V6 |
| Drew Brees | 00-0020531 | NO | QB | PB | 2P | PB1, V6 |
| Eli Manning | 00-0022803 | NYG | QB | PB | 1P | PB1, R1 |
| LeSean McCoy | 00-0027029 | PHI | RB | PB | 1P | PB1 |
| Matt Forte | 00-0026184 | CHI | RB | PB | 1P | PB1 |
| Frank Gore | 00-0023500 | SF | RB | PB | 1P | PB1, PB6 |
| John Kuhn | 00-0022999 | GB | FB | PB | 1P | PB5 |
| Calvin Johnson | 00-0025389 | DET | WR | PB | 1P | PB5 |
| Larry Fitzgerald | 00-0022921 | ARI | WR | PB | 1P | PB5 |
| Steve Smith | 00-0020337 | CAR | WR | PB | 1P | PB5 |
| Greg Jennings | 00-0024267 | GB | WR | PB | 1P | PB5 |
| Jimmy Graham | 00-0027696 | NO | TE | PB | 1P | PB5 |
| Tony Gonzalez | 00-0006101 | ATL | TE | PB | 2P | PB5, V9 |
| Jason Peters | 00-0022531 | PHI | T | PB | 1P | PB5 |
| Joe Staley | 00-0025415 | SF | T | PB | 1P | PB5, PB6 |
| Jermon Bushrod | 00-0025512 | NO | T | PB | 1P | PB5 |
| Jahri Evans | 00-0024323 | NO | G | PB | 1P | PB5, PB7 |
| Carl Nicks | 00-0026304 | NO | G | PB | 1P | PB5, PB7 |
| Davin Joseph | 00-0024238 | TB | G | PB | 2P | PB7, V8 |
| Ryan Kalil | 00-0025446 | CAR | C | PB | 2P | PB5, V8 |
| Scott Wells | 00-0022832 | GB | C | PB | 2P | PB5, V8 |
| Jared Allen | 00-0022740 | MIN | DE | PB | 1P | PB5 |
| Jason Babin | 00-0022695 | PHI | DE | PB | 1P | PB5 |
| Jason Pierre-Paul | 00-0027867 | NYG | DE | PB | 1P | PB5, R1 |
| Justin Smith | 00-0020535 | SF | DT | PB | 1P | PB5, PB6 |
| Jay Ratliff | 00-0023656 | DAL | DT | PB | 1P | PB5 |
| B.J. Raji | 00-0026985 | GB | DT | PB | 1P | PB5 |
| DeMarcus Ware | 00-0023445 | DAL | OLB | PB | 2P | PB5, V10 |
| Clay Matthews | 00-0027002 | GB | OLB | PB | 2P | PB5, V10 |
| Lance Briggs | 00-0022128 | CHI | OLB | PB | 2P | PB5, V10 |
| Patrick Willis | 00-0025398 | SF | ILB | PB | 1P | PB5, PB6 |
| Brian Urlacher | 00-0019456 | CHI | ILB | PB | 1P | PB5, R2 |
| Charles Woodson | 00-0018227 | GB | CB | PB | 1P | PB5 |
| Carlos Rogers | 00-0023444 | SF | CB | PB | 1P | PB5, PB6 |
| Charles Tillman | 00-0022123 | CHI | CB | PB | 1P | PB5 |
| Earl Thomas | 00-0027866 | SEA | FS | PB | 1P | PB5 |
| Dashon Goldson | 00-0025513 | SF | FS | PB | 1P | PB5, PB6 |
| Adrian Wilson | 00-0020505 | ARI | SS | PB | 1P | PB5 |
| Andy Lee | 00-0022824 | SF | P | PB | 1P | PB5, PB6 |
| David Akers | 00-0000108 | SF | K | PB | 1P | PB5, PB6 |
| Patrick Peterson | 00-0027943 | ARI | KR | PB | 1P | PB1 |
| Corey Graham | 00-0025555 | CHI | ST | PB | 1P | PB1 |
| Andy Dalton | 00-0027973 | CIN | QB | ALT | 1P | R1, R8 |
| Vincent Jackson | 00-0023496 | SD | WR | ALT | 2P | R1, V11 |
| Jermaine Gresham | 00-0027873 | CIN | TE | ALT | 2P | R1, V11 |
| Brandon Moore | 00-0020969 | NYJ | G | ALT | 2P | R1, V11 |
| Ben Grubbs | 00-0025416 | BAL | G | ALT | 2P | R1, V11 |
| Geno Atkins | 00-0027720 | CIN | DT | ALT | 2P | R1, V12 |
| Montell Owens | 00-0024103 | JAX | ST | ALT | 2P | R1, V11 |
| Antonio Smith | 00-0022793 | HOU | DE | ALT | 2P | R4, PB2, V13 |
| Chris Myers | 00-0023633 | HOU | C | ALT | 2P | R4, V13 |
| Ryan Clady | 00-0026152 | DEN | T | ALT | 2P | PB2, V14 |
| Willis McGahee | 00-0022178 | DEN | RB | ALT | 2P | V14 |
| Ryan Mathews | 00-0027864 | SD | RB | ALT | 2P | V15 |
| Paul Soliai | 00-0025495 | MIA | DT | ALT | 2P | V16 |
| Brian Dawkins | 00-0004073 | DEN | SS | ALT | 2P | V17 |
| Ryan Clark | 00-0020840 | PIT | FS | ALT | 2P | R3, V18 |
| Jon Condo | 00-0023177 | OAK | LS | ALT | 1P | R1 |
| Cam Newton | 00-0027939 | CAR | QB | ALT | 1P | R1, R5, R8 |
| Julius Peppers | 00-0021140 | CHI | DE | ALT | 1P | R1, R6 |
| Brandon Browner | 00-0023013 | SEA | CB | ALT | 2P | R7, V19 |
| London Fletcher | 00-0005322 | WAS | ILB | ALT | 2P | R2, V20, V21 |
| Chad Greenway | 00-0024232 | MIN | OLB | ALT | 2P | V20 |
| Roddy White | 00-0023462 | ATL | WR | ALT | 2P | R2, V9 |
| Michael Robinson | 00-0024315 | SEA | FB | ALT | 2P | R2, V13, V22 |
| Kam Chancellor | 00-0027733 | SEA | S | ALT | 2P | R2, V23 |
| Brian Jennings | 00-0019548 | SF | LS | ALT | 1P | R1 |

### 2012 season

| Player | gsis player_id | Club | Pos | Honour | Ver. | Sources |
|---|---|---|---|---|---|---|
| Peyton Manning | 00-0010346 | DEN | QB | AP1 | 2P | A1, A2, V1 |
| Adrian Peterson | 00-0025394 | MIN | RB | AP1 | 2P | A1, A2 |
| Marshawn Lynch | 00-0025399 | SEA | RB | AP1 | 2P | A1, A2 |
| Vonta Leach | 00-0022397 | BAL | FB | AP1 | 2P | A1, A2 |
| Calvin Johnson | 00-0025389 | DET | WR | AP1 | 2P | A1, A2, A5 |
| Brandon Marshall | 00-0024334 | CHI | WR | AP1 | 2P | A1, A2 |
| Tony Gonzalez | 00-0006101 | ATL | TE | AP1 | 2P | A1, A2 |
| Duane Brown | 00-0026166 | HOU | T | AP1 | 2P | A1, A2 |
| Ryan Clady | 00-0026152 | DEN | T | AP1 | 2P | A1, A2, A6 |
| Mike Iupati | 00-0027869 | SF | G | AP1 | 2P | A1, A2 |
| Jahri Evans | 00-0024323 | NO | G | AP1 | 2P | A1, A2 |
| Max Unger | 00-0027025 | SEA | C | AP1 | 2P | A1, A2 |
| J.J. Watt | 00-0027949 | HOU | DE | AP1 | 2P | A1, A2 |
| Cameron Wake | 00-0023368 | MIA | DE | AP1 | 2P | A1, A2 |
| Geno Atkins | 00-0027720 | CIN | DT | AP1 | 2P | A1, A2 |
| Vince Wilfork | 00-0022712 | NE | DT | AP1 | 2P | A1, A2 |
| Von Miller | 00-0027940 | DEN | OLB | AP1 | 2P | A1, A2, A6 |
| Aldon Smith | 00-0027945 | SF | OLB | AP1 | 2P | A1, A2 |
| Patrick Willis | 00-0025398 | SF | ILB | AP1 | 2P | A1, A2 |
| NaVorro Bowman | 00-0027894 | SF | ILB | AP1 | 2P | A1, A2 |
| Richard Sherman | 00-0028092 | SEA | CB | AP1 | 2P | A1, A2 |
| Charles Tillman | 00-0022123 | CHI | CB | AP1 | 2P | A1, A2 |
| Earl Thomas | 00-0027866 | SEA | S | AP1 | 2P | A1, A2 |
| Dashon Goldson | 00-0025513 | SF | S | AP1 | 2P | A1, A2 |
| Blair Walsh | 00-0029576 | MIN | K | AP1 | 2P | A1, A2, V3 |
| Andy Lee | 00-0022824 | SF | P | AP1 | 2P | A1, A2, V3 |
| Jacoby Jones | 00-0025460 | BAL | KR | AP1 | 2P | A1, A2, A3, V2, V3 |
| Aaron Rodgers | 00-0023459 | GB | QB | AP2 | 2P | A1, A2, A4, V1 |
| Alfred Morris | 00-0029141 | WAS | RB | AP2 | 2P | A1, A2 |
| Jamaal Charles | 00-0026213 | KC | RB | AP2 | 2P | A1, A2 |
| Jerome Felton | 00-0026286 | MIN | FB | AP2 | 2P | A1, A2 |
| Andre Johnson | 00-0022044 | HOU | WR | AP2 | 2P | A1, A2 |
| A.J. Green | 00-0027942 | CIN | WR | AP2 | 2P | A1, A2 |
| Jason Witten | 00-0022127 | DAL | TE | AP2 | 2P | A1, A2 |
| Joe Thomas | 00-0025390 | CLE | T | AP2 | 2P | A1, A2 |
| Joe Staley | 00-0025415 | SF | T | AP2 | 2P | A1, A2 |
| Marshal Yanda | 00-0025473 | BAL | G | AP2 | 2P | A1, A2 |
| Logan Mankins | 00-0023467 | NE | G | AP2 | 2P | A1, A2 |
| Maurkice Pouncey | 00-0027870 | PIT | C | AP2 | 2P | A1, A2, A7 |
| Justin Smith | 00-0020535 | SF | DE | AP2 | 2P | A1, A2, V4 |
| Julius Peppers | 00-0021140 | CHI | DE | AP2 | 2P | A1, A2 |
| Ndamukong Suh | 00-0027855 | DET | DT | AP2 | 2P | A1, A2, V4 |
| Haloti Ngata | 00-0024227 | BAL | DT | AP2 | 2P | A1, A2, V4 |
| Chad Greenway | 00-0024232 | MIN | OLB | AP2 | 2P | A1, A2, V5 |
| Ahmad Brooks | 00-0024495 | SF | OLB | AP2 | 2P | A1, A2, V4, V5 |
| Clay Matthews | 00-0027002 | GB | OLB | AP2 | 2P | A1, A2, A4, V4, V5 |
| DeMarcus Ware | 00-0023445 | DAL | OLB | AP2 | 2P | A1, A2, V4, V5 |
| Daryl Washington | 00-0027886 | ARI | ILB | AP2 | 2P | A1, A2, V5 |
| London Fletcher | 00-0005322 | WAS | ILB | AP2 | 2P | A1, A2, V5 |
| Tim Jennings | 00-0024277 | CHI | CB | AP2 | 2P | A1, A2, V5 |
| Champ Bailey | 00-0000585 | DEN | CB | AP2 | 2P | A1, A2, V5 |
| Eric Weddle | 00-0025424 | SD | S | AP2 | 2P | A1, A2 |
| Jairus Byrd | 00-0027018 | BUF | S | AP2 | 2P | A1, A2 |
| Phil Dawson | 00-0004091 | CLE | K | AP2 | 2P | A1, A3 |
| Thomas Morstead | 00-0027114 | NO | P | AP2 | 2P | A1, A3, V2 |
| David Wilson | 00-0029251 | NYG | KR | AP2 | 2P | A1, A3, V2 |
| Peyton Manning | 00-0010346 | DEN | QB | PB | 1P | P1, P2, P3 |
| Tom Brady | 00-0019596 | NE | QB | PB | 1P | P1, P3 |
| Matt Schaub | 00-0022787 | HOU | QB | PB | 1P | P1, P3 |
| Arian Foster | 00-0026796 | HOU | RB | PB | 1P | P1, P2 |
| Jamaal Charles | 00-0026213 | KC | RB | PB | 1P | P1, P2 |
| Ray Rice | 00-0026195 | BAL | RB | PB | 1P | P1, P2, P9 |
| Vonta Leach | 00-0022397 | BAL | FB | PB | 1P | P1, P2 |
| A.J. Green | 00-0027942 | CIN | WR | PB | 1P | P1, P2 |
| Andre Johnson | 00-0022044 | HOU | WR | PB | 1P | P1, P2 |
| Reggie Wayne | 00-0020498 | IND | WR | PB | 1P | P1, P2 |
| Wes Welker | 00-0022427 | NE | WR | PB | 1P | P1, P2 |
| Rob Gronkowski | 00-0027656 | NE | TE | PB | 1P | P1, P2 |
| Heath Miller | 00-0023465 | PIT | TE | PB | 1P | P1, P2 |
| Joe Thomas | 00-0025390 | CLE | T | PB | 1P | P1, P2 |
| Duane Brown | 00-0026166 | HOU | T | PB | 1P | P1, P2 |
| Ryan Clady | 00-0026152 | DEN | T | PB | 1P | P1, P2 |
| Logan Mankins | 00-0023467 | NE | G | PB | 1P | P1, P2 |
| Marshal Yanda | 00-0025473 | BAL | G | PB | 1P | P1, P2, P9 |
| Wade Smith | 00-0022131 | HOU | G | PB | 1P | P1, P2 |
| Maurkice Pouncey | 00-0027870 | PIT | C | PB | 1P | P1, P2 |
| Chris Myers | 00-0023633 | HOU | C | PB | 1P | P1, P2 |
| J.J. Watt | 00-0027949 | HOU | DE | PB | 1P | P1, P2 |
| Cameron Wake | 00-0023368 | MIA | DE | PB | 1P | P1, P2 |
| Elvis Dumervil | 00-0024341 | DEN | DE | PB | 1P | P1, P2 |
| Geno Atkins | 00-0027720 | CIN | DT | PB | 1P | P1, P2 |
| Vince Wilfork | 00-0022712 | NE | DT | PB | 1P | P1, P2 |
| Haloti Ngata | 00-0024227 | BAL | DT | PB | 1P | P1, P2, P9 |
| Von Miller | 00-0027940 | DEN | OLB | PB | 1P | P1, P2 |
| Tamba Hali | 00-0024235 | KC | OLB | PB | 1P | P1, P2 |
| Robert Mathis | 00-0022059 | IND | OLB | PB | 1P | P1, P2 |
| Jerod Mayo | 00-0026150 | NE | ILB | PB | 1P | P1, P2 |
| Derrick Johnson | 00-0023449 | KC | ILB | PB | 1P | P1, P2 |
| Champ Bailey | 00-0000585 | DEN | CB | PB | 1P | P1, P2, P3 |
| Johnathan Joseph | 00-0024239 | HOU | CB | PB | 1P | P1, P2, P3 |
| Antonio Cromartie | 00-0024234 | NYJ | CB | PB | 1P | P1, P2, P3 |
| Ed Reed | 00-0021377 | BAL | FS | PB | 1P | P1, P2, P3 |
| Eric Berry | 00-0027858 | KC | SS | PB | 1P | P1, P3 |
| LaRon Landry | 00-0025393 | NYJ | S | PB | 1P | P1, P2 |
| Sebastian Janikowski | 00-0019646 | OAK | K | PB | 1P | P1, P2 |
| Shane Lechler | 00-0019714 | OAK | P | PB | 1P | P1, P2 |
| Jacoby Jones | 00-0025460 | BAL | KR | PB | 1P | P1, P2, V3 |
| Matthew Slater | 00-0026293 | NE | ST | PB | 1P | P1, P2 |
| Aaron Rodgers | 00-0023459 | GB | QB | PB | 1P | P1, P4 |
| Matt Ryan | 00-0026143 | ATL | QB | PB | 1P | P1, P4 |
| Robert Griffin III | 00-0029665 | WAS | QB | PB | 1P | P1, P4 |
| Adrian Peterson | 00-0025394 | MIN | RB | PB | 1P | P1, P4 |
| Marshawn Lynch | 00-0025399 | SEA | RB | PB | 1P | P1, P4 |
| Frank Gore | 00-0023500 | SF | RB | PB | 1P | P1, P4, P5 |
| Jerome Felton | 00-0026286 | MIN | FB | PB | 1P | P1, P4 |
| Calvin Johnson | 00-0025389 | DET | WR | PB | 1P | P1, P4 |
| Brandon Marshall | 00-0024334 | CHI | WR | PB | 1P | P1, P4, P6 |
| Julio Jones | 00-0027944 | ATL | WR | PB | 1P | P1, P4 |
| Victor Cruz | 00-0027265 | NYG | WR | PB | 1P | P1, P4, P7 |
| Tony Gonzalez | 00-0006101 | ATL | TE | PB | 1P | P1, P4 |
| Jason Witten | 00-0022127 | DAL | TE | PB | 1P | P1, P4 |
| Joe Staley | 00-0025415 | SF | T | PB | 1P | P1, P4, P5 |
| Russell Okung | 00-0027859 | SEA | T | PB | 1P | P1, P4 |
| Trent Williams | 00-0027857 | WAS | T | PB | 1P | P1, P4 |
| Mike Iupati | 00-0027869 | SF | G | PB | 1P | P1, P4, P5 |
| Jahri Evans | 00-0024323 | NO | G | PB | 1P | P1, P4 |
| Chris Snee | 00-0022838 | NYG | G | PB | 1P | P1, P4, P7 |
| Max Unger | 00-0027025 | SEA | C | PB | 1P | P1, P4 |
| Jeff Saturday | 00-0014375 | GB | C | PB | 1P | P1, P4 |
| Jason Pierre-Paul | 00-0027867 | NYG | DE | PB | 1P | P1, P4, P7 |
| Julius Peppers | 00-0021140 | CHI | DE | PB | 1P | P1, P4, P6 |
| Jared Allen | 00-0022740 | MIN | DE | PB | 1P | P1, P4 |
| Justin Smith | 00-0020535 | SF | DT | PB | 1P | P1, P4, P5 |
| Henry Melton | 00-0026905 | CHI | DT | PB | 1P | P1, P4, P6 |
| Gerald McCoy | 00-0027856 | TB | DT | PB | 1P | P1, P4 |
| Aldon Smith | 00-0027945 | SF | OLB | PB | 1P | P1, P4, P5 |
| DeMarcus Ware | 00-0023445 | DAL | OLB | PB | 1P | P1, P4 |
| Clay Matthews | 00-0027002 | GB | OLB | PB | 1P | P1, P4 |
| Patrick Willis | 00-0025398 | SF | ILB | PB | 1P | P1, P4, P5 |
| NaVorro Bowman | 00-0027894 | SF | ILB | PB | 1P | P1, P4, P5 |
| Charles Tillman | 00-0022123 | CHI | CB | PB | 1P | P1, P4, P6 |
| Tim Jennings | 00-0024277 | CHI | CB | PB | 1P | P1, P4, P6 |
| Patrick Peterson | 00-0027943 | ARI | CB | PB | 1P | P1, P4 |
| Dashon Goldson | 00-0025513 | SF | FS | PB | 1P | P1, P4, P5 |
| Donte Whitner | 00-0024223 | SF | SS | PB | 1P | P1, P4, P5 |
| Earl Thomas | 00-0027866 | SEA | S | PB | 1P | P1, P4 |
| Blair Walsh | 00-0029576 | MIN | K | PB | 1P | P1, P4 |
| Thomas Morstead | 00-0027114 | NO | P | PB | 1P | P1, P4 |
| Leon Washington | 00-0024332 | SEA | KR | PB | 1P | P1, P4 |
| Lorenzo Alexander | 00-0023259 | WAS | ST | PB | 1P | P1, P4 |
| Andrew Luck | 00-0029668 | IND | QB | ALT | 1P | R1 |
| Russell Wilson | 00-0029263 | SEA | QB | ALT | 1P | R2 |
| Jairus Byrd | 00-0027018 | BUF | FS | ALT | 1P | R3 |
| C.J. Spiller | 00-0027861 | BUF | RB | ALT | 1P | R4 |
| Kyle Williams | 00-0024348 | BUF | DT | ALT | 1P | R4 |
| Richie Incognito | 00-0023516 | MIA | G | ALT | 1P | R5 |
| Marcel Reece | 00-0026393 | OAK | FB | ALT | 1P | R6 |
| London Fletcher | 00-0005322 | WAS | ILB | ALT | 1P | R7 |
| Ryan Kerrigan | 00-0027954 | WAS | OLB | ALT | 1P | R7 |
| Thomas DeCoud | 00-0026238 | ATL | S | ALT | 1P | R8 |
| William Moore | 00-0027031 | ATL | S | ALT | 1P | R8 |
