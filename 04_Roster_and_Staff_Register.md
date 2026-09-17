# 04. Roster and Staff Register

## Document status

- Function: Canonical register for current players, non-protagonist staff, depth roles, packages, availability, workloads, active personnel candidates, person-level commitments, and detailed current financial/eligibility reconciliation.
- Stable content: Field definitions, evidence rules, reconciliation procedure, invariants, and correction procedure.
- Mutable content: Every team, player, non-protagonist staff, candidate, depth, package, player/staff commitment, financial reconciliation, eligibility, health, workload, person-specific relationship, and evaluation entry. The protagonist head coach's contract belongs in Document 3.
- Read requirement: Reread this register and cross-check it against the derived Current Season State before every response. Document 5 cannot override this register's detailed current records. Its source-version manifest must identify this exact register version; resolve any mismatch through Document 6's latest global package checkpoint. Reconcile after every game and material personnel event.
- Statistical authority: The Chronology and Game Ledger controls cumulative game statistics. This register may quote a dated snapshot but must not create a competing total.
- Authority source: Document 3's authority map is the sole source of final organizational authority. This register records operating assignments and cross-references, not competing grants of power.
- Medical-state ownership: A dated, coach-facing Document 6 medical or availability event is the source event. The individual player record in this document is the latest canonical current state derived from it. The player index, medical control table, and Document 5 are derived summaries.
- Correction authority: Document 6 is the sole append-only correction and supersession ledger. This document stores current corrected values and generated pointers only.
- Information boundary: All six principal canonical documents are coach-facing. Information not plausibly known to the head coach must not appear in this package. Any supported private simulator state must live outside the six-document package and outside every handoff.
- Initialization status: Not initialized. Bracketed fields are placeholders, not simulation facts.

## Registry identity

| Field | Canonical value |
|---|---|
| Team | `[TEAM NOT SET]` |
| Competition and governing body | `[NOT SET]` |
| Season | `[NOT SET]` |
| Owned content last changed/effective | `[YYYY-MM-DD, TIME, TIME ZONE NOT SET]` |
| Season phase and week | `[NOT SET]` |
| Real, fictional, or mixed personnel | `[NOT SET]` |
| Divergence point | `[NOT SET]` |
| Applicable roster rule source | `[SOURCEBOOK REFERENCE NOT SET]` |
| Applicable contract, eligibility, or scholarship rule source | `[SOURCEBOOK REFERENCE NOT SET]` |
| Document 2 locked version | `[NOT SET]` |
| Document 3 authority-map version | `[NOT SET]` |
| Document 4 register version | `[UNINITIALIZED TEMPLATE]` |
| Supersedes Document 4 version/content-changing update | `[NONE]` |
| Last Document 4 content-changing update | `[NONE]` |
| Latest Document 6 source event applied to Document 4 content | `[NO CANONICAL EVENT YET]` |
| Last registry-wide reconciliation | `[NOT YET PERFORMED]` |
| Last full continuity audit | `[NOT YET PERFORMED]` |
| Unresolved registry conflicts | `[NONE RECORDED OR LIST IDS]` |

## Canon and evidence conventions

Every material entry must distinguish fact from evaluation. A blank field means unknown, not negative.

### Canon-class crosswalk

Use the first-column labels throughout this document. The other columns are translation aliases only; they do not create additional evidence classes. Evidence strength is recorded separately and never changes a claim's canon class.

| Document 4 canonical class | Document 2 label | Document 3 provenance and any stated Document 4 alias | Document 6 information basis or record form | Permitted use |
|---|---|---|---|---|
| Verified pre-divergence fact | Verified pre-divergence fact | Verified pre-divergence fact; `Verified public fact` is a legacy Document 4 alias only when the source is public | Verified baseline event when chronology requires it; otherwise cite the sourced baseline | Dated fact effective no later than divergence, supported by an appropriate source and available to the head coach through a permitted channel; a retrospective source supports only the exact earlier proposition cited |
| User canon | User canon | User-confirmed coach canon; `User-established canon` is the Document 4 alias | Dated user decision or correction | Explicit user-created, approved, or corrected simulation fact |
| Intentional counterfactual canon | User canon plus divergence register | Intentional counterfactual canon | Approved counterfactual baseline or dated user decision | Explicitly approved departure from reality; state the replaced fact and divergence consequence without using it to authorize a prohibited real-person invention |
| Post-divergence simulation event | Post-divergence simulation event | Post-divergence simulation canon; `Completed simulation event` is the Document 4 alias | Dated simulation event in a closed canonical update | Completed event after divergence; a proposal, expectation, or staged update does not qualify |
| Attributed report or assessment | Attributed report or assessment | Coach self-description or attributed external assessment; aliases include `Staff assessment` and `Report or rumor` | Dated public report, staff assessment, or attributed communication when material | What an identified source said or assessed, not objective truth |
| Labeled inference | Labeled inference | Labeled inference; `Inference` is the Document 4 alias | Preserve within the relevant attributed entry with reasoning and uncertainty; never record it as an objective event | Reasoned conclusion from identified evidence, with limitation and uncertainty |
| Unresolved legacy claim | Unresolved legacy claim | Supplied claim pending confirmation; `Undetermined until resolved` is the Document 4 alias | Unresolved claim, never a completed event | Quarantined; cannot control current state or outcomes |
| Quarantined actual-future comparator | Quarantined actual-future comparator | No active-runtime equivalent | Never entered as an active chronology event | Do not store the comparator in this register; quarantine it outside the active six-document package and never use it as canon or hidden evidence |
| Undetermined | Undetermined | Unknown or undetermined | Omit unless the fact that a matter is unresolved is itself material; then record an unresolved claim | Not fixed; do not invent detail |

### Confidence vocabulary

Use only these evidence labels. They describe support for a claim, not a person's ability.

- Confirmed: An authoritative source, completed simulation event, or explicit user canon establishes the claim.
- Corroborated: Multiple reliable sources support the claim, but no controlling source is available.
- Supported: Credible evidence exists, with a meaningful limitation.
- Tentative: Evidence is thin, ambiguous, stale, or based on a single subjective view.
- Disputed: Material sources conflict.
- Unknown: No adequate evidence exists.

Do not convert these labels into numbers, grades, tiers, ratings, or hidden ability scores.

### Provenance block

Attach this block to every material fact, assessment, health update, role concern, or change that is not self-evident from a completed game event.

| Field | Entry |
|---|---|
| Claim or field affected | `[CLAIM]` |
| Canon class | `[CLASS FROM CROSSWALK]` |
| Source or speaker | `[SOURCE ID, PERSON, OR EVENT ID]` |
| Source date and applicable date | `[DATES]` |
| Coach-facing information channel | `[OFFICIAL RELEASE / AUTHORIZED DIRECT COMMUNICATION / MEETING / FILM / PRACTICE / PUBLIC REPORT / OTHER]` |
| Access basis | `[PUBLIC, CREATED OR DECIDED BY, OBSERVED BY, OR COMMUNICATED TO HEAD COACH; OTHERWISE OMIT]` |
| Evidence label | `[CONFIRMED / CORROBORATED / SUPPORTED / TENTATIVE / DISPUTED / UNKNOWN]` |
| Limitation or competing evidence | `[DETAIL]` |
| Last verified | `[DATE AND TIME]` |

### Coach-facing and real-person safeguards

These rules apply to every real player, staff member, executive, candidate, opponent, and other identifiable person, not only to candidates.

- Establish an exact factual snapshot date and relationship to the divergence point before entering a real person.
- Keep verified pre-divergence history separate from post-divergence simulation events.
- Do not import actual later employment, success, failure, scheme, relationship, injury, reputation, transaction, or private decision after divergence.
- Do not use later real-world career knowledge as an evaluation, fit judgment, or hidden competence rating.
- A retrospective source may verify a specifically dated earlier fact. Do not migrate the source's later honors, roles, evaluations, or outcomes.
- Do not invent real-world interest, availability, retirement, relocation willingness, endorsements, references, quotations, private motives, or family facts.
- Ordinary football injuries may occur to a real player as post-divergence simulation events. Any diagnosis or restriction must come through the simulated medical process, be labeled simulation canon, and never be implied to have occurred in reality.
- Do not fabricate criminal conduct, serious misconduct, substance abuse, stigmatizing or unrelated diagnoses, or damaging private family information about a real person. Use a fictional person if such material is necessary.
- Expressed post-divergence dialogue and ordinary professional decisions are simulation canon, not claims about actual history.
- Do not convert an active player into a coach without resolving contract rights, retirement or release, applicable rules, and the person's simulated decision.
- Do not store an uncommunicated private thought, hidden diagnosis, confidential front-office decision, or staff-held secret in this six-document package. If the platform has no separate private-state facility, leave it undetermined.

## Registry-wide reconciliation

Complete this block whenever the register is created, after each game, and after a material roster, medical, depth, contract, eligibility, or staff change.

### Disjoint primary roster-status reconciliation

Create one row for every exact primary status that exists in the locked competition and season. Primary rows must be mutually exclusive: every person under team control appears in exactly one row. Do not combine a practice squad, reserve list, inactive designation, suspension, exemption, scholarship category, or other mechanism unless the governing rules define them as the same status.

| Exact primary status | Player IDs in status | Current count | Counts toward which exact limit | Applicable limit | Rule or source | Reconciled |
|---|---|---:|---|---:|---|---|
| `[EXACT COMPETITION-DEFINED STATUS]` | `[PLAYER IDS]` | `[COUNT]` | `[NAMED LIMIT OR DOES NOT COUNT]` | `[LIMIT OR N/A]` | `[SOURCE]` | `[DATE / NOT YET]` |

| Primary-status total | Current value | Derivation and limit | Reconciled |
|---|---:|---|---|
| Persons under team control | `[COUNT]` | Sum of disjoint primary rows only | `[DATE / NOT YET]` |
| Open places under each governing limit | `[VALUE BY LIMIT]` | Applicable limit minus only the primary statuses that count toward it | `[DATE / NOT YET]` |

### Derived game-day designation subset

Game-day active, inactive, dressed, emergency, or equivalent designations are subsets of competition-defined eligible primary statuses. They do not create or replace a primary roster status and must never be added to the primary-status total.

| Exact game-day designation | Player IDs | Current count | Eligible parent primary statuses | Applicable limit | Rule or source | Reconciled |
|---|---|---:|---|---:|---|---|
| `[EXACT COMPETITION-DEFINED DESIGNATION]` | `[PLAYER IDS]` | `[COUNT]` | `[STATUS OR STATUSES]` | `[LIMIT OR N/A]` | `[SOURCE]` | `[DATE / NOT YET]` |

Do not sum nested counts. Reconcile primary roster legality first, then reconcile game-day subsets against the eligible parent population.

### Financial, contract, and eligibility reconciliation

Do not merge legal accounting, cash, internal budget, and aid. In a competition with no salary cap or floor, enter `None under applicable rules`; do not calculate cap space.

| Control | Current position | Governing limit or condition | Source | Reconciled |
|---|---|---|---|---|
| League salary-cap and salary-floor legality | `[CAP / FLOOR / NONE / N/A]` | `[EXACT RULE]` | `[SOURCE]` | `[DATE / NOT YET]` |
| League accounting liability | `[CAP CHARGES, DEAD MONEY, ROOKIE POOL, TAX, OR N/A]` | `[ACCOUNTING RULE]` | `[SOURCE]` | `[DATE / NOT YET]` |
| Cash payroll and guarantee commitments | `[VALUE OR UNKNOWN]` | `[CONTRACTUAL CONDITION]` | `[SOURCE]` | `[DATE / NOT YET]` |
| Internal owner, school, or program budget | `[VALUE OR UNKNOWN]` | `[INTERNAL APPROVAL CONDITION; NEVER MISLABELED AS LEAGUE CAP]` | `[SOURCE OR USER CANON]` | `[DATE / NOT YET]` |
| Scholarship, financial-aid, or equivalent commitments | `[VALUE OR N/A]` | `[GOVERNING AND INSTITUTIONAL LIMIT]` | `[SOURCE]` | `[DATE / NOT YET]` |
| Open roster, scholarship, or registration places | `[VALUE BY EXACT LIMIT]` | `[RULE]` | `[SOURCE]` | `[DATE / NOT YET]` |
| Contract, eligibility, waiver, transfer, or registration deadlines | `[DATES]` | `[RULE]` | `[SOURCE]` | `[DATE / NOT YET]` |
| Material unresolved cases | `[PERSON AND ISSUE OR NONE]` | `[CONDITION]` | `[SOURCE]` | `[DATE / NOT YET]` |

### Staff reconciliation

| Check | Current operating result | Mandatory Document 3 authority-map or delegation reference | Verified starting source or closed Document 6 effective event | Reconciled |
|---|---|---|---|---|
| All filled football staff roles | `[ROLES AND NAMES]` | `[DOCUMENT 3 ROWS]` | `[STARTING-SNAPSHOT SOURCE OR APPOINTMENT EVENT]` | `[DATE / NOT YET]` |
| Vacant or interim roles | `[ROLES OR NONE]` | `[DOCUMENT 3 ROWS]` | `[STARTING-SNAPSHOT SOURCE OR STATUS EVENT]` | `[DATE / NOT YET]` |
| Ordinary offensive play caller | `[NAME / NOT SET]` | `[DOCUMENT 3 ROW AND DELEGATION ENTRY]` | `[STARTING SOURCE OR EFFECTIVE EVENT]` | `[DATE / NOT YET]` |
| Ordinary defensive play caller | `[NAME / NOT SET]` | `[DOCUMENT 3 ROW AND DELEGATION ENTRY]` | `[STARTING SOURCE OR EFFECTIVE EVENT]` | `[DATE / NOT YET]` |
| Special-teams operating lead | `[NAME / NOT SET]` | `[DOCUMENT 3 ROW AND DELEGATION ENTRY]` | `[STARTING SOURCE OR EFFECTIVE EVENT]` | `[DATE / NOT YET]` |
| Unresolved responsibility overlaps | `[DETAIL OR NONE]` | `[DOCUMENT 3 ROWS]` | `[SOURCE OR EVENT THAT EXPOSED CONFLICT]` | `[DATE / NOT YET]` |

The source or Document 6 event proves that an appointment, vacancy, or change occurred; it never substitutes for Document 3's authority and delegation record.

### Reconciliation result

- Register status: `[RECONCILED / RECONCILED WITH NOTED UNCERTAINTY / CONFLICTED]`
- Conflicts requiring correction before play continues: `[IDS OR NONE]`
- Matters that may remain uncertain without blocking play: `[LIST OR NONE]`
- Next mandatory reconciliation trigger: `[EVENT]`

### Document 4 initialization gate

Career initialization remains blocked until:

- the register status is `RECONCILED` or `RECONCILED WITH NOTED UNCERTAINTY`, not merely populated, and every noted uncertainty is expressly nonblocking;
- the starting content-effective date and Document 2/3 versions agree with the candidate Document 5 source manifest and candidate Document 6 initial global checkpoint;
- every person under team control has one exact disjoint primary status with a source;
- every applicable governing limit and game-day subset reconciles without nested double-counting;
- material contract, eligibility, financial, aid, and rights records are reconciled to available evidence;
- every active staff member has a verified starting appointment or a closed Document 6 appointment event;
- the operating play callers and staff assignments cross-reference Document 3;
- current coach-facing availability is sourced, and the medical clearance authority or process is established in Document 3;
- no blocking roster, staff, medical, rights, authority, or real-person conflict remains; and
- the starting snapshot is linked to a closed Document 6 canonical update.

## Player index

Maintain one row per player under team control. Do not create duplicate records for a position change, list move, name variant, or jersey change. Availability here is a derived display: it must match the player's individual current-state record and the same latest closed Document 6 medical or availability event.

| Player | Stable player ID | Position group | Exact primary roster status | Contract or eligibility status | Current football role | Derived availability | Latest Document 6 source event | Last closed checkpoint affecting player |
|---|---|---|---|---|---|---|---|---|
| `[NAME]` | `[ID]` | `[POSITION]` | `[EXACT STATUS]` | `[STATUS]` | `[ROLE]` | `[AVAILABILITY]` | `[EVENT ID, DATE, TIME]` | `[UPDATE LABEL]` |

## Individual player record template

Copy this section once for each materially relevant player. Less relevant players may remain index-only until a decision requires detail. A player with a current medical or availability event, a communicated limitation, a material contract or eligibility issue, or a live decision cannot remain index-only.

### `[PLAYER NAME]` (`[STABLE PLAYER ID]`)

#### Identity and status

| Field | Current entry |
|---|---|
| Real or fictional person | `[REAL / FICTIONAL / COMPOSITE NOT PERMITTED UNLESS EXPLICIT]` |
| Name used on simulation date | `[NAME]` |
| Position and secondary position | `[POSITION]` |
| Age or class year on as-of date | `[VALUE]` |
| Acquisition or entry date | `[DATE AND METHOD]` |
| Current governed roster status | `[EXACT RULE TERM]` |
| Current game-day designation | `[EXACT COMPETITION-DEFINED TERM / NOT YET DESIGNATED / NOT APPLICABLE]` |
| Transaction, waiver, transfer, or registration rights | `[DETAIL]` |
| Last status verification | `[DATE, SOURCE]` |

#### Contract, eligibility, or scholarship

Complete only the branch that applies to the locked competition. Mark the others `Not applicable`.

| Field | Current entry |
|---|---|
| Professional contract term and expiration | `[DETAIL OR UNKNOWN]` |
| League accounting treatment or liability | `[CAP CHARGE, DEAD MONEY, OPTION ACCOUNTING, RELEASE CONSEQUENCE, OR N/A, WITH SOURCE]` |
| Cash compensation and guarantees | `[DETAIL OR UNKNOWN, WITH SOURCE]` |
| Internal budget effect or approval | `[DETAIL OR N/A, WITH SOURCE]` |
| Service, waiver, reserve, or transaction status | `[DETAIL OR N/A]` |
| Class year, seasons used, and eligibility remaining | `[DETAIL OR N/A]` |
| Scholarship or financial-aid commitment | `[DETAIL OR N/A, WITH SOURCE]` |
| Registration, transfer, redshirt, academic, or compliance status | `[DETAIL OR N/A]` |
| School, district, state-association, or other participation condition | `[DETAIL OR N/A]` |
| Open uncertainty | `[DETAIL OR NONE]` |

#### Role, depth, packages, and special teams

| Field | Current entry |
|---|---|
| Primary role | `[ROLE]` |
| Nominal depth position | `[SLOT]` |
| Current available depth position | `[SLOT OR UNAVAILABLE]` |
| Offensive or defensive packages | `[PACKAGES AND ASSIGNMENT]` |
| Special-teams units and role | `[UNITS AND ASSIGNMENT]` |
| Emergency or cross-trained role | `[ROLE OR NONE]` |
| Document 3 authority-map cross-reference | `[ROW OR DELEGATION ENTRY]` |
| Latest role decision and communicated source | `[DATE, DECISION, USER OR AUTHORIZED ACTOR, DOCUMENT 6 EVENT]` |

#### Health, availability, and expected effectiveness

The latest closed, dated Document 6 event records what medical or availability information was communicated and when. This individual record owns the resulting latest current state. The player index, medical control table, and Document 5 must derive from it. Availability and effectiveness are separate. The clinician or competition-defined medical process controls diagnosis and clearance; the authority map in Document 3 identifies that process. Coaches control football deployment only within the communicated clearance and limitations and their Document 3 authority.

| Field | Current entry |
|---|---|
| Latest Document 6 communicated medical or availability event | `[EVENT ID, EVENT TIME, CLOSED UPDATE LABEL]` |
| Clinician or governing-process clearance status | `[CLEARED / NOT CLEARED / PENDING / NOT YET COMMUNICATED / NOT APPLICABLE]` |
| Clearance authority or process cross-reference | `[DOCUMENT 3 ROW AND DOCUMENT 2 RULE IF APPLICABLE]` |
| Clearance communication source and time | `[AUTHORIZED CLINICIAN OR PROCESS, DATE, TIME / NONE]` |
| Public injury, practice, or game-status designation | `[EXACT TERM / NONE / NOT APPLICABLE]` |
| Public designation source and time | `[OFFICIAL REPORT OR RELEASE, DATE, TIME / NONE]` |
| Practice participation | `[FULL / LIMITED / DID NOT PARTICIPATE / EXACT APPLICABLE TERM, DATE]` |
| Medical or performance limitation communicated to head coach | `[DETAIL WITHOUT UNSUPPORTED PRECISION / NONE COMMUNICATED / UNKNOWN]` |
| Football-use availability communicated to head coach | `[FULL / LIMITED / PACKAGE OR SNAP BOUND / GAME-TIME DECISION / UNAVAILABLE / UNKNOWN]` |
| Coaching deployment already decided | `[ROLE, PACKAGE, SNAP RANGE, INACTIVE, OR NOT YET DECIDED]` |
| Expected football effectiveness if used | `[QUALITATIVE EXPECTATION, FOOTBALL EVALUATOR, EVIDENCE, DATE, UNCERTAINTY]` |
| Conditioning or workload limitation | `[DETAIL, AUTHORIZED OR FOOTBALL EVALUATOR, DATE / NONE KNOWN]` |
| Next communicated medical or availability update | `[DATE OR EVENT / UNKNOWN]` |

Do not record a diagnosis, return date, restriction, or clearance because a coach, reporter, or narrator guessed it. A public designation, practice participation, or player statement cannot establish medical clearance. Clearance does not itself establish the game-day designation or expected effectiveness. A coach-facing football evaluation cannot override a clinician or governing-process restriction. Do not place medical information here until it has reached the head coach through a plausible authorized or public channel; uncommunicated information remains outside the six-document package.

#### Current demonstrated performance and evaluation

| Dimension | Current assessment | Evidence and evaluator | Evidence label | Last updated |
|---|---|---|---|---|
| Game performance | `[DESCRIPTION]` | `[FILM, STATS, OR EVENT]` | `[LABEL]` | `[DATE]` |
| Practice performance | `[DESCRIPTION]` | `[PERIODS, REPS, EVALUATOR]` | `[LABEL]` | `[DATE]` |
| Physical tools currently observable | `[DESCRIPTION]` | `[EVIDENCE]` | `[LABEL]` | `[DATE]` |
| Technique | `[DESCRIPTION]` | `[EVIDENCE]` | `[LABEL]` | `[DATE]` |
| Processing and communication | `[DESCRIPTION]` | `[EVIDENCE]` | `[LABEL]` | `[DATE]` |
| Scheme and role fit | `[DESCRIPTION]` | `[EVIDENCE]` | `[LABEL]` | `[DATE]` |
| Reliability within assigned role | `[DESCRIPTION]` | `[EVIDENCE]` | `[LABEL]` | `[DATE]` |
| Remaining evaluation uncertainty | `[WHAT IS NOT KNOWN AND WHY]` | `[EVIDENCE GAP]` | `[LABEL]` | `[DATE]` |

Do not collapse these dimensions into one rating. Separate performance from tools, fit, projection, and uncertainty. A staff disagreement remains attributed to each evaluator.

#### Workload and development

| Field | Current entry |
|---|---|
| Recent game snaps, touches, or special-teams exposure | `[DATED, SOURCE-BASED SUMMARY]` |
| Recent practice repetitions | `[DATED SUMMARY, INCLUDING UNIT]` |
| Recovery or conditioning load relevant to football use | `[DETAIL FROM AUTHORIZED STAFF]` |
| Current development priorities | `[SPECIFIC TECHNIQUE OR PROCESS]` |
| Current plan and responsible coach | `[PLAN, OWNER]` |
| Opportunity cost | `[WHO OR WHAT LOSES REPS OR TIME]` |
| Evidence of progress, regression, or no conclusion | `[DATED OBSERVATIONS]` |
| Next evaluation point | `[DATE OR EVENT]` |

Development is gradual, uneven, and uncertain. Do not infer growth from elapsed time or one performance.

#### Person-specific role and relationship concerns

| Concern or relationship | Coach-facing evidence | Communication source and date | Current status | Needed response or next check |
|---|---|---|---|---|
| `[ROLE, COMMUNICATION, CONTRACT, OR RELATIONSHIP ISSUE]` | `[DIRECT STATEMENT / OBSERVATION / ATTRIBUTED REPORT]` | `[CHANNEL, SOURCE, DATE]` | `[OPEN / MONITOR / RESOLVED / UNKNOWN]` | `[ACTION OR DATE]` |

Record only material, person-specific issues. Do not create a locker-room morale score or infer private thoughts. A player may hold mixed views about preparation, role, compensation, teammates, and coaches.

#### Player record control

- Last meaningful update: `[DATE, EVENT, SOURCE, CLOSED CHECKPOINT AFFECTING THIS RECORD]`
- Pending verification: `[ITEMS OR NONE]`
- Linked chronology or game-ledger events: `[EVENT IDS]`
- Document 6 supersession or correction pointers: `[EVENT OR CORRECTION LABELS / NONE]`

## Depth chart, personnel packages, and special teams

These are current football-use records, not permanent player rankings. Preserve both the nominal role and any temporary availability replacement. Document 3 alone supplies decision authority; this section records the resulting assignment and its authority-map reference.

### Base depth chart

| Unit and position | Starter or first unit | Next available | Additional depth | Unavailable nominal player | Decision date and Document 3 cross-reference |
|---|---|---|---|---|---|
| `[UNIT / POSITION]` | `[PLAYER]` | `[PLAYER]` | `[PLAYERS]` | `[PLAYER OR NONE]` | `[DATE, AUTHORITY-MAP ROW OR DELEGATION]` |

### Personnel and situational packages

| Package | Purpose and trigger | Eligible available players | Primary assignments | Communication owner | Last practiced | Last changed and Document 3 cross-reference |
|---|---|---|---|---|---|---|
| `[PACKAGE]` | `[USE]` | `[PLAYERS]` | `[ASSIGNMENTS]` | `[COACH OR PLAYER]` | `[DATE]` | `[DATE, AUTHORITY-MAP ROW OR DELEGATION]` |

### Special-teams assignments

| Unit | Primary players and roles | Alternates | Availability issue | Operating coach | Last changed and Document 3 cross-reference |
|---|---|---|---|---|---|
| `[UNIT]` | `[PLAYERS AND ROLES]` | `[PLAYERS]` | `[DETAIL OR NONE]` | `[COACH]` | `[DATE, AUTHORITY-MAP ROW OR DELEGATION]` |

A player named in a planned package may remain as a nominal reference while unavailable only if a current replacement is explicit. A player actually used in a game must belong to an eligible primary roster status, carry the required game-day active, dressed, or equivalent designation under the locked rule, and not be medically unavailable. No depth, package, or special-teams assignment can override suspension, ineligibility, roster status, or medical clearance.

## Staff index

| Staff member | Stable staff ID | Current title | Employment status | Document 3 authority-map references | Play-calling operating role | Current workload concern | Last meaningful update and closed update |
|---|---|---|---|---|---|---|---|
| `[NAME]` | `[ID]` | `[TITLE]` | `[STATUS]` | `[ROWS OR DELEGATIONS]` | `[ROLE]` | `[DETAIL OR NONE]` | `[DATE: CHANGE; UPDATE LABEL]` |

## Individual staff record template

### `[STAFF NAME]` (`[STABLE STAFF ID]`)

#### Identity and employment

| Field | Current entry |
|---|---|
| Real or fictional person | `[REAL / FICTIONAL]` |
| Current title | `[TITLE]` |
| Hire or appointment date | `[DATE]` |
| Contract term and material conditions | `[DETAIL OR UNKNOWN]` |
| Reports to | `[PERSON OR BODY]` |
| Direct reports | `[PEOPLE OR ROLES]` |
| Document 3 cross-reference for appointment, employment, and reporting authority | `[AUTHORITY-MAP ROWS]` |
| Appointment source | `[VERIFIED STARTING SNAPSHOT OR CLOSED DOCUMENT 6 EVENT]` |
| Employment status | `[ACTIVE / INTERIM / LEAVE / DEPARTING / OTHER]` |

#### Authority, responsibilities, and play calling

| Domain | Document 3 authority-map or delegation reference | Staff member's current operating responsibility | Recommendation, consultation, or delegated rights | Effective source or event |
|---|---|---|---|---|
| Personnel and roster | `[ROW OR DELEGATION]` | `[RESPONSIBILITY]` | `[RIGHTS]` | `[VERIFIED STARTING SOURCE OR CLOSED DOCUMENT 6 EVENT ESTABLISHING THE CURRENT ASSIGNMENT]` |
| Depth and lineup | `[ROW OR DELEGATION]` | `[RESPONSIBILITY]` | `[RIGHTS]` | `[VERIFIED STARTING SOURCE OR CLOSED DOCUMENT 6 EVENT ESTABLISHING THE CURRENT ASSIGNMENT]` |
| Practice and installation | `[ROW OR DELEGATION]` | `[RESPONSIBILITY]` | `[RIGHTS]` | `[VERIFIED STARTING SOURCE OR CLOSED DOCUMENT 6 EVENT ESTABLISHING THE CURRENT ASSIGNMENT]` |
| Offensive play calling | `[ROW OR DELEGATION]` | `[CALLER / INPUT / NONE]` | `[BOUNDARY]` | `[VERIFIED STARTING SOURCE OR CLOSED DOCUMENT 6 EVENT ESTABLISHING THE CURRENT ASSIGNMENT]` |
| Defensive play calling | `[ROW OR DELEGATION]` | `[CALLER / INPUT / NONE]` | `[BOUNDARY]` | `[VERIFIED STARTING SOURCE OR CLOSED DOCUMENT 6 EVENT ESTABLISHING THE CURRENT ASSIGNMENT]` |
| Special teams | `[ROW OR DELEGATION]` | `[RESPONSIBILITY]` | `[BOUNDARY]` | `[VERIFIED STARTING SOURCE OR CLOSED DOCUMENT 6 EVENT ESTABLISHING THE CURRENT ASSIGNMENT]` |
| Player development and discipline | `[ROW OR DELEGATION]` | `[RESPONSIBILITY]` | `[BOUNDARY]` | `[VERIFIED STARTING SOURCE OR CLOSED DOCUMENT 6 EVENT ESTABLISHING THE CURRENT ASSIGNMENT]` |
| Medical, media, contract, or other domain | `[ROW OR DELEGATION]` | `[RESPONSIBILITY]` | `[BOUNDARY]` | `[VERIFIED STARTING SOURCE OR CLOSED DOCUMENT 6 EVENT ESTABLISHING THE CURRENT ASSIGNMENT]` |

Record play-calling delegation explicitly. A title does not establish authority, and this register never creates authority absent from Document 3.

#### Current evaluation

| Dimension | Assessment | Evidence and evaluator | Evidence label | Last updated |
|---|---|---|---|---|
| Coaching or operational strengths | `[SPECIFIC DESCRIPTION]` | `[EVIDENCE]` | `[LABEL]` | `[DATE]` |
| Limitations or support needs | `[SPECIFIC DESCRIPTION]` | `[EVIDENCE]` | `[LABEL]` | `[DATE]` |
| Teaching and communication | `[DESCRIPTION]` | `[EVIDENCE]` | `[LABEL]` | `[DATE]` |
| Planning and game-day execution | `[DESCRIPTION]` | `[EVIDENCE]` | `[LABEL]` | `[DATE]` |
| Scheme contribution and fit | `[DESCRIPTION]` | `[EVIDENCE]` | `[LABEL]` | `[DATE]` |
| Evaluation uncertainty | `[WHAT REMAINS UNKNOWN AND WHY]` | `[EVIDENCE GAP]` | `[LABEL]` | `[DATE]` |

Do not infer current competence from a later real-world career, reputation, title, or résumé claim.

#### Workload, relationships, and incentives

| Field | Current entry |
|---|---|
| Current weekly responsibilities | `[DUTIES]` |
| Material workload or time pressure | `[DETAIL OR NONE]` |
| Relationship with head coach | `[OBSERVABLE, ATTRIBUTED DESCRIPTION]` |
| Material relationships with other staff or players | `[COACH-OBSERVED OR COMMUNICATED DESCRIPTION, SOURCE, DATE]` |
| Current disagreement or unresolved request | `[COACH-OBSERVED OR COMMUNICATED DETAIL, SOURCE, DATE / NONE]` |
| Observable incentive structure | `[PUBLIC OR COMMUNICATED CONTRACT TERM, ROLE, REPORTING CONDITION, MARKET FACT, OR UNKNOWN]` |
| Information or recommendation communicated to the head coach | `[CONTENT, CHANNEL, SOURCE, DATE / NONE]` |
| Next expected decision or review | `[DATE OR EVENT]` |

Record only observable structural incentives or statements actually communicated to the head coach. Do not infer a private ambition, loyalty, resentment, or desire for the head coach's job. A person's response to an incentive remains unknown until plausibly observed or communicated.

#### Staff record control

- Last meaningful update: `[DATE, EVENT, SOURCE, CLOSED CHECKPOINT AFFECTING THIS RECORD]`
- Pending verification: `[ITEMS OR NONE]`
- Linked chronology events: `[EVENT IDS]`
- Document 6 supersession or correction pointers: `[EVENT OR CORRECTION LABELS / NONE]`

## Personnel candidate register

Candidate status is mutable and does not make a hire, offer, interview, interest, or availability real. The head coach may recommend or decide only within the established authority map in Document 3. Every entry is coach-facing; unknown private interest or uncommunicated organizational action is omitted or marked undetermined.

| Candidate | Candidate ID | Role considered | Real or fictional | Exact factual snapshot date | Current employer or rights holder | Contact or permission status | Communicated interest status | Document 3 decision-authority cross-reference | Next step |
|---|---|---|---|---|---|---|---|---|---|
| `[NAME]` | `[ID]` | `[ROLE]` | `[TYPE]` | `[DATE]` | `[ENTITY OR UNKNOWN]` | `[STATUS]` | `[UNKNOWN UNTIL PLAUSIBLY COMMUNICATED]` | `[AUTHORITY-MAP ROW]` | `[STEP]` |

### Candidate record template

#### `[CANDIDATE NAME]` (`[CANDIDATE ID]`)

| Field | Current entry |
|---|---|
| Role considered and reason | `[DETAIL]` |
| Verified background as of snapshot date | `[FACTS WITH SOURCES]` |
| Current employment, contract, playing rights, or required permission | `[DETAIL]` |
| Demonstrated relevant experience | `[EVIDENCE]` |
| Transferable tools | `[EVIDENCE-BASED INFERENCE]` |
| Material limitations and unknowns | `[DETAIL]` |
| Fit hypothesis | `[REASONED, TENTATIVE ASSESSMENT]` |
| Source of candidacy | `[USER REQUEST / STAFF SUGGESTION / AGENT / SEARCH / OTHER]` |
| Contact, interview, and offer status | `[DATED STATUS]` |
| Candidate's communicated interests or conditions | `[DIRECTLY COMMUNICATED INFORMATION OR UNKNOWN]` |
| Other authorities' views communicated to the head coach | `[ATTRIBUTED ASSESSMENTS, CHANNEL, DATE]` |
| Document 3 decision-authority cross-reference | `[AUTHORITY-MAP ROW]` |
| Deadline or next step | `[DATE OR EVENT]` |
| Provenance and evidence label | `[SOURCES AND LABEL]` |
| Last closed checkpoint affecting candidacy | `[DOCUMENT 6 GLOBAL CHECKPOINT LABEL]` |

### Candidate application of document-wide safeguards

Apply the document-wide coach-facing and real-person safeguards above. In particular, verify the exact snapshot, current employer or rights holder, applicable contact permission, and any active playing or employment rights. Candidate interest, willingness, retirement, references, and conditions remain unknown until learned through a plausible channel. A résumé or public reputation is attributed evidence, not proof of competence. A simulated interview, offer, response, or hire must be a dated post-divergence event in a closed Document 6 update and cannot retroactively grant experience the person did not possess at the snapshot.

When a candidate is hired, declines, is rejected, becomes unavailable, or ceases to be relevant, close the disposition through Document 6 and remove the person from the active candidate table. Transfer a hired candidate into the Staff Register only after the appointment and any required permission, release, retirement, or rights resolution are effective. Preserve the candidate history through the Document 6 event rather than rewriting it here.

## Medical and availability control table

This table is a derived coach-facing operational summary, not an independent source of medical truth. Each row must reproduce the latest current state in the individual player record, which in turn must point to the latest closed, dated Document 6 event communicating the information. Document 3 identifies the controlling clinician or process; Document 2 supplies any governing reporting rule.

| Player | Latest Document 6 event and closed update | Clinician or process clearance status | Public designation, source, and time | Communicated medical or performance limitation | Football-use availability communicated to head coach | Expected effectiveness, football evaluator, evidence, and date | Next communicated update |
|---|---|---|---|---|---|---|---|
| `[PLAYER]` | `[EVENT ID; UPDATE LABEL]` | `[STATUS]` | `[EXACT TERM; SOURCE; DATE/TIME / NONE]` | `[DETAIL / NONE COMMUNICATED]` | `[STATUS]` | `[QUALITATIVE VIEW; EVALUATOR; EVIDENCE; DATE]` | `[DATE OR EVENT]` |

When sources conflict, do not select the most convenient status. A public designation, practice report, or media account cannot clear a player. Mark the field disputed, identify the controlling clinician or process from Document 3, preserve the latest valid communication, and pause any decision that depends on the unresolved conflict. Clearance, public designation, communicated football-use limitation, and expected effectiveness are different fields and must not silently substitute for one another.

## Transactional update protocol

### 1. Distinguish proposal from completion

A request, recommendation, negotiation, report, waiver claim, offer, medical expectation, or intended depth change is not a completed transaction. Keep it pending in the Current Season State until the final authority identified only in Document 3 acts and every governing condition is satisfied.

### 2. Validate before committing

For every proposed player or staff change, verify:

1. Exact effective date and time.
2. Document 3 authority-map cross-reference and any required consent or permission.
3. Applicable rule, deadline, list mechanism, eligibility condition, contract right, or budget condition.
4. The person's current status and rights holder.
5. Required corresponding move, open place, or resource consequence.
6. Information actually known to the head coach.
7. Canon class under the document-wide crosswalk and adequate provenance.

### 3. Commit dependent records together

Follow Document 6's unified commit procedure. Use one target global package checkpoint and this order for an event ready to become effective:

1. In candidate Document 6, append the dated source event. It remains open and noncanonical until the candidate bundle's close line and promotion.
2. If and only if the event changes a stable rule or sourcebook field, prepare a candidate Document 2 version; if and only if it changes organizational authority, contract authority, reporting structure, or formal delegation, prepare a candidate Document 3 version. Preserve their version references.
3. If Document 4-owned content changes, prepare a candidate Document 4 version: update the individual record first, then every derived index, disjoint primary-status count, game-day subset, financial or eligibility control, depth or package assignment, staff responsibility, candidate disposition, and medical summary affected by the event. Record the target global checkpoint and preceding Document 4 content-changing update. If no owned content changes, retain the active Document 4 version.
4. Prepare a full candidate Document 5 snapshot from the source records and candidate/current versions. It lists this Document 4 version in its source manifest and carries the target and preceding global package checkpoints. The preceding active Document 5 remains current during staging.
5. Validate all affected invariants. Candidate Document 6's close line and register row then promote the bundle. Only upon promotion do candidate Document 4 values become current and their Document 6 event pointers become `closed`. A changed Document 4 adopts the global checkpoint as its content-changing update; an unchanged Document 4 retains its older pointer while Document 5 advances globally.

If interruption or contradiction prevents closure, the bundle at the preceding global checkpoint remains canonical and candidate replacements are discarded or restaged. Never label staged values `RECONCILED`, expose them as settled current state, or partially advance Document 5. If a substantive conflict exists in the preceding closed state, mark the current register `Conflicted` through the correction procedure. Do not delete a replaced fact without a dated Document 6 successor or correction pointer. Do not rewrite unrelated players or staff.

### 4. Event-specific requirements

- Injury or medical update: Stage the Document 6 communication event and candidate current fields for clinician or process clearance, public designation if any, limitation communicated to the head coach, football-use availability, separately evaluated effectiveness, affected depth and packages, and next communicated update. Upon closure, the current record points to that closed event. Do not add a diagnosis or recovery date without authorized support.
- Depth or package change: Record the Document 3 authority-map cross-reference, effective event, affected repetitions and roles, and any person-specific concern. A depth change does not alter medical clearance, governed roster status, or contract status.
- Acquisition, release, waiver, transfer, scholarship, or registration change: Reconcile rule legality, rights, counts, financial or eligibility effect, corresponding move, and effective time.
- Staff hire, departure, or responsibility change: Resolve former-employer, playing, contract, permission, release, or retirement rights; close the candidate disposition; then reconcile appointment status, Document 3 authority-map or delegation references, reporting line, play-calling role, direct reports, workload transfer, and unresolved prior commitments.
- Position change: Preserve one player identity, update the primary and secondary positions, and revise all affected depth, package, workload, and development entries.
- Team change or season-phase close: Before replacing mutable entries, close and link a dated Document 4 snapshot in Document 6, preserve every unresolved contract, rights, medical, staff, and candidate matter in the handoff, then create the new team's or phase's register under a new version.
- Correction: Create the authoritative correction or supersession only in Document 6, update current values and generated pointers here, and notify the user before continuing if the issue materially affects a decision or result.

## Registry invariants

The register is not reconciled unless all applicable statements are true.

1. The Document 4 content-effective date is no later than Document 5's master date, and no closed Document 6 event after this version changes Document 4-owned content without a successor version.
2. Document 5's source manifest names the exact Document 2 locked version, Document 3 authority-map version, and Document 4 register version used at its global checkpoint; Document 5's checkpoint equals Document 6's latest closed register row.
3. Every person has one stable ID and one current index row; name, position, title, jersey, or status changes do not create a duplicate identity.
4. Every player under team control occupies exactly one mutually exclusive, competition-defined primary roster status.
5. Each primary-status row states exactly which limit it counts toward, the individual records reproduce those statuses, and every open-place calculation uses only the applicable disjoint rows.
6. A game-day active, inactive, dressed, emergency, or equivalent designation is a derived subset of eligible primary statuses and is never added to the primary-status total.
7. Every game-day designation belongs to an eligible parent status and satisfies the exact competition rule, unless a cited exception expressly permits otherwise.
8. Every current player roster status traces to the verified starting snapshot or a closed Document 6 event.
9. League cap and floor legality, league accounting liability, cash and guarantees, internal budget, and scholarship or aid are reconciled separately and never substituted for one another.
10. Contract, eligibility, waiver, transfer, registration, financial, rights, and deadline fields match the person-level records and locked rules to the available precision.
11. Every depth, package, and special-teams assignment points to one registered player. An unavailable nominal player may remain visible only with an explicit available replacement.
12. A player actually used in a game is eligible in the applicable primary status, holds the required game-day designation, and is not suspended, ineligible, or medically unavailable.
13. No football assignment, game-day designation, or coach preference overrides a clinician or governing-process restriction.
14. The latest closed Document 6 medical or availability communication points to the individual current-state record, and every derived index, control-table, and Document 5 summary matches that record.
15. Medical clearance comes only from the clinician or process established in Document 3 and, where applicable, Document 2. A public report, practice participation, player statement, or coach judgment never grants clearance.
16. The latest valid clinician or process communication controls current clearance; a stale or superseded report cannot reopen an earlier status.
17. Clearance does not itself make a player game-day active, and an active designation cannot override non-clearance.
18. Clearance, public designation, practice participation, communicated limitation, football-use availability, coaching deployment, and expected effectiveness remain separate fields.
19. Every effectiveness expectation identifies a football evaluator, evidence, date, and uncertainty; it is not presented as a medical conclusion.
20. Practice repetitions, game workload, recovery load, and development claims do not contradict the dated schedule or Document 6 game ledger.
21. Every active staff member has a verified starting appointment or a closed Document 6 appointment event.
22. A hired or active staff member is not simultaneously active in the candidate register; former-employer, contract, playing-rights, permission, release, and retirement conditions are resolved where applicable.
23. Document 3 is the sole source of final organizational authority. Every authority or formal delegation reference here resolves to its current version, and no title creates an unstated power.
24. Offensive, defensive, and special-teams operating roles and play-calling delegation match Document 3 and the current staff records.
25. Every staff or player assessment identifies its evaluator, evidence, date, uncertainty, and canon class where material.
26. Disagreements remain attributed and are not averaged into a consensus, score, or hidden rating.
27. Person-specific concerns do not become universal morale, trust, prestige, job-security, or relationship meters.
28. All content in this register is public, was created or decided by the head coach, was plausibly observed by the head coach, or was plausibly communicated to the head coach; no hidden diagnosis, private thought, confidential uncommunicated decision, or staff-held secret appears in it.
29. A real person's pre-divergence history is factually dated, any retrospective source is limited to the earlier proposition it proves, and actual later history has not leaked into evaluation or simulation canon.
30. A real person's candidate interest, availability, endorsement, retirement, relocation willingness, references, private motives, and conditions remain unknown until learned through a plausible coach-facing channel.
31. Any injury to a real person after divergence is clearly a simulated football event and is never worded as an assertion about actual history or used to introduce a stigmatizing private claim.
32. No pending proposal, recommendation, report, expectation, negotiation, interview, offer, waiver claim, or intended move is recorded as completed.
33. Every material current-state change comes from a closed dated Document 6 event, follows the atomic update order, and has a matching Document 5 snapshot update.
34. Cumulative game statistics agree with Document 6; this register does not create a competing total.
35. Every corrected current field points to the authoritative Document 6 correction or supersession; this document contains no independent correction history.
36. Before a team change or season-phase reset, a dated Document 4 snapshot is closed and linked in Document 6; unresolved staff, contract, rights, medical, and candidate matters survive the handoff rather than being overwritten.
37. Any player with a current medical or availability event, communicated limitation, material contract or eligibility issue, or live decision has an individual record; an index-only row cannot carry the sole supporting detail.
38. Before career initialization, every requirement in the Document 4 initialization gate is satisfied and the register is explicitly marked `RECONCILED` or `RECONCILED WITH NOTED UNCERTAINTY`, with no blocking uncertainty.

If an invariant fails, mark the register `Conflicted`, identify the affected decisions, and do not silently continue through them.

## Contradictions and corrections

Use the project's canon authority order. Document 6 is the sole authoritative correction and supersession ledger. Do not silently repair a conflict, select a convenient source, erase prior evidence, or create an independent correction history here.

### Correction procedure

1. Identify the exact conflicting fields and the first date on which they diverged.
2. Preserve the competing claims, sources, and evidence labels in the staged Document 6 correction event.
3. Determine the controlling record under the canon authority order.
4. If intent or divergence cannot be determined, ask the user whether the difference is an error, intentional fiction, alternate history, or unresolved contradiction.
5. In Document 6, append the authoritative correction or supersession, its effective date, controlling authority, prior value, corrected value, and every dependent field affected.
6. Replace only the current fields here, attach the generated Document 6 pointer, and apply the normal atomic update order.
7. Reconcile counts, depth, packages, availability, staff assignments, contracts or eligibility, financial controls, and Document 5 before closing the Document 6 update.
8. Tell the user about any correction that changes available actions, prior results, authority, or established canon.

### Generated Document 6 correction-pointer index

| Affected current field | Document 6 correction or supersession label | Effective date | Current corrected value | Last reconciled |
|---|---|---|---|---|
| `[FIELD OR RECORD]` | `[DOCUMENT 6 LABEL]` | `[DATE]` | `[CURRENT VALUE]` | `[DATE, CLOSED UPDATE LABEL]` |

This table is generated from Document 6 and is only a navigation aid. Active unresolved conflicts remain in the reconciliation block and Document 5; resolved history, controlling authority, notification, and superseded values remain only in Document 6.

## End-of-update control block

- Owned content last changed/effective: `[DATE, TIME, TIME ZONE]`
- Document 2 locked version: `[VERSION]`
- Document 3 authority-map version: `[VERSION]`
- Document 4 register version: `[VERSION]`
- Supersedes Document 4 version/content-changing update: `[VERSION AND LABEL / NONE]`
- Last Document 4 content-changing update: `[LABEL]`
- Latest Document 6 source event applied to Document 4 content: `[EVENT, DATE, TIME]`
- Document 4 initialization status: `[RECONCILED / RECONCILED WITH NOTED UNCERTAINTY / CONFLICTED / NOT INITIALIZED]`
- Player counts reconciled: `[YES / NO, WITH ISSUE]`
- Primary roster statuses disjoint and exact limits reconciled: `[YES / NO, WITH ISSUE]`
- Game-day designation subsets reconciled without nested counting: `[YES / NO / NOT APPLICABLE, WITH ISSUE]`
- League cap or floor legality reconciled: `[YES / NO / NOT APPLICABLE, WITH ISSUE]`
- League accounting liability reconciled: `[YES / NO / NOT APPLICABLE, WITH ISSUE]`
- Cash and guarantees reconciled: `[YES / NO / NOT APPLICABLE, WITH ISSUE]`
- Internal budget reconciled: `[YES / NO / NOT APPLICABLE, WITH ISSUE]`
- Scholarship or aid reconciled: `[YES / NO / NOT APPLICABLE, WITH ISSUE]`
- Contract, eligibility, and rights controls reconciled: `[YES / NO / NOT APPLICABLE, WITH ISSUE]`
- Depth, packages, and special teams reconciled: `[YES / NO, WITH ISSUE]`
- Medical and availability table reconciled: `[YES / NO, WITH ISSUE]`
- Coach-facing information boundary checked: `[YES / NO, WITH ISSUE]`
- Document 3 authority cross-references and play calling reconciled: `[YES / NO, WITH ISSUE]`
- Current Season State updated: `[YES / NO]`
- Document 6 update closed: `[YES / NO / NOT REQUIRED]`
- Generated Document 6 correction pointers or unresolved conflicts: `[LABELS OR NONE]`
- Next required registry update: `[EVENT]`
