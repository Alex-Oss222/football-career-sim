# One Separate Result Per Event: reusable output template

**Design status:** Proposed, updated to make the user's per-event output rule explicit. This is a template for **one individual result document**, not an `Event_Results.md` omnibus. Every distinct event that reaches a final disposition receives its own dated, readable Markdown result in the period where it happened, even if multiple events were introduced by the same weekly briefing or answered together on `My_Responses.md`.

## Non-negotiable output ownership

1. **One event, one separate result file.** A trade inquiry, another trade inquiry, a player extension discussion, a staff permission request and a roster transaction must never be merged into one outcome narrative. The result file is distinct from `Game_Report.md`, `Bye_Week_Report.md`, `My_Responses.md`, and the briefing.
2. **Write promptly at disposition.** Create or finalize the result when the event is resolved on its in-career date, *not* only after the week's game closes. If nothing is yet decided, keep a dated open offer/process record and do not invent a final outcome.
3. **Not only successful transactions.** Accepted, rejected, countered-and-closed, withdrawn, lapsed after a valid elapsed deadline, permission granted or denied, and negotiations ending without agreement are all possible dispositions. Each **closed** event gets a separate result. A live counteroffer stays in its dated process record until the matter closes, then gets its result.
4. **Single canonical outcome.** Store each result under the event's proper department or career phase as the authoritative reader-facing outcome, using the repository folder map. The current week/phase index links to each separate output. Do not copy an entire trade or contract into a second competing results file. An executed trade's existing standalone completed-trade record can itself serve as its event output.
5. **Never merge outputs.** A weekly report may say, “Caldwell rejected the [club] proposal” and link to that event's result, but cannot substitute for that file. A combined list of links is an index, not an output.
6. **Time and identity.** Preserve the actual simulated receipt/decision time, final effective date, counterparties, governing authority, user answer and original triggering event ID (the ID stays in machine metadata, not ordinary football prose). Preserve earlier records and any offer version history.

## Reusable contents of EACH individual output

# [Event title: e.g. Trade Result, Player Extension Result, Assistant Interview Permission Result]

**Event date:** [Simulated date and time, if known]

**Resolved on:** [Date/time the final actor decided or the offer properly expired]

**Involving:** [Player, coach, club and participants relevant to THIS event]

**What happened:** [One to three factual sentences describing the offer or issue and the process that actually occurred]

**Stone's answer:** [Actual response or applicable standing instruction, linked to its recorded source, or “No response required”]

**Final decision:** [Who has authority and what that person/club decided, or what independently occurred]

**Outcome:** [Executed / rejected / withdrawn / declined / granted / denied / expired / negotiations ended / other supported disposition]

**Changes effective:** [What changed and when, or “No contract, roster, staff or employment change”]

**Outstanding issue:** [Only a genuinely separate unresolved follow-up, with link, or “None”]

**Source records:** [Links to the actual trade, contract, roster, medical, staff or employment owner; never invented facts]

## Examples of separate outputs in one week

The following are **file-name illustrations**, not real 2014 events. Use the owning event's actual season/phase folder map rather than blindly copying these filenames.

| Event introduced during Week 8 | Its OWN standalone output after resolution |
|---|---|
| Trade discussion with Club A rejected | `Trade_Result_2014-10-21_Club_A.md` in the trade department |
| Separate trade discussion with Club B accepted | A dated standalone completed trade result for Club B in the trade department |
| Player X extension negotiations end without a deal | `Player_Extension_Result_2014-10-23_Player_X.md` in contracts/personnel |
| Player Y is legally moved to a reserve list | `Roster_Move_Result_2014-10-24_Player_Y.md` in the relevant team transaction records |
| Assistant Z interview request is denied | `Assistant_Permission_Result_2014-10-24_Coach_Z.md` in staff/career records |

The Week 8 briefing can contain all five notices. `My_Responses.md` can contain responses to all five. **The five outputs above remain separate**, created on the dates the corresponding events actually resolve, and the Week 8 report links to them individually.

## Scope notes

- An injury by itself is a medical occurrence, not proof of a roster vacancy. If medical status changes, preserve it in its medical record. If it also creates a completed roster move, give *that transaction* a separate output.
- An inquiry does not guarantee a transaction. A rejection is still a documented result of the inquiry.
- No offer is a contract, no permission is an interview, and no interview is a hire. Distinct decisions must remain distinguishable.
- After Stone is dismissed, his employment result and later agent/interview/offer results are kept in his career phase; Jacksonville's private briefings must not follow him.
