# Library: 2013 NFL Head-Coaching Market — Pre-Hire Runtime Reconstruction

**Runtime status:** ACTIVE PRE-HIRE REFERENCE  
**Snapshot:** opening of January 14, 2013.  
**Event cutoff:** 11:59 PM ET, January 13, 2013.  
**Simulation purpose:** give the hiring resolver a deep, dated picture of the five organizations in Alex Stone's established search scope, the competing coaching market, candidate availability, and public organizational criteria without importing any later hiring result.  
**Research status:** rebuilt 2026-09-18 from contemporaneous team and NFL reporting, followed by a separate skeptical verification pass.

> **HARD QUARANTINE — NO HIRING HINDSIGHT:** The resolver may not load, infer from, or reverse-engineer from the eventual real head-coach hire, later finalist list, later coordinator staff, later contract, later draft choice, later free-agent move, later season result, or later coaching career. The historical comparator is library/2013_coaching_market.md and is forbidden during runtime search resolution.

The cutoff is deliberately expressed as an **opening-of-January-14 snapshot** because Stone's simulated 2012 Saints season ended in the Divisional Round on January 13. Facts that became true during the January 12-13 playoff weekend, such as the end of Denver's and Seattle's seasons, are therefore visible at this snapshot. Search actions occurring on January 14 or later are not.

## 1. Evidence model and runtime treatment

This file distinguishes four kinds of information.

| Label | Meaning | Runtime treatment |
|---|---|---|
| **Structural pre-cutoff fact** | Public fact already true by the event cutoff: vacancy, owner/GM, 2012 record, roster/contract context, completed playoff elimination, league interview restriction | May be used directly |
| **Public organization criterion** | Criterion or process stated by an owner, GM, president, or team source before the cutoff | May be frozen as organization-side evidence; do not secretly add weighting the source did not state |
| **Attributed market report** | Contemporaneous report about interest, planned interview, or perceived preference | Evidence that the report existed; not automatic proof of the organization's private ranking |
| **Historical market baseline** | A real-world post-divergence interview, permission request, or candidate connection that helps reconstruct the 2013 market | Use as a plausible baseline candidate field, not as immutable simulation canon when Stone's existence or another branch divergence could have changed the sequence |

### 1.1 The criteria-freeze rule

Before Stone's pitch, preferences, interview answers, contract terms, or hiring-search brief are evaluated, the resolver must freeze each organization's criteria from this file.

The freeze may contain:
- documented decision-makers;
- publicly stated criteria;
- roster/organizational problems already visible by the cutoff;
- legal/calendar constraints;
- candidate availability;
- labeled inference that follows from those facts.

The freeze may **not** contain:
- "Stone fits because..." reasoning;
- a weighting chosen after reading Stone's pitch;
- the eventual real hire as a model for what the organization "really wanted";
- the eventual coordinator staff as evidence of an earlier hidden scheme mandate;
- a later draft pick or free-agent signing as evidence of a January preference;
- invented owner/GM motives;
- a numerical candidate score.

After the freeze closes, Stone and every comparator candidate are evaluated against the same relevant dimensions. A detailed Stone dossier never earns more credit merely because it contains more prose than a real candidate's packet.

### 1.2 Public fact versus simulated event

Alex Stone has existed in this alternate history for decades, so real January 2013 search actions are not automatically immutable history. The safest treatment is:

- **organizational conditions and public criteria** that are not plausibly changed by Stone remain strong baseline evidence;
- **real candidate fields and interview activity** reconstruct who was genuinely in the market and what was plausible, but the simulation may alter the sequence when Stone's candidacy or another branch fact would reasonably change it;
- once the simulated search itself begins, its dated events control.

This distinction is especially important for New Orleans staff, because the simulated Saints reached the 2012 Divisional Round while the real Saints did not.

## 2. Leaguewide state at the cutoff

### 2.1 Eight vacancies opened; three were already closed

Eight NFL head-coaching jobs changed hands in the January 2013 cycle. By the close of January 13, three real vacancies had already been filled and therefore those coaches were no longer part of the open market:

| Club | Status by cutoff | Runtime consequence |
|---|---|---|
| Kansas City | Andy Reid had accepted the Chiefs job in the first week of January | Reid unavailable |
| Buffalo | Doug Marrone had accepted the Bills job | Marrone unavailable |
| Cleveland | Rob Chudzinski had accepted the Browns job | Chudzinski unavailable |
| Jacksonville | Open | In Stone's search scope |
| Arizona | Open | In Stone's search scope |
| Chicago | Open | In Stone's search scope |
| Philadelphia | Open | In Stone's search scope |
| San Diego | Open | In Stone's search scope |

Sources: CLOSED-KC, CLOSED-BUF, CLOSED-CLE.

The five open jobs above are exactly the five organizations Document 3 establishes as Stone's starting search scope. Their real later outcomes are not known to the runtime resolver.

### 2.2 Playoff availability changed during January 12-13

The Divisional Round materially changed candidate availability.

- Denver's loss on January 12 ended the Broncos' season, freeing offensive coordinator Mike McCoy from postseason scheduling restrictions.
- Seattle's loss on January 13 ended the Seahawks' season, freeing defensive coordinator Gus Bradley.
- Green Bay and Houston were also eliminated during the weekend, changing availability for assistants on those staffs.
- Atlanta, San Francisco, New England, and Baltimore remained alive after the weekend. Their assistants remained subject to postseason interview restrictions.

A Philadelphia team article published shortly after midnight on January 14 is used only as a verification source for these already-completed January 12-13 events and the applicable interview procedure. It is not used to import any January 14 interview action. [PHI-PLAYOFF-PROCEDURE]

### 2.3 Already-public candidate withdrawals or commitments

By the event cutoff:
- Chip Kelly had publicly decided to remain at Oregon after interviewing with Philadelphia and Cleveland. His later real-world reversal is quarantined and does not exist in runtime. [CAND-CHIP-KELLY]
- Brian Kelly had publicly announced on January 12 that he would remain at Notre Dame after speaking with Philadelphia. [CAND-BRIAN-KELLY]
- Bill O'Brien had publicly recommitted to Penn State on January 3 after NFL interest. Treat him as unavailable unless a new simulation event changes that fact before the cutoff, which none has. [CAND-OBRIEN-STAY]

## 3. Jacksonville Jaguars

### 3.1 Structural situation

- Owner Shad Khan had dismissed general manager Gene Smith on December 31, 2012.
- David Caldwell was hired as general manager on January 8.
- Caldwell dismissed head coach Mike Mularkey on January 10 after a 2-14 season.
- Jacksonville held the second selection position based on the completed 2012 standings. This is known before the draft and is not a draft-outcome leak.
- The quarterback position was unsettled around 2011 first-round pick Blaine Gabbert.
- The roster was coming off the worst record in franchise history to that point.
- Maurice Jones-Drew entered the offseason after the publicly documented 2012 holdout and an injury-shortened season.
- Precise March cap-space figures do not belong in this January snapshot. The resolver should use only financial data independently established as of the cutoff.

### 3.2 Decision structure

- **Owner:** Shad Khan.
- **General manager / primary football counterpart:** David Caldwell.
- Caldwell had only just taken the GM job, so the head coach would be entering a new GM-HC partnership rather than an inherited long-standing football hierarchy.

### 3.3 Public search criteria

On January 10 Caldwell said:
- finding the head coach was the immediate priority;
- he already had a candidate list;
- there was no fixed timetable;
- previous head-coaching experience was **not** required;
- he was looking for the right person rather than one predetermined experience category. [JAX-CRITERIA]

This supports a broad search. It does **not** establish a private offensive or defensive preference, preferred age, exact personnel-control structure, or preferred candidate.

### 3.4 Football and organizational problems visible at the cutoff

Evidence-supported criteria for a freeze:
1. Ability to establish a functional working relationship with a newly hired GM.
2. Whole-program leadership appropriate to a 2-14 roster, not merely one schematic repair.
3. Credible quarterback evaluation and development plan.
4. Ability to build a staff and operating structure from a near-clean organizational reset.
5. Roster-development judgment under a high draft position and broad reconstruction.
6. No automatic bonus for prior head-coaching experience because Caldwell publicly said it was not a prerequisite.

Do **not** infer that Jacksonville secretly preferred an offensive coach, a defensive coach, a specific system, or a friend/former colleague of Caldwell.

### 3.5 Public/historical market baseline through the cutoff

A January 13 Jaguars report said no interviews had yet been reported as completed, but listed planned or reported interest in:
- Brian Schottenheimer, Rams offensive coordinator;
- Mel Tucker, Jaguars defensive coordinator;
- Keith Armstrong, Falcons special-teams coordinator;
- Jay Gruden, Bengals offensive coordinator;
- Mike McCoy, Broncos offensive coordinator;
- Greg Roman, 49ers offensive coordinator. [JAX-MARKET]

Caldwell had also publicly discussed Greg Roman, Brian Schottenheimer, Vic Fangio, and Jay Gruden when asked about the search on January 10. [JAX-CRITERIA]

Runtime treatment:
- these names form a historically grounded candidate pool;
- a reported plan is not a completed simulated interview;
- Roman and Armstrong were still attached to teams alive in the postseason;
- McCoy had just become fully available after Denver's elimination;
- Stone's presence may change scheduling/order, but not the baseline fact that Jacksonville had a broad coordinator-heavy market available.

### 3.6 Unknown and prohibited

Remain unknown unless established in the simulation:
- private candidate ranking;
- exact contract budget;
- exact personnel-control offer;
- preferred coordinator names;
- willingness to retain staff;
- whether Caldwell's prior relationships create any actual preference;
- any eventual real hiring result.

### 3.7 Criteria-freeze template

A valid Jacksonville freeze should resemble:

**Documented criteria:** broad search; prior HC experience not required; new GM-HC partnership; leadership and roster/QB reconstruction.  
**Structural constraints:** 2-14 baseline, high draft position, unsettled QB, new GM.  
**Candidate-market constraints:** several coordinators in market; some playoff availability restrictions.  
**Private weighting:** unknown.  
**Stone-specific fit:** not evaluated until after freeze closes.

## 4. Arizona Cardinals

### 4.1 Structural situation

- Arizona dismissed head coach Ken Whisenhunt and general manager Rod Graves on December 31 after a 5-11 season.
- The team had opened 4-0 and then lost 11 of its final 12 games.
- Steve Keim was promoted to general manager on January 8.
- Quarterback instability was a central football problem after the club used four starters during 2012.
- Offensive-line/run-game stability was also publicly discussed when Keim took over.
- Larry Fitzgerald remained the offense's established centerpiece.
- Later releases, restructures, and March cap figures are outside this runtime snapshot.

### 4.2 Decision structure

- **Team president:** Michael Bidwill.
- **General manager:** Steve Keim.
- **Principal ownership:** Bidwill family.
- At the opening of the search, Michael Bidwill publicly said there was no fixed rule that the coach or GM had to be hired first and described coach-GM fit as the issue. He did not rule out a coach having personnel influence, but cited strong coach-GM partnerships as a healthy model. [AZ-OPENING]

This means authority structure was legitimately negotiable. It does **not** mean any candidate automatically receives personnel control.

### 4.3 Public search and organizational criteria

The strongest pre-cutoff evidence supports:
1. Coach-GM compatibility.
2. Quarterback evaluation/development.
3. Credibility to stabilize a team after the severe second-half collapse.
4. Ability to improve offensive operation, especially quarterback consistency and protection/run-game functionality.
5. "Retool" rather than assume a total teardown was Keim's public framing on January 8. [AZ-KEIM]
6. Search timing was deliberately not fixed.

### 4.4 Candidate-market baseline

The Cardinals publicly identified or interviewed:
- **Ray Horton**, incumbent defensive coordinator; interviewed early in the process.
- **Mike McCoy**, Denver offensive coordinator; the organization had spoken with him before Denver's elimination.
- **Jay Gruden**, Cincinnati offensive coordinator; interviewed January 10, with his quarterback-development work explicitly relevant to Arizona's situation.
- **Todd Haley**, Steelers offensive coordinator; permission was reported, but as of January 8 no completed interview was established.
- **Andy Reid** was an initial target, but he left the market for Kansas City before the cutoff. [AZ-OPENING] [AZ-KEIM] [AZ-GRUDEN]

On January 13 NFL Network reported, citing informed sources, that Arizona planned a strong push for McCoy now that Denver had been eliminated and described Horton as an alternative. That is **attributed market reporting**, not an objective statement of Arizona's hidden ranking. [AZ-MCCOY-REPORT]

### 4.5 Unknown and prohibited

Do not infer:
- that the January 13 report fixes the simulated preferred candidate;
- that an offensive background is mandatory;
- that Horton is guaranteed retention;
- exact personnel authority;
- exact salary/term;
- later interview additions;
- eventual real hire.

### 4.6 Criteria-freeze template

**Documented criteria:** coach-GM fit, quarterback/offensive stabilization, whole-program credibility, no fixed timetable.  
**Structural constraints:** 5-11 season, dramatic collapse, new GM, QB instability, offensive-line/run-game issues.  
**Attributed reports:** McCoy interest was strong according to NFL Network sources; keep as report, not secret fact.  
**Private weighting:** unknown.  
**Stone-specific fit:** evaluated only after freeze.

## 5. Chicago Bears

### 5.1 Structural situation

- GM Phil Emery dismissed Lovie Smith on December 31 after Chicago finished 10-6 but missed the playoffs.
- Smith had reached the postseason only once in his final six seasons.
- Emery had been hired in January 2012 and was conducting his first Bears head-coaching search.
- Jay Cutler was the established quarterback.
- Offensive-line/protection and broader offensive consistency were visible football issues.
- Because the outgoing coach had a winning 2012 record, this was not a 2-14-style rebuild. The organization was trying to change its operating trajectory while remaining competitive.

### 5.2 Decision structure

- **General manager:** Phil Emery, who publicly held the final selection responsibility.
- **Chairman:** George McCaskey.
- **President/CEO:** Ted Phillips.
- Emery would conduct the initial search; McCaskey and Phillips were expected to meet a small finalist group. [CHI-PROCESS]

### 5.3 Explicit public criteria

Chicago supplied unusually detailed criteria before the result was known.

Emery publicly said he wanted:
1. demonstrated excellence in the candidate's current role, regardless of whether that role was offense, defense, special teams, NFL, or college;
2. strong organization, leadership, and administration;
3. command of operational detail, including CBA/practice constraints;
4. energy and ability to unify the building;
5. credible public/media representation;
6. consistency under adversity;
7. a staff package that added to the candidate's case;
8. ultimately, consistent playoff/championship contention. [CHI-CRITERIA] [CHI-PROCESS]

This is strong enough to create a real criteria freeze without inventing hidden motives.

### 5.4 Market baseline through the cutoff

Publicly reported Chicago candidates/interest included:
- Marc Trestman, Montreal Alouettes head coach;
- Bruce Arians, Indianapolis offensive coordinator / 2012 interim head coach;
- Mike Sullivan, Tampa Bay offensive coordinator;
- Mike McCoy, Denver offensive coordinator;
- Keith Armstrong, Atlanta special-teams coordinator;
- Joe DeCamillis, Dallas special-teams coach;
- Tom Clements, Green Bay offensive coordinator;
- Rick Dennison, Houston offensive coordinator;
- Darrell Bevell, Seattle offensive coordinator;
- Mike Singletary, Minnesota linebackers coach and former 49ers head coach. [CHI-TRESTMAN] [CHI-MARKET]

Brian Kelly was reported not to be part of the Chicago search by January 10. [CHI-MARKET]

A real-history report also listed Saints offensive coordinator Pete Carmichael Jr. That specific candidate fact is **not portable into this simulation** because Stone's branch changed Carmichael's role, the Saints' 2012 record, and New Orleans' playoff availability. See §11.

### 5.5 Availability at the snapshot

- McCoy became fully available after Denver's January 12 elimination.
- Bevell became fully available after Seattle's January 13 elimination.
- Clements became available after Green Bay's elimination.
- Dennison became available after Houston's elimination.
- Atlanta assistants such as Armstrong remained on a live playoff team.
- Chicago had publicly indicated willingness to let the process extend if a desired candidate's playoff run required waiting. [CHI-PROCESS]

### 5.6 Unknown and prohibited

Do not infer:
- that Chicago had secretly decided it must hire an offensive coach;
- that Cutler alone determines the search;
- the eventual finalist order;
- any later real finalist list;
- any later staff construction;
- that a candidate's eventual Bears performance validates or invalidates the ex-ante choice.

### 5.7 Criteria-freeze template

**Documented criteria:** demonstrated excellence, leadership, organization/admin, building-wide cohesion, staff quality, public representation, consistency, sustainable contention.  
**Structural football issues:** offense/protection and Cutler are relevant but not a published exclusive scheme mandate.  
**Candidate pool:** deliberately broad by Emery's own public statements.  
**Private weighting:** unknown.  
**Stone-specific fit:** evaluated only after freeze.

## 6. Philadelphia Eagles

### 6.1 Structural situation

- Jeffrey Lurie dismissed Andy Reid on December 31 after 14 seasons.
- Philadelphia finished 4-12 in 2012.
- Howie Roseman remained general manager.
- Michael Vick remained under a major existing 2013 contract obligation at the cutoff.
- Nick Foles had completed his rookie season.
- LeSean McCoy and DeSean Jackson were major offensive pieces.
- Any later Vick restructure, later draft choice, or later roster move is prohibited as search evidence.

### 6.2 Decision structure

- **Chairman/CEO:** Jeffrey Lurie.
- **General manager:** Howie Roseman.
- **Team president:** Don Smolenski was involved in the interview process.
- The search was explicitly described as exhaustive rather than a single-archetype hunt.

### 6.3 Explicit public criteria

Lurie published a detailed January 1 framework:
1. high-level leadership;
2. ability to set short-, medium-, and long-term strategy;
3. forward thinking and openness to innovation;
4. attention to detail;
5. ability to surround himself with high-caliber assistants and colleagues;
6. toughness and discipline;
7. strategic understanding of personnel strengths/weaknesses;
8. ability to understand and represent the Philadelphia football environment. [PHI-CRITERIA]

These criteria are usable directly. They do not establish one required offensive scheme.

### 6.4 Confirmed/reported search activity through the cutoff

**Confirmed early interviews:**
- Mike Nolan, Atlanta defensive coordinator;
- Keith Armstrong, Atlanta special-teams coordinator;
- Bill O'Brien, Penn State head coach;
- Chip Kelly, Oregon head coach;
- Mike McCoy, Denver offensive coordinator. [PHI-FIRST-WAVE] [PHI-WEEKEND]

**Additional known activity:**
- permission had been granted to speak with Bruce Arians and Gus Bradley;
- Lovie Smith was scheduled and subsequently publicly confirmed as meeting with Philadelphia during the week; [PHI-LOVIE] [PHI-LOVIE-COMPLETE]
- Brian Kelly spoke with Philadelphia, then announced January 12 that he would stay at Notre Dame;
- Brian Billick was reported on January 13 to have interviewed earlier in the week;
- Gus Bradley was reported on January 13 to have interviewed on Saturday, though Philadelphia had not formally confirmed that meeting;
- Jay Gruden was publicly in the pipeline, but his Philadelphia interview occurred after this event cutoff and is not loaded as a completed event. [PHI-ARIANS-BRADLEY] [PHI-LOVIE] [PHI-BILLICK]

### 6.5 Candidates no longer available at the cutoff

- Chip Kelly had told Philadelphia he was staying at Oregon. In this runtime snapshot he is unavailable. His later historical reversal is forbidden. [CAND-CHIP-KELLY]
- Brian Kelly had officially announced he was staying at Notre Dame. [CAND-BRIAN-KELLY]
- Bill O'Brien had recommitted to Penn State before the cutoff.

### 6.6 Market implications

Philadelphia had the broadest clearly documented search among Stone's five target teams. That matters mechanically in only one legitimate way: the organization has a **deep comparator field**, so Stone is not evaluated against an anonymous placeholder.

It does **not** mean:
- that more interviews make Stone less likely by fiat;
- that the resolver can choose a favorite from hindsight;
- that the eventual real hire reveals the hidden ideal;
- that innovation automatically outweighs leadership, staff, discipline, or organizational management.

### 6.7 Criteria-freeze template

**Documented criteria:** leadership, multi-horizon strategy, innovation, detail, staff construction, discipline, organizational/city fit.  
**Structural constraints:** 4-12 reset after 14-year coach, unresolved QB direction, existing offensive skill talent.  
**Market:** unusually broad and competitive.  
**Unavailable real candidates:** Chip Kelly, Brian Kelly, Bill O'Brien at this snapshot unless simulation changes a prior fact.  
**Private ranking:** unknown.  
**Stone-specific fit:** evaluated only after freeze.

## 7. San Diego Chargers

### 7.1 Structural situation

- Head coach Norv Turner and general manager A.J. Smith were dismissed December 31 after a 7-9 season and a third straight year outside the playoffs.
- The organization deliberately prioritized the GM search first.
- Tom Telesco was hired general manager on January 9.
- Philip Rivers remained the established quarterback.
- Rivers had been sacked 49 times in 2012, making pass protection and offensive operation visible football issues.
- Antonio Gates remained a major veteran offensive player.
- Later Rivers contract restructuring, later draft choices, and later free-agent actions do not belong in this snapshot.

### 7.2 Decision structure

Before Telesco was hired, the coaching-search committee was described as:
- team president/chairman leadership under Dean Spanos;
- John Spanos;
- Ed McGuire;
- consultant Ron Wolf;
- with the newly hired general manager joining the process. [SD-GM-FIRST]

After January 9, Telesco joined the coaching search. [SD-TELESCO]

### 7.3 Evidence-supported criteria

Unlike Chicago and Philadelphia, San Diego did not publish an equally detailed written candidate rubric before the cutoff. A valid freeze should therefore remain narrower:

1. Functional partnership with the newly hired GM.
2. Ability to reverse a multi-year decline without pretending the roster is equivalent to a bottom-two team.
3. Quarterback/offensive-line plan around Rivers is a material football issue.
4. Leadership and staff construction are necessarily relevant head-coach functions, but no exact private weighting is established.
5. Do **not** turn the offense-heavy real candidate pool into a secret rule that only offensive coaches can win the job.

### 7.4 Market baseline through the cutoff

Publicly reported San Diego activity included:
- Lovie Smith interviewed on January 11;
- Ken Whisenhunt was in the candidate mix and was scheduled/reported for the weekend;
- Jay Gruden was scheduled to interview January 13;
- Mike McCoy was scheduled for January 14, after Denver's elimination;
- Bruce Arians publicly expressed interest after Telesco's hire;
- Gus Bradley was reported in the candidate pool;
- Mike Zimmer and UCLA head coach Jim Mora had been identified as planned candidates when Telesco was hired. [SD-LOVIE] [SD-GRUDEN] [SD-ARIANS] [SD-TELESCO]

Media described the field as heavy on offensive coaches. That is an observation about the visible field, not proof of a private offensive-only mandate. [SD-GRUDEN]

### 7.5 Stone-specific boundary

Stone's established playing career with the Chargers is a candidate résumé fact from library/alex_stone_character_dossier_pre_hire.md.

It may affect an interview only through a plausible evaluator response generated **after** San Diego's organization criteria are frozen. Do not:
- assign automatic loyalty or nostalgia;
- assume ownership remembers him favorably;
- grant an interview advantage merely because the user controls him;
- treat his former-player status as irrelevant if a simulated decision-maker legitimately brings it up.

The same rule would apply to any real candidate with prior organization history.

### 7.6 Unknown and prohibited

Remain unknown:
- exact candidate ordering;
- whether Telesco privately prefers a former Colts colleague;
- exact scheme mandate;
- exact personnel authority;
- exact salary/term;
- eventual real hire.

## 8. Standardized candidate evidence packets

These packets exist to prevent an asymmetry where Stone has a detailed dossier and everyone else is an unnamed "other candidate." They summarize what was publicly established by the cutoff. They are not rankings.

### Alex Stone — simulation candidate

**Current status:** Saints 2012 interim head coach whose simulated season ended January 13.  
**Record/experience:** use library/alex_stone_character_dossier_pre_hire.md and Document 3 only.  
**Important established evidence:** 12-4 simulated 2012 regular season, 1-1 postseason; prior NFL offensive-coordinator/play-calling work; prior Patriots/Saints experience; one full simulated season of team-level interim HC authority.  
**Open questions:** permanent staff construction, post-hire philosophy, requested authority, contract terms, interview answers.  
**Rule:** do not expand Stone's evidence beyond the permitted dossier before comparing him to others.

### Mike McCoy — Denver offensive coordinator

**Age/current role at the time:** 40, Broncos offensive coordinator.  
**Public résumé:** 13 NFL coaching seasons, four as Denver OC; gained attention for adapting the offense from Kyle Orton to Tim Tebow in 2011 and then to Peyton Manning in 2012. [CAND-MCCOY]  
**HC experience:** none.  
**Market connections:** Arizona, Chicago, Philadelphia, San Diego, Jacksonville baseline interest.  
**Availability:** Denver eliminated January 12; fully available at snapshot.  
**Evaluation uncertainty:** how much credit belongs to coordinator versus elite quarterback personnel; no answer is predetermined.

### Ray Horton — Arizona defensive coordinator

**Current role:** Cardinals defensive coordinator.  
**Public résumé:** former NFL player; long assistant career including Pittsburgh secondary; two seasons running Arizona's defense. [CAND-HORTON]  
**HC experience:** none.  
**Market:** Arizona interviewed him; had other league interest.  
**Evaluation question:** internal organizational knowledge and defensive résumé versus first-time-HC projection.  
**No hidden advantage:** being the incumbent coordinator does not automatically make him preferred.

### Jay Gruden — Cincinnati offensive coordinator

**Current role:** Bengals offensive coordinator.  
**Public résumé:** two NFL seasons as Bengals OC by the cutoff; credited publicly with developing Andy Dalton; prior head-coaching experience in Arena football and the UFL. [AZ-GRUDEN]  
**Market:** Arizona interview completed; San Diego interview scheduled for January 13; Jacksonville/Philadelphia interest or planned contact.  
**Availability:** Cincinnati had been eliminated in the Wild Card round.  
**Projection question:** NFL head-coaching translation of offensive/QB work plus non-NFL head-coaching experience.

### Bruce Arians — Indianapolis offensive coordinator / 2012 interim head coach

**Current role:** Colts offensive coordinator; served as interim HC for 12 games during Chuck Pagano's treatment.  
**2012 interim record:** 9-3 in the games he directed.  
**Background:** extensive NFL offensive/QB coaching plus prior college head-coaching experience.  
**Market:** Chicago, Philadelphia, San Diego and other openings connected publicly.  
**Availability/medical:** Indianapolis had been eliminated; a January illness briefly affected scheduling, but he was out of the hospital and discussing jobs by January 10. [SD-ARIANS]  
**Evaluation question:** veteran experience and quarterback work versus organization-specific fit. Do not import later outcomes.

### Gus Bradley — Seattle defensive coordinator

**Current role:** Seahawks defensive coordinator, fourth season in that role.  
**Public profile:** defense/leadership candidate with no prior NFL HC job.  
**Market:** Philadelphia had permission to speak with him and a January 13 report said an interview may have occurred; San Diego media reports included him in the field.  
**Availability:** Seattle eliminated January 13, so he becomes fully available at this snapshot. [PHI-BILLICK]  
**Evaluation question:** first-time head coach projection and staff/organizational leadership, not later record.

### Marc Trestman — Montreal Alouettes head coach

**Current role:** CFL head coach.  
**Public résumé:** five seasons leading Montreal by this point, 59-31, three Grey Cup appearances and championships in 2009 and 2010; approximately 17 prior seasons of NFL assistant/offensive work. [CHI-TRESTMAN]  
**Market:** Chicago.  
**Evaluation question:** demonstrated head-coaching/offensive experience versus transition from CFL to NFL organizational environment.

### Darrell Bevell — Seattle offensive coordinator

**Current role:** Seahawks offensive coordinator.  
**Public résumé:** prior Packers assistant and Vikings offensive coordinator; coordinated Seattle's offense during Russell Wilson's rookie season.  
**Market:** Chicago baseline interest/interview reporting.  
**Availability:** Seattle eliminated January 13.  
**Evaluation question:** offensive/QB résumé and first-time-HC projection.

### Ken Whisenhunt — former Arizona head coach

**Current status:** available after being dismissed by Arizona December 31.  
**Public résumé:** Cardinals HC 2007-12, 45-51; NFC champion/appearance in Super Bowl XLIII; prior Steelers offensive coordinator.  
**Market:** San Diego and other clubs.  
**Evaluation question:** value of prior HC/offensive experience versus reasons for Arizona's decline. Use only evidence available then.

### Lovie Smith — former Chicago head coach

**Current status:** available after Chicago dismissal.  
**Public résumé:** Bears HC 2004-12, 81-63; three NFC North titles; Super Bowl appearance following 2006 season; defensive background. [PHI-LOVIE]  
**Market:** Philadelphia and San Diego had interviews/meetings in the process.  
**Evaluation question:** demonstrated NFL team leadership/defense versus organization-specific desire for change.

### Mike Nolan — Atlanta defensive coordinator

**Current role:** Falcons defensive coordinator.  
**Public résumé:** former 49ers head coach (2005-08) and extensive NFL defensive-coordinator experience. [PHI-FIRST-WAVE]  
**Market:** Philadelphia confirmed interview.  
**Availability:** Atlanta remained alive; postseason restrictions apply.

### Keith Armstrong — Atlanta special-teams coordinator

**Current role:** Falcons special-teams coordinator.  
**Public résumé:** long NFL special-teams coaching career.  
**Market:** Philadelphia confirmed interview; Jacksonville baseline interest. [PHI-FIRST-WAVE] [JAX-MARKET]  
**Availability:** Atlanta remained alive; postseason restrictions apply.  
**Important anti-bias point:** special-teams background is not inherently lesser than offense/defense where the hiring organization's own public criteria are role-agnostic.

### Brian Schottenheimer — St. Louis offensive coordinator

**Current role:** Rams offensive coordinator; previously Jets OC.  
**Market:** Jacksonville planned/reported interest. [JAX-MARKET]  
**Availability:** fully available.  
**Evaluation question:** offensive/QB record and staff projection.

### Mel Tucker — Jacksonville defensive coordinator / assistant head coach

**Current role:** Jaguars defensive coordinator and assistant head coach; had served as Jacksonville interim HC late in 2011.  
**Market:** Jacksonville planned/report interest. [JAX-MARKET]  
**Availability:** fully available.  
**Evaluation question:** internal continuity versus desire for broader organizational reset.

### Greg Roman — San Francisco offensive coordinator

**Current role:** 49ers offensive coordinator.  
**Public connection:** Jacksonville baseline interest; Caldwell knew him professionally/personally from prior history. [JAX-CRITERIA]  
**Availability:** San Francisco remained in the postseason.  
**Rule:** prior relationship is evidence of familiarity, not evidence of a promised preference.

### Brian Billick — former Baltimore head coach

**Current status:** broadcaster/former coach.  
**Public résumé:** Ravens HC 1999-2007; 80-64 regular season, 5-3 postseason, Super Bowl XXXV champion.  
**Market:** Philadelphia interview was reported January 13. [PHI-BILLICK]  
**Evaluation question:** extensive prior HC record versus time out of coaching.

### Mike Zimmer — Cincinnati defensive coordinator

**Current role:** Bengals defensive coordinator.  
**Market:** San Diego publicly reported plans to meet him after Telesco's hire. [SD-TELESCO]  
**Availability:** Cincinnati eliminated in Wild Card round.  
**Evaluation question:** long defensive-coordinator résumé and first-time-HC projection.

### Jim Mora — UCLA head coach

**Current role:** UCLA head coach.  
**Public résumé:** prior NFL head-coaching experience with Atlanta and Seattle; one season at UCLA by the cutoff.  
**Market:** San Diego publicly reported interest/planned meeting. [SD-TELESCO]  
**Evaluation question:** mixed college/NFL HC experience and willingness to leave UCLA.

### Other Chicago baseline candidates

Chicago reporting also connected Mike Sullivan, Joe DeCamillis, Tom Clements, Rick Dennison, and Mike Singletary to the broad search. Their inclusion is evidence of the width of Emery's search, not evidence that every name must receive an identical simulated interview. [CHI-TRESTMAN] [CHI-MARKET]

## 9. Candidate availability / market topology at the snapshot

Legend:
- **Interviewed** = completed real-historical interview publicly established by cutoff; use as market baseline, not immutable sim canon.
- **Planned/reported** = public plan, permission, or credible contemporaneous report.
- **Unavailable/closed** = no longer reasonably in open market at cutoff.
- **Playoff-restricted** = active team still playing.
- **Divergence-sensitive** = real-history action cannot simply be imported because Stone's branch directly changed the candidate's role/availability.

| Candidate | Jacksonville | Arizona | Chicago | Philadelphia | San Diego | Snapshot status |
|---|---|---|---|---|---|---|
| Alex Stone | Scope opportunity | Scope opportunity | Scope opportunity | Scope opportunity | Scope opportunity | Sim candidate; no interview result assumed |
| Mike McCoy | Planned/reported | Interview/talk baseline + attributed strong interest | Reported interest | Interviewed baseline | Jan. 14 scheduled | Available after Denver elimination |
| Ray Horton | — | Interviewed baseline | — | — | — | Available; incumbent AZ DC |
| Jay Gruden | Planned/reported | Interviewed baseline | — | Planned; interview after cutoff | Jan. 13 scheduled/reported | Available |
| Bruce Arians | — | — at cutoff baseline | Reported interest | Permission granted | Public interest / candidate | Available |
| Gus Bradley | — at cutoff JAX baseline | — | — | Permission + reported interview | Reported candidate | Available after SEA elimination |
| Marc Trestman | — | — | Planned/interview candidate | — | — | Available |
| Darrell Bevell | — | — | Reported candidate | — | — | Available after SEA elimination |
| Lovie Smith | — | Reported in broader market | — | Interviewed baseline | Interviewed | Available |
| Ken Whisenhunt | — | Former incumbent, not candidate | — | No completed interview by cutoff | Weekend candidate | Available |
| Mike Nolan | — | — | — | Interviewed | — | ATL playoff-restricted |
| Keith Armstrong | Planned/reported | — | Reported interest | Interviewed | — | ATL playoff-restricted |
| Brian Schottenheimer | Planned/reported | — | — | — | — | Available |
| Mel Tucker | Planned/reported | — | — | — | — | Available |
| Greg Roman | Reported interest | — | — | — | — | SF playoff-restricted |
| Mike Zimmer | — | — | — | — | Planned/reported | Available |
| Jim Mora | — | — | — | — | Planned/reported | College coach; availability not assumed beyond report |
| Brian Billick | — | — | — | Reported interview | — | Available |
| Chip Kelly | — | — | — | Interviewed, then declined/stayed Oregon | — | Unavailable at cutoff |
| Brian Kelly | — | — | Not in Bears field | Interviewed, then stayed Notre Dame | — | Unavailable at cutoff |
| Bill O'Brien | — | — | — | Interviewed, then stayed Penn State | — | Unavailable at cutoff |
| Andy Reid | — | Initial target, then market closed | — | — | — | Unavailable: accepted KC job |
| Doug Marrone | — | — | — | Earlier market connection | — | Unavailable: accepted BUF job |
| Rob Chudzinski | — | — | — | — | — | Unavailable: accepted CLE job |
| Pete Carmichael Jr. | — | — | **Divergence-sensitive** | — | — | Do not import real-history candidacy |

A dash means no relevant connection was established in this research pass by the cutoff. It does not prove there was no private contact.

## 10. How a hiring organization should evaluate the field

### 10.1 Normalize evidence before comparison

For every candidate actually considered in the simulation, reduce evidence to comparable categories:

- current role and authority;
- demonstrated head-coaching experience;
- coordinator/play-calling experience;
- whole-team operational experience;
- staff-building evidence;
- quarterback/player-development evidence where relevant;
- scheme/roster fit where the organization's **frozen** criteria make it relevant;
- prior organizational relationship where documented;
- current availability;
- public competing-market demand where known;
- material documented uncertainty.

Do not create one global weighted score. Different organizations may care about different evidence, but the criteria and any weighting must be established before Stone-specific material is considered.

### 10.2 Equal-evidence rule

If Stone and another candidate possess the same relevant evidence on a criterion, they receive the same treatment.

Stone does not get:
- an "interim HC" bonus larger than a comparable interim HC merely because his season is user-authored;
- a communication bonus because his interview answer is longer;
- an innovation bonus because the user describes his football ideas in more detail;
- a relationship bonus from professional overlap unless an actual communicated relationship is established.

Real candidates do not get:
- an authority bonus from later jobs;
- a success bonus from later careers;
- a scheme bonus inferred from the staff they eventually built;
- a prestige penalty or bonus from hindsight labels.

### 10.3 Search actions are not predetermined

An organization's next action may be:
- request interview;
- defer because of availability;
- decline;
- conduct first interview;
- request second-stage meeting;
- ask for staff/authority detail;
- discuss compensation/term;
- make an offer;
- choose another candidate;
- continue searching.

Those actions arise from the frozen criteria, current field, new simulation interactions, and bounded uncertainty. They do not arise because the historical calendar says a real hire happened on a certain date.

## 11. Divergence adjustments specific to this simulation

### 11.1 New Orleans staff cannot be copied from real 2013 history

The real 2012 Saints finished 7-9 and did not enter the postseason. In this branch Stone's Saints went 12-4, won a Wild Card game, and played through the Divisional Round on January 13.

That changes:
- when Saints assistants become fully available for outside interviews;
- the public résumé attached to Saints coaches;
- which person held which responsibilities;
- how outside organizations might perceive the staff.

### 11.2 Pete Carmichael Jr.

Real-history reporting connected Saints offensive coordinator Pete Carmichael Jr. to Chicago's search.

In this simulation:
- Stone held the Saints offensive-coordinator role from 2009 through April 2012;
- Carmichael remained a major passing-game staff member;
- during Stone's 2012 interim-HC season, Carmichael handled substantial weekday passing-game/offensive coordination as a senior offensive staff member but did **not** hold the OC title;
- user canon establishes that he becomes Saints offensive coordinator only after Stone leaves New Orleans; at this pre-hire cutoff that promotion has not happened;
- he therefore does **not** possess the identical real-world résumé;
- the simulated Saints remained alive through January 13.

Result: the real Chicago-Carmichael candidacy is a **historical comparator only**. Do not insert it as a completed or required simulated interview. If Chicago becomes interested in Carmichael inside the branch, that must arise as a simulation event from his branch résumé and availability.

### 11.3 Aaron Kromer

Real history gave Kromer interim-HC duties during part of the Saints' suspension season. The branch gives the full interim-HC role to Stone.

Therefore:
- Kromer's branch résumé is offensive-line/running-game coach, not real-history interim head coach;
- any later real coaching-market action that depended on his interim title cannot be imported as if the résumé were unchanged;
- his later real staff destinations are prohibited runtime evidence.

### 11.4 Stone's Chargers playing history

Stone's 1986-95 Chargers playing career is branch canon. It makes him a known former Charger, but it does not pre-write San Diego's feelings about him.

Treat:
- playing history = fact;
- organizational familiarity = possible factual channel if documented/generated;
- affection, loyalty, nostalgia, resentment, "homecoming" preference = unknown unless expressed in simulation.

## 12. Research-source register

These are the sources permitted to support the runtime reconstruction. A source published after the cutoff may be used only where explicitly identified as retrospective verification of a fact already true by the cutoff; it may not contribute a later search action or outcome.

### Jacksonville
- **JAX-CRITERIA:** Jaguars, "No timetable on coaching search," Jan. 10, 2013.  
  https://www.jaguars.com/news/no-timetable-on-coaching-search-9337150
- **JAX-MARKET:** Jaguars, "Don't overthink it," Jan. 13, 2013.  
  https://www.jaguars.com/news/don-t-overthink-it-9350736

### Arizona
- **AZ-OPENING:** Cardinals, "Ken Whisenhunt, Rod Graves Relieved Of Duties," Dec. 31, 2012.  
  https://www.azcardinals.com/news/ken-whisenhunt-rod-graves-relieved-of-duties-9248504
- **AZ-CANDIDATES:** Cardinals, "A Look At The Coaching Candidates," Dec. 31, 2012.  
  https://www.azcardinals.com/news/a-look-at-the-coaching-candidates-9254642
- **AZ-KEIM:** Cardinals, "Steve Keim Named General Manager," Jan. 8, 2013.  
  https://www.azcardinals.com/news/steve-keim-named-general-manager-9310937
- **AZ-GRUDEN:** Cardinals, "QB Work Jay Gruden's Strength," Jan. 10, 2013.  
  https://www.azcardinals.com/news/qb-work-jay-gruden-s-strength-9337079
- **AZ-MCCOY-REPORT:** NFL.com, "Arizona Cardinals plan 'major push' to hire Mike McCoy," Jan. 13, 2013. This is attributed reporting, not a hidden-preference fact.  
  https://www.nfl.com/news/arizona-cardinals-plan-major-push-to-hire-mike-mccoy-0ap1000000125658

### Chicago
- **CHI-CRITERIA:** Bears, "Phil Emery wants Bears to contend on consistent basis," Jan. 1, 2013.  
  https://www.chicagobears.com/news/phil-emery-wants-bears-to-contend-on-consistent-basis-9257746
- **CHI-EVAL:** Bears, "Emery updates coaching search during WBBM interview," Jan. 3, 2013.  
  https://www.chicagobears.com/news/emery-updates-coaching-search-during-wbbm-interview-9274340
- **CHI-PROCESS:** Bears, "Bears management has faith in Emery to pick right coach," Jan. 7, 2013.  
  https://www.chicagobears.com/news/bears-management-has-faith-in-emery-to-pick-right-coach-9301623
- **CHI-TRESTMAN:** NFL.com, "Chicago Bears to interview CFL coach Marc Trestman," Jan. 5, 2013.  
  https://www.nfl.com/news/chicago-bears-to-interview-cfl-coach-marc-trestman-0ap1000000122420
- **CHI-MARKET:** NFL.com, "Brian Kelly reportedly not in mix for Bears coach job," Jan. 10, 2013. The Pete Carmichael item in this article is divergence-sensitive and is not imported as runtime fact.  
  https://www.nfl.com/news/brian-kelly-reportedly-not-in-mix-for-bears-coach-job-0ap1000000124524

### Philadelphia
- **PHI-CRITERIA:** Eagles, "Eagles Launch Search For Head Coach," Jan. 1, 2013.  
  https://www.philadelphiaeagles.com/news/eagles-launch-search-for-head-coach-9257041
- **PHI-FIRST-WAVE:** Eagles, "First Wave Of Candidates Emerges," Jan. 2, 2013.  
  https://www.philadelphiaeagles.com/news/first-wave-of-candidates-emerges-9263386
- **PHI-ARIANS-BRADLEY:** Eagles, "Arians, Bradley To Interview With Eagles," Jan. 4, 2013.  
  https://www.philadelphiaeagles.com/news/arians-bradley-to-interview-with-eagles-9284597
- **PHI-WEEKEND:** Eagles, "Eagles Wrap Up Weekend Interviews," Jan. 6, 2013.  
  https://www.philadelphiaeagles.com/news/eagles-wrap-up-weekend-interviews-9295939
- **PHI-LOVIE:** Eagles, "Eagles To Interview Lovie Smith," Jan. 8, 2013.  
  https://www.philadelphiaeagles.com/news/eagles-to-interview-lovie-smith-9310014
- **PHI-LOVIE-COMPLETE:** Eagles, Jan. 10 article confirming the club met with Smith that Thursday.  
  https://www.philadelphiaeagles.com/news/tony-dungy-lovie-a-fit-in-philly-9324544
- **PHI-BILLICK:** Eagles, "Report: Eagles Interviewed Billick," Jan. 13, 2013. The Bradley interview is explicitly reported, not treated as team-confirmed.  
  https://www.philadelphiaeagles.com/news/report-eagles-interviewed-billick-9352945
- **PHI-PLAYOFF-PROCEDURE:** Eagles, "How This Weekend Affected The Search," published Jan. 14, 2013 at 1:34 AM. Permitted only to verify playoff results/availability and interview procedure already fixed by the close of Jan. 13. Do not import later Jan. 14 search actions.  
  https://www.philadelphiaeagles.com/news/how-this-weekend-affected-the-search-9357565

### San Diego
- **SD-GM-FIRST:** NFL.com, "San Diego Chargers to continue GM search from East Coast," Jan. 3, 2013.  
  https://www.nfl.com/news/san-diego-chargers-to-continue-gm-search-from-east-coast-0ap1000000121611
- **SD-TELESCO:** NFL.com, "Tom Telesco hired by Chargers as general manager," Jan. 9, 2013.  
  https://www.nfl.com/news/tom-telesco-hired-by-chargers-as-general-manager-0ap1000000124149
- **SD-ARIANS:** NFL.com, "Bruce Arians interested in San Diego Chargers job," Jan. 10, 2013. Candidate-side interest is not organization-side preference.  
  https://www.nfl.com/news/bruce-arians-interested-in-san-diego-chargers-job-0ap1000000124960
- **SD-LOVIE:** NFL.com, "Lovie Smith interviews with San Diego Chargers," Jan. 11, 2013.  
  https://www.nfl.com/news/lovie-smith-interviews-with-san-diego-chargers-0ap1000000124969
- **SD-GRUDEN:** NFL.com, "Jay Gruden, San Diego Chargers to meet Sunday," Jan. 13, 2013.  
  https://www.nfl.com/news/jay-gruden-san-diego-chargers-to-meet-sunday-0ap1000000125661

### Candidate-market / closed-job sources
- **CAND-MCCOY:** NFL.com, "Chip Kelly, Perry Fewell among top NFL head coach candidates," 2012 candidate overview; Mike McCoy profile.  
  https://www.nfl.com/news/chip-kelly-perry-fewell-among-top-nfl-head-coach-candidates-0ap1000000084807
- **CAND-HORTON:** Same contemporaneous NFL.com candidate overview; Ray Horton profile.  
  https://www.nfl.com/news/chip-kelly-perry-fewell-among-top-nfl-head-coach-candidates-0ap1000000084807
- **CAND-OBRIEN-STAY:** NFL.com, "Bill O'Brien will stay at Penn State after NFL flirtation," Jan. 3, 2013.  
  https://www.nfl.com/news/bill-o-brien-will-stay-at-penn-state-after-nfl-flirtation-0ap1000000121829
- **CAND-CHIP-KELLY:** NFL.com, "Chip Kelly will stay at Oregon, not make jump to NFL," Jan. 6, 2013.  
  https://www.nfl.com/news/chip-kelly-will-stay-at-oregon-not-make-jump-to-nfl-0ap1000000123320
- **CAND-BRIAN-KELLY:** Notre Dame, "Brian Kelly To Continue As University Of Notre Dame Football Coach," Jan. 12, 2013.  
  https://fightingirish.com/brian-kelly-to-continue-as-university-of-notre-dame-football-coach/
- **CLOSED-KC:** Chiefs, January 2013 transactions / contemporaneous team announcements establishing Reid's hire before cutoff.  
  https://www.chiefs.com/team/transactions/2013
- **CLOSED-BUF:** Bills, 2013 transactions establishing Doug Marrone hired Jan. 6.  
  https://www.buffalobills.com/team/transactions/2013
- **CLOSED-CLE:** Browns, 2013 transactions establishing Rob Chudzinski hired before cutoff.  
  https://www.clevelandbrowns.com/team/transactions/2013

## 13. Verification record

### Pass 1 — reconstruction

The first pass:
1. identified the five target-team vacancies and decision-makers;
2. reconstructed only public criteria and roster/organizational conditions available by the cutoff;
3. assembled the real candidate market to prevent anonymous-comparator bias;
4. reconstructed postseason availability;
5. separated confirmed interviews from reported/planned activity;
6. excluded actual later hires.

### Pass 2 — skeptical verification

A second pass specifically challenged the first:
- **Cutoff correction:** "January 14" is now defined precisely as an opening-of-day snapshot with an event cutoff at 11:59 PM ET Jan. 13. This avoids accidentally importing Jan. 14 search actions while preserving the completed Divisional Round.
- **Candidate-status correction:** Chip Kelly is unavailable at the snapshot because his Jan. 6 decision to stay at Oregon is an actual pre-cutoff fact. His later reversal is quarantined.
- **Candidate-status correction:** Brian Kelly is unavailable after Notre Dame's Jan. 12 announcement.
- **Jacksonville correction:** a Jan. 13 team report said no interviews had yet been reported completed, so planned names are not labeled as completed interviews.
- **Arizona correction:** the Jan. 13 McCoy story is labeled attributed reporting rather than converted into a hidden preference.
- **Chicago correction:** Pete Carmichael's real-world candidacy is not imported because Stone's branch changed his role and postseason availability.
- **Philadelphia correction:** reported Billick/Bradley interviews are kept explicitly as reports where the club had not confirmed them.
- **San Diego correction:** media description of an offense-heavy pool is not turned into a private offense-only criterion.
- **Stone neutrality check:** no team criterion in this file was written from Stone's biography, interview pitch, preferred destination, or desired contract.
- **Hindsight scan:** no eventual target-team hire, later coordinator staff, later draft selection, later free-agent move, or later coaching success/failure appears as a resolution input.

## 14. Explicit exclusions

The runtime resolver must never add or consult:
- the actual real hire by any of the five target teams after this cutoff;
- a real later finalist list as if it were already known;
- January 14-or-later interviews as completed cutoff events;
- later coordinator or assistant staffs;
- later staff retention or firing choices;
- later player restructures/releases/signings;
- actual 2013 draft selections as evidence of January priorities;
- later team records;
- later coach firings, awards, championships, reputations, or career trajectories;
- retrospective rankings of the 2013 coaching hires;
- private motives reconstructed from later outcomes.

The simulator is allowed to know the market that existed. It is not allowed to know how that market turned out.
