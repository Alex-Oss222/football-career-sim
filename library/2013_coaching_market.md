# Library: 2013 NFL Coaching and Front-Office Market — Historical Comparator

> [!CAUTION]
> **QUARANTINED ACTUAL-FUTURE COMPARATOR — NEVER LOAD DURING THE 2013 HIRING SEARCH.**
>
> This file deliberately contains the actual post-cutoff hires, later interviews, staff construction, and market ripple effects. It exists for research, auditing, factual correction, and later historical comparison only. Runtime hiring resolution uses library/2013_coaching_market_pre_hire.md.

**Status:** rebuilt and independently verified 2026-09-18.  
**Historical scope:** the eight NFL head-coaching vacancies of the January 2013 cycle, with detailed treatment of the five clubs in Stone's established search scope and the immediate coordinator/staff ripple effects.  
**Runtime authority:** none.

## 1. Why this file exists

The project needs two different things that must not be blended:

1. a **pre-hire information state** that lets the simulator resolve a fair counterfactual search without hindsight; and
2. a **historical comparator** that records what really happened so later audits can identify factual errors, understand the real market, and measure where the simulation diverged.

This is the second file.

A real later event recorded here proves only that the event happened in actual history. It does **not** prove:
- that the event would occur in the simulation;
- that the organization secretly preferred that outcome at the runtime cutoff;
- that a later draft or roster move reveals an earlier hidden criterion;
- that the eventual hire was the best ex-ante candidate;
- that later success/failure validates the hiring process.

## 2. Source and date discipline

Historical coaching transactions in January 2013 sometimes carry slightly different dates across:
- contemporaneous public reports;
- team transaction ledgers;
- introductory press conferences;
- agreement dates versus formal announcement dates.

This file preserves those differences instead of silently forcing false precision.

Where a team transaction archive and a contemporaneous announcement differ by one calendar day, both are identified. For runtime purposes this does not matter because the five Stone-scope jobs remain quarantined after the January 13 event cutoff.

## 3. The eight actual 2013 NFL head-coach hires

| Club | Actual hire | Historical timing | Verification note |
|---|---|---|---|
| Kansas City | Andy Reid | Public agreement/announcement first week of January; Chiefs retrospective identifies Jan. 4, while the current transaction archive lists Jan. 3 | Date-source discrepancy retained rather than hidden |
| Buffalo | Doug Marrone | Agreement Jan. 6; introduced/signed Jan. 7 | Bills transaction ledger and team account agree on the sequence |
| Cleveland | Rob Chudzinski | Jan. 10 public hire; current Browns transaction archive displays Jan. 9 | Public announcement versus transaction-ledger date differ by one day |
| San Diego | Mike McCoy | Chargers transaction archive lists Jan. 14; introductory press conference Jan. 15 | Distinguish club transaction date from public introduction |
| Chicago | Marc Trestman | Named Jan. 16; Bears article was posted late Jan. 15 and refers to the Wednesday appointment | Do not collapse publication timestamp and appointment date |
| Philadelphia | Chip Kelly | Team announcement Jan. 16; current Eagles transaction archive lists Jan. 15 | Same transaction/announcement distinction |
| Jacksonville | Gus Bradley | Jan. 17 | Team announcement and introduction sequence verified |
| Arizona | Bruce Arians | Public hire Jan. 17; Cardinals transaction archive records agreement Jan. 16 | Agreement/public-announcement distinction |

Sources: HIST-KC, HIST-BUF, HIST-CLE, HIST-SD, HIST-CHI, HIST-PHI, HIST-JAX, HIST-AZ.

The important runtime lesson is **not** the order above. The important research lesson is that five jobs were still open at the January 13 cutoff and then closed in a compressed four-day span. A simulation should reproduce that market pressure only through contemporaneous availability and competing processes, never by scheduling the same winners.

## 4. Jacksonville Jaguars — actual historical resolution

### 4.1 Pre-hire baseline

The runtime reconstruction correctly records that David Caldwell:
- became GM in early January;
- dismissed Mike Mularkey;
- publicly said prior HC experience was not mandatory;
- had a broad candidate pool;
- had not publicly completed interviews by the January 13 team report.

See the runtime file for the uncontaminated evidence state.

### 4.2 What actually happened after the cutoff

After Seattle's elimination, Gus Bradley entered Jacksonville's active process and was hired January 17.

At Bradley's introductory/staff-search press availability, Caldwell said the club had interviewed:
- Gus Bradley;
- Rams offensive coordinator Brian Schottenheimer;
- Jaguars defensive coordinator Mel Tucker.

Caldwell said he might have interviewed 49ers offensive coordinator Greg Roman later had the search continued. Earlier public reports had connected additional names, but the later Caldwell statement is the cleanest source for the completed interview set. [HIST-JAX-SEARCH]

### 4.3 Actual staff construction

Jacksonville then hired:
- **Jedd Fisch** as offensive coordinator;
- **Bob Babich** as defensive coordinator;
- **Mike Mallory** as special-teams coordinator;
with a largely new position-coach staff. [HIST-JAX-STAFF]

This later staff is **not** evidence that Jacksonville secretly required a defensive head coach or that Bradley's eventual scheme should be reverse-engineered into the January criteria freeze.

## 5. Arizona Cardinals — actual historical resolution

### 5.1 Pre-hire baseline

Before the cutoff Arizona had:
- interviewed/considered Ray Horton, Mike McCoy, and Jay Gruden;
- hired Steve Keim as GM;
- publicly emphasized coach-GM alignment;
- publicly discussed quarterback/offensive repair;
- generated an attributed January 13 report of strong interest in McCoy.

None of that fixed the eventual winner.

### 5.2 What actually happened after the cutoff

Arizona continued the process and ultimately interviewed Indianapolis offensive coordinator Bruce Arians. The Cardinals' own hire announcement describes Arians as the last candidate interviewed and records a four-year contract with a club option for a fifth. [HIST-AZ]

This is a useful example of why the runtime file cannot treat the January 13 McCoy report as a hidden truth. A strong contemporaneous report and the eventual outcome were different things.

### 5.3 Actual staff construction

Arizona's first major assistant hires under Arians included:
- **Harold Goodwin**, offensive coordinator;
- **Todd Bowles**, defensive coordinator;
- **Tom Moore**, assistant head coach/offense. [HIST-AZ-STAFF]

Again, those hires are a historical result, not retroactive proof that Arizona's January search criteria contained a hidden preference for those coaches or systems.

## 6. Chicago Bears — actual historical resolution

### 6.1 Pre-hire baseline

Phil Emery publicly built the most explicit criteria framework among the five Stone-scope teams:
- demonstrated excellence in current role;
- organization/leadership/administration;
- operational detail;
- energy/building cohesion;
- media representation;
- consistency;
- quality of staff;
- sustained contention.

The runtime file freezes those criteria before evaluating Stone.

### 6.2 What actually happened after the cutoff

Post-hire Chicago reporting identifies the three finalists as:
- Marc Trestman;
- Bruce Arians;
- Darrell Bevell.

All three received extended second-stage interviews, including meetings involving George McCaskey and Ted Phillips. Emery selected Trestman. [HIST-CHI-FINALISTS]

That finalist list is **forbidden runtime information**. It is recorded here only to document real history.

### 6.3 Actual staff construction and branch conflict

Trestman's early staff included:
- **Aaron Kromer**, offensive coordinator/offensive line;
- **Joe DeCamillis**, special-teams coordinator;
- **Mel Tucker**, defensive coordinator. [HIST-CHI-KROMER] [HIST-CHI-TUCKER]

This is highly divergence-sensitive in Stone's simulation.

Real-history Kromer had served as a Saints interim head coach during the 2012 suspension sequence. In the simulation Stone holds the full-season interim-HC role and Kromer does not. Therefore:
- Kromer's actual Bears hire remains valid historical comparator data;
- it is not evidence that simulated Kromer has the same market value, title history, availability, or relationship path;
- it cannot be used to construct Stone's future staff or Chicago's simulated staff.

## 7. Philadelphia Eagles — actual historical resolution

### 7.1 Pre-hire baseline

Philadelphia ran a broad search. By the runtime cutoff the club had already interviewed or pursued candidates from:
- NFL offense;
- NFL defense;
- special teams;
- college head coaching;
- former NFL head coaches.

The organization had published leadership, strategy, innovation, detail, staff quality, discipline, and city/organizational fit as desired characteristics.

### 7.2 Post-cutoff search activity

After the cutoff:
- Philadelphia interviewed Jay Gruden and Ken Whisenhunt on January 14;
- Gus Bradley returned for a lengthy second meeting on January 15;
- the search remained active and publicly uncertain. [HIST-PHI-JAN14] [HIST-PHI-BRADLEY]

Philadelphia then returned to Chip Kelly, who had publicly decided earlier in January to remain at Oregon, and named Kelly head coach January 16. [HIST-PHI]

This is one of the strongest reasons for strict runtime quarantine:
- at the cutoff, Kelly had **actually withdrawn**;
- knowing his later reversal would materially distort a no-hindsight simulation;
- therefore runtime correctly treats him as unavailable unless the simulation independently generates a reversal.

### 7.3 Actual staff construction

Kelly's completed staff included:
- **Pat Shurmur**, offensive coordinator;
- **Billy Davis**, defensive coordinator;
- **Dave Fipp**, special-teams coordinator. [HIST-PHI-STAFF]

Later Kelly explained that NFL experience on the staff was particularly useful because he himself lacked NFL coaching experience. That is a later explanation of his own staff-building decision. It must not be inserted backward as a January Philadelphia-owner criterion.

## 8. San Diego Chargers — actual historical resolution

### 8.1 Pre-hire baseline

San Diego:
- dismissed Norv Turner and A.J. Smith;
- deliberately completed the GM search before the HC search;
- hired Tom Telesco January 9;
- interviewed or pursued a broad field including Lovie Smith, Ken Whisenhunt, Jay Gruden, Mike McCoy, and others;
- had a visible quarterback/protection problem around Philip Rivers.

Media described the pool as offense-heavy, but the runtime file correctly treats that as observation, not proof of a private offense-only mandate.

### 8.2 Actual result

The Chargers' transaction archive records Mike McCoy as head coach on January 14; his introductory press conference occurred January 15. [HIST-SD]

That is why the runtime event cutoff ends January 13.

### 8.3 Actual staff construction

San Diego subsequently hired:
- **Ken Whisenhunt**, offensive coordinator;
- retained **John Pagano**, defensive coordinator;
- later filled the remainder of the staff. [HIST-SD-STAFF]

Telesco's prior Indianapolis connection and Whisenhunt's eventual OC role are historical facts. They are not permission to invent a private pre-cutoff guarantee or to conclude that any candidate with Indianapolis ties should automatically receive a simulated advantage.

## 9. The three already-closed jobs at the runtime cutoff

These jobs are relevant because their hires removed candidates from the market before Stone's own simulated search begins.

### Kansas City — Andy Reid

Kansas City reached agreement with former Eagles head coach Andy Reid in the first week of January. Chiefs sources differ by one date between transaction archive and public-retrospective phrasing, but the material point is uncontested: Reid was off the market well before January 13. [HIST-KC]

### Buffalo — Doug Marrone

Buffalo hired Syracuse head coach Doug Marrone after a multi-candidate search. The club transaction ledger records the hire January 6 and introduced him January 7. [HIST-BUF]

### Cleveland — Rob Chudzinski

Cleveland selected Panthers offensive coordinator Rob Chudzinski. NFL reporting places the public hire on January 10; the current Browns transaction archive records January 9. [HIST-CLE]

These three actual pre-cutoff hires are legitimate runtime constraints because they had already happened by the information-state boundary.

## 10. Actual coordinator / assistant ripple effects

The head-coaching carousel immediately reshaped the coordinator market.

| Head-coach hire | Actual major coordinator choices | Audit significance |
|---|---|---|
| Andy Reid, Kansas City | Doug Pederson OC; Bob Sutton DC | Removed/repositioned assistants before later market stages |
| Doug Marrone, Buffalo | Nathaniel Hackett OC; Mike Pettine DC | Demonstrates how quickly staffs assembled after HC hire |
| Rob Chudzinski, Cleveland | Norv Turner OC; Ray Horton DC | Horton moved from HC candidate market to coordinator market |
| Gus Bradley, Jacksonville | Jedd Fisch OC; Bob Babich DC | Staff relationships later clarified Bradley's build, but cannot reveal pre-hire hidden criteria |
| Mike McCoy, San Diego | Ken Whisenhunt OC; John Pagano DC | A former HC candidate became coordinator after losing HC process |
| Marc Trestman, Chicago | Aaron Kromer OC/OL; Mel Tucker DC | Kromer's real path conflicts materially with Stone branch résumé |
| Chip Kelly, Philadelphia | Pat Shurmur OC; Billy Davis DC; Dave Fipp ST | Later staff experience mix must not be back-projected into ownership criteria |
| Bruce Arians, Arizona | Harold Goodwin OC; Todd Bowles DC; Tom Moore AHC/offense | Later staff construction reflects Arians's choices, not secret pre-hire answer key |

Sources: HIST-KC-STAFF, HIST-BUF-STAFF, HIST-CLE-STAFF, HIST-JAX-STAFF, HIST-SD-STAFF, HIST-CHI-KROMER, HIST-CHI-TUCKER, HIST-PHI-STAFF, HIST-AZ-STAFF.

## 11. What later roster moves and draft choices can and cannot tell us

The previous version of this file sometimes used later draft choices as proof that an issue had been the organization's "clear priority" during the head-coaching search.

That is too strong.

Examples of later actions can be useful in retrospective organizational history, but they cannot prove a private January weighting because:
- the eventual coach changes the decision process;
- free agency changes the roster before the draft;
- medical and scouting information changes;
- trades change draft position;
- other players come off the board;
- the simulation itself may have already diverged.

Therefore this rebuilt comparator does **not** use:
- Chicago's later selection of an offensive lineman;
- San Diego's later selection of an offensive lineman;
- Philadelphia's later quarterback decision;
- Arizona's later quarterback moves;
as proof of what those teams secretly wanted from a head coach before the cutoff.

Those events belong in their own historical transaction/draft research if needed.

## 12. Branch-specific non-portable history

The following real events are particularly unsafe to port into Stone's branch.

### 12.1 Pete Carmichael Jr.

Real-world January reporting connected Carmichael, the real Saints offensive coordinator, to the Chicago search.

Stone's branch changes that résumé:
- Stone holds the Saints OC role before becoming 2012 interim HC;
- Carmichael works under/alongside Stone and handles substantial weekday offense during Stone's interim season;
- simulated New Orleans reaches the Divisional Round.

Therefore the real Carmichael candidacy is not fixed branch history.

### 12.2 Aaron Kromer

Real-world 2012 Kromer served as interim head coach for part of the Saints suspension sequence.

In Stone's branch he does not; Stone holds the full-season interim role.

Chicago's later real hire of Kromer as OC/OL is therefore comparator-only and cannot be assumed to reproduce itself.

### 12.3 New Orleans playoff availability

Real New Orleans missed the playoffs. Simulated New Orleans played through January 13.

Any real January interview availability involving Saints staff must be re-evaluated against the branch calendar rather than copied.

### 12.4 Stone's Chargers history

The real Chargers did not have a former player named Alex Stone with the branch résumé in their 2013 candidate market.

Therefore any simulated "homecoming" reaction is genuinely counterfactual. It must be generated from the organization-side process, not sourced from actual history.

## 13. Corrections to the prior version of this file

The rebuild makes the following substantive corrections:

1. **No more unsourced "verified" claims.** Every major hiring/search/staff result now maps to an identified source.
2. **Date discrepancies are preserved.** Team transaction ledgers and public announcement dates sometimes differ by one day; the file no longer pretends one exact date is universally reported.
3. **Jacksonville candidate completion corrected.** Later Caldwell comments identify Bradley, Schottenheimer, and Tucker as completed interviewees; earlier planned/reported candidates are no longer silently promoted to completed interviews.
4. **Later draft picks removed as evidence of January search priorities.**
5. **Later cap snapshots removed from the core coaching-market analysis.** Financial state should come from dated financial research, not a later article used as a coaching criterion.
6. **Media observations separated from private organizational criteria.**
7. **Philadelphia's Kelly reversal explicitly fenced as hindsight.**
8. **Saints staff outcomes explicitly marked divergence-sensitive.**
9. **Actual coordinator staffs remain for audit, but are expressly prohibited as hidden search criteria.**
10. **The five Stone-scope results are never described as the path the simulation should reproduce.**

## 14. Historical source register

### Actual head-coach hires
- **HIST-KC:** Chiefs 2013 transaction archive; Chiefs Jan. 5 article "A New Era Underway in Kansas City."  
  https://www.chiefs.com/team/transactions/2013  
  https://www.chiefs.com/news/a-new-era-underway-in-kansas-city-9287288
- **HIST-BUF:** Bills 2013 transaction archive; "Doug Marrone named new head coach of Buffalo Bills," Jan. 7, 2013.  
  https://www.buffalobills.com/team/transactions/2013  
  https://www.buffalobills.com/news/doug-marrone-named-new-head-coach-of-buffalo-bills-9299906
- **HIST-CLE:** NFL.com, "Rob Chudzinski hired to be Cleveland Browns' coach"; Browns 2013 transaction archive.  
  https://www.nfl.com/news/rob-chudzinski-hired-to-be-cleveland-browns-coach-0ap1000000124943  
  https://www.clevelandbrowns.com/team/transactions/2013
- **HIST-SD:** Chargers 2013 transaction archive; NFL.com, "Mike McCoy set to begin fixing San Diego Chargers," Jan. 15, 2013.  
  https://www.chargers.com/team/transactions/2013  
  https://www.nfl.com/news/mike-mccoy-set-to-begin-fixing-san-diego-chargers-0ap1000000126896
- **HIST-CHI:** Bears, "Trestman hired as 14th coach in Bears history."  
  https://www.chicagobears.com/news/trestman-hired-as-14th-coach-in-bears-history-9372335
- **HIST-PHI:** Eagles, "Chip Kelly Named New Head Coach," Jan. 16, 2013.  
  https://www.philadelphiaeagles.com/news/chip-kelly-named-new-head-coach-9373523
- **HIST-JAX:** Jaguars, "Gus Bradley named head coach of Jaguars," Jan. 17, 2013.  
  https://www.jaguars.com/news/gus-bradley-named-head-coach-of-jaguars-9379286
- **HIST-AZ:** Cardinals, "Cardinals Make Bruce Arians Head Coach," Jan. 17, 2013.  
  https://www.azcardinals.com/news/cardinals-make-bruce-arians-head-coach-9383910
- **Cross-check:** NFL.com 2013 head-coaching search tracker.  
  https://www.nfl.com/news/nfl-head-coaching-search-tracker-0ap1000000120834

### Search-resolution sources
- **HIST-JAX-SEARCH:** Jaguars, post-hire search summary / assistant-search comments identifying completed interviews.  
  https://www.jaguars.com/news/assistant-search-begins-9386961
- **HIST-CHI-FINALISTS:** Bears, "Marc Trestman met all of Phil Emery's criteria for job," Jan. 20, 2013.  
  https://www.chicagobears.com/news/marc-trestman-met-all-of-phil-emery-s-criteria-for-job-9395800
- **HIST-PHI-JAN14:** Eagles, "Eagles Interview Gruden, Whisenhunt," Jan. 14, 2013.  
  https://www.philadelphiaeagles.com/news/eagles-interview-gruden-whisenhunt-9360462
- **HIST-PHI-BRADLEY:** Eagles, "Reports: Meeting With Bradley Over," Jan. 15, 2013.  
  https://www.philadelphiaeagles.com/news/reports-meeting-with-bradley-over-9372229

### Actual staff sources
- **HIST-JAX-STAFF:** Jaguars, "Fisch, Babich named coordinators," Jan. 19, 2013; final staff listing.  
  https://www.jaguars.com/news/fisch-babich-named-coordinators-9389858  
  https://www.jaguars.com/news/jaguars-finalize-2013-coaching-staff-9550558
- **HIST-AZ-STAFF:** Cardinals transaction archive; "Cardinals Add Key Assistant Coaches."  
  https://www.azcardinals.com/team/transactions/2013  
  https://www.azcardinals.com/news/cardinals-add-key-assistant-coaches-9400119
- **HIST-CHI-KROMER:** Bears, "Bears hire Kromer as offensive coordinator, line coach."  
  https://www.chicagobears.com/news/bears-hire-kromer-as-offensive-coordinator-line-coach-9377423
- **HIST-CHI-TUCKER:** Bears, "Mel Tucker hired as Bears defensive coordinator."  
  https://www.chicagobears.com/news/mel-tucker-hired-as-bears-defensive-coordinator-9387795
- **HIST-PHI-STAFF:** Eagles, "Meet Chip Kelly's Coordinators."  
  https://www.philadelphiaeagles.com/news/meet-chip-kelly-s-coordinators-9554452
- **HIST-SD-STAFF:** Chargers 2013 transaction archive; NFL.com Whisenhunt coordinator report.  
  https://www.chargers.com/team/transactions/2013  
  https://www.nfl.com/news/ken-whisenhunt-in-as-chargers-offensive-coordinator-0ap1000000127670
- **HIST-KC-STAFF:** Chiefs 2013 transaction archive / staff announcements.  
  https://www.chiefs.com/team/transactions/2013
- **HIST-BUF-STAFF:** Bills January 2013 staff announcements.  
  https://www.buffalobills.com/news/bills-coordinators-raised-on-football-9337495
- **HIST-CLE-STAFF:** Browns 2013 transaction archive.  
  https://www.clevelandbrowns.com/team/transactions/2013

## 15. Verification pass

The second research pass independently checked:
- all eight head-coach results;
- date discrepancies between transaction ledgers and public announcements;
- Jacksonville's actual completed interview set;
- Chicago's later finalist group;
- Philadelphia's post-cutoff Gruden/Whisenhunt and Bradley meetings;
- actual coordinator staffs for the five target organizations;
- the branch conflict created by Stone replacing the real Saints interim-HC/OC sequence.

Where the evidence did not support a precise claim, the claim was narrowed rather than padded.

## 16. Quarantine rule

During a live 2013 hiring search:
- do not load this file;
- do not quote this file;
- do not use its eventual winners;
- do not use its finalist lists;
- do not use its assistant staffs;
- do not use its later explanations;
- do not use its later roster moves;
- do not use its later performance.

The only runtime coaching-market file is library/2013_coaching_market_pre_hire.md.

This file tells an auditor what actually happened. It never tells the simulator what should happen.
