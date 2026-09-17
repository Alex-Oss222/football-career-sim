# Football Head-Coaching Simulation Rebuild

## Audit, architecture, migration, and stress-test report

**Audit date:** 2026-09-02  
**Files audited:** All 16 supplied source files, completely  
**Rebuild status:** Complete draft; career NOT INITIALIZED  
**Intended use:** Review the corrections and confirm the remaining variables before any in-world event occurs.

---

# A. Direct assessment

## A1. Intended simulation

The intended project is a persistent football-management simulation in which the user authors and controls one head coach while the simulator operates an independent football world. Its subject is not merely play calling. It includes scheme, teaching, staff work, medical boundaries, personnel authority, preparation, game management, labor or eligibility rules, organizational politics, material constraints, public reaction, career movement, and the uneven behavior of real people and institutions.

The core bargain is precise:

- the user owns the protagonist's consequential decisions, words, motives, and career choices;
- other people and institutions own their decisions within an explicit authority structure;
- results follow established conditions, execution, opponents, rules, and bounded variance rather than dramatic need;
- the simulator reveals only information that could reach the coach through a plausible channel;
- dated canonical records, not chat memory or a turn counter, preserve the career.

That is a strong and achievable design target for a chatbox if the state is kept compact, the factual mode is fixed, and the system does not pretend to calculate football more exactly than its evidence permits.

## A2. What is already strong

The source set contains several valuable intentions and pieces of proposed canon:

1. **Clear concern for causality and consequence.** The files repeatedly try to connect preparation, personnel, authority, scheme, resources, and results rather than letting choices operate as magic.
2. **A distinctive proposed coaching identity.** The Stone materials consistently favor fundamentals, individualized teaching, concise communication, honest standards, player context, progressive installation, and responsibility without spectacle. Those are usable preferences once contradictions are resolved and they stop being automatic dialogue.
3. **Attention to organizational work.** The files recognize that a coaching career includes staff construction, contracts, budgets, relationships, career markets, and preparation—not just games.
4. **Useful football taxonomies.** The playbook and play-calling files know that personnel, formations, concepts, protections, fronts, coverages, pressure, motions, situations, and adjustments are different things. Their categories can seed a much smaller installed system.
5. **A desire for exact continuity.** Headers, prior-decision consequences, game statistics, records, schedules, pending matters, and next events are all represented somewhere in the old system.
6. **Audience-specific reputation.** One legacy file recognizes that ownership, players, staff, media, and the public may evaluate the coach differently. That principle survives, without scores.
7. **Preparation as a finite process.** The game-week file understands film study, meetings, installation, individual work, team periods, situation work, travel, and staff coordination. The rebuilt version retains these as constrained modules rather than a universal minute chart.
8. **Real-person and historical ambition.** Candidate dossiers and 2010 materials show an attempt to anchor the world in a particular league and era. The problem is verification and chronology, not the ambition itself.

## A3. Direct verdict on reliability

The supplied system should not be run as written. It is not one coherent simulator; it is several incompatible systems layered together:

- a January 2009 coach/job-search profile;
- a counterfactual Detroit 2009–10 world;
- a purported 2010 cap and draft model;
- a late-2010s/2020s-style offensive catalogue;
- a 16-section “Grinder” dashboard;
- a fixed-turn numerical career engine;
- and an unrelated 2024 high-school-player-to-NFL RPG.

Those layers disagree about protagonist role, chronology, authority, rules, technology, randomization, ratings, output format, and what the user controls. Adding more rules to them would make them less reliable, not more.

### The highest-risk failures

1. **The factual mode is not fixed.** Dates range from January 2009 through a fictional 2010 offseason, while one engine defaults to 2024 high-school football. The exact divergence point is absent.
2. **Alex Stone's biography conflicts with itself.** Playing position, seasons, coaching dates and titles, spouse name and program, relocation constraint, and education differ. The career statistics describe a historically transformative player, not the modest career claimed elsewhere.
3. **Some proposed facts are impossible, false, or chronologically ambiguous.** A 1997 UC San Diego MBA predates the Rady School; the 2008-season Patriots missed the playoffs, while a reference to a playoff loss in calendar 2008 might instead mean Super Bowl XLII after the 2007 season; several real coaches are assigned jobs they did not hold; Kevin O'Connell is treated as a coach while still an active player; and Duce Staley receives a fabricated 2007–09 Steelers coaching career.
4. **The 2010 financial model is structurally wrong.** The NFL's 2010 Final League Year had no salary cap or team salary floor. A fictional $123 million “baseline cap” and derived “space” cannot be used as actual transaction law. Cash payroll, cap accounting, contract value, and budget are mixed.
5. **The draft record cannot reconcile.** A future pick is retroactively called the second overall pick on the May 2009 trade date; a 9–7 record does not by itself yield No. 13; later-round overall numbers ignore rotating tied-team order and compensatory picks.
6. **The game engines cannot maintain a game.** They offer formulas, a faulty random tape, selected highlights, or fixed play counts, but none derives score, clock, possession, down, distance, ball location, timeouts, challenges, penalties, substitutions, and statistics from one persistent event ledger.
7. **The old output forces drama.** It mandates crises, criticism, relationship fractures, harsh costs, personal deterioration, and dozens of decisions. That defeats quiet weeks, independent causality, and fair outcome resolution.
8. **It acts for the protagonist.** Several templates narrate the coach's thoughts, motives, speeches, media answers, fourth-down choices, and personal reactions. Silence even triggers automatic decisions in one file.
9. **It exposes or fabricates private information.** Trust scores, exact thoughts, relationship quality, medical states, substance-use cues, references, endorsements, and hidden plans are presented as knowable. This is especially unsafe for real people.
10. **The playbook is not an installable playbook.** It contains 704 template-generated records numbered 32 through 735 while its index treats missing identifiers as real plays, plus impossible personnel combinations, missing promised sections, conflicting personnel percentages, false expected-yardage precision, and unsupported claims of NFL authenticity.
11. **The era is contaminated.** Pervasive modern RPO language, extreme motion/pistol usage, live sideline analytics interfaces, tablets, NIL, portal rules, and post-2011 contract assumptions appear in a project otherwise pointing toward the 2010 NFL.
12. **Human behavior is mechanical.** Global morale, trust, chemistry, stress, skill, loyalty, job-security, reputation, and “warrior” personality numbers turn people into predictable archetypes.
13. **Career movement is automatic.** Fixed experience gates, skill thresholds, interview clocks, and turn-based promotion replace actual vacancies, competition, fit, resources, reputation by audience, contracts, and independent hiring decisions.
14. **Context use is unsustainable.** Re-reading a 10,298-line play catalogue plus giant turn engines would crowd out current roster, rule, authority, and live-game facts—the information most likely to prevent hallucination.

## A4. Critical factual corrections before migration

- The likely 2010 NFL setting must be treated as **provisional**, not assumed. Official labor history confirms that 2010 was uncapped after the owners' opt-out; it was governed by Final League Year provisions, not a $123 million team cap. See [NFLPA CBA history](https://nflpa.com/about/history/2000s-a-landmark-cba) and the [NFL's uncapped-year explanation](https://www.nfl.com/news/uncapped-year-hasn-t-exactly-led-to-a-spending-spree-09000d5d816fbd4e).
- Only Dallas and Washington later lost future cap room for 2010 contract treatment; that later enforcement cannot be imported automatically after an earlier simulation divergence. See the [NFL's 2012 account](https://www.nfl.com/news/nfl-union-files-suit-against-league-over-2010-cap-09000d5d82948be1).
- Draft assets must be reconstructed from the simulated standings, playoffs, tiebreak procedures, trades, forfeitures, and compensatory awards. The [NFL's official 2010 round-by-round order](https://www.nfl.com/news/full-round-by-round-order-for-2010-nfl-draft-09000d5d81721a24) is a rules and real-history reference, not automatically the alternate world's order.
- The claimed 1997 UCSD MBA is not viable; UC San Diego states that the Rady School was founded in 2003. See [UC San Diego's Rady history](https://today.ucsd.edu/story/ten_years_of_firsts).
- Pre-tablet sideline technology must be preserved in a 2010 mode. The NFL's technology history dates Surface sideline use to 2014 and describes the earlier printed still-photo process. See [NFL Football Operations: evolution of technology](https://operations.nfl.com/game-operations-logistics/technology/evolution-of-technology/).
- Real-person candidate records must use exact-date public history. For example, the [Jets' September 6, 2009 transaction](https://www.newyorkjets.com/news/jets-trade-for-qb-o-connell-on-a-busy-sunday-2512779) establishes that Kevin O'Connell was still a player; the [Cleveland Browns' Duce Staley biography](https://www.clevelandbrowns.com/team/coaches-roster/duce-staley) places his coaching entry with Philadelphia in 2010; and the [Colorado Jon Embree biography](https://cubuffs.com/sports/football/roster/coaches/jon-embree/325) does not support the supplied 2008 Detroit job.

The rebuild therefore quarantines all disputed legacy claims. None becomes simulation canon merely by appearing in a source file.

---

# B. Keep, rewrite, move, convert, or remove map

The following map covers every major functional section of all 16 files. “Convert” means turn the content into dated mutable state, not a stable rule. A section can require more than one action when useful material and defective structure are mixed.

## File 01 — `Alex Stone Coach Profile.json`

| Major section | Disposition | Concise reason/destination |
|---|---|---|
| Metadata | Move | Keep source version/date as migration provenance, not world state. |
| Biographical | Rewrite + move | Put confirmed stable identity in Document 3; derive age from date; define language proficiency; current residence is mutable. |
| Current status | Convert | Employment, target jobs, geography, and contract status belong in dated Current State; remove “level.” |
| Coaching attributes | Remove/rewrite | Delete exact and hidden 0–100 ratings and caps; retain only evidence-based strengths, limits, and uncertainty in Document 3/4. |
| Personality | Remove | Numerical archetypes improperly determine a user-controlled person's inner state. |
| Play-calling experience | Rewrite + move | Reconcile the one-year/two-season conflict and unsupported counts; record verified scope and authority qualitatively in Document 3. |
| Playing career | Rewrite + move | Resolve TE/receiver and 1988–97/1989–98 conflict; confirm whether elite statistics are intentional alternate history and move divergence accordingly. |
| Coaching career | Rewrite + move | Exact titles conflict with real Patriots staffs and file 04; remove unverified salary and single-coach causal claims. |
| Education | Rewrite | The UCSD MBA date is impossible and doctorate label/timeline unclear; obtain exact institutions, programs, dates, and attendance logistics. |
| Financial status | Convert or remove | Use only if high off-field detail is selected; replace net-worth mechanics with material known constraints. |
| Family | Rewrite + split | Stable user-approved facts go to Document 3; present logistics to Document 5; delete relationship/patience meters. |
| Relationships | Rewrite + convert | Record observable contact/history and communicated positions, not private trust, rivalry, or guaranteed references. |
| Network scores | Remove | Replace scores with dated, concrete professional contacts when material. |
| System knowledge | Rewrite + move | Describe public/evidenced experience and uncertainty, not exact knowledge values. |
| Coaching philosophy | Keep + consolidate | Strong portable material; merge with file 04 and file 16 in Document 3. |
| Stress factors | Remove | Arithmetic psychology assigns the user-controlled coach feelings and diagnoses. |
| Job-search status | Convert | Archive the Jan. 2009 snapshot unless it is the chosen start; live applications/interviews belong in Document 5/6. |
| Turn state | Convert | Keep an exact date only if selected; remove turn-as-time and vague carousel trigger. |
| Decision history/pending consequences | Move | Dated events go to Document 6; active unresolved commitments go to Document 5. |
| Validation | Remove | It validates rejected ratings and caps rather than rules, dates, or state invariants. |

## File 02 — `AARON A. KROMER - O-Line Coach.md`

| Major section | Disposition | Concise reason/destination |
|---|---|---|
| Header/contact | Remove | Dummy contact data must not be attached to a real person. |
| Professional objective/availability | Rewrite + convert | Candidate interest is unknown and must emerge through dated contact; actual 2009 Saints employment matters. |
| New Orleans, 2008 | Keep facts + rewrite | Correct role/record; remove Reggie Bush Pro Bowl error and future championship hindsight. |
| Tampa Bay, 2005–07 | Rewrite | Restore exact year-by-year titles; separate evidence from promotional unit claims. |
| Oakland, 2001–04 | Keep facts + rewrite | Preserve public employment and team results; verify scheme/development claims before using them. |
| Collegiate experience | Rewrite | Restore Miami GA, TE/H-back, and OL role sequence plus Northwestern tenure. |
| Playing experience | Rewrite | Use period team name and verified honors; remove unsupported embellishment. |
| Philosophy/competencies | Move + rewrite | Store as preliminary candidate assessment with source, evidence, limitations, and confidence—not objective truth. |
| Professional development | Remove | Unsourced boilerplate adds no decision value. |
| Education | Rewrite | Keep institution/degree only at the confidence supported by sources. |
| References | Remove/convert | Professional overlap may remain; availability or endorsements do not exist until communicated. |
| Relocation and “immediate” availability | Remove | Private, time-sensitive, and inconsistent with actual employment. |

## File 03 — `2010 NFL League-Wide Salary Cap Table.md`

| Major section | Disposition | Concise reason/destination |
|---|---|---|
| Overview | Rewrite + move | Keep uncapped-year fact, define every accounting basis, and source figures in Document 2. |
| League payroll table | Remove/rebuild | It is incomplete, mixes rankings/accounting measures, and understates Detroit relative to [contemporary NFLPA cash-payroll reporting carried by the Associated Press](https://www.bangordailynews.com/2010/12/03/sports/no-nfl-salary-cap-but-no-spending-spree-either/). |
| Detroit “cap situation” | Remove | A fictional $123M baseline creates fake legal cap space in an uncapped year and improperly combines current commitments with later expirations while omitting replacement and future obligations. |
| Detroit strategic conclusions | Rewrite | Use actual contract commitments, cash budget, ownership approval, transaction rules, and uncertainty—not “top-10 flexibility.” |
| Historical context | Rewrite + move | Preserve sourced league context, correct the later penalty account, and quarantine post-divergence history. |
| Source note | Remove/rebuild | “Best available information” is not provenance; use dated proposition-level sources. |

## File 04 — `Alex Stone - Coaching Philosophy & Identity.md`

| Major section | Disposition | Concise reason/destination |
|---|---|---|
| Background | Rewrite + move | Reconcile position, years, Patriots tenure, spouse, and career quality in Document 3. |
| People first | Keep principle; remove/rewrite anecdote | Player context can inform teaching; a tidy sensitive-family story should not become objective proof. |
| Teach, don't tell | Rewrite + move | Keep questioning plus adaptable direct instruction; remove absolutes and guaranteed perfect next reps. |
| Good, Better, Best | Keep if confirmed | Motto is usable; staged statistical anecdote is not canon. |
| Player development | Rewrite + move | Keep individualized evidence and goals; player-sensitive notes belong in Document 4 with source/access limits. |
| Leadership style | Keep principle; remove anecdote | Honest consistent standards are useful; unilateral benching and instant apology require authority and dated canon. |
| Teaching | Rewrite | Concision is a preference, not a universal three-play/five-minute formula. |
| Standards | Keep principle | Remove staged demonstration that guarantees respect. |
| Culture | Rewrite + move | Keep “compete, support, improve” if confirmed; remove warrior/mercenary archetypes and scripted harmony. |
| Communication | Rewrite + move | Keep information-first concision; never auto-generate speeches or volume changes for the user. |
| Teaching through experience | Rewrite + move | Keep only user-confirmed, evidence-based lessons; remove neat retrospective stories that assign reactions or prove the philosophy. |
| Personal life | Move + Rewrite | Stable family facts to Document 3, current logistics to Document 5, future choices remain with user. |
| Failure | Rewrite | Keep error admission/learning principle; correct the false/ambiguous 2008 playoff reference and authority assumptions. |
| Relationships with players/coaches | Rewrite | Replace universal closeness and respect claims with specific observable relationships and uncertainty. |
| Current situation: January 2009 | Convert to mutable state | Preserve only if January 5, 2009 is selected; otherwise archive it as dated prior chronology. |
| Summary | Rewrite + move | Consolidate confirmed principles in Document 3; remove promotional repetition and unapproved motive claims. |
| Overall identity/personal mission | Rewrite + consolidate | Remove idealized résumé praise and any motive the user has not authorized. |

## File 05 — `COACHING CAREER TURN OUTPUT.txt`

| Major section | Disposition | Concise reason/destination |
|---|---|---|
| Protocol/consequence checks | Rewrite | Keep silent causality/agency checks; remove mandatory cost, twist, or new problem after success. |
| Header | Keep + rewrite | Exact date/team/competition/record/focus survive; remove turn primacy and fixed cadence. |
| 1. Identity/status | Move + Rewrite | Stable coach/contract/authority to Document 3; current date/record to Document 5; remove levels, ranks, meters, quotes, and inferred motives. |
| 2. Previous outcomes | Keep purpose + move | Dated decisions/events to Document 6 and compact active consequences to Document 5; delete reward/punishment maturation formulas. |
| 3. Previous-turn narrative | Remove | Duplicates history and invents the coach's reasons, development, and interior cost. |
| 4. Game/activity/media | Remove + Rewrite | Use selected game granularity and a coherent event ledger; remove internal thoughts, auto-dialogue, bias meters, forced fractures, and hostile-media quotas. |
| 5. Holdings/obligations | Move + Rewrite | Organization/resources to Documents 2–5 as appropriate; delete feudal language, tier ratings, mutiny formulas, and fake facility bonuses. |
| 6. Economics/roster | Rewrite + move | Verified rules/budget/contracts/assets to Documents 2, 4, and 5; remove mixed league branches and numerical unit ratings. |
| 7. Staff/front office | Rewrite + move | Roles/authority in Document 3; mutable evidence/workload/disputes in Document 4; remove loyalty/competence meters. |
| 8. Relationships/reputation | Convert | Track dated person/audience-specific evidence without bonds, hostility points, mandatory rivals, or hidden quotes. |
| 9. Personal life/health | Remove by default | Only user-authorized facts and material logistics survive if selected; do not invent diagnoses, substances, thoughts, or firing probabilities. |
| 10. Skills/abilities | Remove | Delete levels, traits, skill points, and exact abilities; use evidence and uncertainty. |
| 11. Ethics | Remove as subsystem | Record actual choices and consequences; no integrity meter, haunting, or generated criminality. |
| 12. Intelligence | Rewrite + move | Head-coach-known scouting with source/date/sample/confidence goes in Document 5; no hidden opponent plan or exact belief. |
| 13. Brutal reality | Remove | Mandatory melodrama and deterioration directly violate natural event emergence. |
| 14. Decisions | Remove + Rewrite | Present one material decision when one exists, with authority/deadline/known/unknown/tradeoffs; no exact crisis quotas or closed menus. |
| 15. Metrics | Remove/split | Keep factual record/standing/stats/budget where valid; delete morale, job-security, health, integrity, network, and relationship arithmetic. |
| 16. Certification/next turn | Remove + Rewrite | Use silent reconciliation, event-based audits, exact next event, and a compact continuity update—not section checksums or turn modulo. |
| Submission format | Remove + Rewrite | Replace the old mandatory paste/menu format with the current-focus decision interface and six-document handoff. |

## File 06 — `2010 Draft Picks.txt`

| Major section | Disposition | Concise reason/destination |
|---|---|---|
| Claimed picks owned | Convert + rebuild | Use round/original club/status until simulated order is actually final; current overall numbers do not reconcile. |
| Traded-away pick | Move | Record the exact dated transaction and approval in Document 6; mirror asset effect in current state. |
| Culpepper/Tampa trade summary | Move | Quarantine pending confirmation as migration evidence; a May 2009 trade cannot know the pick is No. 2. |
| 2009 Detroit 9–7 result | Move | Quarantine pending confirmation as migration evidence; it cannot coexist silently with real 2–14 history. |
| Draft strategy/recommendation | Rewrite + convert | Treat OT or other priorities as dated staff advice based on roster/board/evidence and actual authority, not fact. |
| Overall-pick arithmetic | Remove/recompute | Tied-team rotation, playoff order, compensatory picks, forfeitures, and trades prevent “add 32” calculations. |

## File 07 — `Alex Stone Lions Playbook.md`

| Major section | Disposition | Concise reason/destination |
|---|---|---|
| Title/TOC/provenance | Rewrite | Label as a proposed fictional framework; remove false authenticity, incorrect index, missing-section promises, and truncation note. |
| 1. Identity/philosophy | Rewrite + move | A compact user-approved identity belongs in Document 3; conflicting personnel/QB assumptions do not. |
| 2. Personnel usage | Convert | Only legal rostered, active, installed packages belong in Documents 4/5; delete random quotas and automatic score shifts. |
| 3. Formations | Remove bulk/rebuild | Use a small installed inventory with exact eligible locations, strength, motion, and alignment rules. |
| 4.1 Pass concepts | Keep taxonomy; rewrite | Consolidate duplicates; installed entries need assignments, landmarks, coverage adjustments, protection, personnel, and teaching status. Delete expected yards. |
| 4.2 RPOs | Remove most/research | Impossible cross-products and modern volume are not 2010 canon; retain only legal, era-supported alerts/checks or installed concepts. |
| 4.3 Play action | Rewrite | Name run action, fake, protection, launch, routes, and eligible personnel; empty formations cannot perform absent fakes. |
| 4.4 Screens | Rewrite/consolidate | Define recipient, release, landmarks, timing, and legality; delete plays lacking the required RB/TE. |
| 4.5 Runs | Keep core families; rewrite | Add actual blocking rules, identifiers, tracks, reads, and personnel; remove impossible 00 handoffs and expected yards. |
| 4.6 Gadgets | Remove as core | A tiny, practiced, personnel-legal list may later become mutable weekly state. |
| 4.7 Situations | Rewrite | A weekly call sheet must condition on exact distance, field, score, clock, rules, personnel, and preparation. |
| 5. Blocking/protection | Keep categories; rewrite | Add count/ID/scan, front change, route compatibility, back/TE responsibility, and legal blocker totals. |
| 6. Defensive considerations | Move + rewrite | Store opponent-specific hypotheses with evidence/confidence in Document 5, not universal coverage-counter lookup. |
| 7. Operations | Remove/rewrite | Delete randomization, fixed rates, invented calls, and unsupported team/playbook claims; preserve approved communication/install principles. |
| 8. Indices and promised templates | Remove/regenerate | The index does not match 704 calls and later sections are missing; regenerate only from the installed inventory. |

## File 08 — `COACH ALEX-LAMAR STONE'S GAME IN-DAY PLAY-CALLING SYSTEM.md`

| Major section | Disposition | Concise reason/destination |
|---|---|---|
| Overview/identity | Rewrite + move | Confirm whether Stone is HC, OC, offensive caller, defensive caller, or neither; fixed modern rates are not canon. |
| Opening script | Convert | A weekly conditional opening menu can be useful; rigid 25-play quotas and 85–90% motion are not. |
| Formation inventory | Remove bulk | Replace combinatorial families with a small installed, roster-legal weekly inventory. |
| Concept distribution/timing | Keep taxonomy; rewrite | Distinguish concepts from elements and alerts from RPOs; remove universal timing and depth precision. |
| Scouting process | Keep + convert | Store dated opponent evidence, sample, source, confidence, and uncertainty in Document 5. |
| Quarter-by-quarter approach | Rewrite | Flexible objectives may guide observation; possessions and opponent responses cannot be scheduled. |
| Down/distance matrices | Rewrite | Use current state and matchup rather than predictable universal percentages. |
| Fourth-down rules | Move + rewrite | Head-coach authority and exact score/time/field/kicker/model uncertainty control; no universal go/kick/punt table. |
| Field/hash/score/clock guidance | Rewrite | Correct NFL timing, avoid simplistic hash/FG assumptions, and condition run/pass choices on full context. |
| Coverage identification | Rewrite | Treat alignment/motion as clues, not confirmation; account for disguise, match rules, leverage, and uncertainty. |
| Pressure/protection | Rewrite | Correct count arithmetic and responsibilities; no automatic pressure answer or impossible ten-blocker “nine-man” protection. |
| Motion/audibles | Rewrite | Checks must be installed and QB-authorized; observe legal reset/motion/substitution procedures; remove certainty and fixed rates. |
| Formation selection process | Rewrite + Convert to mutable state | Use only installed, personnel-legal formations selected for the current opponent and situation; do not randomize from a giant inventory. |
| Two-minute/victory | Rewrite to exact rules | Calculate NFL clock, play clock, timeouts, spikes, boundaries, runoffs, and kneels; first downs do not operate like college. |
| Red-zone menu | Convert | Use a compact installed weekly menu and consistent field bands; spread/heavy is matchup-dependent. |
| LOS/tempo | Rewrite | Respect helmet-radio cutoff, actual communication time, and defensive matching rights after offensive substitution. |
| Game-flow responses | Rewrite | Complements and adjustments are hypotheses with install costs, not guaranteed chains. |
| Front/coverage matrices | Remove | Universal counters ignore technique, personnel, numbers, and disguise. |
| Weather/special situations | Rewrite | Treat effects symmetrically and probabilistically; calculate endgame state exactly. |
| Call sheet | Keep + convert | A compact player-specific weekly artifact belongs in Document 5. |
| Communication | Rewrite + move | Document 3 sets HC/OC/QB authority; Document 2 sets period technology and radio rules. |
| Analytics | Rewrite | Use period-available precomputed research or staff advice with uncertainty, not an assumed live modern interface. |
| Defensive system/checklists | Move + Remove | Only the responsible coordinator's approved plan survives; fixed aggression/turnover modes are deterministic and role-confused. |
| Summary/checklist | Rewrite | Keep only a silent readiness and postgame validation checklist. |

## File 09 — `Alex Stone - Media Communication Style Guide.md`

| Major section | Disposition | Concise reason/destination |
|---|---|---|
| Title/current role | Rewrite | “Offensive Coordinator” conflicts with head-coach protagonist; current role/play-calling is mutable. |
| Core traits | Rewrite + move | Store loose, user-approved phrasing tendencies, not motives or absolute behavior. |
| Bad-offense example | Remove | It invents stats, causes, play-calling responsibility, blame, and a promise. |
| Quarterback-development example | Remove | It creates practices and false installation precision. |
| Losing-season/culture example | Remove | It presumes prior failure, damage, philosophy, and guaranteed improvement. |
| Background/science example | Rewrite | Confirm education; remove simplistic neuroscience and fixed practice claims. |
| Benching example | Remove | It speaks for Stone on effort, discipline, role, and future response without authority/user choice. |
| Scheme-complexity example | Remove | It invents installation and omniscient player understanding. |
| Fan-frustration example | Remove | It imports biography and promises improvement/results. |
| Communication patterns/body language | Rewrite | Optional phrasing aid only after the user chooses substance; do not perform the protagonist's body language or motives. |
| Difficult topics | Move + Rewrite | Medical/PR/agency boundaries go to Documents 1/3; all substantive answers require user control. |
| Humor | Rewrite | Dry humor may be a preference; delete scripted cultural stereotypes. |
| “What makes Alex different” | Remove/rewrite | Idealized noble-leader praise is an archetype, not evidence. |
| Tone note | Rewrite | “Generally measured” may be a tendency; identical behavior after every result is not human realism. |

## File 10 — `JON WILLIAM EMBREE - TE Coach.md`

| Major section | Disposition | Concise reason/destination |
|---|---|---|
| Name/role | Convert | Only a dated hire makes him staff; otherwise he is a candidate with interest unknown. |
| Summary | Rewrite | Remove Hall-of-Fame hindsight and development causation. |
| Detroit experience | Remove or explicit counterfactual | He coached Kansas City in 2008; a Detroit role requires an earlier divergence and dated hire. |
| Kansas City | Keep facts + correct | Use 2006–08, include the complete tenure, and avoid claiming sole causation for an established elite player. |
| UCLA | Keep facts + rewrite | Preserve roles and public player achievements, not “developed into” causation. |
| Colorado coaching | Keep + condense | Preserve sourced sequence/associations and correct duration errors. |
| Professional/college playing | Keep verified core | Source medical/comeback detail before use. |
| Education | Keep degree; remove trivia | Dean's List is immaterial unless verified. |
| Philosophy | Rewrite + convert | Candidate interview/evaluation evidence with limitations, not promotional truth. |
| Achievements | Rewrite | Remove future labels, unsupported superlatives, and apparently false “three first-round TEs.” |
| Personal/references | Remove unless material | Do not use private family or implied reference availability as character shorthand. |

## File 11 — `KEVIN W. O'CONNELL - QB Coach.md`

| Major section | Disposition | Concise reason/destination |
|---|---|---|
| Header/contact | Remove | Dummy/private contact data has no canon value. |
| Objective/availability | Remove/convert | In Aug.–Sep. 2009 he was an active player; coaching interest requires release/retirement and actual contact. |
| Patriots experience | Keep + correct | Record complete public playing evidence and exact transaction date; do not call one rookie “two years” of NFL experience. |
| San Diego State | Keep verified facts | Preserve starts/captaincy; remove promotional football-IQ conclusions. |
| Football knowledge | Rewrite | NFL meeting exposure supports a hypothesis, not demonstrated coaching; remove hindsight RPO claims. |
| Education | Keep if verified | Separate degree from playing captaincy. |
| Philosophy | Remove as fact | It is fictional speech retrofitting later coaching identity to a real 24-year-old player. |
| Competencies/attributes | Rewrite | Track tools, risks, and unknown teaching/administrative ability, not “natural” proven coaching. |
| Coaching interests | Convert | Private intentions emerge only through simulation after divergence. |
| References/quote | Remove | The attributed endorsement and availability are unsourced. |
| Additional/current date | Rewrite | Use exact date because Aug. 30, Sept. 1, and Sept. 6, 2009 materially change club status. |

## File 12 — `DUCE STALEY - RB Coach.md`

| Major section | Disposition | Concise reason/destination |
|---|---|---|
| Header/contact/objective | Remove/rewrite | Dummy data and three years of coaching are false; potential interest remains unknown. |
| Pittsburgh coaching/scouting | Remove | The 2007–09 staff role did not occur unless divergence is deliberately moved before it. |
| Pittsburgh playing | Keep verified core | Remove false immediate coaching transition and unsupported development causation. |
| Philadelphia playing | Keep + correct | Correct 1,000-yard seasons to 1998, 1999, and 2002; source captain/mentoring claims. |
| Career totals | Keep if material | Public playing evidence can inform—but not prove—coaching tools. |
| College | Keep facts + rewrite | Remove “elite vision” as objective conclusion. |
| Coaching qualifications | Rewrite | Present a novice former-player candidate with unknown teaching, planning, and staff competence. |
| Proven development | Remove | Claims rest on nonexistent employment or later outcomes. |
| Philosophy | Rewrite only if elicited | Do not attribute invented beliefs to a real person; remove medically irresponsible universal comeback lesson. |
| Competencies | Rewrite + enforce boundaries | Playing experience may suggest knowledge; medicine, nutrition, scouting, and performance remain other departments' authority. |
| Achievements | Keep corrected playing facts | Delete all fabricated coaching achievements. |
| Community/personal/education | Remove from active canon unless relevant and sourced | These do not prove coaching character or willingness to relocate. |
| References/endorsements | Remove | The real-person quotations are unsourced and should never be invented. |
| “Why hire me”/date stamp | Remove/replace | Promotional duplication and false employment do not become evidence. |

## File 13 — `UNIVERSAL TURN-BY-TURN.md`

| Major section | Disposition | Concise reason/destination |
|---|---|---|
| Core identity/meta | Rewrite | Keep causality, role realism, and time feasibility; remove “Grinder,” formula supremacy, and self-certification. |
| Framework/output/enforcement | Remove | Fixed weekly/biweekly/five-day turns and 16 required sections cause boilerplate and chronology errors. |
| Timeline/activity constraints | Rewrite | Use exact dates and real schedule; finite install time survives without arbitrary “one decision per turn.” |
| Hierarchy | Rewrite | Use organization-specific authority, not percentage power or title-based skill caps. |
| Game/skill/stress mathematics | Remove | Cannot generate coherent football state and improperly diagnoses/controls people. |
| Career system | Rewrite | Competence, evidence, networks, vacancies, fit, and competition survive; thresholds and relationship gates do not. |
| Event emergence | Keep principle + rewrite | Organic events survive; “balance” and quotas bias outcomes. |
| Relationships/reputation | Convert | Qualitative person/audience-specific evidence replaces points. |
| Finances | Move/limit | Competition economics to Document 2; material coach contract/budget to Documents 3/5; no speculative tax/net worth engine. |
| Mandatory decisions/triggers | Remove | Exact crises, secondary choices, revolt/morale, health, and firing triggers manufacture drama. |
| Integrity/execution | Rewrite + move | Compact reconciliation belongs in Documents 5/6; remove visible math, fixed next-turn rules, and section counts. |
| Input/full-save paste | Remove | Canonical documents and handoff replace repeated giant prompt pastes. |
| Continuity | Keep + move | Dated material user decisions/consequences belong in Document 6. |
| Certification | Remove | A prompt cannot certify its own accuracy. |
| Grounding/archetypes | Rewrite | Keep anti-caricature and feasible-action aims; remove ban on useful options and claims of supremacy over user/system instructions. |
| Mandatory proportional cost | Remove | It forces every success to cause permanent loss or enemies. |
| Labels/failure audit | Rewrite | Evidence-based descriptors are useful; event-triggered audits replace debug output and turn counters. |

## File 14 — `FOOTBALL CAREER SIM 3.0.txt`

| Major section | Disposition | Concise reason/destination |
|---|---|---|
| Random tape | Remove | It contains 10,000 values, an invalid 913, 1–100/0–99 mismatch, and contradictory 2,000/10,000 pointer logic; use internal bounded randomness after plausibility is set. |
| 2024 high-school initialization | Remove | Wrong protagonist, role, league, era, and team. |
| Difficulty/harsh realism | Remove | Buffs, penalties, mandatory criticism/injuries/controversy, and worst-outcome rules predetermine adversity. |
| Attribute caps | Remove | Universal hidden ratings and anti-cheating gates conflict with qualitative uncertainty. |
| Calendar | Rewrite | Exact dates/events replace 26 two-week turns and month-locked activities. |
| Measurables/stat formulas | Remove | False precision, no game-state reconciliation, and mathematical errors including the inverted BMI factor. |
| Opponent generation | Rewrite | Persist independent full organizations; do not create a team from five ratings or scale it to protagonist skill. |
| Personality | Remove | Five archetypes deterministically govern human behavior across unrelated domains. |
| Academics | Remove from NFL; rebuild if selected | Exact governing/institutional rules belong in Document 2; invented GPA/APR mechanics do not. |
| Transfer portal | Remove from 2010; rebuild if selected | Use exact-season rules only; current portal mechanics are anachronistic. |
| Chemistry | Remove | Person/group evidence replaces one global modifier. |
| Injury | Rewrite | Medical-led availability and uncertainty replace generic risk tables, exact deductions, and personality-shortened recovery. |
| Development | Rewrite | Longitudinal evidence replaces rolls, fixed age curves, and point gains. |
| NIL | Remove from 2010 | Only an exact applicable college-era sourcebook could activate it. |
| Draft | Move/rebuild if relevant | Exact rules, player agency, and personnel authority replace deterministic scores and auto-declaration. |
| Contracts/money | Rewrite | Exact selected-era rules and authority replace 2024 markets, post-2011 rookie scale, tax, and investment simulation. |
| Retirement | Remove | No mandatory age or score trigger. |
| Coaching conversion | Remove | Protagonist is already an HC; playing traits do not mechanically become coaching ability. |
| Skill progression/career ladder | Rewrite | Evidence, vacancies, fit, networks, process, and independent hiring replace XP/gates/salary bands. |
| Playbook management | Move + rewrite | Stable philosophy to Document 3; installed/current scheme to Documents 4/5; remove rating prerequisites and fixed bonuses. |
| Game engine | Remove | It equates decision quality with success and lacks legal game state. |
| Delegation/situations | Rewrite | Actual authority, competence, workload, and user control replace fixed capacity and skill-scaled problems. |
| Interviews | Rewrite | User supplies substantive answers; independent, organization-specific processes replace fixed stages/scores/probabilities. |
| Coaching turn template | Remove + Rewrite | Use Documents 1/5 response protocol; delete visible hidden ratings and auto-selected HC calls. |
| Skill development | Remove | Evidence and gradual learning replace clinics/XP/decay. |
| Staff management | Convert | Document 4 holds observations and uncertainty; no exact true ratings or guaranteed multipliers/departures. |
| Media | Rewrite | Audience/source-specific reactions replace media-as-ally points and mandatory viral outcomes. |
| Rival coaches | Remove | Independent coaches replace matched-skill mirror/opposite archetypes. |
| Realignment | Remove unless material | If selected, research actual institutional process; no HC-driven invitation meter. |
| NFL-specific appendix | Move/rebuild | Exact 2010 roster/transaction/finance rules and authority replace cap-space and trade-win mechanics. |
| Stress/burnout | Remove | Track known workload and user-authorized personal facts, not diagnosis or gamified family cost. |
| Legacy/Hall of Fame | Remove | Audience-specific reputation and real selection processes replace points. |
| Commands/validation/templates/automation | Remove | Duplicative dashboards, visible dice, auto-decisions, and self-certification violate agency and continuity. |
| Dialogue enforcement | Remove | Mandatory hostile or corrective dialogue speaks for the protagonist, stereotypes other people, and forces drama. |

## File 15 — `SEAN M. McVAY - WR Coach.md`

| Major section | Disposition | Concise reason/destination |
|---|---|---|
| Header/contact | Keep name; remove private/dummy data | Candidate identity is public; fabricated contact information is not. |
| Objective | Rewrite + convert | Candidate status and interest require an exact date and actual post-divergence contact. |
| Tampa Bay, 2008 | Keep + correct | Use “offensive assistant” unless stronger dated evidence supports another title; Antonio Bryant was not a Pro Bowler. |
| Florida Tuskers, 2009 | Keep facts + rewrite | Preserve WR/QC context and 6–0/title-game result; attribute detailed duties as résumé/interview claims if unsourced. |
| Education | Keep verified core | Use degree/public recognition; verify Dean's List, award label, and coursework before use. |
| Playing experience | Keep facts + qualify | Preserve public stats/achievements; captaincy/scheme/leadership claims need source or attribution. |
| Philosophy/competencies/attributes | Move + rewrite | Treat as stated views and uncertain evaluator hypotheses for a 23-year-old, not later-career genius. |
| Connections | Keep verified overlap | Relationships provide context/access, not automatic competence or loyalty. |
| References | Remove/convert | Do not assume calls or endorsements; record only if they occur. |
| Actual 2010 Washington job | Move | Quarantine it as future-history research after divergence; it must not occur automatically if simulation diverges earlier. |

## File 16 — `Game Week Preparation - Offense (Regular Season).md`

| Major section | Disposition | Concise reason/destination |
|---|---|---|
| Core principles | Keep + rewrite + move | Fundamentals, active film, progressive install, and position ownership go to Document 3 without perfection absolutes. |
| Sunday-game schedule | Convert | Build a dated weekly plan from labor rules, recovery, staff authority, travel, shared field time, and user priorities—not fixed minute blocks. |
| Thursday short-week schedule | Rewrite | Its chronology can begin before the preceding Sunday game and its physical load is unrealistic; retain simplification/recovery aims. |
| Monday-game schedule | Convert + correct | Resolve mislabeled hotel/stadium arrival and tailor to actual prior game, off day, travel, and kickoff. |
| Staff coordination | Rewrite + split | Document 3 defines decision boundaries; Document 4 tracks workload. Resolve overlapping protection and combined TE/WR roles. |
| Competitive elements | Keep as optional methods | Use only when teaching goal/personnel warrant them; do not mandate contests in every session. |
| Standards/evaluation | Rewrite + split | Stable evidence-oriented principles to Document 3; weekly observations to Documents 4/5; no causal guarantee that preparation wins. |
| Contingencies | Keep + rewrite | Triggers require medical/performance/operations input; actual adaptations consume reps and enter Current State. |
| Final philosophy | Rewrite | Remove promotional repetition and deterministic “Sunday demonstration” claims. |
| Technology/workload assumptions | Move + Rewrite | No assumed 2010 tablets; account for player off time, phase rules, treatment, special teams, defense, contact, and travel. |
| Halftime/postgame protocols | Rewrite | Parallelize or fit actual time; avoid universal mandatory mini-meetings. |
| Alex's role | Move + Rewrite | File treats him as an offensive subordinate presenting to an HC, which conflicts with the requested protagonist role; resolve it in Document 3. |

---

# C. Recommended architecture

The rebuilt system uses exactly six principal canonical documents. This audit report is migration-only: it is not a seventh in-world canon file, must not be loaded during play, and must not be included in a new-chat handoff. After mode lock, the active sourcebook likewise excludes unchosen candidates and actual-future comparator material.

| Document | Stability | Function | Normal read/update rule |
|---|---|---|---|
| 1. Project Instructions | Stable | Agency, realism, research, information, time, outcome, response, continuity, and correction rules | Load as governing instructions; amend only by explicit user direction/correction. |
| 2. League, Era, and Sourcebook | Stable, versioned | Exact mode and detail settings, governing rules, calendar, roster/labor/eligibility/finance structure, technology, social/historical setting, sources, divergence | Consult whenever a rule, date, mechanism, or factual snapshot matters; version source changes. |
| 3. Head Coach, Organization, and Authority Canon | Mostly stable, versioned | User-created coach facts, contract, responsibilities, play-calling, authority map, organization, staff structure, standing instructions | Consult for every material authority/agency question; version jobs or contract/role changes. |
| 4. Roster and Staff Register | Mutable records | Player/non-protagonist-staff status and commitments, roles, depth/packages, availability/effectiveness, evidence, workload, development, person-specific relationships, and detailed current financial/eligibility reconciliation | Update affected records transactionally; do not rewrite unaffected people. |
| 5. Current Season State | Mutable replacement snapshot | Exact date, source-version manifest, global checkpoint, phase, schedule window, record, derived availability/resources, strategy, recent decisions, pending matters, deadlines, knowledge boundary, live game | **Read in full before every response.** Replace with a fresh compact snapshot after state advances. |
| 6. Chronology, Game Ledger, and Handoff | Append-only with explicit supersession | Dated events, results, decisions, transactions, injuries, staff/career changes, game events/stats, audits, corrections, archives, handoffs | Append material events; never erase a superseded record; generate handoff after required audit. |

## C1. Ownership boundaries

- Document 1 owns the stable operating rules.
- Document 2 owns mode, game/career detail settings, divergence, competition rules, calendar, era, and sources.
- Document 3 owns head-coach canon and contract, durable organization/relationship canon, audience-specific career reputation, and the sole final-authority map.
- Document 4 owns the latest coach-known player/non-protagonist-staff status, commitments, roles, packages, availability, workload, person-specific staff relationships, current evaluation, and detailed current financial/eligibility reconciliation.
- Document 6 owns dated events, corrections, game evidence, results, and cumulative statistics.
- Document 5 is a derived resume snapshot, exact source-version manifest, and global package-checkpoint pointer; it owns only current non-person logistics for which no detailed register exists.

If the same field appears as a summary in Document 5, the designated detailed document remains authoritative. A mismatch is a contradiction, not permission to choose whichever value is convenient.

## C2. Operating cycle

1. Before a response, read Document 5 in full and reconcile relevant Documents 1–4 plus the latest handoff/ledger entries.
2. Present only information available through plausible channels and stop before a consequential coach choice.
3. After a user choice, simulate only authorized routine implementation until the next meaningful branch.
4. Stage and validate a candidate bundle outside the active canonical copies. Candidate Document 6 receives decision/event/correction entries first; revise Document 1 only for an explicit stable-instruction change; version Documents 2 or 3 if their owned content changed; create Document 4 only if its owned content changed; always build a replacement Document 5 with the exact effective Document 1–4 versions.
5. Run required invariants and any event-triggered continuity audit. Close and promote the candidate bundle only when Document 5's target global checkpoint/version manifest matches candidate Document 6's close line and register row. Unchanged Documents 1–4 retain older content-changing pointers without conflict.

## C3. Games, seasons, career changes, and new chats

- A game is initialized in Documents 5 and 6 from a verified pregame packet. Each response ends with one exact checkpoint. The event ledger proves score, possession, clock, and statistics.
- A completed game triggers a full audit before the next event. The schedule/result, record, standings, injuries, and ex-ante decision evaluations are reconciled.
- At a season-phase boundary, Document 6 archives the phase totals and unresolved matters; Document 5 is replaced for the new phase. The sourcebook is versioned only if rules/calendar change.
- A team change creates a frozen team-tenure closure record and roster/staff snapshot in Document 6, versions and re-locks Document 2 for the new team/competition, versions Document 3 for the new contract/authority, rebuilds Document 4, and carries unresolved old-team matters until independently resolved.
- A new chat uses Document 5's global checkpoint and exact Document 1–4 version manifest, the matching Document 6 closed checkpoint, and only the later or expressly named ledger excerpts needed for active matters. It never requires an entire season or the old chat.
- A mid-game handoff is permitted only after the exact live checkpoint and score/possession/stat invariants pass.

---

# D. Complete rebuilt documents

The complete replacement documents are supplied as separate canonical files so they can be updated without duplicating or corrupting unrelated state:

1. `01_Project_Instructions.md`
2. `02_League_Era_and_Sourcebook.md`
3. `03_Head_Coach_Organization_and_Authority_Canon.md`
4. `04_Roster_and_Staff_Register.md`
5. `05_Current_Season_State.md`
6. `06_Chronology_Game_Ledger_and_Handoff.md`

They are complete usable templates, not outlines. Genuine unknowns are labeled. The possible 2010 Detroit material is kept in a clearly marked provisional/quarantine section and is not an initialized world.

---

# E. Migration plan

## E1. Freeze and classify the legacy material

1. Preserve the 16 source files as read-only migration evidence.
2. For every asserted fact, attach one provenance class: verified public pre-divergence fact; explicit user-created canon; dated simulation event; attributed claim; evaluator inference; proposed preference; template text; or unresolved conflict.
3. Do not migrate template examples, placeholder numbers, headings, résumé advocacy, future-history hindsight, hidden ratings, or repeated claims as facts.
4. Establish one exact divergence point before importing any counterfactual employment, result, trade, roster, or relationship.

For runtime, normalize the migration labels to the shared canon classes in Documents 2–6: verified pre-divergence fact; user canon; post-divergence simulation event; attributed report or assessment; labeled inference; unresolved legacy claim; undetermined; or quarantined actual-future comparator (authoring only). An intentional counterfactual baseline is user canon plus a divergence entry. “Template text” and “proposed preference” have no factual force until the user adopts them. Evidence strength and ledger record form are recorded separately from canon class.

## E2. Reconcile the head coach first

Create a conflict-resolution worksheet from file 01, file 04, file 09, and file 16. The user confirms exact identity, playing position/seasons/statistics, education, coaching posts/titles, family naming, geographic preference/constraint, and whether the career itself altered real history before 2009. Record confirmed stable facts in Document 3 and the corresponding dated events in Document 6. Archive rejected variants as superseded source claims; do not silently delete the fact that they conflicted.

Do not convert Stone's ratings, personality totals, stress, network, or relationship values. Where a rating was trying to express something useful, translate it into an attributed qualitative claim plus its evidence and uncertainty.

## E3. Lock the league snapshot and divergence

1. Confirm competition, team, season, exact date, and mode.
2. Build Document 2 from rules and sources effective on that date.
3. For a real team, load the exact-date roster, staff, schedule, transactions, public injuries, record, standings, deadlines, and material contracts/eligibility.
4. Mark all earlier real events fixed. Mark later actual history unavailable as canon.
5. If the fictional 2009 Detroit season is retained, rebuild every downstream fact—standings, same-place schedule opponents, draft order, transactions, staff history, and knowledge—from the altered world rather than mixing it with real 2010 results.
6. Create the locked runtime edition of Document 2 containing only the selected mode, approved institutional-rules rail, and applicable sources. Leave the provisional candidate and actual-future comparators in this migration report, not in runtime context.

## E4. Rebuild organization, staff, and authority

1. Record the actual or user-confirmed reporting line, contract, and 22-item authority map in Document 3.
2. Treat Kromer, Embree, O'Connell, Staley, and McVay as exact-date real people with public history only. Any interest, interview, reference call, retirement, offer, acceptance, or hire occurs after divergence and is recorded as a simulation event.
3. A person hired into the altered world receives a Document 4 staff record containing role, authority, responsibilities, workload, demonstrated evidence, limitations, uncertainty, career incentives, and last update. Later real-world success is never imported as a hidden ability.
4. Keep staff job titles/decision rights in Document 3 and operating evidence/status in Document 4 to avoid duplicate authority.

## E5. Rebuild roster, assets, and schedule

1. Load each player once into Document 4 from the chosen exact-date roster.
2. Reconcile contract/eligibility status, roster designation, depth, packages, special teams, health source, and availability separately from effectiveness.
3. Rebuild draft assets from a transaction ledger. If the Culpepper/Tampa trade is confirmed, record what was known on May 8, 2009—Tampa's 2010 first, not “pick No. 2”—then determine final position only from the simulated completed season/order process.
4. Rebuild financial state using the actual selected-era legal structure and the organization's cash/contract/budget facts. Document 4 owns the detailed current reconciliation; Document 5 displays only a decision-facing derivative. Never carry the fake $123M 2010 cap forward.
5. Recompute the schedule if altered standings change schedule-formula opponents. Do not import the actual real-world schedule blindly.

## E6. Reduce the scheme to what can be installed

1. Archive files 07 and 08 as noncanonical design references.
2. Ask the user to confirm a compact offensive identity and the coach's play-calling role after the roster and era are known.
3. Create a small installed core with legal personnel, exact assignments/protections, teaching status, and actual player fit. Treat modern concepts as intentional counterfactual innovation only when period-feasible and paid for in installation/communication costs.
4. Put stable philosophy and terminology ownership in Document 3, actual personnel/package responsibilities in Document 4, and the current opponent plan/call sheet in Document 5.
5. Never migrate “expected yardage” or universal counter tables into outcome resolution.

## E7. Establish the first snapshot without beginning play

Build candidate Document 5 with the confirmed exact date, source-version manifest, roster reconciliation, staff roles, record, schedule window, public availability, active deadlines, current knowledge, and unresolved decisions. Build candidate Document 6 with all accepted pre-start chronology and a first audited handoff. After validation, close candidate Documents 3, 5, and 6 together as `READY` under one pre-initialization global checkpoint. Stop there.

Only after the user explicitly instructs initialization may the simulator surface the first in-world decision.

## E8. Ongoing preservation rules

- Each material user decision is recorded exactly enough to prevent later motive invention.
- Each transaction, injury-status change, staff action, game result, and correction receives an exact date and source/channel.
- Current State is replaced; the ledger is appended and explicitly superseded when corrected.
- At every new chat, use the audited handoff rather than reconstructing events from memory.

---

# F. Stress test and corrections

## F1. Failures exposed before finalization

The first draft failed its own QA in ways the legacy system could not detect. Every failure below was corrected before this version was packaged:

1. Documents 1, 4, and 6 gave incompatible commit orders.
2. A stale Current Season State could outrank the detailed field owner.
3. Interrupted replace-in-place updates lacked a shared last-closed marker.
4. Corrections could be written after dependent state rather than before it.
5. Ex-ante decision evaluation was optional, allowing outcome hindsight.
6. The four-response non-game audit cadence had no durable counter.
7. A new-chat handoff could require an entire season of ledger entries and had no pre-phase fallback.
8. Live checkpoints omitted running/stopped clock status, restart basis, administrative phase, and next-half/overtime possession entitlement.
9. Game events were validated statistically without a canonical postgame and cumulative season-statistics register.
10. A midseason team change could leave the former team's sourcebook and mutable roster controlling.
11. Pre-initialization history and corrections were required by migration but prohibited by the ledger.
12. User-visible files could contain facts expressly unknown to the head coach.
13. Final authority was duplicated outside Document 3 and could drift.
14. Roster summaries mixed nested game-day designations with disjoint primary statuses.
15. Medical clearance, public designation, communicated limitation, and football effectiveness were insufficiently separated.
16. The audit/provisional future-history material could leak into runtime context.
17. Mutable coach logistics had no current-state destination.
18. Several supplied headings lacked an explicit disposition and some disposition labels fell outside the requested classification.
19. One pointer was still being asked to mean both the package's latest closed state and an individual file's last content change; unchanged files could never satisfy that rule.
20. Documents 3, 5, and 6 required one another to be `READY` without a simultaneous administrative transition.
21. Document 6 used a narrower provenance vocabulary than the shared canon classes and did not separate canon class from ledger record form.
22. Current financial aggregates were duplicated between the detailed register and current snapshot.
23. The head coach's contract was accidentally included in Document 4's general person-contract language despite Document 3 ownership.
24. Game granularity and career/off-field detail were stored canonically in both Documents 2 and 3.
25. Current person-specific staff relationships were duplicated in Documents 3 and 4.
26. The mandatory ex-ante decision record had a live-game form but no general non-game form.

The corrected documents now use one field owner per data type, separate global-package and per-document-content pointers, a simultaneous pre-start readiness close, a shared provenance vocabulary, general and live ex-ante decision records, one closed-update sequence, coach-facing canon only, a bounded certified handoff, exact live restart state, frozen team-tenure closures, separate medical and roster dimensions, and Document 6 as the sole event/correction/statistical history.

## F2. Executed six-response live-state fixture

This is a **noncanonical validation fixture**, not a career game, scene, historical claim, or initialized simulation. Team A is the abstract protagonist team. The fixture rules specify protagonist-team-first scoring, a 40-second ordinary play clock, a 25-second reset after the two-minute warning, final-five-minute out-of-bounds clock stoppage, a seven-yard field-goal placement, and a kickoff touchback at Team B's 25.

Starting state: Team A trails 17–20 with 2:18 left in the fourth quarter; Team A has first-and-10 at its own 42 going toward Team B's goal; the game clock is stopped, play clock 40; timeouts A 3/B 2; challenges available A 2/B 1; no review, penalty, medical stoppage, or substitution issue.

| Response checkpoint | Complete committed delta | Score A–B | Clock / play clock | Possession, down, and spot | Timeouts / challenges | Decision or administrative state |
|---:|---|---:|---|---|---|---|
| 1 | A completes for 8 yards and receiver exits bounds | 17–20 | 2:11, stopped; 40 | A, 2nd-and-2 at 50 | TO 3–2; challenges 2–1 | Ready for snap; pass totals +1 completion/+1 attempt/+8 |
| 2 | A rushes 3 yards in bounds; clock reaches two-minute warning | 17–20 | 2:00, stopped; 25 after warning | A, 1st-and-10 at B47 | TO 3–2; challenges 2–1 | Two-minute warning complete; rush totals +1/+3 |
| 3 | Incomplete pass, then 12-yard completion in bounds | 17–20 | 1:45, running; 40 | A, 1st-and-10 at B35 | TO 3–2; challenges 2–1 | Timeout choice pending; test input is **no timeout**, logged ex ante before response 4 |
| 4 | Under the no-timeout choice, A rushes 6 to B29, then takes a 7-yard sack | 17–20 | 0:50, running; 40 | A, 3rd-and-11 at B36 | TO 3–2; challenges 2–1 | Timeout choice pending; test input is **A timeout**, logged before response 5 |
| 5 | A timeout is charged; A then completes for 9 yards and receiver exits bounds | 17–20 | 0:44, stopped; 40 | A, 4th-and-2 at B27 | TO 2–2; challenges 2–1 | Fourth-down choice pending; test input is **44-yard field-goal attempt**, logged and evaluated ex ante |
| 6 | Field goal is good at 0:39; ensuing kickoff is a touchback | 20–20 | 0:39, stopped; 40 | B, 1st-and-10 at B25 | TO 2–2; challenges 2–1 | Ready for B snap; no pending review/penalty; field goals 1/1 |

Fixture validation:

- Spot sequence reconciles: A42 +8 = 50; +3 = B47; +12 = B35; +6 = B29; sack 7 = B36; +9 = B27.
- Score changes only on the recorded field goal, from 17–20 to 20–20.
- Game clock never increases; every stopped/running transition has a stated rule basis.
- Team A uses exactly one timeout; challenge counts do not change.
- Possession remains with A through the field goal and transfers only through the ensuing kickoff.
- Cumulative deltas through checkpoint 6 are preserved: passing 3 completions on 4 attempts for 29 yards, rushing 2 for 9, one sack for 7 lost, and one made field goal. Competition-specific official-stat conventions would control the final team-net calculation.
- A new chat can resume solely from checkpoint 6 plus the certified game aggregate: score 20–20, 0:39 fourth quarter, B ball at B25, first-and-10, clock stopped, play clock 40, timeouts 2–2, challenges 2–1, no administrative issue.

This trace exposed and drove the additions for clock status, restart basis, administrative state, possession entitlement, cumulative statistics, ex-ante decision entries, and shared closed-update markers.

## F3. Required scenarios

| Test | Failure the legacy system would produce | Final-system behavior and correction | Result |
|---|---|---|---|
| 1. Game continues across six turns | No single ledger proves score, clock, possession, spot, timeouts, or prior play; highlights/formulas drift. | The executed fixture above preserves six exact checkpoints. Document 6 owns event/stat evidence; Documents 4/5 close through the same update marker. | Pass after correction |
| 2. User delegates offensive calls but faces late fourth down | Legacy delegation or template may auto-select go/kick/punt. | Document 3 separately assigns ordinary offensive calling and retained game-management authority. Document 1 requires a stop; staff may recommend, but the user decides within the decision clock. | Pass |
| 3. Major injury to a nonfocus player | It is missed or becomes a random-tape drama with an exact recovery. | Urgency may interrupt one-team focus only through a plausible sideline/medical channel. Documents 4/5/6 update availability, roster effect, and known uncertainty; diagnosis/return remains medical. | Pass |
| 4. Medical personnel rule out a wanted player | Ratings or “warrior” traits shorten recovery; coach may practice through injury. | Document 3 gives medical staff final diagnosis/clearance. The unavailable designation blocks use. User may choose among legal replacements or address process, not overrule medicine. | Pass |
| 5. GM/AD rejects a personnel request | Relationship/skill score determines acceptance or creates a villain. | The authority map controls. Rejection stands unless the authorized decision-maker changes it. The user may persuade, revise, escalate through actual channels, accept, or choose another plausible action, including a resignation threat only if the user chooses it. | Pass |
| 6. Coordinator recommends conflict with established strategy | Opponent-perfect adjustment is auto-installed or disagreement becomes a feud. | Recommendation is attributed with evidence and uncertainty. If material, implementation stops. The head coach decides only within established authority; disagreement and relationship effect are recorded only if observable. | Pass |
| 7. Statistically sound fourth-down decision fails | Old engine treats “good” as success or imposes a compensating lesson. | A consequential decision cannot be resolved until its ex-ante entry is committed. Outcome is resolved independently; postgame evaluation preserves sound process and bad result separately. | Pass after correction |
| 8. Questionable decision succeeds | Outcome retroactively validates the call. | The same mandatory pre-result record preserves limited evidence or weak reasoning. Successful execution/result does not erase the ex-ante concern. | Pass after correction |
| 9. Quiet bye week | Mandatory crises, criticism, injuries, or 20 decisions appear. | Document 1 permits compression through routine recovery, self-scout, personnel work, and ordinary life until the next meaningful choice. “No material event” is a valid result. | Pass |
| 10. League rule differs from generic football knowledge | A modern NFL/NCAA rule is silently substituted. | Date-specific Document 2 controls. If absent, pause, research an authoritative source, version the sourcebook, and only then resolve the action. | Pass |
| 11. Real historical season diverges | Actual future injuries, hires, schedule outcomes, and draft slots leak back in. | Pre-divergence facts are fixed; post-divergence simulation events control. Actual future history is quarantined and cannot serve as hidden knowledge. Downstream schedule/order is recomputed from altered state. | Pass |
| 12. New chat resumes midseason | Giant prior chat or turn summary is needed; commitments vanish. | A certified closed checkpoint supplies governing versions, exact Document 5, active matters, and only named later excerpts; it has a starting-baseline fallback and never requires an entire season. | Pass after correction |
| 13. New chat resumes live game | Last narrated paragraph is ambiguous about state. | The required checkpoint now includes clock/restart, administrative phase, toss/possession entitlement, current drive, legal personnel when material, and cumulative game stats. Checkpoint 6 above is independently resumable. | Pass after correction |
| 14. Head coach changes teams with unresolved matters | Old staff/contracts disappear when profile is replaced. | Document 6 freezes the outgoing tenure and roster/staff state, preserves obligations, and requires Documents 2 and 3 to be versioned/re-locked before the new team's state is active. | Pass after correction |

## F4. Residual limitations

The architecture reduces drift but cannot make an LLM an exact football simulator. Play-level statistical realism still depends on the quality of roster evidence, selected granularity, and disciplined event reconciliation. Private playbooks and actual private human intentions remain unknown. Long careers still require periodic sourcebook updates, audited season archives, and explicit corrections when the evidence changes. Those limits are stated rather than hidden behind ratings or formulas.

After the corrections embodied in Documents 1–6, the executed trace and fourteen scenario checks reveal no unresolved architectural blocker. Initialization still requires the factual and user-controlled variables below. Later play remains subject to ordinary evidence gaps and open correction when a real inconsistency is found.

---

# G. Remaining variables requiring user confirmation

## G1. Unconditional mode and control confirmations

1. Competition level, league/governing body, and applicable jurisdiction.
2. Team and location.
3. Exact season and exact starting date.
4. Real, fictional, mixed, historical, current, or counterfactual mode.
5. Exact divergence point, including whether Alex Stone's pre-2009 playing/coaching career already altered real history.
6. The protagonist's canonical name and enough exact playing/coaching history to be compatible with the start date and divergence.
7. Head-coach team, contract, reporting line, staff-hiring authority, personnel/draft/roster/budget authority, discipline authority, and media boundary.
8. Offensive, defensive, and special-teams play-calling responsibility.
9. Desired game granularity: executive head-coach, play-calling head-coach, critical-decision, or full tactical mode.
10. Desired personnel-decision granularity: which routine depth/package/active/personnel implementation is delegated and which choices always return to the user, within legal authority.
11. Desired career and off-field detail level.
12. Real-person policy after divergence: retain real eligible personnel where plausible, use fictional replacements, or allow a controlled mixture.

## G2. Conditional migration confirmations

These are required only if the related legacy material or detail is retained:

1. For a reconstructed 2010 Detroit continuation, whether the fictional 9–7 2009 result and Culpepper/Tampa 2010-first transaction are accepted, corrected, or rejected, followed by reconstruction of the missing 2009 league state.
2. If Stone's supplied playing career remains, exact position, seasons, statistics, honors, entry route, and historical downstream effects.
3. If the supplied education remains, corrected institutions, degrees, dates, and feasible attendance chronology.
4. If family/relocation detail is enabled, spouse naming/program, residence, family base, and whether geography is a preference or hard constraint.
5. If a January 2009 divergence precedes later real league rules or calendar events, whether those institutions follow historical external rules, evolve entirely through simulation, or use an expressly defined hybrid rail.
6. If a real-team mode is selected, the exact-date roster, staff, schedule, contracts or eligibility, public availability, standings, transactions, and deadlines required for initialization.
7. If intentionally ahead-of-era tactics are desired, which concepts are part of the counterfactual and what installation/communication costs apply.

## G3. Choices that may remain for the first in-world decision

The compact offensive, defensive, special-teams, preparation, and game-management identities do not have to be silently inferred or preinstalled. Once team, roster, staff, authority, and era are fixed, they may be presented as the head coach's first consequential choices after an explicit initialization instruction. The legacy catalogues remain proposals only.

The career remains uninitialized. After the unconditional and applicable conditional variables are confirmed, the sourcebook and starting snapshot can be factually completed. A separate explicit instruction to initialize is still required.
