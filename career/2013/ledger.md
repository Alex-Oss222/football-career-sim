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

## Entry 8 — Rookie contracts and rookie minicamp completed

**Contract execution:** May 2, 2013.
**Football event:** May 3-5, 2013.
**Global package checkpoint:** `Canonical update - May 5, 2013 - rookie minicamp closed`
**Preceding global package checkpoint:** `Canonical update - post-draft 2013 roster build`

### Calendar gate and inherited discrepancy

Two-pass calendar research established Jacksonville's April 1 early program start, April 16-18 new-head-coach voluntary veteran minicamp, May 3-5 rookie minicamp, OTA dates, June 11-13 mandatory minicamp, and separate July rookie/veteran report dates. Source and verification record: `library/2013_offseason_program_calendar.md`.

The April 16-18 voluntary minicamp fell between the already-closed March 12 free-agency entry and April 25 draft. Per user instruction, Entries 3-7 are not rewritten and the missed phase is not retroactively simulated. The discrepancy remains explicit; no veteran attendance, install, evaluation, or performance is invented.

### Rookie contracts

Caldwell executed four-year rookie contracts for Lane Johnson (#2), Travis Kelce (#33), Jordan Poyer (#64), Sio Moore (#98), Lavar Edwards (#135), Bacarri Rambo (#169), and Tyler Bray (#208) on May 2. Johnson's deal includes the CBA first-round club-option mechanism. Exact slot totals and signing bonuses were verified by draft position; gross scheduled 2013 cap charges total $7,326,170. Exact Top-51 displacement, net current room, later-year allocation detail, and the wider unresolved club worksheet remain open. Full booking: `offseason/initial_cap_sheet.md`; person/selection record: `offseason/draft/draftees.md`.

### Onboarding and football result

The seven draftees and four signed UDFAs received the complete active 2013 Iteration I playbook, Prowl/readiness/support materials, rookie roadmap, and position material. Stone and position-coach follow-up calls were completed before the opening session on an honestly compressed post-draft timeline; no exact call date was invented where the UDFA execution timestamp remained unfixed.

Jacksonville ran the durable rookie-minicamp plan May 3-5. Teaching stayed narrow, followed Explain -> Show -> Walk -> Rep -> Correct -> Rep again -> Retain -> Add complexity, and separated assignment, communication, technique, physical loss, processing delay, medical limit, and teaching failure. Johnson, Poyer, and Moore supplied the strongest complete phase evidence, without earning a starting job or roster guarantee. No significant injury or new medical restriction was communicated. The Rookie Welcome Family Dinner occurred under the plan's voluntary/privacy boundary. Complete output: `offseason/rookie_minicamp/output.md`.

### Current-state consequences

All eleven rookie participants remain in open competition. The working inventory remains 75: draft-rights status converted to signed-contract status for seven players, with no player added or removed. No depth chart or role hierarchy was fixed. Rookie minicamp closed May 5; OTAs have not begun. The next verified football date is May 13.

**Commit closed — Canonical update - May 5, 2013 - rookie minicamp closed — canonical through rookie minicamp, before OTAs**

## Entry 9 — May 5 roster, contract, cap and calendar correction

**Effective checkpoint:** May 5, 2013, after rookie minicamp and before OTAs.
**Correction recorded:** September 19, 2026.
**Target global package checkpoint:** `Canonical correction - May 5, 2013 - roster/cap/calendar reconciled`.
**Preceding global package checkpoint:** `Canonical update - May 5, 2013 - rookie minicamp closed`.
**Nature:** Research-backed correction and dependency reconciliation. No football event is rerun and no new practice/player result is generated.

### Why a correction was required

Entry 8 correctly preserved the already-simulated May 3-5 rookie minicamp, but three supporting assumptions were wrong or incomplete:

1. the Jacksonville offseason-program calendar listed an April 1 start and incorrect OTA clusters;
2. the working roster carried expired 2012 contracts as unresolved Jacksonville-controlled players and omitted four pre-divergence reserve/future contracts;
3. the May 2 drafted-rookie contract table overstated gross 2013 charges and the club still lacked a transaction-aware Top-51 worksheet.

This entry supersedes only those factual/current-state fields. It does not erase Entries 3-8 or rewrite the decisions/results they document.

### Calendar correction

Jacksonville's official new-head-coach offseason program began **Tuesday, April 2, 2013**, not April 1.

Correct Jacksonville football calendar through mandatory minicamp:

- April 2 — official offseason program begins;
- April 16-18 — additional voluntary veteran minicamp;
- May 3-5 — rookie minicamp;
- May 13-15 — OTA block;
- May 20-21 — OTA block;
- May 23 — OTA day;
- June 4-7 — OTA block;
- June 11-13 — mandatory veteran minicamp;
- July 22 — rookies and quarterbacks report to training camp;
- July 25 — full team / veterans report;
- July 26 — first full-team training-camp practice.

The full preseason, regular-season, roster-deadline and conditional postseason calendar is now in `career/2013/calendar.md`, sourced by `library/2013_jacksonville_master_calendar.md`.

The **April 16-18 voluntary veteran minicamp remains missed in the branch**. Entries 3-7 had already closed without running it. No veteran attendance, install, rep, evaluation, injury, medical clearance or performance is retroactively invented.

### January 15 control correction

The old January research spine contained 63 active/reserve names but omitted four reserve/future contracts Jacksonville executed on December 30, 2012:

- John Parker Wilson, QB;
- Ryan Davis, DE;
- Brandon King, DB;
- Will Ta'ufo'ou, FB.

Those contracts predate Stone's January 15 hire. Correct January 15 inherited control is therefore **67 players**.

Actual later real-world releases of any of those players occurred after divergence and are not imported into branch canon.

### March 12 rights correction

Jacksonville's contemporaneous own-free-agent list establishes that 17 names in the old research inventory reached free agency on March 12. This branch re-signed Brad Meester and Daryl Smith. It did **not** record a tender or new Jacksonville contract for the remaining fifteen:

Kyle Bosworth, Eben Britton, John Chick, Derek Cox, Greg Jones, Terrance Knighton, Rashean Mathis, Antwaun Molden, Jordan Palmer, Jalen Parmele, Zach Potter, George Selvie, Jordan Shipley, Keith Toston and Steve Vallos.

Their prior Jacksonville control therefore expired. This is not a new release event and does not import their later destinations.

### Correct current roster count

| Reconciliation | Players |
|---|---:|
| Correct Jan. 15 inherited control | 67 |
| March free agents not retained | -15 |
| Branch releases | -4 |
| Branch outside FA additions | +4 |
| Post-FA controlled roster | **52** |
| Cousins acquisition | +1 |
| Gabbert-for-C.J. Wilson swap | 0 net |
| Pre-draft controlled roster | **53** |
| Seven drafted players | +7 |
| Four signed UDFAs | +4 |
| **May 5 controlled roster** | **64** |

The prior working count of 75 is superseded for current state. The complete 64-player control list is in `career/2013/roster.md`.

### Drafted-rookie contract correction

All seven branch draftees remain signed May 2 on four-year CBA rookie-scale contracts, with Lane Johnson also carrying the first-round fifth-year option mechanism.

The corrected schedules are:

| Pick | Player | 2013 cap | Four-year total |
|---:|---|---:|---:|
| #2 | Lane Johnson | $3,854,836 | $21,201,598 |
| #33 | Travis Kelce | $994,382 | $5,469,104 |
| #64 | Jordan Poyer | $572,794 | $3,100,676 |
| #98 | Sio Moore | $529,257 | $2,657,028 |
| #135 | Lavar Edwards | $458,403 | $2,373,612 |
| #169 | Bacarri Rambo | $437,205 | $2,288,820 |
| #208 | Tyler Bray | $422,225 | $2,228,900 |
| **Total** | | **$7,269,102** | **$39,319,738** |

The prior **$7,326,170** gross 2013 total is corrected. Full annual schedules and signing bonuses are in `offseason/draft/draftees.md`.

Under the May 5 Top-51 worksheet, the seven drafted contracts create a **$4,134,102 net Top-51 effect**, not a $7.269M net reduction in room.

### UDFA contracts closed

Brynden Trawick, A.J. Bouye, Adam Thielen and C.J. Anderson are each under a three-year rookie minimum contract:

- 2013 base: $405,000;
- 2014 base: $495,000;
- 2015 base: $585,000;
- signing bonus: $0;
- additional guarantee: $0.

At the current 64-player roster, those four salaries are below the Top-51 cutoff and carry no bonus proration. Their May 5 net Top-51 effect is therefore **$0**.

### Transferred contracts and releases reconciled for planning

The current worksheet now includes:

- Kirk Cousins' incoming 2013 base obligation, with Washington retaining prior signing-bonus proration;
- Gabbert's pre-June-1 trade acceleration;
- C.J. Wilson's incoming 2013 base obligation, with Green Bay retaining its prior bonus proration;
- the four branch releases;
- Top-51 displacement from the six March agreements and seven drafted-rookie contracts.

The old `~$8.35M` figure was a gross post-free-agency shortcut and is no longer current.

**May 5 Top-51 planning room: approximately $7.0M-$7.4M.**

The range is deliberate. The recovered historical starting club-room figure was itself approximate, and Aaron Ross's exact execution timing within the compressed branch release batch is not separately fixed. Do not manufacture penny precision.

Jacksonville is cap-compliant at the current checkpoint. Recalculate after any new transaction and at the August 27, August 31 and September 4 roster/accounting checkpoints.

### Football state unchanged by this correction

The May 3-5 rookie-minicamp teaching/evaluation record remains intact.

- no depth chart is awarded by this correction;
- no veteran medical clearance is inferred;
- no April minicamp is backfilled;
- no later real career outcome is imported;
- next scheduled team football work is the **May 13-15 OTA block**.

### Closed correction register

| Global package checkpoint | Canonical through | Corrected current facts |
|---|---|---|
| `Canonical correction - May 5, 2013 - roster/cap/calendar reconciled` | May 5, after rookie minicamp, before OTAs | Apr. 2 program start; full 2013 calendar; 67 Jan. 15 controls; 64 May 5 controls; corrected rookie contracts; closed UDFA terms; ~$7.0M-$7.4M Top-51 room |

**Commit closed — Canonical correction - May 5, 2013 - roster/cap/calendar reconciled — canonical through May 5, before May 13 OTAs**

## Entry 10 — May 13-15 OTA block 1

**Effective checkpoint:** May 15, 2013, after OTA block 1.
**Global package checkpoint:** `Canonical update - May 15, 2013 - OTA block 1 closed`.
**Preceding global package checkpoint:** `Canonical correction - May 5, 2013 - roster/cap/calendar reconciled`.

Jacksonville confirmed the reconciled 64-player control list, completed the established welcome/package/playbook and individual follow-up process for controlled veterans without a closed onboarding record, and obtained qualified medical participation communication before team work. Daryl Smith was cleared for and completed assigned OTA work without a communicated restriction. Brent Grimes remained in meetings and medically directed rehabilitation/individual work but was withheld from team periods; no new diagnosis or return date was communicated. Every other controlled player was cleared for assigned work and participated. No new injury or restriction was communicated during the block.

The May 13-15 work followed Explain -> Show -> Walk -> Rep -> Correct -> Rep again -> Retain -> Add complexity. The offense taught common operation, Power, Inside Zone, Stick, Drive, protection communication and limited purposeful motion. The defense worked base alignment, fits, coverage distribution and a limited pressure presentation; special teams installed core substitution, lane, leverage and operation language.

Cousins produced the cleanest huddle/protection communication; Meester stabilized line calls; Shorts preserved taught route landmarks; and Posluszny stabilized defensive communication. Johnson, Poyer and Moore added useful evidence without winning jobs. Trawick and Thielen added provisional multi-unit special-teams evidence. Specific open teaching points remain for Kelce, Bray, Henne, Rambo and the interior line. Tice simplified combination/protection vocabulary, and Crennel postponed an added pressure disguise until the base coverage exchange is stable. No permanent depth chart or roster role was awarded.

The full-team offseason/OTA family dinner occurred May 15 under voluntary, non-evaluative and privacy boundaries. No attendance or family circumstance became personnel evidence.

No signing, release, trade, waiver move, contract change, verified workout-bonus consequence or Top-51 change occurred. The 64-player count and May 5 approximately $7.0M-$7.4M Top-51 planning range remain current; the cap worksheet is unchanged.

The April 16-18 voluntary veteran-minicamp gap remains unfilled. The May 20-21 OTA block has **not** been run and is the next scheduled football event.

**Commit closed — Canonical update - May 15, 2013 - OTA block 1 closed — canonical through May 15, before May 20 OTAs**

## Entry 11 — May 20-21 OTA block 2

**Effective checkpoint:** May 21, 2013, after OTA block 2.
**Global package checkpoint:** `Canonical update - May 21, 2013 - OTA block 2 closed`.
**Preceding global package checkpoint:** `Canonical update - May 15, 2013 - OTA block 1 closed`.

Jacksonville obtained fresh qualified medical instructions before May 20 work. Daryl Smith completed both days without a communicated restriction. Brent Grimes remained in meetings and medically directed rehabilitation/individual work May 20, then was cleared after reassessment for a limited set of controlled, non-contact team repetitions May 21. Medical staff controlled the assignment and excluded extended and pressure-period work; he completed it without a communicated setback. No new diagnosis or unrestricted-return date was supplied. Every other controlled player completed assigned work without a new communicated restriction.

Stone made retention and transfer the block's governing test. The offense retained huddle, cadence, point, Power, Inside Zone, Stick and Drive, while the interior line's combination timing remained late when the front changed. Stone and Tice therefore deferred another run family and broader protection/motion expansion. The unit earned only a narrow early Mesh install, moving from explanation and walk-through to selected May 21 team repetitions. Y-Cross, Counter, Outside Zone and PRESS tempo were not installed.

Cousins again supplied the cleanest operation and carried it into the harder presentation. Henne improved, but did not fully close, his changed-picture reset correction. Wilson remained assignment-sound without separating his role. Bray improved cadence-to-footwork connection, while progression timing under a changed picture remained open. Stone set a provisional May 23 practice sequence—Cousins first into the harder changed-presentation core, Henne continuing in the same competitive band, Wilson in the working rotation and Bray concentrated on core timing—but named no QB1 or permanent depth order.

Meester continued to stabilize line communication; Johnson retained his assignment through the harder front presentation; Shorts transferred taught landmarks through limited motion. Kelce improved his run-block fit on a constant surface but did not yet carry it consistently across an alignment change. Posluszny's unit needed less rescue on base alignment, Moore retained his prior landmark correction before taking a new changed-distribution correction, and Poyer retained leverage and exchange communication.

Base defensive exchange improved enough for Crennel to retest one previously postponed pressure presentation. A late first exchange was re-walked and the return rep was clean, so that single presentation remains available for recall without expanding the disguise menu. Rambo's earlier special-teams substitution correction held; a late defensive exchange call became a separate open correction. Trawick and Thielen retained multiple special-teams jobs with less coach placement and earned continued cross-unit exposure, not final-unit awards.

No signing, release, trade, waiver move, contract change, verified bonus consequence or Top-51 change occurred. The roster remains 64 and the unchanged May 5 worksheet remains financial authority at approximately $7.0M-$7.4M planning room. The April 16-18 continuity gap remains unfilled.

The next football event is the **May 23 OTA day**. Medical instructions, core recall, the interior combination, the single defensive pressure presentation and the narrow Mesh progression are carry-forward items. **May 23 has not been run.**

**Commit closed — Canonical update - May 21, 2013 - OTA block 2 closed — canonical through May 21, before May 23 OTA work**

## Entry 12 — May 23 OTA day

**Effective checkpoint:** May 23, 2013, after OTA Day 6.
**Global package checkpoint:** `Canonical update - May 23, 2013 - OTA Day 6 closed`.
**Preceding global package checkpoint:** `Canonical update - May 21, 2013 - OTA block 2 closed`.

Jacksonville obtained fresh qualified medical instructions before work. Daryl Smith and every controlled player other than Brent Grimes were available for and completed assigned non-contact work without a newly communicated restriction. Grimes again received a medically controlled assignment of meetings, rehabilitation, individual work and selected group/base team repetitions; he remained excluded from the extended team and pressure-recall periods. He completed the assignment without a communicated setback, but no new diagnosis, unrestricted clearance or return date was supplied.

Stone ran May 23 as a retention checkpoint. Meetings and walkthrough preceded individual, group, special-teams, legal 7-on-7/9-on-7 and selected 11-on-11 work. When the interior line's changed-front combination echo was late, Stone and Tice returned to point, echo and confirmation, repeated the period and obtained correct return work. The correction improved but remains a June 4 opening test, so Counter, Outside Zone and broader protection expansion stayed deferred.

The retained offensive core survived: huddle/cadence/formation operation, protection point, Power, Inside Zone, Stick, Drive and limited purposeful motion. Narrow Mesh spacing compressed on its first team sequence; after Tice re-taught the stagger, the return work held for Cousins, Henne and Wilson. Stone retained only that narrow version. He did not install broader Mesh, Y-Cross, Counter, Outside Zone, PRESS, expanded protection or a larger motion package.

Cousins handled the opening harder operation cleanly, corrected one late movement to the underneath Mesh window and remains first in the provisional practice sequence on cumulative evidence. Henne handled comparable changed-picture work cleanly, narrowing the operational gap and earning immediate comparable harder work behind Cousins on June 4. Wilson remained assignment-sound without separating. Bray retained cadence-to-footwork improvement but was again late in progression timing after a coverage change, so Stone narrowed his remaining work to correct core timing. No QB1 or permanent depth order was named.

Meester remained the line's communication stabilizer; Johnson retained his assignment through harder presentation and keeps that developmental exposure without a starting award. Shorts and Anderson retained taught jobs. Kelce's hand placement/base traveled through multiple alignments before widening on a later group rep, leaving the correction improved but open.

Crennel called and sequenced the defense. Base fronts, fits and coverage exchange held with less Posluszny rescue. Moore's changed-distribution handoff, Poyer's leverage/exchange and Rambo's defensive exchange communication held in the assigned work. The single retained pressure presentation operated with correct rush/replacement and secondary ownership, including on the return against permitted motion. Crennel retained exactly that presentation and added no broader pressure/disguise menu. Grimes did not take pressure-period work.

Lowry's core special-teams substitution, alignment and lane/leverage work survived with reduced coach placement. Trawick earned first June 4 exposure to another already-taught cross-unit sequence. Thielen retained cross-unit work after correcting one unnecessary wait for confirmation; Rambo's substitution language remained clean. No final unit or roster job was awarded.

Stone closed the day by directing lawful voluntary conditioning, recovery, treatment and individual study during the break, with no unscheduled club practice and no attendance-based role judgment. June 4 begins with fresh medical communication, unprompted core recall, the changed-front combination, narrow Mesh spacing, base defensive exchange and the one pressure presentation. No injury, transaction, staff change, permanent role award or financial event occurred. The roster remains 64 and the unchanged May 5 Top-51 worksheet remains authority at approximately $7.0M-$7.4M.

The next football event is **June 4-7 OTA block 3**. **June 4 has not been simulated.**

**Commit closed — Canonical update - May 23, 2013 - OTA Day 6 closed — canonical through May 23, before June 4 OTA work**

## Entry 13 — Repository continuity and readiness reconciliation

**Record class:** Administrative correction authorized September 19, 2026; no simulated football event.
**Effective checkpoint:** May 23, 2013, after OTA Day 6; the clock does not advance.
**Global package checkpoint:** `Canonical correction - May 23, 2013 - repository continuity and readiness reconciled`.
**Preceding global package checkpoint:** `Canonical update - May 23, 2013 - OTA Day 6 closed`.

The owner approved the repository organization plan and requested game-readiness work. This entry reconciles stale presentation and dependencies against events already closed in Entries 1-12.

- Root and season indexes now route to current state and the correct phase folders. Training camp remains under `offseason/training_camp/`; its approved output, standouts, battles and roster-decision placeholders do not imply work has occurred.
- OTA standouts now summarize the completed May 13-23 evidence. Rookie-minicamp standouts summarize May 3-5. Mandatory minicamp and training camp remain NOT STARTED. Durable teaching plans keep their content and point to separate execution records.
- Document 2 now has an active 2013 Jacksonville edition. The full superseded authoring master is archived; unused candidate modes do not enter runtime. Known staff/caller assignments are reconciled in Document 3 from the existing operating staff record.
- Project and ledger-protocol status pointers now refer to the established career. The trade ledger points forward to Entry 9/current cap reconciliation without rewriting the older entries' as-recorded uncertainty.
- Repository checks now cover file dependencies, evidence-summary receipts, local links, source versions, checkpoints and controlled-player membership. They do not generate new evidence or replace semantic review.
- Game readiness remains BLOCKED. Pre-2013 league aggregate research and deterministic packet support are added; full verified game rules, calibration, football kernel and a deployed private Engine State service remain incomplete. No game score or secret state is invented.

The current count remains 64 controlled players with 26 open offseason places. Existing staff appointments, provisional football roles, medical restrictions, draft capital, branch contracts and the May 5 approximate $7.0M-$7.4M Top-51 planning range are unchanged. The April 16-18 continuity gap is preserved. Entry 12 remains the last football event; June 4-7 OTAs remain the next scheduled work and have not been simulated.

| Global package checkpoint | Canonical through | Reconciled documents |
|---|---|---|
| `Canonical correction - May 23, 2013 - repository continuity and readiness reconciled` | May 23, 2013, after OTA Day 6 | Active foundation references, phase views, repository dependencies and Documents 4/5 |

**Commit closed — Canonical correction - May 23, 2013 - repository continuity and readiness reconciled — canonical through May 23, before June 4 OTA work**
