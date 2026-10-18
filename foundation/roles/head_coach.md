# Role: Head Coach

**Document status:** Durable description of the head coach's job in the career layer
**Adopted:** October 18, 2026, from the user's design of the career layer of the same date; no simulation clock advance.
**Desk:** Built. `python scripts/render_career_views.py` renders it in the active season's `README.md` from the current job record.

This file describes the job, not the current appointment, and the actual employment agreement adjusts it. Who employs Stone, what each Document 3 row lets him do, who calls each phase and which standing instructions are in force are in the [current job record](../../state/current_job.json). When the run stops is set by the [decision rules](../decision_rules.md); which of his decisions may hold which events is the [decision classes](../../docs/career_layer.md#3-decision-classes), and when they fall in the year is the [season cycle](../../docs/season_cycle_milestones.md#1-the-yearly-cycle) and the [career milestones](../../docs/season_cycle_milestones.md#2-career-milestones). This file restates none of them. An interim head coach uses this role and this desk.

## 1. The six areas

The head coach works from a team-wide view in six areas.

| Area | What he needs in front of him | What he does | Document 3 rows it draws on |
|---|---|---|---|
| Team preparation | All three unit plans, installation limits, practice priorities, staffing conflicts | Sets priorities, resolves conflicts and delegates | 11; 12 to 14 for the unit plans |
| Players and roles | Roster, availability, depth, competitions, development evidence and alternatives | Chooses eligible lineups, roles and game-day use | 8 to 10; 15 to 17 for availability |
| Coaching staff | Responsibilities, performance, contracts and available budget | Hires, assigns and evaluates within his established authority | 2, 6 and 22 |
| Personnel partnership | Needs, candidate evaluations, proposed transactions, costs and consequences | Makes recommendations; exercises required consultation rights | 3, 3a, 4, 5, 7 and 20 |
| Game management | Approved plans, contingencies, retained decisions and coordinator responsibilities | Makes the decisions he retains and the game actually supports | 12 to 14 |
| Employment | Owner and general manager expectations, feedback, contract status, market contacts | Responds, negotiates and makes his own career choices | 1 |

A draft recommendation is his contribution; the general manager's actual selection remains the general manager's decision. A medical restriction is information he must respect; choosing the replacement is a football decision.

## 2. The six fields

Every appointment records six things separately, so that a change of job changes them. The current appointment records them here:

| Field | Where the current appointment records it |
|---|---|
| What he can see | `authority.domains[].sees`; null means the default, `default_sees`, which links Document 3's boundary rules (section 6.2) |
| What he prepares and recommends | The `authority.domains[]` rows whose `stone_action` is `recommends`, `consulted`, `responds` or `informs`, with their `scope` |
| What he decides | The rows whose `stone_action` is `decides` or `decides_part` (with its `scope`), and `delegation.game_management` for the retained game decisions |
| What has been delegated, to him or by him | `authority.domains[].delegated` names the phase whose dated intervals in `delegation.play_calling` say who calls, prepares and transmits it; `delegation.relay` and `delegation.emergency` hold the game-day relays and the emergency leads |
| Who can overrule him | `authority.domains[].final` (who holds final authority on each row) and `overruled_by` (null where nothing is recorded); `reporting` for who decides his employment and the line he reports through |
| What evidence his employer will use | `evaluation` and `employer_requests`, each linked to its source, and `authority.domains[].evaluated_on` (null where nothing is recorded) |

## 3. What runs automatically

Routine preparation within the approved plans runs on its own, and so does the evidence each stage assembles: for a game week, the last game's evidence, the opponent brief, availability, standings and the routine preparation. Decisions that belong to others under their own authority rows also run without him: the general manager's transactions, the medical staff's diagnosis and clearance, the employer's employment decisions, and every other club's games and moves. The game itself runs except for the decisions that pause it. What resolves on its own at each point in the year is the season cycle's "Resolves automatically" column.

An ordinary week runs: the brief, his consolidated decisions, automatic preparation, the supported game decisions, then the result and the next brief.

## 4. Game management

The job record's `delegation.game_management.decisions[].mechanism` says which retained game decisions the game actually puts to him: `live` (a pause, unless the week's call sheet freezes a rule), `sheet_rule` (the call sheet's frozen rule, or a pause when the rule says ask), `not_live` (set by the game model) or `not_modelled`. As the record stands, fourth downs are live, two-point tries and onside kicks follow the sheet rule, and timeouts, clock use and kneels are not yet Stone's live calls: the game model sets them with each replayed drive ([defect register](../../runtime/defect_register.md) item 30). No replay challenge is modelled. If this section and the record differ, the record controls.

A defensive call sheet is a record of the calls: in the current game model it changes no result ([coordinator](coordinator.md#2-calling)).

## 5. Stops

His stops are the open holder-owned items in the [decision queue](../../state/decision_queue.json). The decision classes say which events each kind may hold, the season cycle says when they fall, and the [decision rules](../decision_rules.md) say what each presented decision contains. The desk's "Waiting on you" section lists the open ones.

## 6. Evaluation

What his employer measures is the job record's `evaluation`. Evidence that could support a bigger opportunity for a head coach: managing all three phases; assembling and supervising staff; working with personnel leadership; developing players; handling adversity; making team-level decisions. The annual review updates that evidence; it awards nothing automatically.

## 7. Desk

The desk's sections are Team, Staff, Weekly plan, Personnel partnership, Ownership and Career (`ROLE_SECTIONS` in `runtime/current_job.py`), with the items waiting on him, the items with others, the next dated events, who does what on game day and the standing instructions. Like every view, it links the same underlying records and holds no copy of the roster.
