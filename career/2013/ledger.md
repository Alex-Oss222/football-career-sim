# 2013 season ledger

This is the 2013 slice of Document 6's append-only ledger (schema/format defined in `foundation/06_Chronology_Game_Ledger_and_Handoff.md`, not here). Per Document 6 §12.5, it opens with a single audited closure entry summarizing the already-resolved pre-hire search, not a re-resolution of it.

## Entry 1 — PRE-HIRE SEARCH CLOSURE

**Date range:** January 14-16, 2013 (search), January 15, 2013 (accepted hire).

**Teams pursued:** Jacksonville Jaguars, Arizona Cardinals, Philadelphia Eagles, Chicago Bears, in that priority order (San Diego Chargers excluded per the user's own brief). Full detail: `offseason/hiring_search.md`, Entries 1-7.

**Material user decisions:** priority order and per-team terms (`hiring_search_brief/00`-`04`); consolidated interview positions, framed as interview-only and not permanent coaching-identity canon (`hiring_search_brief/05`); the Saints bounty-knowledge answer, also interview-only (`hiring_search_brief/06`); the Jacksonville counter-offer authorization trading partial guarantee vesting for a limited quarterback-decision concurrence right, with an explicit fallback to accept the original offer if declined (`hiring_search_brief/07`).

**Offers and counters:** Jacksonville offered a 4-year, fully guaranteed head-coaching contract (Entry 6). Stone's countered exchange (partial Years 3-4 vesting for a franchise-quarterback concurrence right) was declined by Caldwell without a counter-counter; the pre-authorized fallback then applied.

**Accepted result:** Stone accepted Jacksonville's original offer, unchanged, on January 15, 2013 — 4 years, fully guaranteed. Stone: play-calling, staff selection, depth chart, game-day authority. Caldwell: contracts, cap, scouting, acquisitions, draft, and final say on franchise-level quarterback decisions after required consultation. Full terms: Document 3 §3.1 and the Authority Map (§5).

**Hiring-search ledger reference:** `career/2013/offseason/hiring_search.md`, Entry 7.

This entry documents the completed pre-hire history. It does not re-resolve the search or import any later development as a hiring-search event.

## Entry 2 — Staff hired

Full coaching staff closed across two rounds of calls, late January 2013. Record: `offseason/staff_building/hires.md`. Current staff: `coaching_staff.md`.

## Open item blocking further entries

Free agency (real opening: March 12, 2013) cannot be resolved as a simulated event until `offseason/initial_cap_sheet.md`'s per-player 2013 cap-charge gap is closed — see `offseason/free_agency/signings.md` for the blocking record from the attempted March 12 batch. No game, transaction requiring cap-legality, or further dated event may be entered here until that reconciliation closes and `state/05_Current_Season_State.md` reflects it.

## Entry 3: completed free-agency batch reconciled

**Global package checkpoint:** `Canonical update - March 12, 2013, 4:00 p.m. ET - reconcile completed free agency`
**Preceding global package checkpoint:** `PRE-HIRE SEARCH CLOSURE, career/2013/ledger.md, 2026-09-18`
**Canonical through:** March 12, 2013, 4:00 p.m. ET, the existing batch's operative timestamp; individual execution times are not supplied.
**Documentation date:** September 19, 2026.
**Record type:** Retrospective reconciliation of accepted post-divergence simulation outcomes; no new resolution or elapsed time.

### Controlling source and supersession

The user expressly identified these as simulated signings to preserve and requested improved layout, full cap ramifications and a roster update. The controlling completed record is [signings.md at commit 9493ead](https://github.com/Alex-Oss222/football-career-sim/blob/9493ead88a40c58aaddebb38db2990a717c279ce/career/2013/offseason/free_agency/signings.md), merged into main by PR #26. Its outcomes and contract terms are unchanged.

This entry supersedes the old **Open item blocking further entries** paragraph above for the accepted March 12 batch, and the obsolete January/pre-hire current-state fields in Documents 4-5. That earlier text remains as append-only history. Current state becomes “opening FA batch complete, with accounting/control uncertainties,” not “FA still unrun.” Missing financial data remain open; no release decision is reopened. January source tables remain historical snapshots.

This reconciliation does not reconstruct a prior ex-ante decision packet, reroll outcomes or certify full game readiness. It records the user's controlling preservation instruction and aligns the dependent records to the completed source.

### Preserved transactions

| Player | Recorded outcome | Terms or effect |
|---|---|---|
| Sen'Derrick Marks | Signed | 1 year, $1.50M; $0.40M bonus, $1.10M 2013 base |
| Alan Ball | Signed | 1 year, $1.00M; $0.20M bonus, $0.80M 2013 base |
| Brad Meester | Re-signed | 1 year, $1.50M; $0.50M bonus, $1.00M 2013 base |
| Roy Miller | Signed | 2 years, $5.00M; $1.50M bonus; bases $1.00M/$2.50M; only bonus guaranteed |
| Daryl Smith | Re-signed | 2 years, $6.00M; $1.00M bonus; bases $2.00M/$3.00M; only bonus guaranteed |
| Brent Grimes | Signed after Bennett declined | 1 year, $5.50M; $2.00M bonus, $3.50M base; full amount guaranteed |
| Michael Bennett | Declined | Offered 1 year, $6.25M, $4.00M guaranteed; activates Grimes contingency; no charge |
| Justin Forsett | Declined | Offered 1 year, $1.10M, $0.30M guaranteed; no charge |
| Guy Whimper | Released | Removed from working roster; financial effects unresolved |
| Aaron Ross | Released | Removed from working roster; financial effects unresolved |
| Dawan Landry | Released | Removed from working roster; financial effects unresolved |
| Laurent Robinson | Released | Removed from working roster; financial effects unresolved |

Caldwell executed the recorded player decisions under the existing authority map. No trade was solicited or resolved for the released veterans. Bennett and Forsett's actual later destinations remain unknown in branch canon. Marks, Ball and Meester's base-salary guarantees are unspecified.

Smith's medical review remains satisfactory for the short return; Grimes' review remains completed with Achilles uncertainty. Neither supplies practice clearance, a return date or guaranteed performance. No starter, workload or package assignment is added. Original pursuit explanations remain verbatim in the reformatted signing file.

### Accounting and roster delta

- Six-deal value: $20.50M. Signing bonuses: $5.60M. Scheduled cap: $13.75M in 2013 and $6.75M in 2014.
- 2013 salary plus signing bonus: $15.00M if all salary is earned; payment installments unrecorded. 2014 salary if retained: $5.50M.
- Bonuses plus expressly guaranteed salary: at least $9.10M; not a claim that all other base salary is unguaranteed.
- Existing planning arithmetic: approximately $22.10M less $13.75M = approximately $8.35M. The full gross charges remain provisional debits; no unsupported Top-51 displacement credit or release saving is added.
- Full adjusted cap, inherited obligations, release dead money and exact net counted changes remain unreconciled. Unknown release exposure may reduce available room.
- Working inventory: 63 historical names - 4 departures + 4 outside additions = 63. Two re-signings update existing people. Six current batch agreements plus 57 carry-forwards are evidence categories, not exact official roster statuses.
- Staff appointments and operating assignments come from Entry 2 and the existing coaching-staff register. No staff term, acquisition authority or medical authority changes.

### Candidate-bundle manifest

Target and preceding checkpoints in every row below are the exact labels defined above. Documents 1-3 retain their pre-existing content and pointers; their git blobs identify the exact versions used.

| Candidate file | Candidate/current version | Target checkpoint | Preceding checkpoint | Preceding content-changing update | Owned content changes? |
|---|---|---|---|---|---|
| Document 1 | `697208640886f9f63581f4b865f917f16007f036` | Entry 3 target above | Entry 3 preceding above | Existing September 18 rebuild | No |
| Document 2 | `4dcdaa9bb3812ffe47b1bc7007dda73204cbc170` | Entry 3 target above | Entry 3 preceding above | Existing September 18 sourcebook | No |
| Document 3 | `9538b8e4831eba1a407c394a37c21972f8b8e290` | Entry 3 target above | Entry 3 preceding above | Existing September 18 canon | No |
| Document 4 | `JAX-2013-FA-ROSTER-1` | Entry 3 target above | Entry 3 preceding above | JAX-2013-INIT-STAGED-1 / 2013-INIT-ROSTER | Yes; supersedes that staged register |
| Document 5 | `JAX-2013-FA-SNAPSHOT-1` | Entry 3 target above | Entry 3 preceding above | Pre-hire snapshot 1.1 / preceding checkpoint above | Yes; replacement snapshot |

Supporting files in the same bundle: reformatted `offseason/free_agency/signings.md`; new `roster.md`; navigation-only additions to `offseason/initial_roster.md` and `offseason/initial_cap_sheet.md`. Both historical source tables remain unchanged.

### Bounded reconciliation audit

The original pursuit narratives and twelve outcomes are preserved; agreement arithmetic, annual cap/cash splits, unique player IDs, additions/departures, re-signing counts, medical limitations, relative links and cross-file checkpoint/version references are checked. The roster view and Documents 4-5 share the same six confirmed agreements and four departures. Unresolved inherited people are not newly signed.

No game or statistics require reconciliation. No actual future result or new private-state claim is introduced. This is a bounded documentation audit, not the first full initialization or game-readiness audit. The prior cadence counter remains 0 because retrospective migration does not count as a substantive simulated turn.

### Closed canonical update register

| Global package checkpoint label | Canonical through | Preceding global checkpoint | Content versions changed | Closed continuity baseline created | Non-game cadence count after closure |
|---|---|---|---|---|---:|
| Canonical update - March 12, 2013, 4:00 p.m. ET - reconcile completed free agency | March 12, 2013, 4:00 p.m. ET, batch time | PRE-HIRE SEARCH CLOSURE, career/2013/ledger.md, 2026-09-18 | Document 4: JAX-2013-FA-ROSTER-1; Document 5: JAX-2013-FA-SNAPSHOT-1; this season ledger and supporting files | Completed-FA transaction reconciliation only | 0 |

Commit closed — Canonical update - March 12, 2013, 4:00 p.m. ET - reconcile completed free agency — canonical through March 12, 2013, 4:00 p.m. ET

Closure applies when this complete candidate bundle is promoted together. Intermediate file commits on the review branch do not replace the preceding active package.

## Entry 4 — PRE-DRAFT TRANSACTION AND SELECTION PACKET (closed ex ante)

**Packet closed:** Before the quarterback calls during the March 12-April 24, 2013 window; April 24, 2013 for the draft decisions.
**Information ceiling:** April 24, 2013.
**Status at closure:** Outcomes unresolved. This entry records the decision inputs before any response, selection, or draft-day trade is generated; results follow in later entries and transaction files.

### Authorized Jacksonville actions

- Caldwell will ask Washington whether Kirk Cousins is available. Jacksonville may offer either (a) selection #208 plus its 2014 third, escalating in place of that third to a 2014 second if Cousins makes 10 regular-season starts or plays 65% of Jacksonville's 2013 regular-season offensive snaps, or (b) Jacksonville's 2014 second by itself. No other compensation is authorized.
- Caldwell will check Blaine Gabbert's market with Green Bay, Atlanta, Cincinnati, and Chicago, opening at a 2014 fifth and permitted to consider a 2014 sixth escalating to a fifth on a defined playing-time condition. If a pick return does not materialize, Caldwell may compare a direct player return that addresses a documented roster need; C.J. Wilson or a comparable defensive-front depth piece is inside the user-authorized alternative.
- Caldwell will check Chad Henne's market with the same four clubs, opening at a 2014 fifth and permitted to consider a fifth, sixth, or conditional sixth escalating to a fifth. Jacksonville may retain both incumbents; no sale is required.
- Caldwell has final transaction authority. Stone's documented quarterback projection and consultation right apply to a premium-capital quarterback acquisition. Stone's football preference is evidence, not a veto and not an instruction to force a deal.

### Frozen trade conditions and uncertainty

Washington has a concrete reason to value inexpensive quarterback insurance while Robert Griffin III rehabilitates, but its private valuation and willingness to trade are unknown. The four clubs on Jacksonville's outbound call list may value veteran depth, yet none has an established need or bid in this branch. Gabbert's remaining guaranteed contract and both incumbents' value to Jacksonville are real frictions. Plausible outcomes include no discussion, a counter beyond authority, an acceptable structure, a weak outbound offer, or no bid. Carrying Gabbert and Henne is inside the plausible range.

### Frozen draft conditions

- Jacksonville enters with selections #2, #33, #64, #98, #135, #169, and #208, subject to any trade actually completed before or during the draft.
- Stone recommends Lane Johnson within the top tackle cluster at #2; a serious Travis Kelce comparison at #33; Keenan Allen and Jordan Poyer in their stated ranges; David Bakhtiari around #98; and Lavar Edwards around #135. The full comparison set and role objections remain those in `offseason/draft/player_draft_board.md`.
- Caldwell retains final selection and draft-trade authority. He may deviate where the contemporaneous scouting/value case supports it. A first-round quarterback would trigger Stone's consultation right; no quarterback is mandated or barred.
- Other clubs choose autonomously from dated pre-selection evidence, roster need, value, and bounded uncertainty. Their real 2013 selections and every post-April-24 outcome are quarantined. Jacksonville receives no protection from another club selecting one of Stone's preferred players.

### Resolution discipline

The packet is reduced to terms, authority, roster needs, contemporaneous public evaluations, and known contract/medical uncertainty. Authorship, protagonist status, persuasiveness, desired outcome, and later player success are excluded. The label-swap test applies. Any bounded random draw is derived only after this packet closes; no seed may be changed to obtain a preferred result.

## Entry 5 — Pre-draft quarterback/front transactions completed

**Date:** March 12-April 24, 2013 pre-draft window; exact execution dates are not separately established.
**Ex-ante authority:** Entry 4; trades/trade_targets.md.
**Result:** Two completed trades.

### Kirk Cousins acquired

Washington accepted Jacksonville's 2014 second-round selection outright for Kirk Cousins. The deal uses one of the two structures already authorized in Entry 4. No 2013 selection is included and there is no playing-time escalator. Caldwell completed the required franchise-quarterback consultation with Stone before execution.

**Roster/draft-capital delta:** Cousins joins Jacksonville; Washington receives Jacksonville's 2014 second. All seven 2013 selections remain with Jacksonville.

### Blaine Gabbert exchanged for C.J. Wilson

After the Cousins acquisition, Green Bay offered DE C.J. Wilson instead of Jacksonville's preferred future-pick return for Gabbert. Caldwell accepted the direct roster-value exchange after comparing Jacksonville's defensive-front need with the value of carrying a third veteran quarterback.

**Roster delta:** Gabbert leaves Jacksonville for Green Bay; Wilson joins Jacksonville. No pick changes hands.

Chad Henne remains a Jaguar as veteran quarterback insurance. Exact Gabbert/Wilson contract assignment, acceleration, Top-51 displacement, and Cousins incoming cap treatment remain unresolved pending the financial ledger; no unsupported dollar delta is invented.

Complete transaction record: trades/trades.md. Negotiation record: trades/trade_targets.md, §8.

## Entry 6 — 2013 NFL Draft completed

**Dates:** April 25-27, 2013.
**Ex-ante authority and information ceiling:** Entry 4; offseason/draft/player_draft_board.md; pre-selection library through April 24.
**Result:** Seven Jacksonville selections; no Jacksonville draft-day trade.

| Selection | Player | Position | School |
|---:|---|---|---|
| #2 | Lane Johnson | OT | Oklahoma |
| #33 | Travis Kelce | TE | Cincinnati |
| #64 | Jordan Poyer | CB | Oregon State |
| #98 | Sio Moore | OLB | Connecticut |
| #135 | Lavar Edwards | DE | LSU |
| #169 | Bacarri Rambo | S | Georgia |
| #208 | Tyler Bray | QB | Tennessee |

Kansas City selected Eric Fisher before Jacksonville's first turn. Keenan Allen was unavailable by #64, and David Bakhtiari was unavailable by #98. Other clubs' intervening selections were resolved autonomously from contemporaneous information; actual 2013 selections and later careers were not used. The Jacksonville availability record, Caldwell's decisions, Stone's initial role plans, and evidence limits are in offseason/draft/draftees.md.

The pre-draft trades did not consume a 2013 selection, so all seven picks remained live and were exercised. The working inventory moves from the March 12 baseline of 63 to 64 after the net pre-draft trade activity, then to 71 after the seven draft-rights additions. No rookie compensation is invented or booked before contract execution.

Tyler Bray enters as a developmental quarterback behind the newly acquired Cousins competition and Henne's veteran insurance; he is not a premium-capital franchise-quarterback commitment and receives no roster or depth-chart guarantee.

## Entry 7 — Post-draft undrafted rookie signings

**Timing:** Post-draft signing wave after April 27, 2013 and before rookie minicamp; exact individual execution times are not separately established.
**Authority:** User-directed personnel outcome executed by Caldwell under the existing contract/acquisition authority.
**Result:** Four undrafted rookies signed.

| Player | Position | School | Initial football treatment |
|---|---|---|---|
| Brynden Trawick | S | Troy | Safety/special-teams competition; no depth position promised |
| A.J. Bouye | CB | UCF | Corner/special-teams competition; no starting role promised |
| Adam Thielen | WR | Minnesota State | Receiver/special-teams competition; no roster role promised |
| C.J. Anderson | RB | California | Running-back competition; no workload or roster role promised |

These four players are user-authorized simulation additions. Their later real NFL careers, teams, awards, statistics, and reputation are not used as evidence for this branch. Exact rookie-free-agent signing bonuses, guarantees, cap charges, and Top-51 displacement are not invented; the contracts are recorded as executed with detailed financial reconciliation still open in offseason/initial_cap_sheet.md.

**Working inventory:** 71 after the draft plus four UDFA signings = **75**. This is an offseason working inventory, not an active-roster declaration.

Detailed signing record: offseason/draft/udfa_signings.md.

## Closed post-draft canonical update

**Global package checkpoint:** Canonical update - post-draft 2013 roster build
**Preceding global package checkpoint:** Canonical update - March 12, 2013, 4:00 p.m. ET - reconcile completed free agency
**Canonical through:** Post-draft 2013, after the UDFA signing wave and before rookie minicamp.
**Documentation date:** September 19, 2026.

This checkpoint carries the Cousins acquisition, Gabbert/Wilson trade, unchanged seven-pick Jacksonville draft, four UDFA signings, roster reconciliation, and financial/draft-capital caveats into Documents 4-5 and the supporting career files. No practice, medical clearance, depth-chart win, game, or later-career result is generated by this closure.

Commit closed — Canonical update - post-draft 2013 roster build — canonical through the post-draft signing wave before rookie minicamp
