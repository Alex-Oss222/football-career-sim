# Role: Between Jobs

**Document status:** Durable description of the coach's position between appointments in the career layer
**Adopted:** October 18, 2026, from the user's design of the career layer of the same date; no simulation clock advance.
**Desk:** No desk is built for this role yet. The job record marks this position with `status: "BETWEEN_JOBS"` and no current appointment; the employment events that lead to it (dismissal, search, offer, acceptance and onboarding) are not built either.

This file describes the position, not a particular search. When the run stops is set by the [decision rules](../decision_rules.md) and the [decision classes](../../docs/career_layer.md#3-decision-classes); the procedure for a search in which Stone is the candidate is Document 3's [search-cycle procedure](../03_Head_Coach_Organization_and_Authority_Canon.md#10-external-hiring-market-and-search-cycle-procedure) and the AGENTS.md hiring-search task; this file restates none of them.

## 1. What he works with

The main workspace changes to:

- his accumulated career and coaching evidence;
- actual vacancies and dated interest;
- references and contacts established in the career;
- public information about prospective employers;
- additional information specifically supplied during interviews;
- offers, competing deadlines and unresolved employment obligations.

He keeps his knowledge and career history. He loses continuing access to the old employer's newly generated internal information, and another club's confidential scouting, medical or negotiation information is never exposed merely because it exists somewhere in the repository ([decision rules](../decision_rules.md#5-access), section 5).

## 2. The sequence and where it stops

Each step is a separate event: an opening exists; the other club is interested; Stone chooses whether to interview; the interview produces rejection, further discussion or an offer; Stone chooses whether to accept the actual terms. Interest is not an offer, and an offer is not an acceptance. Only while he is still under contract to a club, for example after resigning before his contract expires (rule E5, labelled a pattern there), does the interested club request permission, which is granted or refused, before he chooses whether to interview. A dismissed or unemployed coach, or one whose contract has expired, needs no permission ([hiring rules](../../library/2014_coaching_hiring_and_anti_tampering_rules.md#12-contract-status-unemployed-expired-resigned-own-staff), section 1.2, rules E1 and E2).

- **After a dismissal.** The career records the effective date, the communicated explanation, what is established about continuing compensation, and any open terms. Nothing unrecorded about the contract, such as salary, offsets or termination mechanics, is invented. It stops for his next direction: pursue head-coaching openings, consider coordinator roles, consider other work, or remain out of coaching. These can be combined into a search brief with boundaries.
- **While the market runs.** It stops for a substantive interview commitment, an offer, a counter outside existing instructions, or a conflict between deadlines.
- **Before he accepts a job.** He receives a concrete dossier: who the head coach and general manager are; why the position is open; whether he would call plays; who chooses the system and what the head coach requires retained; which assistants are inherited and what staffing input he has; the unit's roster, existing assignments and known weaknesses; the personnel resources and constraints the club communicates; the contract terms and evaluation expectations; what success would mean in that job.
- **After he accepts.** Acceptance creates a new appointment in the job record. It does not transfer the former club's players, staff, cap space or medical records into the new club. It stops to establish his program within the accepted authority.

## 3. What runs automatically

Clubs evaluate him, request interviews, decline interest, pursue other candidates and make offers under their own authority and criteria. Administrative scheduling proceeds under his search brief. Each employer's decision and its notification are the employer's; his response is his.

## 4. Evaluation by a new employer

Evidence that could support a new appointment for a former head coach rebuilding his career: explaining the previous tenure honestly; demonstrating useful current expertise; succeeding within reduced authority; establishing why another employer should trust him. A downward move, such as from head coach to coordinator elsewhere, is a normal career branch. The 2014 permission, timing and Rooney Rule constraints are in the [hiring rules](../../library/2014_coaching_hiring_and_anti_tampering_rules.md), and the career examples in the [coaching career path](../../library/nfl_coaching_career_path.md).

## 5. Desk sections

Career, Vacancies, Contacts and Offers (`ROLE_SECTIONS` in `runtime/current_job.py`). No desk is built for this role yet.
