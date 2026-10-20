# Coaching vacancy / assistant hiring, three-page templates

**Design:** Candidate Report → My Hire → Staff Hire. An actual vacancy appears first as a conspicuous insert in whichever briefing is active. If your hiring input is required, this vacancy gets its own full Candidate Report, a fill-in My Hire page, and a search outcome/index. Each concluded permission request, candidate interview when recorded as a distinct event, offer resolution, departure and accepted appointment keeps its own independent dated event output. The weekly/phase report merely links these records.

**Status:** Research/design only. No changes to the football-career-sim repository or current staff. No future Jacksonville 2015 hiring result is assumed or created. Historic 2014 Lowry/Westhoff sequence is used as a **closed example only**.

## Files

| File | Who uses it | What it contains |
|---|---|---|
| `Candidate_Report_TEMPLATE.md` | Football operations creates it | Vacancy, real duties, candidates with employer/permission/interest status, evidence, advice, and precise question for Stone |
| `My_Hire_TEMPLATE.md` | Stone fills it | Interim coverage, outreach order, interview direction, post-interview choice, explicit negotiating limits, fallbacks |
| `Staff_Hire_TEMPLATE.md` | Club creates it after actual events | Search status and index of individual dated results, with executed appointment terms only if a hire closes |
| `Individual_Search_Event_Result_TEMPLATE.md` | Club creates one per concluded material event | Each permission denial, withdrawal, offer resolution or accepted appointment, on its in-career date |
| `2014_Westhoff_Precedent_and_2015_Setup.md` | Example and testing | Real 2014 special-teams search without retroactive changes; no invented next-cycle candidate |
| `Implementation_Spec.md` | Developer/runner | Applicable 2014 NFL rights, contracts, state transitions, data-owner routing and 32 regression tests |

## When to use

Use for a confirmed departure, actual open assistant job, authorized new coaching position or a conditional vacancy after its condition becomes true. January is common, but a real vacancy may also occur during the playing season. If the assistant's deal is merely approaching expiry, handle the retention question in the Staff Status Report first. Do not open a hiring search from a rumor, from an unverified coach contract lapse, or because the system thinks the staff could use a stronger name.

## Rules that survive every change

- A shortlist is not a permission grant, an interview, an offer or a hire.
- Stone hires his assistants within his actual authority; Caldwell verifies funding and executes the club's finances; the candidate controls acceptance.
- Being a familiar former head coach does not prove he will accept, teach well, improve a unit or want a lesser title.
- A new title does not automatically shift Stone's existing offensive/defensive play calls.
- A declined candidate does not disappear from history. The record has a dated outcome, while the vacancy may remain open.
- One event, one independent output at the time it is resolved. `Staff_Hire.md` summarizes and links, never replaces them.
- No future real coaching changes are imported as outcomes in this divergent 2013-onward Jacksonville career.
