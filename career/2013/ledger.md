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

## Entry 14 — June 4-7 OTA block 3 and OTA phase closed

**Effective date:** June 7, 2013
**Checkpoint:** `Canonical update - June 7, 2013 - OTA phase closed`

Jacksonville completed the verified voluntary, non-contact OTA block with the frozen recall/communication test. All 64 controlled players completed assigned work; Grimes advanced to broader medically controlled non-contact repetitions but remained restricted from the longest competitive period, with no setback, new diagnosis or unrestricted clearance. No other new restriction was communicated.

Power, Inside Zone, Stick, Drive, narrow Mesh, base protection/changed-front communication, base defense, one pressure presentation and core special-teams substitution survived the close. Broader Mesh, Y-Cross, Outside Zone, PRESS, broad protection/motion and extra defensive disguise were deferred. Cousins retained a narrow first practice sequence over a closing Henne; no QB1 was named. Individualized cutups/teaching sheets were assigned through existing staff for Bray, the interior line, Kelce and the defensive exchange. There was no transaction, permanent depth award or cap change.

**Primary record:** `offseason/otas/output.md`; reviewed summary: `offseason/otas/standouts.md`.
**Next event:** June 11-13 mandatory veteran minicamp.

## Entry 15 — June 11-13 mandatory veteran minicamp closed

**Effective date:** June 13, 2013
**Checkpoint:** `Canonical update - June 13, 2013 - mandatory minicamp closed`

Stone froze the three-day exam before work and ran common-floor, changed-picture, situational and retention periods without moving the test. The offense carried the retained core plus simple Counter and selected Boot Flood; Counter remained presentation-limited, while broader Mesh, Y-Cross, Outside Zone and PRESS stayed out of the dependable camp-entry menu. Crennel carried sound base defense and one pressure but removed added disguise when communication cost exceeded its benefit. Lowry's core units became more independent, with emergency replacement still open.

All 64 controlled players completed assigned work. Grimes remained medically limited from the longest competitive period; no new injury or restriction was communicated. Cousins entered camp narrowly first in practice order, Henne immediately competitive, Wilson steady and Bray on a reduced core. Johnson led provisional right-tackle work; right guard remained open. Moore, Poyer, Rambo, Trawick and Thielen earned harder camp work, not permanent jobs. The Veteran Minicamp Family Dinner occurred under voluntary, private and non-evaluative rules.

The staff issued lawful individual conditioning, recovery, treatment, study and correction priorities for the June 14-July 21 break. No transaction, final roster decision or cap change occurred.

**Primary record:** `offseason/mandatory_minicamp/output.md`; reviewed summary: `offseason/mandatory_minicamp/standouts.md`.
**Next event:** July 22 rookie and quarterback report.

## Entry 16 — June 14-July 21 protected pre-camp interval closed

**Effective date:** July 21, 2013
**Checkpoint:** `Canonical update - July 21, 2013 - protected pre-camp interval closed`

Jacksonville held no invented club practice during the verified break. Players retained lawful individual conditioning, recovery, treatment/rehab, active-playbook study, support communication and personal/family time. Staff prepared camp scripts, competition structure and individualized 2013-era teaching materials. No player practice performance, attendance grade, transaction, injury, role award or cap change was manufactured during the interval.

**Next event:** July 22 rookie and quarterback report.

## Entry 17 — July 22-25 camp reporting and acclimation closed

**Effective date:** July 25, 2013
**Checkpoint:** `Canonical update - July 25, 2013 - full training-camp report closed`

Rookies and quarterbacks completed reporting, medical communication, equipment/administrative work, conditioning preparation, meetings and lawful acclimation July 22-24; no full-team veteran practice occurred. All 64 controlled players reported by July 25 and completed assigned entry work. Medical staff cleared Grimes for full football participation with ordinary workload monitoring and no football restriction. No new injury or limitation was communicated.

Stone communicated the common standard, medical honesty, intelligent recovery and evidence-based competition rules, then froze the opening football goals before practice. The Camp Opening Family Dinner occurred under voluntary, private and non-evaluative rules. No job was awarded from reporting, no transaction occurred and the May 5 cap worksheet remained unchanged.

**Primary record:** `offseason/training_camp/output.md`.
**Next event:** July 26 opening full-team practice.

## Entry 18 — July 26-August 3 opening camp and stadium scrimmage closed

**Effective date:** August 3, 2013
**Checkpoint:** `Canonical update - August 3, 2013 - stadium scrimmage closed`

Jacksonville completed the verified opening sequence, preserved July 30 as a players' day off and progressed from recall to lawful padded execution, situation and stadium operation. Cousins earned the provisional first quarterback hierarchy with Henne second and still competitive; Wilson remained steady and Bray stayed on assigned core work. Johnson led right tackle; Rackley moved provisionally first at right guard; Jones-Drew, Shorts/Blackmon and Lewis led their working groups. Crennel kept base defense plus one trusted pressure, with Moore, Poyer and Rambo earning defined harder work. Lowry expanded multi-unit opportunities for Trawick, Rambo and Thielen.

The August 3 scrimmage confirmed improved huddle/sideline operation while exposing corrections in red-zone decision-making, protection/substitution, second punt-return emergency procedure and selected defensive force/fit communication. The Mid-Camp Family Night/Dinner and a light voluntary recreation period occurred without football evaluation. All 64 remained controlled and available; no new restriction, transaction or cap change occurred.

**Primary record:** `offseason/training_camp/output.md`; role details: `position_battles.md` and `roster_decisions.md`.
**Next event:** August 5 post-scrimmage practice.

## Entry 19 — August 5-8 Miami preparation and final walkthrough closed

**Effective date:** August 8, 2013
**Checkpoint:** `Canonical update - August 8, 2013 - final Miami walkthrough closed`

Stone converted the scrimmage corrections into a reduced, executable preseason menu and closed the August 8 walkthrough without adding a large package. Cousins opens the Miami evaluation, Henne follows with meaningful work, Wilson is prepared next and Bray may receive a later reduced-core segment; this is a preseason exposure plan, not a permanent QB1 declaration or promised snap distribution. Stone remains offensive caller, Crennel defensive caller and Lowry special-teams coordinator.

Current practice roles are synchronized in the camp battle/decision records: Johnson and Rackley are provisional firsts on the right side; Jones-Drew leads the backs; Shorts/Blackmon lead the receivers; Lewis leads the tight ends; Grimes/Ball lead outside corners with Poyer in nickel/outside evaluation; Lowery/Rambo take first safety work; and Moore receives selected first-group/sub-package work. The roster remains 64. Qualified medical staff communicated all 64 available for assigned work through the walkthrough, subject to fresh game-day communication. No transaction or cap event occurred; May 5 Top-51 planning room remains approximately $7.0M-$7.4M.

**Primary record:** `offseason/training_camp/output.md`; reviewed summary: `offseason/training_camp/standouts.md`.
**Last completed event:** August 8 final walkthrough.
**Next event:** August 9 Preseason Game 1 vs Miami. **The game is NOT STARTED.**

**Commit closed — Canonical update - August 8, 2013 - final Miami walkthrough closed — canonical through August 8, after the final walkthrough and before Preseason Game 1**

## Entry 20 — August 9 preseason opener closed

**Effective date:** August 9, 2013
**Checkpoint:** `Canonical update - September 4, 2013 - preseason, roster and cap block closed`

Jacksonville beat Miami 33-17 in the first privately closed production-runtime result. Cousins opened and threw the sole Jacksonville interception; later quarterbacks produced no turnover. Protection allowed six sacks despite identified assignments and continued effort. No Jacksonville injury occurred.

## Entry 21 — August 12-15 training camp closed

**Effective date:** August 15, 2013
**Checkpoint:** `Canonical update - September 4, 2013 - preseason, roster and cap block closed`

Stone used targeted Miami cutups and the established teaching cycle across three verified practices and the final walkthrough. Protection, quarterback decision, substitution, coverage-exchange and teams responsibilities were retested. Training camp concluded; recovery and voluntary personal/family time stayed ungraded.

## Entry 22 — Preseason Game 2 closed

**Effective date:** August 17, 2013
**Checkpoint:** `Canonical update - September 4, 2013 - preseason, roster and cap block closed`

The Jets beat Jacksonville 24-17. Jacksonville protected the ball and reduced sacks but failed to finish enough possessions. Pasztor sustained a simulated head/neck injury and entered an independent medical hold.

## Entry 23 — Preseason Game 3 and QB decision closed

**Effective date:** August 24, 2013
**Checkpoint:** `Canonical update - September 4, 2013 - preseason, roster and cap block closed`

Philadelphia beat Jacksonville 31-20. After cumulative camp and three-game evidence, Stone named Cousins QB1 and Henne QB2; Johnson/Rackley, Thielen and Kelce received settled regular-season roles. Pasztor remained unavailable.

## Entry 24 — 75-player deadline compliance

**Effective date:** August 27, 2013
**Checkpoint:** `Canonical update - September 4, 2013 - preseason, roster and cap block closed`

Jacksonville controlled 64 players and required no release to satisfy the 75-player deadline.

## Entry 25 — Preseason Game 4 closed

**Effective date:** August 29, 2013
**Checkpoint:** `Canonical update - September 4, 2013 - preseason, roster and cap block closed`

Jacksonville beat Atlanta 33-27 and finished preseason 2-2. Wilson supplied the cleaner final quarterback operation; Bray threw the only turnover. Mosley became medically unavailable with an upper-extremity injury; Smith received a short medical restriction.

## Entry 26 — Final 53 closed

**Effective date:** August 31, 2013
**Checkpoint:** `Canonical update - September 4, 2013 - preseason, roster and cap block closed`

Caldwell approved the cumulative-evidence reduction from 64 to 53. Eleven players were waived/released. Pasztor and Mosley remained active despite medical limitations; availability was not treated as effort.

## Entry 27 — Waivers and practice squad closed

**Effective date:** September 1, 2013
**Checkpoint:** `Canonical update - September 4, 2013 - preseason, roster and cap block closed`

Lane, Marshall and Stanback were claimed by autonomous clubs. Eight other waived players cleared and signed to Jacksonville’s separate practice squad. Wilson remained QB3; Bray moved to the practice squad.

## Entry 28 — Medical transition reconciled

**Effective date:** September 4, 2013
**Checkpoint:** `Canonical update - September 4, 2013 - preseason, roster and cap block closed`

Smith cleared his short restriction. Pasztor remained on independent medical hold and Mosley remained unavailable. No reserve-list move was invented.

## Entry 29 — Regular-season cap compliance closed

**Effective date:** September 4, 2013
**Checkpoint:** `Canonical update - September 4, 2013 - preseason, roster and cap block closed`

Top-51 accounting ended. The active roster is 53, the practice squad is eight, and source-bounded working room is approximately $6.2M-$6.6M before weekly practice-squad charges, or $5.4M-$5.8M if the opening eight remain all season. Regular-season record remains 0-0; September 8 Kansas City is next and has not been simulated.

**Commit closed — Canonical update - September 4, 2013 - preseason, roster and cap block closed — canonical through September 4, after regular-season cap compliance and before Week 1**


## Entry 30 — Regular Season Week 1 closed

**Effective date:** September 9, 2013, after the full Week 1 slate and Jacksonville postgame work.
**Checkpoint:** `Canonical update - September 9, 2013 - Week 1 closed`

Kansas City defeated Jacksonville 30-27 in the first privately closed regular-season runtime result. Jacksonville generated 475 yards and led 27-23 in the fourth quarter, but three interceptions and Kansas City's late touchdown decided the game. Kirk Cousins remains QB1. The kernel attributed isolated work and one interception each to Henne and Wilson without a generated injury; Stone ended that usage and carries no quarterback rotation into Week 2. Jacksonville allowed three sacks, with generated evidence separating identified assignments from leverage losses. The defense recorded four sacks and two takeaways but did not control Jamaal Charles, who produced 171 rushing yards and 164 receiving yards.

The runtime generated no new Jacksonville injury. Pasztor remains on independent medical hold and Mosley remains medically unavailable. Week 1 inactives were Pasztor, Mosley, Asper, Brewster, Ryan Davis, Lavar Edwards and Rutland; game-day designations expire after the contest. No transaction, contract, cap, controlled-player or practice-squad change occurred.

All fifteen non-Jacksonville games were closed once through the same production runner. The complete scores and highlights are in `league_results/week_01.md`; `standings.md` is current through Week 1. Jacksonville is 0-1.

**Primary records:** `regular_season/week_01_kansas_city_at_jacksonville/output.md`; `league_results/week_01.md`.
**Next competitive event:** September 15 Week 2 at Oakland, 4:25 p.m. ET. **Week 2 has not been simulated.**

**Commit closed — Canonical update - September 9, 2013 - Week 1 closed — canonical through the full Week 1 slate and Jacksonville postgame work**

## Entry 31 — Regular Season Week 1 full-fidelity reset closed

**Effective date:** September 9, 2013, after the full generation-2 Week 1 slate and Jacksonville postgame work.
**Checkpoint:** `Canonical update - September 9, 2013 - Week 1 full-fidelity reset closed`

The generation-2 replacement supersedes Entry 30's legacy Week 1 results and all 16 associated scores, statistics, injuries and standings. All 32 TeamInputs were frozen before any replacement draw. Jacksonville defeated Kansas City 34-13, produced 431 yards and five defensive interceptions, and is 1-0. Cousins remains QB1; isolated Henne and Wilson series do not establish a continuing rotation.

Montell Owens sustained a generated minor trunk injury and is out pending reassessment. Bacarri Rambo sustained a generated short-term trunk injury and is medically unavailable. Pasztor remains on medical hold and Mosley remains medically unavailable. No transaction, contract, cap, controlled-player or practice-squad change occurred.

All 16 games were closed through the shared production runner. The Jacksonville receipt is full detail; the other 15 receipts use `compact_stats`. Standings and every season-stat view were rebuilt from those receipts. Entry 30 remains an audit record only and is not active Week 1 canon.

**Primary records:** `regular_season/week_01_kansas_city_at_jacksonville/output.md`; `league_results/week_01.md`; `stats/game_receipts/`.
**Next competitive event:** September 15 Week 2 at Oakland, 4:25 p.m. ET. **Week 2 has not been simulated.**

**Commit closed — Canonical update - September 9, 2013 - Week 1 full-fidelity reset closed — canonical through the full Week 1 slate and Jacksonville postgame work**

## Entry 32 — Week 1 attribution and Week 2 handoff correction closed

**Effective date:** September 9, 2013
**Checkpoint:** `Canonical correction - September 9, 2013 - Week 1 attribution and Week 2 handoff reconciled`

A pre-Week-2 continuity audit found that the generation-2 Week 1 historical-roster reconstruction had retained eight player identities on non-Jacksonville clubs even though earlier branch transactions already placed those players under Jacksonville control. The affected receipts were Baltimore-Denver, Miami-Cleveland, Green Bay-San Francisco, Philadelphia-Washington and Kansas City-Jacksonville.

This is an outcome-preserving administrative/statistical correction. No Week 1 game was rerun. Every published final score, team total, standing and Jacksonville's own Week 1 player line remains unchanged; Jacksonville remains **1-0** after the 34-13 win over Kansas City. The impossible non-Jacksonville player lines were moved to explicit pseudo/unattributed rows in their existing receipts. Because the exact eligible teammate who would have received each generated statistic cannot be reconstructed without inventing a result, those five receipts now mark the affected clubs' exact player attribution as partial. League player views retain known lines, while formal league leaderboards are withheld.

The weekly input contract now requires a branch-exclusivity gate before any future event closes: Jacksonville-controlled active-roster and practice-squad players may appear only in Jacksonville's TeamInput, and no player may appear on two clubs in the same weekly slate. Historical roster rails yield to branch transactions/control.

The audit also identified why the post-merge private snapshot advance for the published generation-2 Week 1 state returned a conflict: the earlier audited generation-1 rollback left a legacy unique transition row. Runtime snapshot history now preserves that old audit record while permitting a later legitimate CAS progression after a documented recovery. This bookkeeping repair does not alter football canon.

**Primary records:** `regular_season/week_01_kansas_city_at_jacksonville/output.md`; corrected `stats/game_receipts/`; `stats/league_player_stats.md`; `stats/all_player_stats.md`; `stats/league_leaders.md`; `migrations/week_01_full_fidelity_reset.md`.
**Next competitive event:** September 15 Week 2 at Oakland, 4:25 p.m. ET. **Week 2 has not been simulated.**

**Commit closed — Canonical correction - September 9, 2013 - Week 1 attribution and Week 2 handoff reconciled — canonical through September 9, after Week 1 and before Week 2 preparation**

## Entry 33 — Week 1 attribution audit completion and Week 2 readiness correction closed

**Effective date:** September 9, 2013
**Checkpoint:** `Canonical correction - September 9, 2013 - Week 1 attribution audit completed for Week 2 readiness`
**Preceding global package checkpoint:** `Canonical correction - September 9, 2013 - Week 1 attribution and Week 2 handoff reconciled`

A follow-up pre-Week-2 generation-readiness audit cross-checked all sixteen generation-2 Week 1 receipts against Jacksonville's branch-controlled active roster and practice squad. It found two additional impossible historical-team player credits that Entry 32 had missed: Antwon Blake on Pittsburgh in the Tennessee-Pittsburgh receipt and C.J. Mosley on Detroit in the Minnesota-Detroit receipt. Blake was under Jacksonville control before Week 1 and on the Jacksonville practice squad; Mosley remained on Jacksonville's active roster and was medically unavailable for Jacksonville's Week 1 game.

This follow-up brings the cumulative branch-control correction to ten player identities across seven receipts and nine non-Jacksonville clubs. The two newly identified lines were moved to explicit pseudo/unattributed rows in their existing receipts, and Pittsburgh and Detroit were added to the clubs with partial exact player attribution. No Week 1 game was rerun. Every final score, team total, standing, Jacksonville player line, generated medical event and the Jacksonville 34-13 result remain unchanged.

The season-stat cache and readable player views were regenerated from the corrected receipts. Formal league player rankings remain withheld because exact player attribution is incomplete for the corrected clubs. The stat renderer's correction-aware version labels were reconciled with the checked-in views, and repository validation now rebuilds the generated season-stat cache and Markdown views from the receipt set so future drift fails closed.

This correction does not simulate or authorize Week 2. Oakland remains unplayed. Before any Week 2 event closes, the full weekly TeamInput slate must pass the branch-exclusivity gate and ordinary game readiness, including fresh qualified-medical communication.

**Primary records:** `migrations/week_02_generation_readiness.md`; corrected `stats/game_receipts/2013-week01-reset-v2-03.json` and `2013-week01-reset-v2-09.json`; regenerated `stats/season_totals.json` and stat views.
**Next competitive event:** September 15 Week 2 at Oakland, 4:25 p.m. ET. **Week 2 has not been simulated.**

**Commit closed — Canonical correction - September 9, 2013 - Week 1 attribution audit completed for Week 2 readiness — canonical through September 9, after Week 1 and before Week 2 preparation**


## Entry 34: Week 1 voided for kernel 2013.4 restart

**Effective canonical state:** September 4, 2013, after regular-season cap compliance and before Week 1
**Recorded:** September 27, 2026
**Checkpoint:** `Canonical correction - September 4, 2013 - Week 1 voided for kernel 2013.4 restart`
**Preceding global package checkpoint:** `Canonical correction - September 9, 2013 - Week 1 attribution audit completed for Week 2 readiness`

The user directed a full Week 1 restart after a statistical audit of the sixteen generation-2 receipts found engine and input defects that no attribution correction could repair:

- the kernel picked a passer per drive from every available quarterback and weighted "competition" players above "core" starters, so 29 of 32 team-games used two or three passers and backups often led;
- carries and targets were drawn with near-equal weight across positions, giving receivers about a third of all carries;
- linebackers were largely absent from the reconstructed background TeamInputs, and OLB/ILB labels could never be selected, so linebackers made 20 of about 2,050 tackles;
- every tackle was solo and losing runs were almost never generated;
- drive clock and snap counts ignored the calibrated drive rate, producing about 84 plays per team-game against the verified 2012 figure of 64.2.

Game-level efficiency (completion rate, yards per carry, sack rate) was close to the 2012 baseline; the defects were in play volume and player attribution.

**Void.** Entries 30 through 33 are superseded. The legacy Week 1 slate, generation 2 (events `2013-week01-reset-v2-01` through `-16`) and every downstream Week 1 fact are void: the Jacksonville 34-13 result, all Week 1 scores and standings, all Week 1 player statistics and receipts, the generated Owens and Rambo injuries, and the post-game quarterback-rotation statement. Generation 1 remains a recorded technical abort. Void events stay in the private append-only journal; they are marked void there by `scripts/mark_week1_generations_void.py` before any replacement event closes, and their results are never shown or selected among.

**Why this is not outcome selection.** The restart is triggered by verified engine and input defects measured against sourced 2012 play-by-play, not by whether any result was desirable. Every one of the sixteen games is replaced, including every non-Jacksonville game, under one corrected kernel.

**Engine change.** Kernel 2013.4 adds depth-chart-aware attribution from a two-source 2012 play-by-play baseline (`library/2012_position_usage_calibration.md`), one passer per club per game, assisted tackles, losing runs, outcome-shaped drive length and clock, sourced third-down and first-down volume, a game-day unit gate that fails closed on thin TeamInputs, and a non-blocking statistical band audit.

**Restored state.** Roster, register, calendar, standings and current state return to their September 4 content. Jacksonville is 0-0 with 53 active players and 8 on the practice squad; no transaction, contract, cap or roster-control fact changed. Pasztor remains on medical hold and Mosley medically unavailable, as before Week 1. The Week 1 ex-ante preparation and a recovered structured call sheet are kept for the replay.

**Primary records:** `migrations/week_01_kernel_2013_4_restart.md`; `regular_season/week_01_kansas_city_at_jacksonville/output.md` and `call_sheet.json`; empty regenerated `stats/` views.
**Next competitive event:** September 8 Week 1 vs Kansas City, 1:00 p.m. ET, replayed under kernel 2013.4. **Not simulated.**

**Commit closed - Canonical correction - September 4, 2013 - Week 1 voided for kernel 2013.4 restart - canonical through September 4, after regular-season cap compliance and before Week 1**

## Entry 35: Week 1 closed, generation 3

**Effective canonical state:** September 8, 2013, after Week 1
**Recorded:** September 27, 2026
**Checkpoint:** `Canonical update - September 8, 2013 - Week 1 vs Kansas City closed`
**Preceding global package checkpoint:** `Canonical correction - September 4, 2013 - Week 1 voided for kernel 2013.4 restart`

**Result.** Jacksonville 31, Kansas City 13 at EverBank Field. Jacksonville is 1-0.

**Replacement batch.** All sixteen Week 1 games closed once each as generation 3 (`2013-week01-reset-v3-01` through `-16`) under kernel 2013.4 through `runtime.game_runner.run_game` and the private Engine State service, after `scripts/mark_week1_generations_void.py` marked generations 1 and 2 and `scripts/check_week1_reset_ready.py` and the weekly exclusivity gate passed on all 32 frozen TeamInputs. This generation supersedes the void Week 1 of Entry 34; no earlier Week 1 result was shown or compared.

**Inputs.** The 31 background clubs came from the sourced, branch-reconciled [Week 1 depth-chart library](../../library/2013_week1_depth_charts.md). Jacksonville used the September 4 roster, medical state and roles; the ex-ante inactives (Pasztor, Mosley, Asper, Brewster, Davis, Edwards, Rutland); and Stone's Week 1 plan, which amended the recovered call sheet before the draw by adding the weekly menu (Inside Zone, Counter, Power + Smoke, Y-Cross, Smash, Texas, Power Pass, Tunnel) to the opening fifteen. Co-starters without a recorded order were sequenced by 2012 usage, the same rule used for every background club. Every club, Jacksonville included, carried the Average low-confidence unit anchor under Document 7 section 2.2.

**Statistics and standings.** A full receipt for Jacksonville and compact receipts for the other fifteen games are preserved; the box score, standings and statbook were generated from them. Every row of the band audit is WITHIN the sourced 2012 bands.

**Availability.** No Jacksonville injury was generated. Pasztor remains on medical hold and Mosley medically unavailable. Background injuries are listed in `league_results/week_01.md`.

**Engine findings (investigated, not grounds to rerun).** The Jacksonville snap ledger shows drive-detail defects that do not affect the score or statistics: snaps logged after a drive-ending interception or touchdown, and one possession continuing across halftime. They are recorded for an engine fix; the closed result stands.

**Primary records:** `regular_season/week_01_kansas_city_at_jacksonville/output.md`; `league_results/week_01.md`; `stats/game_receipts/2013-week01-reset-v3-*.json`; `standings.md`; `migrations/week_01_kernel_2013_4_restart.md`.
**Next competitive event:** September 15 Week 2 at Oakland, 4:25 p.m. ET. **Not simulated.**

**Commit closed - Canonical update - September 8, 2013 - Week 1 vs Kansas City closed - canonical through September 8, after Week 1**

## Entry 36: Blackmon suspension ruling

**Effective canonical state:** September 9, 2013, Week 2 preparation
**Recorded:** September 27, 2026
**Checkpoint:** `Canonical update - September 9, 2013 - Blackmon to Reserve/Suspended`
**Preceding global package checkpoint:** `Canonical update - September 8, 2013 - Week 1 vs Kansas City closed`

**User branch ruling.** The league's four-game substance-abuse suspension of Justin Blackmon takes effect after Jacksonville's completed Week 1. He is on Reserve/Suspended for Weeks 2-5, does not count against the 53 and does not practice; he may attend meetings, study film, use the facility and receive treatment as the league's rules allow. Stone separately sets him game-day inactive for Weeks 6 and 7 while he practices on the active roster; that is Stone's availability decision, not a second suspension. He is eligible for a normal role in Week 8. Public statement: Blackmon is unavailable, and Jacksonville will announce any change in his playing status.

**Roster and money.** Active roster 52 with one open spot; Caldwell has not filled it. Blackmon forfeits his base-salary game checks for Weeks 2-5; the forfeited amount and its cap credit are unresolved (`offseason/current_cap_worksheet.md`).

**Roles.** Shorts WR1, Thielen WR2, Clemons WR3, Brown WR4 (`depth_chart.json`, `roster.md`).

**Commit closed - Canonical update - September 9, 2013 - Blackmon to Reserve/Suspended - canonical through September 9, Week 2 preparation**

## Entry 37: Week 2 closed

**Effective canonical state:** September 15, 2013, after Week 2
**Recorded:** September 27, 2026
**Checkpoint:** `Canonical update - September 15, 2013 - Week 2 at Oakland closed`
**Preceding global package checkpoint:** `Canonical update - September 9, 2013 - Blackmon to Reserve/Suspended`

**Result.** Oakland 17, Jacksonville 13 at O.co Coliseum. Jacksonville is 1-1.

**Batch.** All sixteen Week 2 games closed once each under kernel 2013.4 through `runtime.game_runner.run_game` and the private Engine State service, from the package frozen by `scripts/build_week_inputs.py 2` after the sixteen-game exclusivity and game-day gate passed. The events were closed by an earlier pass of this task that was interrupted before the public record was written; before publication the inputs were rebuilt byte for byte from canon plus Entry 36, and all sixteen identical packets were resubmitted to the private service, which returned the same event references and reproduced every result exactly. No event was drawn twice.

**Inputs.** Background clubs carried forward from the Week 1 depth-chart library with Week 1 branch injuries and pre-existing returns applied. Jacksonville used Stone's Week 2 plan (opening fifteen as the structured sheet; 10 Empty off the sheet, Spacing carried from 12 Doubles), the Entry 36 receiver order and inactives Pasztor, Mosley, Asper, Brewster, Edwards and Rutland, with Ryan Davis active. Every club carried the Average low-confidence unit anchor.

**Statistics and standings.** A full Jacksonville receipt and fifteen compact receipts are preserved; the box score, standings and statbook were generated from them. Every band-audit row is WITHIN. Jacksonville is fourth in the AFC South and eleventh in the AFC.

**Availability.** Brad Meester is out (upper extremity, projected return September 27). C.J. Wilson is out (trunk, projected return January 30, 2014); any reserve-list move is a Caldwell and medical decision and has not been made. Pasztor remains on medical hold and Mosley unavailable. Background injuries are listed in `league_results/week_02.md`.

**Engine findings (investigated, not grounds to rerun).** The same snap-ledger drive-detail defects recur: snaps after the final-possession fumble and one Oakland possession spanning halftime. Score and statistics are unaffected; the result stands.

**Primary records:** `regular_season/week_02_jacksonville_at_oakland/output.md` and `call_sheet.json`; `league_results/week_02.md`; `stats/game_receipts/week_02_*.json`; `standings.md`.
**Next competitive event:** September 22 Week 3 at Seattle, 4:25 p.m. ET. **Not simulated.**

**Commit closed - Canonical update - September 15, 2013 - Week 2 at Oakland closed - canonical through September 15, after Week 2**

## Entry 38: Week 3 closed

**Effective canonical state:** September 22, 2013, after Week 3
**Recorded:** September 27, 2026
**Checkpoint:** `Canonical update - September 22, 2013 - Week 3 at Seattle closed`
**Preceding global package checkpoint:** `Canonical update - September 15, 2013 - Week 2 at Oakland closed`

**Result.** Jacksonville 16, Seattle 13 at CenturyLink Field. Josh Scobee's third field goal came on the final snap. Jacksonville is 2-1.

**Batch.** All sixteen Week 3 games closed once each under kernel 2013.5 through `runtime.game_runner.run_game` and the private Engine State service, from the package frozen by `scripts/build_week_inputs.py 3` after the sixteen-game exclusivity and game-day gate passed. No event was drawn twice.

**Inputs.** Jacksonville used Stone's Week 3 plan: the opening fifteen plus Dagger (SOLID only) as the structured sheet, with Boot Flood and 10 Empty off it. Mike Brewster started at center for Brad Meester, with Mark Asper active. The edge order was Babin, Mincey, Branch and Davis. Inactives were Pasztor, Meester, Mosley, C.J. Wilson, Edwards and Rutland, and Blackmon remained on Reserve/Suspended. Background clubs were carried forward from the Week 1 depth-chart library with branch injuries and pre-existing returns applied. Before the draw, a data-preparation defect was corrected: background clubs had been dressing every available player (up to 53), while Jacksonville dressed 46. From Week 3, each background club dresses 46, made inactive mechanically from the bottom of its depth order without breaking a legal game-day unit. The weekly gate now rejects more than 46 actives. Kernel injury exposure is drawn per dressed player, so the earlier rule gave background clubs more injury draws than Jacksonville. Weeks 1 and 2 stand as closed. Every club carried the Average low-confidence unit anchor.

**Statistics and standings.** A full Jacksonville receipt and fifteen compact receipts are preserved; the box score, standings and statbook were generated from them. Every band-audit row is WITHIN. Jacksonville is third in the AFC South and ninth in the AFC.

**Availability.** Paul Posluszny is out (upper extremity, projected return October 2), which covers the Week 4 game. Meester's projection clears September 27. His return to center is a Stone decision; he is on the Week 3 inactive list, which carries forward unless reset. C.J. Wilson remains out, Pasztor on medical hold and Mosley unavailable. Background injuries are listed in `league_results/week_03.md`.

**Engine findings (investigated, not grounds to rerun).** The snap-ledger drive-detail defects recur. Jacksonville's touchdown drive records snaps after Toney Clemons' 19-yard touchdown catch. Seattle's fourth-quarter possession after Scobee's first field goal ends with no punt, score or turnover row. Its last possession records 76 net yards before a punt, with no field position in the ledger to reconcile them. Score and statistics are unaffected; the result stands.

**Primary records:** `regular_season/week_03_jacksonville_at_seattle/output.md` and `call_sheet.json`; `league_results/week_03.md`; `stats/game_receipts/week_03_*.json`; `standings.md`; `depth_chart.json`.
**Next competitive event:** September 29 Week 4 vs Indianapolis, 1 p.m. ET. **Not simulated.**

**Commit closed - Canonical update - September 22, 2013 - Week 3 at Seattle closed - canonical through September 22, after Week 3**

## Entry 39: Engine correction, kernel 2013.6

**Effective canonical state:** September 22, 2013, after Week 3 and before Week 4
**Recorded:** September 27, 2026
**Checkpoint:** `Canonical update - September 22, 2013 - Kernel 2013.6 engine correction`
**Preceding global package checkpoint:** `Canonical update - September 22, 2013 - Week 3 at Seattle closed`

**Why.** Two engine defects, recorded in Entries 35, 37 and 38 and reported to the user, were corrected at the user's instruction before Week 4:
- Field goals and extra points were always made.
- The public snap ledger could contain impossible entries: snaps after a touchdown or turnover in the same drive, drives with no terminal row, possessions across halftime, kickoffs after time expired, and drive yardage unrelated to how the drive ended.

**What changed.** Kernel 2013.6 draws each possession's result from a reproducible 2012 drive model. The model is built from nflverse play-by-play and checked against a second pass on nflscrapR; both come from the same NFL GSIS feed, so the check is not fully independent. It reconciles exactly to the verified 2012 totals of 1,016 field-goal attempts, 852 made and 468 interceptions. Each possession then resamples a real 2012 drive of that outcome for its plays, net yards and time. The changes:
- Field goals are made at the sourced 2012 rate for their distance, and extra points at 1,229 of 1,237.
- Safeties, turnovers on downs and clock-expired possessions are explicit.
- Each half is bounded, and the second half opens with a kickoff to the other team.
- No kickoff follows a score that ends a half.
- Overtime follows the 2012 rules.
- A touchdown or turnover is always the drive's last snap.
- Every possession ends in exactly one terminal row, and a coherence check runs on every result.

The kernel constants and the private service identity move together to 2013.6. No field position is published; that remains a known gap.

**Verification.** In 250 synthetic games resolved locally with synthetic seeds (never the private service), the coherence check found zero impossible entries. Every graded band read WITHIN except drive-ending punts, which run slightly high because of how drives are redirected at the end of a half; it is disclosed and not tuned. Kickoffs per team-game is informational, because the 2012 count includes kicks the kernel does not model. Scoring runs about 1.3 points per team-game below 2012 because non-offensive touchdowns are not modelled. No coefficient, pool or tolerance was changed after the results were seen.

**Canon.** Weeks 1-3 (Entries 35, 37 and 38) stand as closed under kernels 2013.4 and 2013.5. They were not rerun, redrawn or edited, and the band audit shows them as a legacy cohort. Week 4 has not been simulated.

**Primary records:** `runtime/README.md` (2013.6 contract); `library/2012_drive_model_calibration.md`; `library/data/2012_nfl_drive_model.json`; `scripts/research/build_2012_drive_model.py`.
**Next competitive event:** September 29 Week 4 vs Indianapolis, 1 p.m. ET. **Not simulated.**

**Commit closed - Canonical update - September 22, 2013 - Kernel 2013.6 engine correction - canonical through September 22, after Week 3**

## Entry 40: Week 4 closed

**Effective canonical state:** September 29, 2013, after Week 4
**Recorded:** September 27, 2026
**Checkpoint:** `Canonical update - September 29, 2013 - Week 4 vs Indianapolis closed`
**Preceding global package checkpoint:** `Canonical update - September 22, 2013 - Kernel 2013.6 engine correction`

**Result.** Jacksonville 31, Indianapolis 10 at EverBank Field. Jacksonville is 3-1 and leads the AFC South.

**Batch.** All fifteen Week 4 games closed once each under kernel 2013.6 (Entry 39) through `runtime.game_runner.run_game` and the private Engine State service. They closed from the package frozen by `scripts/build_week_inputs.py 4` after the fifteen-game exclusivity and game-day gate passed. Carolina and Green Bay had byes. No event was drawn twice.

**Inputs.**
- **Call sheet:** Stone's runner-ready sheet, with 12 Ace Right, Power R frozen once. It was listed twice, as calls 1 and 9, and a duplicate would have doubled that label's share of snap labels (see `call_sheet.json` provenance).
- **Line:** Brewster started at center. Meester's projection cleared September 27, and he dressed as reserve center.
- **Linebackers:** Smith and Allen were the base pair, then Stanford and Moore, with Posluszny out.
- **Edge:** Babin, Mincey, Branch, Davis.
- **Inactives:** Pasztor, Mosley, C.J. Wilson, Posluszny, Edwards and Rutland. Blackmon remained on Reserve/Suspended.
- **Background clubs** dressed 46 players each, from depth order with branch injuries applied. Every club carried the Average low-confidence unit anchor.

**Statistics and standings.** A full Jacksonville receipt and fourteen compact receipts are preserved, all carrying the 2013.6 drives summary. The box score, standings and statbook were generated from them. In the 2013.6 cohort, every band-audit row is WITHIN and every ledger-coherence count is zero. Jacksonville is first in the AFC South and second in the AFC.

**Availability.** Will Rackley had a minor trunk injury, limited with no projected absence. Posluszny's projection clears October 2. C.J. Wilson remains out, Pasztor on medical hold and Mosley unavailable. Background injuries, including Drew Brees on an independent head/neck hold, are listed in `league_results/week_04.md`.

**Engine findings (investigated, not grounds to rerun).** Indianapolis's opening possession is a one-snap, seven-yard touchdown drive after a touchback on the opening kickoff. Kernel 2013.6 resamples real 2012 drives and publishes no field position. It therefore does not link a drive's length to where the previous kick or drive ended, a gap Entry 39 left open deliberately. The ledger check covers what the ledger records, and it passes. The result stands.

**Primary records:** `regular_season/week_04_indianapolis_at_jacksonville/output.md` and `call_sheet.json`; `league_results/week_04.md`; `stats/game_receipts/week_04_*.json`; `standings.md`; `depth_chart.json`.
**Next competitive event:** October 6 Week 5 at St. Louis, 1 p.m. ET. **Not simulated.**

**Commit closed - Canonical update - September 29, 2013 - Week 4 vs Indianapolis closed - canonical through September 29, after Week 4**

## Entry 41: Week 5 closed

**Effective canonical state:** October 6, 2013, after Week 5
**Recorded:** September 27, 2026
**Checkpoint:** `Canonical update - October 6, 2013 - Week 5 at St. Louis closed`
**Preceding global package checkpoint:** `Canonical update - September 29, 2013 - Week 4 vs Indianapolis closed`

**Result.** St. Louis 26, Jacksonville 24 at the Edward Jones Dome. Jacksonville is 3-2 and first in the AFC South on a three-way tie.

**Batch.** All fourteen Week 5 games closed once each under kernel 2013.6 through `runtime.game_runner.run_game` and the private Engine State service. They closed from the package frozen by `scripts/build_week_inputs.py 5` after the fourteen-game exclusivity and game-day gate passed. Minnesota, Pittsburgh, Tampa Bay and Washington had byes. No event was drawn twice.

**Inputs.**
- **Call sheet:** Stone's runner-ready sheet, frozen verbatim. Every package on it (6OL, 12 Shift Empty, Jet, TE Delay, Snag) is in the active 2013 offensive iteration.
- **Line:** Brewster started at center with Meester as reserve, and Bradfield was the sixth offensive lineman.
- **Linebackers:** Posluszny returned to the base defense with Smith, and Smith stayed the communication lead. Allen was first off the bench.
- **Inactives:** Pasztor, Mosley, C.J. Wilson, Edwards, Rutland and John Parker Wilson (a game-day numbers decision; he stays QB3). Blackmon served the last game of the league suspension on Reserve/Suspended.
- **Background clubs** dressed up to 46 players each, from depth order with branch injuries applied; the Jets dressed 43 because fewer were available (they dressed 44 in Weeks 3 and 4, where Entries 38 and 40 said 46 each; corrected here). Every club carried the Average low-confidence unit anchor.

**Statistics and standings.** A full Jacksonville receipt and thirteen compact receipts are preserved. The box score, standings and statbook were generated from them. In the 2013.6 cohort every ledger-coherence count is zero, and every graded band row is WITHIN except field-goal accuracy under 30 yards: 26 of 30 against 231 of 239. It was investigated. `runtime.drive_model.fg_make_prob` applies the sourced rate correctly, and a result this low has about a 1.7% probability at that sample size, among some forty graded rows. No defect was found.

**Availability.**
- Adam Thielen is out (upper extremity, projected return October 9), before Week 6.
- Will Rackley has a minor upper-extremity injury, limited with no projected absence (roster availability now reads "Limited, no projected absence", which the week-input builder treats as available, the same rule as every club).
- Posluszny is available.
- C.J. Wilson remains out, Pasztor on medical hold and Mosley unavailable.
- Background injuries are listed in `league_results/week_05.md`.

**Engine findings (investigated, not grounds to rerun).**
- **Safety after a touchback.** Jacksonville's fourth-quarter possession after a touchback lost 13 yards on two runs and is recorded as a safety. From the 20 that is physically impossible. Kernel 2013.6 resamples real 2012 drives with no field position, so it does not tie a drive to where the previous kick or drive left the ball. This gap was left open deliberately in Entry 39 and first observed in Entry 40. The two points are the final margin.
- **Short touchdown drive after a punt.** Jacksonville's one-net-yard touchdown drive after an unreturned 34-yard punt has the same cause.
- **Call labels.** They are assigned uniformly from the sheet regardless of ball carrier. Five snaps carry the Jet L label, two of them Cousins runs. The labels do not represent Stone's call frequencies.
- **Late punt.** The punt with 1:56 left while trailing by two reflects the kernel's lack of score-dependent fourth-down choice, a gap not addressed by Entry 39 and first recorded here.

Under AGENTS.md these are engine defects to investigate, never grounds to rerun or select a result, and the result stands.

**Primary records:** `regular_season/week_05_jacksonville_at_st_louis/output.md` and `call_sheet.json`; `league_results/week_05.md`; `stats/game_receipts/week_05_*.json`; `standings.md`; `depth_chart.json`.
**Next roster event:** Blackmon's reinstatement from Reserve/Suspended at the end of the league suspension (Entry 36). Its date and roster treatment (open spot or roster exemption) are unverified and must be sourced before the Week 6 transaction. Stone's game-day inactive applies for Weeks 6 and 7.
**Next competitive event:** October 13 Week 6 at Denver, 4:05 p.m. ET. **Not simulated.**

**Commit closed - Canonical update - October 6, 2013 - Week 5 at St. Louis closed - canonical through October 6, after Week 5**

## Entry 42: Blackmon reinstated and activated

**Effective canonical state:** October 7, 2013
**Recorded:** September 27, 2026
**Checkpoint:** `Canonical update - October 7, 2013 - Blackmon reinstated and activated`
**Preceding global package checkpoint:** `Canonical update - October 6, 2013 - Week 5 at St. Louis closed`

**Transaction.** Justin Blackmon's four-game league suspension (Entry 36) ended with Jacksonville's Week 5 game. Under the sourced 2013 rule (`library/2013_suspension_reinstatement_rules.md`: eligible the day after the club's fourth suspended game; confirmed), he was reinstated from Reserve/Suspended on Monday, October 7. Jacksonville activated him to the 53-man roster the same day, using the spot Caldwell had held open since September 9. The club may activate a returning player at any time, so no league roster exemption was needed or resolved. The activation is a roster move within Caldwell's authority. It carries out Stone's recorded plan for Blackmon to practice and be a game-day inactive in Weeks 6 and 7. He is eligible for Week 8.

**Effects.**
- Active roster 53; no Reserve/Suspended player; practice squad 8.
- Game checks: Blackmon's base-salary game checks resume. The sourced rule sets the forfeiture for the four suspended games at 4/17 of his 2013 base salary. The dollar amount and its cap credit remain unresolved, because his base/proration split is not verified in the worksheet.
- Stone's Week 6-7 game-day inactive decision is unchanged.

**Primary records:** `roster.md`; `offseason/current_cap_worksheet.md`; `depth_chart.json`.

**Commit closed - Canonical update - October 7, 2013 - Blackmon reinstated and activated - canonical through October 7**

## Entry 43: Week 6 closed

**Effective canonical state:** October 13, 2013, after Week 6
**Recorded:** September 27, 2026
**Checkpoint:** `Canonical update - October 13, 2013 - Week 6 at Denver closed`
**Preceding global package checkpoint:** `Canonical update - October 7, 2013 - Blackmon reinstated and activated`

**Result.** Jacksonville 26, Denver 10 at Sports Authority Field at Mile High. Jacksonville is 4-2, first in the AFC South and first in the AFC.

**Batch.** All fifteen Week 6 games closed once each under kernel 2013.6 through `runtime.game_runner.run_game` and the private Engine State service. They closed from the package frozen by `scripts/build_week_inputs.py 6` after the fifteen-game gate passed. Atlanta and Miami had byes. No event was drawn twice. The user chose to play Week 6 before kernel 2013.7 (in development) was ready.

**Inputs.**
- **Call sheet:** Stone's runner-ready sheet, frozen verbatim. Sprint Flood, H Chip-Release, Smoke/Now, Zip, Snag, TE Delay and 6OL all appear in the active 2013 book.
- **Line:** Brewster confirmed as the starting center, with Meester as reserve.
- **Inactives:** Blackmon, Pasztor, Mosley, C.J. Wilson, Edwards, Rutland and John Parker Wilson. Thielen returned as WR2.
- **Development emphasis:** Kelce and Thielen, through assignments rather than quotas.
- **Background clubs** dressed up to 46 players each, from depth order. Every club carried the Average low-confidence unit anchor.

**Statistics and standings.** A full Jacksonville receipt and fourteen compact receipts are preserved. The box score, standings and statbook were generated from them. Every graded band-audit row is WITHIN, and every ledger-coherence count is zero.

**Availability.** Jacksonville generated no injury. Rackley remains limited (minor). Background injuries are listed in `league_results/week_06.md`, including Pittsburgh's Antonio Brown (projected 173 days) and Denver's Orlando Franklin (head/neck hold).

**Engine findings (investigated, not grounds to rerun).**
- **Safety after a kickoff return.** Denver's third-quarter possession began after a 28-yard kickoff return, lost 13 yards on two plays and is recorded as a safety, which cannot reach the end zone. It is the same known lack of field position as the Week 5 safety against Jacksonville (Entries 39-41), this time in Jacksonville's favour. Under the rules both stand.
- **Call labels.** The TE Delay label was attached to throws to Clemons and Mike Brown because 2013.6 labels are not tied to the ball carrier. Kelce was not targeted: 2013.6 targets follow the tight-end depth order.

Kernel 2013.7 addresses the first three defect classes and the sack rate.

**Primary records:** `regular_season/week_06_jacksonville_at_denver/output.md` and `call_sheet.json`; `league_results/week_06.md`; `stats/game_receipts/week_06_*.json`; `standings.md`; `depth_chart.json`.
**Next competitive event:** October 20 Week 7 vs San Diego, 1 p.m. ET. **Not simulated.**

**Commit closed - Canonical update - October 13, 2013 - Week 6 at Denver closed - canonical through October 13, after Week 6**

## Entry 44: Week 7 closed

**Effective canonical state:** October 20, 2013, after Week 7
**Recorded:** September 27, 2026
**Checkpoint:** `Canonical update - October 20, 2013 - Week 7 vs San Diego closed`
**Preceding global package checkpoint:** `Canonical update - October 13, 2013 - Week 6 at Denver closed`

**Result.** Jacksonville 30, San Diego 24 at EverBank Field. Jacksonville is 5-2, first in the AFC South (ahead of 5-2 Tennessee on record in common games) and first in the AFC.

**Batch.** All fifteen Week 7 games closed once each under kernel 2013.6 through `runtime.game_runner.run_game` and the private Engine State service. They closed from the package frozen by `scripts/build_week_inputs.py 7` after the fifteen-game gate passed. New Orleans and Oakland had byes. No event was drawn twice. Kernel 2013.7 was still in development; the user directed that it be finished later and, if not ready, deferred to 2014.

**Inputs.**
- **Call sheet:** Stone's runner-ready fifteen-call sheet, frozen verbatim. The new calls Wham R, Split Leak with TURNBACK protection and Thielen Whip (Whip/Pivot) all appear in the active 2013 book.
- **Line and skill groups:** unchanged from Week 6, with Brewster at center, Meester reserve and Bradfield the swing and sixth lineman.
- **Inactives:** the Week 6 list carried over: Blackmon (his final Stone inactive week), Pasztor, Mosley, C.J. Wilson, Edwards, Rutland and John Parker Wilson.
- **Development emphasis:** Kelce (Wham, Split Leak) and Thielen (Whip), through assignments rather than quotas.
- **Background clubs** dressed up to 46 players each, from depth order. Every club carried the Average low-confidence unit anchor.

**Statistics and standings.** A full Jacksonville receipt and fourteen compact receipts are preserved (107 of 107 through Week 7). The box score, standings and statbook were generated from them. Every ledger-coherence count is zero.

**Availability.** Jacksonville generated no injury. Rackley remains limited (minor). Blackmon's Stone game-day inactive period (Weeks 6-7) is complete; he is eligible from Week 8. Background injuries are listed in `league_results/week_07.md`. Among them, San Francisco, the Week 8 opponent, lost Bruce Miller and Jon Baldwin, each projected three days.

**Engine findings (investigated, not grounds to rerun).**
- **Field position and downs.** San Diego's fourth-quarter touchdown came on a two-play, two-yard drive after a 16-yard kickoff return. In the second quarter, San Diego kept the ball through five runs totalling no gain before an 80-yard touchdown pass. Kernel 2013.6 tracks neither field position nor downs against snap yardage (Entries 39-43).
- **Call labels.** The Whip and Split Leak labels were attached to throws to Lewis, Shorts, Brown and Clemons because 2013.6 labels are not tied to the receiver. Kelce was not targeted. Under 2013.6, targets follow position-group usage and depth order, so the second tight end draws few; he drew four in Week 5. Entry 43's statement that targets follow the tight-end depth order overstated this: depth order lowers the TE2's share and does not exclude him.
- **FG accuracy under 30 yards (band audit).** The 2013.6 cohort now reads OUTSIDE: 51 of 57 (0.895) against the sourced 231 of 239 (0.967). The rate rose from Week 6 (0.886); the row flipped because its tolerance narrows as the sample grows. Four of the six misses came at 24 yards, spread over four games and four clubs.
  - **Investigation:** the make chance is one sourced rate for every attempt under 30 yards, drawn independently of the resampled distance, so no code path can favour a miss at one distance.
  - **Probability:** six or more misses in 57 at the sourced rate has about a 1.2% chance, among some forty graded rows.
  - **Conclusion:** no defect found. The row stays under watch, and kernel 2013.7 starts a new cohort.

Kernel 2013.7 adds field position, real per-drive first-down and third-down counts, carrier-true labels and the late-game model.

**Primary records:** `regular_season/week_07_san_diego_at_jacksonville/output.md` and `call_sheet.json`; `league_results/week_07.md`; `stats/game_receipts/week_07_*.json`; `standings.md`; `depth_chart.json`.
**Next competitive event:** October 27 Week 8 vs San Francisco at Wembley Stadium, London, 1 p.m. ET (Jacksonville designated home). **Not simulated.** Next deadline: trade deadline, October 29, 4 p.m. ET.

**Commit closed - Canonical update - October 20, 2013 - Week 7 vs San Diego closed - canonical through October 20, after Week 7**

## Entry 45: Week 8 closed

**Effective canonical state:** October 27, 2013, after Week 8
**Recorded:** September 27, 2026
**Checkpoint:** `Canonical update - October 27, 2013 - Week 8 vs San Francisco closed`
**Preceding global package checkpoint:** `Canonical update - October 20, 2013 - Week 7 vs San Diego closed`

**Result.** Jacksonville 20, San Francisco 13 at Wembley Stadium, London, with Jacksonville the designated home team. Jacksonville is 6-2, first in the AFC South (5-2 Tennessee had a bye) and first in the AFC, ahead of the 6-2 Jets on conference record.

**Batch.** All thirteen Week 8 games closed once each under kernel 2013.6 through `runtime.game_runner.run_game` and the private Engine State service. They closed from the package frozen by `scripts/build_week_inputs.py 8` (sha256 `6680c723...`) after the thirteen-game gate passed. Baltimore, Chicago, Houston, Indianapolis, San Diego and Tennessee had byes. No event was drawn twice. The Jacksonville game was drawn with venue `neutral`. Kernel 2013.7 was built but did not pass its acceptance and is not deployed.

**Inputs.**
- **Call sheet:** Stone's runner-ready fifteen-call sheet, frozen verbatim and committed before the draw. Every concept is in the active 2013 offensive book: Inside Zone with the ACCESS Smoke tag, Slant-Flat, Y-Cross, Mills with MAX, Wham, Whip/Pivot, Split Leak with TURNBACK, Sprint Flood, Spacing and 6OL Heavy.
- **Blackmon dressed** as WR3 and the outside Z receiver, with no target quota. The receiver order became Shorts, Thielen (WR2/H), Blackmon, Clemons, Brown.
- **Inactives:** Pasztor, Mosley, C.J. Wilson, Edwards, Pendleton, Rutland and John Parker Wilson.
- **Background clubs** dressed up to 46 players from depth order (the Jets 42, from a 44-player sourced unit less two injuries). Every club carried the Average low-confidence unit anchor.

**Gate hardening (before the draw).** A readiness audit found two gaps:
- `build_week_inputs.py` wrote the package before running the gate, so a blocked build could leave a failing package at the frozen path. It now writes only after the gate passes.
- `close_week.py` drew whatever package was on disk. It now re-runs the weekly gate before any draw.

A test that hard-coded Blackmon as inactive was generalised. No kernel, packet or result logic changed.

**Statistics and standings.** A full Jacksonville receipt and twelve compact receipts are preserved (120 of 120 through Week 8). The box score, standings and statbook were generated from them. Every graded band-audit row is WITHIN, including field-goal accuracy under 30 yards (0.917), and every ledger-coherence count is zero.

**Availability.**
- **Jacksonville:** no injury was generated.
- **San Francisco:** Colin Kaepernick (upper extremity, out, projected one day) and B.J. Daniels (trunk, limited).
- **Background clubs:** injuries are listed in `league_results/week_08.md`. From this week the roundup states the rule as the engine applies it: a background player returns on his projected date, and the staged concussion-protocol clearance is not modelled as a separate event. Earlier roundups said return required independent sign-off whatever the projection, which the engine did not do.

**Open reconciliation: Pasztor and Mosley.** Their preseason injuries (Entries 22 and 25) were logged with class and restriction only. No preseason receipt or projected return was preserved, so their holds cannot clear on a date, while every other club's generated injuries do. That is a protagonist-blind gap (Document 1 section 9.1), and no clearance or date is invented here. The fix is to recover the original injury records through the Document 7 section 3.4 correction path, or to adopt a club-blind rule. Both were Stone's game-day inactives this week, so the draw is unaffected.

**Engine findings (investigated, not grounds to rerun).**
- **Field position.** Thielen's 20-yard touchdown came two snaps after an unreturned San Francisco punt that ended a 3-yard drive from a touchback.
- **Downs.** Jacksonville's 14-play drive is recorded as a turnover on downs, but its last snap was an 18-yard completion.
- **Call labels.** "Access Blackmon Smoke" was attached to nine running-back and fullback carries, and Blackmon never touched the ball on it. The Mills "Blackmon Post Alert" label went to a sack and to throws to Lewis, Jones-Drew and Thielen. Cousins's runs carried running-back labels.
- **Neutral site.** Kernel 2013.6 applies its small home term to the designated home team regardless of venue. So Jacksonville received it at Wembley, as Minnesota did in the Week 4 Wembley game. The public receipt does not record the venue.

Under the standing rule these are fixed going forward, and every result stands.

**Kernel 2013.7 status.** Kernel 2013.7 is built and passes its structural, coherence, defect, label, isolation and determinism checks. 54 of its 57 graded rows are WITHIN. Three drive-model rows read OUTSIDE (FGM per team game, drive share ending on the clock, clock-expired drives), traced to its first-half end-of-half model. It is not committed to main or deployed; adoption awaits the user's decision.

**Primary records:** `regular_season/week_08_san_francisco_at_jacksonville/output.md` and `call_sheet.json`; `league_results/week_08.md`; `stats/game_receipts/week_08_*.json`; `standings.md`; `depth_chart.json`.
**Next:** trade deadline Tuesday, October 29, 4 p.m. ET (no proposal open); Week 9 bye; November 10 Week 10 at Tennessee, 1 p.m. ET. **Not simulated.**

**Commit closed - Canonical update - October 27, 2013 - Week 8 vs San Francisco closed - canonical through October 27, after Week 8**

## Entry 46: Pasztor and Mosley injury projections recovered

**Effective canonical state:** October 27, 2013, after Week 8
**Recorded:** September 27, 2026
**Checkpoint:** `Canonical correction - October 27, 2013 - Pasztor and Mosley injury projections recovered`
**Preceding global package checkpoint:** `Canonical update - October 27, 2013 - Week 8 vs San Francisco closed`

**Defect.** Austin Pasztor's August 17 head/neck injury (Entry 22) and C.J. Mosley's August 29 upper-extremity injury (Entry 25) were generated with a projected return, as every injury is (`runtime/injuries.py`). Only the class and restriction were recorded, though, and no preseason receipt was kept. Their holds therefore could never clear on a date, while every other club's generated injuries clear on their projection. That is a protagonist-blind gap (Document 1 section 9.1), recorded as open in Entry 45.

**Exact replay not possible.** The Document 7 section 3.4 correction path needs the original packet rebuilt to its committed digest. The preseason TeamInputs were built transiently and never committed; commit `4cf2ad7` holds only prose, and no builder or input file exists in the history. So no packet can be rebuilt, and no replay was sent.

**Audited redraw (user's choice, September 27, 2026).**
- **What was drawn.** Each missing projection was drawn once from the model every club uses. The draw was conditioned only on the class and restriction recorded when the injury was generated. A head/neck hold constrains nothing, since every severity yields a hold. An upper-extremity "out" restriction means at least one day. Later availability records were not used as evidence, because they were written without the projection.
- **Pre-registration.** The procedure (`scripts/recover_injury_projection.py`) and both packets were committed and pushed before the draw: `career/2013/migrations/injury_projection_recovery.json`, with procedure `injury-projection-recovery-v1`, the private snapshot and the model digest.
- **The draw.** The private service committed each packet digest and supplied the entropy, as for a game. A second submission of each packet returned the same reference and the same result.

**Results.**

| Player | Injury | Severity | Return days | Projected return |
|---|---|---|--:|---|
| Austin Pasztor | Head/neck, independent medical hold (August 17) | Minor | 2 | August 19, 2013 |
| C.J. Mosley | Upper extremity, out (August 29) | Minor | 1 | August 30, 2013 |

**Application.** On the rule applied to every club, both would have returned before Week 1, so both are available from this checkpoint. They were held out of Weeks 1-8 by the recording defect. Every result stands, and no game is rerun.

The Week 8 inactive list, which names both, carries forward for Week 10 unless Stone changes it. Their depth-chart places are the preseason ones, and their roles are Stone's to set. No roster count, contract or cap figure changes.

**Primary records:** `migrations/injury_projection_recovery.json`; `roster.md`; Documents 4 and 5.
**Next:** trade deadline Tuesday, October 29, 4 p.m. ET; Week 9 bye; November 10 Week 10 at Tennessee. **Not simulated.**

**Commit closed - Canonical correction - October 27, 2013 - Pasztor and Mosley injury projections recovered - canonical through October 27, after Week 8**

## Entry 47: League awards record created; Weeks 1-8 and September backfilled

**Effective canonical state:** October 27, 2013, after Week 8
**Recorded:** September 27, 2026
**Checkpoint:** `Canonical update - October 27, 2013 - League awards backfilled`
**Preceding global package checkpoint:** `Canonical correction - October 27, 2013 - Pasztor and Mosley injury projections recovered`

**Authority.** On September 27, 2026 the user directed that a league awards record be created, that the missed Weeks 1-8 be backfilled, and that each winner be chosen from a formula shortlist by an audited panel draw.

**Structure.** The award categories and calendar come from `library/2013_nfl_awards_structure.md`, which records no winners. Weekly awards are the AFC and NFC Offensive, Defensive and Special Teams Player of the Week; monthly awards are the same six. Months are assigned by NFL week: September Weeks 1-4, October 5-8, November 9-12, December 13-17. Fan-voted awards are not generated, and Rookie of the Month waits for a sourced 32-club rookie list.

**Method.** `career/2013/awards/methodology.json` fixes one scoring formula per category, applied identically to every player from the receipts, plus a conference top-three shortlist and a 6:3:1 panel pick whose entropy comes from the private service. It was committed and pushed (67a2ea0) before any draw.

**Draws.** Fifty-four awards were drawn through the private service: Weeks 1-8 and September. Every packet digest and result reference is in `awards/results.json`, and the readable record is `awards/weekly_and_monthly.md`. No Jacksonville player won. No game result or statistic changed. October's awards are drawn on the league's announcement date of October 31.

**Commit closed - Canonical update - October 27, 2013 - League awards backfilled - canonical through October 27, after Week 8**

## Entry 48: Kernel 2013.7 adopted

**Effective canonical state:** October 27, 2013, after Week 8
**Recorded:** September 27, 2026
**Checkpoint:** `Canonical update - October 27, 2013 - League awards backfilled; kernel 2013.7 adopted`
**Preceding global package checkpoint:** `Canonical update - October 27, 2013 - League awards backfilled`

**Decision.** On September 27, 2026 the user adopted kernel 2013.7 as documented.

**What 2013.7 adds:**
- start-bin-conditioned field position with a spot chain;
- each drive's real 2012 first-down, third-down and sack counts;
- call labels tied to the ball carrier, with a fail-closed family map;
- a late-game fourth-down partition.

**User authorization.** Fourth-down calls are user-controlled under Document 1 section 3.1. In autonomous management mode, the league-wide late-game model decides them for every club alike, including Jacksonville's. The user authorized this by adopting the kernel.

**Acceptance.** 54 of 57 graded rows were WITHIN. The three OUTSIDE rows are FGM per team game, drive share ending on the clock, and clock-expired drives per team game, all traced to the first-half end-of-half model. They are registered as known detections in `runtime/bands.py` and are still graded and displayed. No centre, tolerance, coefficient or pool changed.

**Scope.** Every slate closed after Week 8 runs under 2013.7, with its own audit cohort. Weeks 1-8 stand under 2013.4-2013.6 and are never rerun. Their stat views re-render byte-identical.

**Unchanged.** The neutral-site home term (Entry 45) is not changed in 2013.7.

**Call families.** The family map adds "Inside + Smoke", from the active 2013 book's ACCESS, Inside Zone and Smoke rules, so all Week 1-8 sheets resolve. A new family on a later sheet fails closed until it is declared.

**Deployment.** The private service is redeployed at 2013.7 from merged main. Readiness requires that version.

**Next:** trade deadline Tuesday, October 29, 4 p.m. ET; October awards on October 31; Week 9 bye; November 10 Week 10 at Tennessee. **Not simulated.**

**Commit closed - Canonical update - October 27, 2013 - League awards backfilled; kernel 2013.7 adopted - canonical through October 27, after Week 8**

## Entry 49: Week 9 bye closed

**Effective canonical state:** November 3, 2013, after Week 9
**Recorded:** September 28, 2026
**Checkpoint:** `Canonical update - November 3, 2013 - Week 9 bye closed`
**Preceding global package checkpoint:** `Canonical update - October 27, 2013 - League awards backfilled; kernel 2013.7 adopted`

**Jacksonville.** Bye week, run on Stone's midseason review and second-half plan:
- Monday: return-from-London recovery, team meeting and film.
- Tuesday: one self-scout correction practice (ball security, protection, third down, core runs and 6OL, run fits, rush finish, back and tight-end coverage).
- Wednesday to Sunday: players off.
- Staff: self-scout, coordinator meetings and second-half planning, including a Houston short-week skeleton for Week 14.

Pasztor and Mosley practised for the first time since Entry 46. Neither moved on the depth chart; their roles are decided from practice evidence. No injury, no roster change. Record 6-2. The durable second-half choices are recorded in `regular_season/week_09_bye/output.md`:
- Duo, Texas and a TE screen become weekly options.
- Boot Flood stays out.
- A Thursday complement period is added to the practice week.

**Trade deadline.** Stone gave Caldwell his assessment before the Tuesday, October 29 deadline. There was no need at quarterback, receiver, running back or center; any move for pass rush or line depth had to come on value alone, and none before Pasztor and Mosley were evaluated. No proposal was open, and the deadline passed with no Jacksonville transaction.

**League.** Thirteen games closed once each under kernel 2013.7, the first slate on it. They were drawn from the package frozen by `build_week_inputs.py 9` (sha256 `8c8c14ad...`), which now runs without a call sheet in Jacksonville's bye week. Thirteen compact receipts were kept, 133 of 133 in total. The 2013.7 cohort's graded rows are WITHIN, registered known detections or of insufficient sample, and every measurable ledger-coherence count is zero. The label and snap-level classes need a full receipt and are not measurable in a week without a Jacksonville game. Tennessee lost and is 5-3. The Jets are 7-2 and hold the AFC's top seed; Jacksonville is second.

**Awards.** The six Week 9 awards and the six October Players of the Month were drawn by the registered method. October covers Weeks 5-8 and was announced by the league on October 31. No Jacksonville player won.

**Primary records:** `regular_season/week_09_bye/output.md`; `league_results/week_09.md`; `stats/game_receipts/week_09_*.json`; `awards/`; `standings.md`.
**Next competitive event:** November 10 Week 10 at Tennessee, 1 p.m. ET. **Not simulated.**

**Commit closed - Canonical update - November 3, 2013 - Week 9 bye closed - canonical through November 3, after Week 9**

## Entry 50: Week 10 at Tennessee closed

**Effective canonical state:** November 10, 2013, after Week 10
**Recorded:** September 28, 2026
**Checkpoint:** `Canonical update - November 10, 2013 - Week 10 at Tennessee closed`
**Preceding global package checkpoint:** `Canonical update - November 3, 2013 - Week 9 bye closed`

**Result.** Tennessee 41, Jacksonville 11 at LP Field. Jacksonville is 6-3. Tennessee, also 6-3, leads the AFC South on head-to-head, and Jacksonville is the AFC's fifth seed.

**Batch.** All fourteen Week 10 games closed once each under kernel 2013.7, the first Jacksonville game on it. They were drawn from the package frozen by `build_week_inputs.py 10` (sha256 `4064efc2...`) after the gate passed; the call sheet and depth chart were committed before the draw (3c41ca9).

**Inputs.**
- **Call sheet:** Stone's fifteen calls. Duo, Texas, TE Delay, RB Slow Screen and Post-Cross all resolve in the 2013.7 family map from the active 2013 book.
- **Base personnel:** 12, with 13, 21 and 6OL protection packages.
- **Line:** Pasztor dressed as the interior reserve and Asper was inactive.
- **Inactives:** Asper, Mosley, C.J. Wilson, Edwards, Pendleton, Rutland, John Parker Wilson.

**Game.**
- Jacksonville turned the ball over six times: four Cousins interceptions and fumbles by Jones-Drew and Cousins. Those giveaways led to 13 Tennessee points.
- Scobee made three of five field goals, missing from 22 and 27.
- The defense had three sacks, including Roy Miller's safety, and an interception by Posluszny.
- Tennessee ran for 210 yards, 126 of them by Chris Johnson.

**Availability.** Cornerback Alan Ball was hurt (trunk, long-term; out, projected return January 22, 2014). No reserve-list move has been made; that is Caldwell's decision, and 2013 injured-reserve rules are not yet sourced in the library. Ball's starting spot is Stone's decision for Week 11.

**Statistics, standings and awards.** One full receipt and thirteen compact receipts were kept, 147 of 147 in total. The box score, standings and statbook were regenerated, and the six Week 10 league awards were drawn by the registered method.

**Engine notes (the result stands).** Kernel 2013.7 ties call labels to the ball carrier but not to personnel groups, so a 13-personnel Cross was completed to Clemons.

**Overtime defect (investigated; the result stands).** Washington at Minnesota went to overtime. Kernel 2013.7 drew the whole period as one half-final possession, and Minnesota's opening drive (six plays, 77 yards, recorded as running 15:00 to 0:00) ended the game with a 20-yard field goal. Under the 2013 regular-season overtime rule, a field goal on the opening possession gives the other club a possession. Kernel 2013.6 tracked overtime possessions (`ot_status`); the 2013.7 overtime path drew one possession for the whole period.

This is an engine defect. It is fixed going forward, and no game is rerun. Until it is fixed, any overtime game is recorded with this note.

**Primary records:** `regular_season/week_10_jacksonville_at_tennessee/output.md` and `call_sheet.json`; `league_results/week_10.md`; `stats/game_receipts/week_10_*.json`; `awards/`; `standings.md`; `depth_chart.json`.
**Next competitive event:** November 17 Week 11 vs Arizona, 1 p.m. ET. **Not simulated.**

**Commit closed - Canonical update - November 10, 2013 - Week 10 at Tennessee closed - canonical through November 10, after Week 10**

## Entry 51: Kernel 2013.8 adopted (2013 overtime rules)

**Effective canonical state:** November 10, 2013, after Week 10
**Recorded:** September 28, 2026
**Checkpoint:** `Canonical update - November 10, 2013 - Kernel 2013.8 adopted (2013 overtime rules)`
**Preceding global package checkpoint:** `Canonical update - November 10, 2013 - Week 10 at Tennessee closed`

**Decision.** At the user's instruction, which was to fix the defect and follow the football rules of the era, kernel 2013.8 replaces 2013.7 for every slate from Week 11.

**Rules source.** `library/2013_nfl_playing_rules_for_simulation.md` sources the 2013 rules the engine uses, each checked by a separate verification pass, and records the engine audit against them.

**Fixed in 2013.8:**
- **Regular-season overtime.** One 15-minute period on a real clock, with possessions alternating. The period follows the 2013 modified sudden-death rule: an opening-possession touchdown or a safety ends it; an opening field goal gives the other club a possession; after that it is sudden death; and the game is a tie if the period expires level.
- **Postseason overtime.** Periods are continuous, a possession carries across a period break, and the game never ends tied.
- **Replay.** The booth has review authority throughout overtime.
- **Game-day actives.** The 46-active limit is enforced in the production packet.

**Unchanged.** Regulation play is identical to 2013.7, and no calibrated centre, pool, coefficient or tolerance changed. A 250-game sample shows every aggregate row WITHIN, zero coherence violations and the same three known detections. Its 21 overtime games all followed the rule.

**Listed, not yet modelled:**
- two-point tries;
- onside kicks;
- defensive and return touchdowns;
- snap-by-snap timeouts;
- the neutral-site home term (Entry 45).

**Closed results stand.** The Week 10 Washington at Minnesota overtime result stands as closed 2013.7 canon and is not rerun. That choice does not depend on which club won. Weeks 9-10 remain the 2013.7 audit cohort.

**Commit closed - Canonical update - November 10, 2013 - Kernel 2013.8 adopted (2013 overtime rules) - canonical through November 10, after Week 10**

## Entry 52: Week 11 vs Arizona closed

**Effective canonical state:** November 17, 2013, after Week 11
**Recorded:** September 28, 2026
**Checkpoint:** `Canonical update - November 17, 2013 - Week 11 vs Arizona closed`
**Preceding global package checkpoint:** `Canonical update - November 10, 2013 - Kernel 2013.8 adopted (2013 overtime rules)`

**Result.** Jacksonville 29, Arizona 7 at EverBank Field. Jacksonville is 7-3, first in the AFC South a game ahead of 6-4 Tennessee, and the AFC's top seed, ahead of the 7-3 Jets on conference record.

**Batch.** All fifteen Week 11 games closed once each under kernel 2013.8, the first slate on it. They were drawn from the package frozen by `build_week_inputs.py 11` (sha256 `b8f8e957...`); the call sheet and depth chart were committed before the draw (7ca9cda).

**Inputs.**
- **Call sheet:** Stone's fifteen calls.
- **Secondary:** Mike Harris started outside for the injured Ball; Poyer stayed at nickel, with Bouye the first outside reserve.
- **Dressed:** Mosley and Rutland.
- **Inactives:** Ball, C.J. Wilson, Edwards, Pendleton, Asper, John Parker Wilson, Mike Brown.

**2014 scouting focus.** Stone's coaching-focus directive for the 2014 draft is recorded as a plan in `scouting/2014_draft_focus_directive.md`. Caldwell retains authority, the no-hindsight rule applies, and the list changes no prospect's grade or availability.

**Game.**
- Jacksonville ran for 267 yards: Jones-Drew 25 carries for 191 and a touchdown, Grimes 62 and a touchdown.
- Cousins completed 19 of 24 with no turnover.
- The defense took three interceptions (Daryl Smith, Russell Allen, Poyer) and had four sacks (Alualu two, Harris, Lowery).
- Scobee made five of six field goals.

**Availability.** A.J. Bouye was hurt (lower extremity, short; out, projected return November 26).

**Statistics, standings and awards.** One full receipt and fourteen compact receipts were kept, 162 of 162 in total. In the new 2013.8 cohort (30 team-games), third-down rate is OUTSIDE its band: 0.445 against 0.383 ±0.060. Investigated as a possible defect, none was found. The 2013.8 change touched only overtime, the 46-active limit and overtime booth review; no regulation third-down code changed. Weeks 4-10 ran from 0.350 to 0.408, and 0.445 on 393 attempts is within three standard errors (±0.074) of the centre, so this reads as one-week variance. No centre, tolerance or coefficient was changed and no game was rerun; the row stays graded as the cohort grows. The Week 11 awards were drawn; Jones-Drew and Scobee were shortlisted but not drawn.

**Primary records:** `regular_season/week_11_arizona_at_jacksonville/output.md` and `call_sheet.json`; `league_results/week_11.md`; `stats/game_receipts/week_11_*.json`; `awards/`; `scouting/2014_draft_focus_directive.md`; `standings.md`; `depth_chart.json`.
**Next competitive event:** November 24 Week 12 at Houston, 1 p.m. ET. **Not simulated.**

**Commit closed - Canonical update - November 17, 2013 - Week 11 vs Arizona closed - canonical through November 17, after Week 11**

## Entry 53: Week 12 at Houston closed

**Effective canonical state:** November 24, 2013, after Week 12
**Recorded:** September 28, 2026
**Checkpoint:** `Canonical update - November 24, 2013 - Week 12 at Houston closed`
**Preceding global package checkpoint:** `Canonical update - November 17, 2013 - Week 11 vs Arizona closed`

**Result.** Houston 38, Jacksonville 6 at Reliant Stadium. Jacksonville is 7-4, first in the AFC South a game ahead of 6-5 Tennessee, and the AFC's third seed behind the 8-3 Jets and 7-4 Pittsburgh.

**Batch.** All fourteen Week 12 games closed once each under kernel 2013.8, drawn from the package frozen by `build_week_inputs.py 12` (sha256 `ee191707...`) after the gate passed. The call sheet, depth chart and scouting Phase II plan were committed before the draw (204f119).

**Inputs.**
- **Call sheet:** Stone's fifteen calls.
- **Secondary:** Grimes and Harris outside, Poyer at nickel, Rutland first outside reserve.
- **Dressed:** Edwards, Mosley and Rutland.
- **Inactives:** Ball, Bouye, C.J. Wilson, Pendleton, Asper, John Parker Wilson, Mike Brown.

**Game.**
- Scoring: Scobee kicked field goals of 49 and 33. Jacksonville reached the Houston 24 or closer four times and scored no touchdown (a field goal, two turnovers on downs, an interception).
- Cousins completed 25 of 42 for 176 yards with two interceptions (Reed, Joseph) and was sacked three times (Watt two, Mays).
- Jones-Drew ran 12 times for 86 yards.
- Houston: Foster ran 29 times for 133 yards and a touchdown; Andre Johnson caught 8 for 134 and three touchdowns; Schaub threw four touchdowns.
- Grimes intercepted Schaub.
- Stone entered no game-management decision; both fourth-down attempts came from the engine's 2012 resolution.

**Availability.** No injury for either team. Bouye's projected return (November 26) falls before Week 13; his status needs fresh medical communication.

**Rematch notes.** Tice, Crennel and Lowry recorded Stone's four questions after the game, from the receipt only. They are closed and are not a Week 14 plan (`houston_rematch_notes.md`).

**Scouting Phase II.** The role-validation directive and interim-card format are recorded as a plan (`scouting/2014_draft/phase_ii_role_validation.md`). No interim card was written: the card's tape fields need a dated, sourced record of what was knowable by November 22, 2013, and the repository holds none yet. No card content, grade or eligibility fact was invented, and every prospect file still reads not started.

**Statistics, standings and awards.**
- **Receipts:** one full receipt and thirteen compact receipts were kept, 176 of 176 in total.
- **Calibration audit:** every graded 2013.8 row is WITHIN, including the third-down rate that was OUTSIDE after Week 11 (now 0.421 over 58 team-games). Every ledger-coherence count is zero.
- **Awards:** Week 12 and November awards were drawn; no Jacksonville player was shortlisted.

**Engine notes.**
- **Spike after a fair catch:** Houston's first snap after Jacksonville's fair-caught punt at 2:01 of the second quarter was a spike, although the clock was already stopped. `play_detail._layout` shuffles a drive's 2012 spikes into any slot, so a spike can land on the first snap of a possession. This changes play order only: the drive's totals, terminal and the result are fixed by the kernel. It is the only such spike in any full receipt. It is recorded for a forward fix and was not corrected here, since that would change the kernel.
- **0-yard punt:** Anger's 0-yard punt from the Houston 49, downed at the line, is a real 2012 pool record (LOS 49, downed, gross 0) drawn as-is; it is not a defect.
- **Clock-expired drive:** Houston's first-half drive to the Jacksonville 30 that ran out of time is the registered clock-expired known detection.

**Primary records:** `regular_season/week_12_jacksonville_at_houston/output.md`, `call_sheet.json` and `houston_rematch_notes.md`; `league_results/week_12.md`; `stats/game_receipts/week_12_*.json`; `awards/`; `scouting/2014_draft/phase_ii_role_validation.md`; `standings.md`; `depth_chart.json`.
**Next competitive event:** December 1 Week 13 at Cleveland, 1 p.m. ET. **Not simulated.**

**Commit closed - Canonical update - November 24, 2013 - Week 12 at Houston closed - canonical through November 24, after Week 12**

## Entry 54: Kernel 2013.9 adopted (spike seating)

**Effective canonical state:** November 24, 2013, after Week 12
**Recorded:** September 28, 2026
**Checkpoint:** `Canonical update - November 24, 2013 - Kernel 2013.9 adopted (spike seating)`
**Preceding global package checkpoint:** `Canonical update - November 24, 2013 - Week 12 at Houston closed`

**Decision.** At the user's instruction ("fix the spike bug"), kernel 2013.9 replaces 2013.8 for every slate from Week 13.

**Defect.** Every possession starts on a stopped clock (a change of possession is an administrative stoppage, rules library R14), and an incompletion stops the clock too. The play-order layout nevertheless placed a drive's real 2012 spikes in any slot, so a spike could open a drive or follow an incompletion (Entry 53). On the 250-game synthetic sample, 40 of 87 spikes were misplaced. Background receipts keep no snap order, which is why only one surfaced in canon.

**Fix.** `play_detail._seat_spikes` moves each misplaced spike to just after the nearest run, sack or completion. The change touches snap order only. It consumes no randomness, and scores, drive summaries, statistics and attributions are identical to 2013.8 across all 250 sample games. After the fix, 0 of 87 spikes are misplaced. Sources and tests: `library/2013_nfl_playing_rules_for_simulation.md` (R13/R14 spikes row), `runtime/README.md`, `tests/test_spike_seating.py`.

**Closed results stand.** Weeks 11-12 remain the 2013.8 audit cohort, and the Week 12 spike stays as closed. Nothing is rerun.

**Commit closed - Canonical update - November 24, 2013 - Kernel 2013.9 adopted (spike seating) - canonical through November 24, after Week 12**

## Entry 55: Week 13 at Cleveland closed

**Effective canonical state:** December 1, 2013, after Week 13
**Recorded:** September 28, 2026
**Checkpoint:** `Canonical update - December 1, 2013 - Week 13 at Cleveland closed`
**Preceding global package checkpoint:** `Canonical update - November 24, 2013 - Kernel 2013.9 adopted (spike seating)`

**Result.** Jacksonville 22, Cleveland 19, in overtime, at FirstEnergy Stadium. Regulation ended 19-19. Cleveland received in overtime and punted. Under the modified sudden-death rule the next score won, and Scobee kicked a 34-yard field goal. Jacksonville is 8-4, first in the AFC South a game ahead of 7-5 Tennessee, and the AFC's second seed behind 8-4 Pittsburgh.

**Batch.** All sixteen Week 13 games closed once each under kernel 2013.9, the first slate on it. They were drawn from the package frozen by `build_week_inputs.py 13` (sha256 `2ab521a8...`) after the gate passed; the call sheet, depth chart and scouting Phase III plan were committed before the draw (d12e431). Four games went to overtime; Cincinnati and San Diego tied 30-30 when the period expired.

**Inputs.**
- **Call sheet:** Stone's fifteen calls, including the new 22-personnel Power and Snag.
- **Bouye:** cleared at his projected return (November 26) under the rule every club gets, and dressed as first outside reserve.
- **Inactives:** Ball, C.J. Wilson, Pendleton, Edwards, Asper, John Parker Wilson, Mike Brown.

**Game.**
- **Run and pass:** 28 runs against 36 dropbacks. Jones-Drew 16 carries for 93 yards and 3 catches for 40.
- **Passing:** Cousins 20 of 34 for 328 yards, two touchdowns (Shorts 37, Clemons 43) and two interceptions, both by Haden (the second at the Cleveland 28 with 20 seconds left). Lewis caught 7 for 110.
- **Defense:** Lowery had an interception, 10 tackles and a 40-yard overtime punt return; Allen had a sack. Richardson ran 25 times for 129 yards; Cameron caught 1 of 3 targets.
- **Kicking:** Scobee made 3 of 4 field goals and missed an extra point. Cundiff made 4 of 4.
- **Game management:** Stone entered no game-management decision.

**Availability.**
- **Posluszny:** head/neck, independent medical hold, long-term, projected return April 5, 2014, so he is out for the regular season. No reserve-list move has been made; that is Caldwell's transaction.
- **Kelce:** minor, out two days, projected return December 3.
- **Ball:** remains out.

**Scouting Phase III.** Each focus prospect file has a verification entry dated November 30, 2013, using only information public by that date:
- identity, school and class;
- eligibility;
- dated sources;
- unresolved items;
- the requested cut-up;
- a prepared coaching window.

Turner is an underclassman and is not in the 2014 pool until a dated declaration. Harris's status is unresolved (dismissed from Illinois State before 2013; no dated fall-2013 source). Every football first-entry question is OPEN, because no dated tape evidence is recorded; nothing was projected to fill it. There is no tier, no round movement and no recommendation.

**2014 draft library.** `library/2014_draft_information_gates.md` and `library/2014_draft_pool_registry.md` were built in two passes: research, then a separate skeptical verification.
- **Source limit:** both passes relied on search-result text, because page fetches are blocked by the environment's network policy. Each file says so.
- **Corrections:** Harris's college path (Wisconsin 2009, then Illinois State); Turner's declaration date (January 13, 2014, gated) and the January 19, 2014 special-eligibility list; the combine invitation gate (February 6, 2014); Butler's Alcorn State detail.
- **Hindsight:** two hindsight items found in the first pass were removed.
- **Branch-resolved:** draft order, traded picks and compensatory picks.
- **Coverage:** full-class coverage is not built.

**Audit correction.** The band audit's yards row compared gross passing yards plus rushing against the 2012 centre of 347.2, which is net of sack yards (118,418 + 59,349 over 512 team-games). `bands.py` now subtracts each passer's sack yards, which lowers every cohort's row by about 14 yards per team-game. Before the correction, the 2013.9 cohort read 393.5 (OUTSIDE); it now reads 376.9 (WITHIN). The synthetic sample sits at the same level, so no engine defect is indicated. No centre, tolerance or result changed, and every graded row is WITHIN.

**Label limitation (recorded, not changed).** Call labels are chosen after each snap from the call's family and position group; personnel is not checked. Three Week 13 completions carry 22-personnel labels though the receiver (Clemons, Blackmon twice) is not in Stone's 22 package. Across the full receipts of Weeks 10-13 this happened on 7 of 135 labelled passes. Labels only; no result depends on them.

**Statistics and awards.** One full receipt and fifteen compact receipts were kept, 192 of 192 in total. Week 13 awards were drawn; no Jacksonville player was shortlisted.

**Primary records:** `regular_season/week_13_jacksonville_at_cleveland/output.md` and `call_sheet.json`; `league_results/week_13.md`; `stats/game_receipts/week_13_*.json`; `awards/`; `scouting/2014_draft/`; `library/2014_draft_information_gates.md`; `library/2014_draft_pool_registry.md`; `standings.md`; `depth_chart.json`.
**Next competitive event:** Thursday, December 5, Week 14 vs Houston, 8:25 p.m. ET. **Not simulated.**

**Commit closed - Canonical update - December 1, 2013 - Week 13 at Cleveland closed - canonical through December 1, after Week 13**

## Entry 56: Kernel 2013.10 adopted (personnel-true labels)

**Effective canonical state:** December 1, 2013, after Week 13
**Recorded:** September 28, 2026
**Checkpoint:** `Canonical update - December 1, 2013 - Kernel 2013.10 adopted (personnel-true labels)`
**Preceding global package checkpoint:** `Canonical update - December 1, 2013 - Week 13 at Cleveland closed`

**Decision.** At the user's instruction ("fix the label bug before week 14"), kernel 2013.10 replaces 2013.9 for every slate from Week 14.

**Defect (Entry 55).** Call labels ignored personnel, so a receiver who is not in a package could carry that package's label (Week 13: the WR4's touchdown labelled 22 Heavy Snag).

**Fix.** A snap's label must come from a call whose personnel could include the player who made it:
- his position group needs a slot;
- his depth rank may be at most one past the slot count (one rotation spot, matching the weekly plans' "Thielen / Blackmon" and "MJD / Grimes");
- a fullback needs two backs;
- quarterbacks and 6OL codes always fit.

A snap no call fits carries the generic label. Source and tests: `runtime/README.md`, `tests/test_personnel_labels.py`.

**Evidence.** Labels only. Scores, drives and every player statistic are identical to 2013.9 across the 250-game sample. On that sample 10% of labels changed and 2.1% became generic, against 0.02% before.

**Closed results stand.** Closed receipts keep their labels; nothing is rerun.

**Commit closed - Canonical update - December 1, 2013 - Kernel 2013.10 adopted (personnel-true labels) - canonical through December 1, after Week 13**

## Entry 57: Week 14 vs Houston closed (generation 2, after a technical void)

**Effective canonical state:** December 5, 2013, after Week 14
**Recorded:** September 28, 2026
**Checkpoint:** `Canonical update - December 5, 2013 - Week 14 vs Houston closed`
**Preceding global package checkpoint:** `Canonical update - December 1, 2013 - Kernel 2013.10 adopted (personnel-true labels)`

**Result.** Jacksonville 21, Houston 20, Thursday night at EverBank Field. Jacksonville is 9-4, first in the AFC South a game ahead of 8-5 Tennessee, and the AFC's top seed ahead of the 9-4 Jets.

**Generation-1 void.** The first Week 14 build left A.J. Bouye unavailable, so Jacksonville's unit had 45 players, not the 46 in Stone's plan.
- **Cause:** his roster note read "No communicated restriction (Week 11 injury cleared November 26)", and `roster_available` matched only the exact phrase.
- **How it closed:** the build and the close were chained, so all sixteen generation-1 events closed before the unit was inspected.
- **Blind decision:** no generation-1 receipt, score or view was opened. The user was offered void-and-replay or keep, with no result known, and chose to void.
- **Void:** the whole slate was voided. The generation-1 artifacts were deleted unread, and the sixteen events were recorded as corrections in the private journal (`scripts/void_week_generation.py`).
- **Fixes:** the availability rule now accepts an explained clear note and fails the build on any unclassifiable note. A new gate fails when Jacksonville would dress fewer than 46 while healthy players sit inactive.
- **Replacement:** the package (sha256 `1b206955...`) differs from generation 1 only in Bouye (45 to 46 actives). It was committed before the draw (1910d9d, 250a5c2).
- **Record:** `migrations/week_14_generation_void.md` and `migrations/event_generations.json`.

**Batch.** All sixteen generation-2 events (`...-g2`) closed once each under kernel 2013.10, the first slate on it.

**Inputs.**
- **Call sheet:** Stone's fifteen calls, with no new family.
- **Linebackers:** Daryl Smith base linebacker and communication lead; Russell Allen started beside him for Posluszny.
- **Kelce:** cleared at his projected return (December 3) and dressed.
- **Inactives:** Posluszny, Ball, C.J. Wilson, Pendleton, Asper, John Parker Wilson, Mike Brown.

**Game.**
- **Run and pass:** 25 runs against 27 dropbacks; third down 8 of 12.
- **Passing:** Cousins 15 of 24 for 226 yards, two touchdowns (Jones-Drew 17, Shorts 36 with 3:34 left) and no interception.
- **Rushing:** Jones-Drew 13 carries for 89 yards and a touchdown.
- **Turnover:** Grimes lost a fumble at the Houston 18.
- **Defense:** Daryl Smith forced and recovered Andre Johnson's fumble at the Jacksonville 39 with 1:56 left; Babin had two sacks; Foster ran 17 times for 40.
- **Game management:** Stone entered no game-management decision.

**Availability.** No injury for either team. Posluszny out (projected April 5, 2014); Ball out.

**Statistics, standings and awards.** One full receipt and fifteen compact receipts were kept, 208 of 208 in total. Week 14 awards were drawn; no Jacksonville player was shortlisted.

**Audit.** The first 2013.10 cohort (Week 14, 32 team-games) reads OUTSIDE on net yards per team game: 394.2 against 347.2 ±40.
- **Not caused by 2013.10:** it changes labels only, and results were identical on the 250-game sample.
- **Engine level:** on that sample the kernel's own net level is 369.6, with a standard deviation of 86.5 per team-game. At that level a single 32-team-game week reads above 387.2 about 12% of the time.
- **Reading:** one-week variance on top of a standing level about 22 yards above the 2012 centre. That level is inside tolerance and is listed here for future calibration.
- **Unchanged:** nothing was tuned or rerun, and every other graded row is WITHIN.

**Primary records:** `regular_season/week_14_houston_at_jacksonville/output.md` and `call_sheet.json`; `league_results/week_14.md`; `stats/game_receipts/week_14_*.json`; `migrations/week_14_generation_void.md`; `awards/`; `standings.md`; `depth_chart.json`.
**Next competitive event:** December 15 Week 15 vs Buffalo, 1 p.m. ET. **Not simulated.**

**Commit closed - Canonical update - December 5, 2013 - Week 14 vs Houston closed - canonical through December 5, after Week 14**

## Entry 58: Week 15 vs Buffalo closed

**Effective canonical state:** December 15, 2013, after Week 15
**Recorded:** September 28, 2026
**Checkpoint:** `Canonical update - December 15, 2013 - Week 15 vs Buffalo closed`
**Preceding global package checkpoint:** `Canonical update - December 5, 2013 - Week 14 vs Houston closed`

**Result.** Buffalo 45, Jacksonville 16 at EverBank Field. Jacksonville is 9-5 and second in the AFC South: Tennessee is also 9-5 and holds the head-to-head tiebreaker (Week 10). Jacksonville is the AFC's fifth seed, a wild card.

**Batch.** All sixteen Week 15 games closed once each under kernel 2013.10. They were drawn from the package frozen by `build_week_inputs.py 15` (sha256 `6f41f90b...`) after the gate passed; Jacksonville's unit was inspected before the close (46 dressed; Wilson, Posluszny and Ball unavailable). The call sheet, depth chart and scouting Phase IV plan were committed before the draw (2c38fa5).

**Inputs.**
- **Call sheet:** Stone's fifteen calls, with Outside Zone and RB Slow Screen on the sheet.
- **Linebackers:** Smith and Allen base, Stanford first base reserve, Moore in packages.
- **Inactives:** unchanged from Week 14.

**Game.**
- **Buffalo:** ran 33 times for 237 yards. Spiller had 24 carries for 147 and two touchdowns plus a touchdown catch; Manuel threw four touchdowns without an interception.
- **Turnovers:** Jacksonville lost four. Anderson's fumble (forced and recovered by Lawson at the Jacksonville 12) and interceptions by McKelvin and Rogers each led directly to a Buffalo touchdown; Searcy also intercepted.
- **Jacksonville offense:** Cousins 23 of 36 for 242 yards, a touchdown and three interceptions; Jones-Drew 134 yards from scrimmage and a touchdown.
- **Kicking:** Scobee 3 of 3.
- **Game management:** Stone entered no game-management decision.

**Availability.** No Jacksonville injury. Posluszny out (projected April 5, 2014); Ball out.

**Scouting Phase IV.** The plan is recorded (`scouting/2014_draft/phase_iv_first_coach_reads.md`). No coach read was entered as a conclusion: the repository holds no dated football evidence for any focus prospect, so each question stays OPEN (Harris: no conclusion by directive; Turner: not in the pool). The prospect files carry a December 13 entry saying so. Nothing was invented.

**Statistics, standings and awards.** One full receipt and fifteen compact receipts were kept, 224 of 224 in total. Every graded audit row is WITHIN (2013.10 cohort, 64 team-games). Week 15 awards were drawn; no Jacksonville player was shortlisted.

**Primary records:** `regular_season/week_15_buffalo_at_jacksonville/output.md` and `call_sheet.json`; `league_results/week_15.md`; `stats/game_receipts/week_15_*.json`; `awards/`; `scouting/2014_draft/`; `standings.md`; `depth_chart.json`.
**Next competitive event:** December 22 Week 16 vs Tennessee, 1 p.m. ET. **Not simulated.**

**Commit closed - Canonical update - December 15, 2013 - Week 15 vs Buffalo closed - canonical through December 15, after Week 15**

## Entry 59: Week 16 vs Tennessee closed

**Effective canonical state:** December 22, 2013, after Week 16
**Recorded:** September 28, 2026
**Checkpoint:** `Canonical update - December 22, 2013 - Week 16 vs Tennessee closed`
**Preceding global package checkpoint:** `Canonical update - December 15, 2013 - Week 15 vs Buffalo closed`

**Result.** Jacksonville 38, Tennessee 27 at EverBank Field. Jacksonville is 10-5 and first in the AFC South, a game ahead of 9-6 Tennessee; the season series is 1-1, and a Week 17 win clinches the division. Jacksonville is the AFC's second seed behind the 11-4 Jets.

**Batch.** All sixteen Week 16 games closed once each under kernel 2013.10. They were drawn from the package frozen by `build_week_inputs.py 16` (sha256 `dc859452...`) after the gate passed; Jacksonville's unit was inspected before the close (46 dressed; Wilson, Posluszny and Ball unavailable). The call sheet and depth chart were committed before the draw (fce62df).

**Inputs.**
- **Call sheet:** Stone's fifteen calls, with no new family and Wham on the sheet.
- **Lineup and inactives:** unchanged.
- **Scouting:** the plan's scouting section is handled outside this record at the user's direction.

**Game.**
- **Jacksonville offense:** no turnover.
  - Cousins: 16 of 32 for 356 yards and three touchdowns, no interception.
  - Rushing: 36 runs against 34 dropbacks. Jones-Drew 25 carries for 93 and a touchdown; Grimes 79 yards from scrimmage and a touchdown on Wham.
  - Third quarter: three touchdowns.
- **Tennessee:** ran 20 times for 77 yards. Locker threw for 432 yards and three touchdowns; Britt caught 15 of 24 targets for 187.
- **Defense:** Lowery intercepted Locker; Tennessee's final drive was stopped on downs at the Jacksonville 1 with 44 seconds left.
- **Game management:** Stone entered no game-management decision.

**Availability.** No injury for either team. Posluszny out (projected April 5, 2014); Ball out.

**Statistics, standings and awards.** One full receipt and fifteen compact receipts were kept, 240 of 240 in total. Every graded audit row is WITHIN. Week 16 awards were drawn; no Jacksonville player was shortlisted.

**Engine defect recorded (not fixed here).**
- **Symptom:** a published fourth-down state can show more yards to go than yards to the goal line. Tennessee's final drive reads "4th & 7 at opp 1".
- **Cause:** the kernel carries the real 2012 drive's down and distance with the simulated spot, and nothing caps the distance at goal-to-go.
- **Extent:** three records across all receipts (Week 11 Minnesota at Seattle, Week 13 St. Louis at San Francisco, Week 16 here). The ledger coherence check does not test for it.
- **Impact:** the drive's result, its end spot and every statistic come from their own records, so no score or result depends on the published down and distance.
- **Fix:** capping the distance at goal-to-go and adding a coherence class needs a kernel change, so it is recorded and not made here.

**Primary records:** `regular_season/week_16_tennessee_at_jacksonville/output.md` and `call_sheet.json`; `league_results/week_16.md`; `stats/game_receipts/week_16_*.json`; `awards/`; `standings.md`; `depth_chart.json`.
**Next competitive event:** December 29 Week 17 at Indianapolis, 1 p.m. ET. **Not simulated.**

**Commit closed - Canonical update - December 22, 2013 - Week 16 vs Tennessee closed - canonical through December 22, after Week 16**

## Entry 60: Week 17 at Indianapolis closed; regular season complete

**Effective canonical state:** December 29, 2013, after Week 17
**Recorded:** September 28, 2026
**Checkpoint:** `Canonical update - December 29, 2013 - Week 17 at Indianapolis closed`
**Preceding global package checkpoint:** `Canonical update - December 22, 2013 - Week 16 vs Tennessee closed`

**Result.** Indianapolis 23, Jacksonville 22 at Lucas Oil Stadium. Jacksonville finishes the regular season 10-6. Tennessee beat Houston 27-21 to finish 10-6, and with the season series split 1-1 it wins the AFC South on division record (4-2 against 3-3). Jacksonville is the AFC's fifth seed, a wild card, and plays at fourth-seeded Kansas City (9-7) on Wild Card weekend, January 4-5, 2014.

**Batch.** All sixteen Week 17 games closed once each under kernel 2013.10. They were drawn from the package frozen by `build_week_inputs.py 17` (sha256 `cb72c870...`) after the gate passed; Jacksonville's unit was inspected before the close (46 dressed; Wilson, Posluszny and Ball unavailable). Indianapolis's Vick Ballard cleared his one-day Week 16 hold under the rule every club gets. The call sheet and depth chart were committed before the draw (69d9e2a).

**Inputs.**
- **Call sheet:** Stone's fifteen calls, with Draw in 20 personnel and no new family.
- **Lineup:** no starter rested; inactives unchanged.
- **Scouting:** the plan's scouting section is handled outside this record at the user's direction.

**Game.**
- **Jacksonville offense:** no turnover.
  - Ball control: 32 runs and 38 dropbacks; held the ball 36:35.
  - Scoring: one touchdown (Grimes, 6 yards) and five Scobee field goals (45, 26, 31, 28, 27).
  - Cousins: 24 of 35 for 278 yards, no interception, three sacks.
- **Defense:** Marks strip-sacked Luck at the Colts 8. Indianapolis ran 19 times for 49 yards. Luck completed 28 of 38 for 308 yards and two touchdowns, both to Wayne (11 catches for 114).
- **The finish:** Jacksonville led 22-16 with the ball at its 20 and 22 seconds left. It ran three times and punted from its 26 with 3 seconds left. Hilton returned the punt 26 yards to the Jacksonville 43, Luck hit Allen for 36 and Wayne for a 7-yard touchdown on the final snap, and the extra point won it.
- **Game management:** Stone entered no game-management decision.

**Engine limitation (listed since Entry 51; recorded here, not fixed).**
- **Mechanism:** timeouts and kneel-downs are not simulated snap by snap. A late possession replays a real 2012 drive from the same score-and-time cell (leading by 1-8 with 120 seconds or fewer), and that cell includes real drives that ended in punts because the trailing team still held timeouts.
- **Why it matters:** the engine cannot tell whether a kneel-out was available, so the Jacksonville possession's clock management and the punt it produced may not reflect what a 2013 club would have done.
- **Consequence:** it decided a division title.
- **Decision:** the result stands as closed. A closed result is never rerun, and the decision cannot depend on which club it favoured. The user has deferred engine fixes; this item is listed with the fourth-down display defect (Entry 59) for that work.

**Availability.** No injury for either team. Posluszny out (projected April 5, 2014); Ball out.

**Statistics, standings and awards.**
- **Receipts:** one full receipt and fifteen compact receipts were kept, 256 of 256 in total, and the regular season is complete. Every graded audit row is WITHIN.
- **Awards:** Week 17 and December awards were drawn. Scobee was shortlisted for Week 17 special teams and not drawn.
- **Final seeds:**
  - AFC: Jets, Tennessee, Pittsburgh, Kansas City, Jacksonville, Buffalo.
  - NFC: Minnesota, St. Louis, New Orleans, Philadelphia, Tampa Bay, Dallas.

**Postseason prerequisite.** The weekly pipeline reads only the regular-season schedule. Before any Wild Card draw, a postseason slate must be built from the final seeds, with `postseason` game type and continuous overtime. The branch pairings are not the real 2013 pairings, so their date slots cannot be imported and need a stated, result-blind rule.

**Primary records:** `regular_season/week_17_jacksonville_at_indianapolis/output.md` and `call_sheet.json`; `league_results/week_17.md`; `stats/game_receipts/week_17_*.json`; `awards/`; `standings.md`; `depth_chart.json`.
**Next competitive event:** AFC Wild Card at Kansas City, January 4-5, 2014. **Not simulated.**

**Commit closed - Canonical update - December 29, 2013 - Week 17 at Indianapolis closed - canonical through December 29, after Week 17**

## Entry 61: Postseason bracket built; Wild Card slate set

**Effective canonical state:** December 29, 2013, after Week 17
**Recorded:** September 28, 2026
**Checkpoint:** `Canonical update - December 29, 2013 - Postseason bracket built (Wild Card slate set)`
**Preceding global package checkpoint:** `Canonical update - December 29, 2013 - Week 17 at Indianapolis closed`

**Decision.** At the user's instruction ("build for wildcard and for each round of the playoff - you decide realistic to 2013"), the pipeline now builds and closes all four postseason rounds under the 2013 format. No kernel change: the postseason runs on kernel 2013.10.

**Format.** Sourced in `library/2013_postseason_format_and_schedule.md` (two-pass; no real postseason result recorded; two source URL slugs that named real Super Bowl participants are withheld).
- Six clubs per conference; division winners seeded 1-4, wild cards 5-6; seeds 1-2 have byes.
- Wild Card: 3 hosts 6, 4 hosts 5.
- Divisional: reseeded, with the 1 seed hosting the lowest survivor.
- Conference: the higher seed hosts.
- Super Bowl XLVIII: MetLife Stadium, with the AFC champion as designated home team.
- Overtime: 15-minute periods until a winner (kernel 2013.8 onward).
- Game-day actives: 46.
- Weekly awards: none in the postseason.

**Slot rule, fixed before any postseason draw.** Each branch game takes the real 2013-14 date, kickoff and network of the slot with the same conference and seed matchup (`library/data/2013_postseason_slots.json`). The rule never looks at a result.

**Pipeline.**
- Rounds are weeks 18-21 (`runtime/postseason.py`).
- `build_week_inputs.py` and `close_week.py` run them like regular-season weeks.
- Receipts go to `career/2013/stats/postseason_receipts/`, so standings, the regular-season statbook, awards and the audit are unchanged.
- The bracket page is `career/2013/postseason/README.md`.
- Tests: `tests/test_postseason.py`. A trial package build for week 18 passed the four-game exclusivity gate and was discarded before any draw.

**Wild Card slate (week 18):**

| Date and kickoff (ET) | Round | Game | Network |
|---|---|---|---|
| Sat. Jan. 4, 4:35 p.m. | AFC 5 at 4 | Jacksonville at Kansas City | NBC |
| Sat. Jan. 4, 8:10 p.m. | NFC 6 at 3 | Dallas at New Orleans | NBC |
| Sun. Jan. 5, 1:05 p.m. | AFC 6 at 3 | Buffalo at Pittsburgh | CBS |
| Sun. Jan. 5, 4:40 p.m. | NFC 5 at 4 | Tampa Bay at Philadelphia | FOX |

The Jets, Tennessee, Minnesota and St. Louis have byes.

**Known limit carried.** The neutral-site home term (Entry 45) would give the AFC champion the kernel's small home term in the Super Bowl. The fourth-down display defect and the timeout/kneel limitation also remain open; the user has deferred both.

**No game was simulated.**

**Commit closed - Canonical update - December 29, 2013 - Postseason bracket built (Wild Card slate set) - canonical through December 29, after Week 17**

## Entry 62: AFC Wild Card at Kansas City closed

**Effective canonical state:** January 4-5, 2014, after the Wild Card round
**Recorded:** September 28, 2026
**Checkpoint:** `Canonical update - January 5, 2014 - AFC Wild Card at Kansas City closed`
**Preceding global package checkpoint:** `Canonical update - December 29, 2013 - Postseason bracket built (Wild Card slate set)`

**Result.** Jacksonville 38, Kansas City 14 at Arrowhead Stadium (Sat. January 4, 4:35 p.m. ET, NBC). Jacksonville (AFC 5) advances to the Divisional round at Tennessee (AFC 2), Sat. January 11, 8:15 p.m. ET, CBS. Stone's NFL postseason head-coaching record is 2-1.

**Batch.** The four Wild Card games (postseason week 18) closed once each under kernel 2013.10 as `postseason` games. They were drawn from the package frozen by `build_week_inputs.py 18` (sha256 `69ff1ada...`) after the four-game exclusivity gate passed. Jacksonville's unit was inspected before the close: 46 dressed, with exactly Stone's seven inactives. The call sheet and depth chart were committed before the draw. Receipts are in `career/2013/stats/postseason_receipts/` (Jacksonville full, others compact_stats). Standings, the regular-season statbook and the calibration audit are unchanged. No postseason awards are drawn (Entry 61).

**Inputs.**
- **Call sheet:** Stone's fifteen calls, 12 personnel base, no new family, Boot Flood off.
- **Lineup:** no reshuffle; the established seven inactives.
- **Scouting:** position-coach draft work frozen for the postseason by Stone. The plan's scouting section is otherwise handled outside this record at the user's direction.

**Game.**
- **Jacksonville offense:** 504 yards (179 rushing, 325 passing), 7 of 13 on third down, one sack allowed, one turnover.
  - Scoring: five touchdowns in the first 33 minutes. Jones-Drew ran 33 on Split; Lewis caught 13 on Texas and 32 on Sprint Flood; Shorts ran 4; Shorts caught 12 on the Power Pass Post-Cross. Scobee added a 22-yard field goal.
  - Cousins: 20 of 30 for 325 yards, three touchdowns, no interception.
  - Jones-Drew: 22 carries for 144 and a touchdown; lost one fumble (DeVito).
- **Defense:**
  - Allen's interception on the game's seventh snap set up the first touchdown.
  - Rambo intercepted at the goal line to end an 84-yard Kansas City drive.
  - Kansas City ran for 47 yards; Charles had 13 carries for 48. Avery caught 12 of 13 targets for 111.
  - Daryl Smith had 14 tackles and a sack; Marks had a sack.
- **Game management:** Stone entered no decision. The end-game check came at 3:41 with a 24-point lead, and the drive ended in three kneel-downs from the real 2012 drive for that cell.

**Other Wild Card games:**

| Result | Notes |
|---|---|
| Dallas 40, New Orleans 10 | |
| Buffalo 33, Pittsburgh 30 | Overtime: Pittsburgh field goal on the first possession, Buffalo matched, Suisham missed from 48, Carpenter's 32-yarder won it in the second overtime period. Modified sudden death applied as the 2013 rules require. |
| Philadelphia 30, Tampa Bay 20 | |

Roundup: `career/2013/league_results/week_18.md`.

**Divisional pairings (reseeded, per Entry 61):**

| Date and kickoff (ET) | Game | Seeds |
|---|---|---|
| Sat. Jan. 11, 4:35 p.m., FOX | Dallas at Minnesota | NFC 6 at 1 |
| Sat. Jan. 11, 8:15 p.m., CBS | Jacksonville at Tennessee | AFC 5 at 2 |
| Sun. Jan. 12, 1:05 p.m., FOX | Philadelphia at St. Louis | NFC 4 at 2 |
| Sun. Jan. 12, 4:40 p.m., CBS | Buffalo at the Jets | AFC 6 at 1 |

**Availability.**
- **Montell Owens:** out, lower extremity, minor; projected return January 5, 2014.
- **Adam Thielen:** out, lower extremity, minor; projected return January 6, 2014.
- Both projections fall before the Divisional game; no other Jacksonville status changed.

**Commit closed - Canonical update - January 5, 2014 - AFC Wild Card at Kansas City closed - canonical through January 5, 2014, after the Wild Card round**

## Entry 63 - Player birth dates, calendar ages and historical retirement audit

**Effective:** January 5, 2014, after the AFC Wild Card round; administrative reconciliation only.
**Recorded:** September 28, 2026.
**Authority:** User request to check and update player ages in their proper simulation records and research historical retirement dates.

The prior current player tables had no populated DOB/age fields. Added a sourced birth-date registry for the 1,661 distinct players in the current Jacksonville roster (53 active plus eight practice-squad players) and the branch background depth library. Exact GSIS identities distinguish namesakes, especially the defensive tackle C.J. Mosley, defensive end C.J. Wilson, receiver Mike Brown and Purdue defensive back Brandon King. The source notes record verification limits and source disagreements; no age was inferred from an NFL experience count.

Document 4 and the readable roster now show DOB and completed calendar age. The league age view is generated from the same source. Ages refresh from Document 5's master date, and repository validation rejects stale columns or a stale as-of marker. Weekly preparation includes ages at each actual game date as public metadata outside TeamInput and the outcome packet. Birthdays do not change hidden anchors, seeded results, depth order or eligibility.

Historical retirement research is retained in `archive/2013_jacksonville_historical_retirements.md`, with announcement dates distinguished from effective periods and ceremonial contracts. Unverified dates stay unknown. This is an explicitly requested historical audit, not a simulation event: no real later retirement, injury, result or current real-world status is imported into branch availability. A simulation retirement still requires a dated branch event under the existing rules. Meester remains on the branch roster for Divisional preparation.

**Correction:** Document 4's header, identity and ending control block still displayed October 27 / Week 8 even though its version and player rows were through January 5 / AFC Wild Card. Reconciled those stale date/phase/next-event labels to Document 5 and Entry 62. Historical October 27 records remain dated history.

**Dependency closure:** Birth-date evidence and verification notes; roster and register DOB/age columns; generated league ages; age renderer and validation; weekly preparation metadata; current-state version manifest; workflow/index pointers. Roster control, medical restrictions, finances, game receipts, scores and standings do not change. No football event or retirement was simulated, and the clock remains January 5, 2014.

**Commit closed - Canonical update - January 5, 2014 - Player age register reconciled - canonical through January 5, 2014, after the AFC Wild Card round**

## Entry 64: AFC Divisional at Tennessee closed; Jacksonville eliminated

**Effective canonical state:** January 11-12, 2014, after the Divisional round
**Recorded:** September 28, 2026
**Checkpoint:** `Canonical update - January 12, 2014 - AFC Divisional at Tennessee closed`
**Preceding global package checkpoint:** `Canonical update - January 5, 2014 - Player age register reconciled`

**Result.** Tennessee 20, Jacksonville 13 at LP Field (Sat. January 11, 8:15 p.m. ET, CBS). Jacksonville's season ends at 10-6 in the regular season and 1-1 in the postseason. Stone's NFL postseason head-coaching record is 2-2.

**Batch.**
- **Package:** the four Divisional games (postseason week 19) closed once each under kernel 2013.10 as `postseason` games. They were drawn from the package frozen by `build_week_inputs.py 19` (sha256 `c799c8ed...`) after the four-game exclusivity gate passed.
- **Snapshot:** advanced to the merged Entry 63 state before the build, so no draw ran against a stale snapshot. Entry 63's age metadata sits outside TeamInput.
- **Jacksonville's unit:** inspected before the close. 46 dressed with exactly Stone's seven inactives. Owens and Thielen had reached their projected returns (January 5 and 6) and dressed, under the plan's cleared branch.
- **Jets:** dressed 44 from their thin library entry, as in the regular season.
- **Freeze:** the call sheet and depth chart were committed before the draw.
- **Receipts:** `career/2013/stats/postseason_receipts/` (Jacksonville full, others compact_stats). No postseason awards are drawn.

**Inputs.**
- **Call sheet:** Stone's fifteen calls; Split opener; 22 Power and Snag; no new family.
- **Lineup:** no role changes; the established seven inactives.
- **Scouting:** position-coach draft work stayed frozen by Stone. The plan's scouting section is otherwise handled outside this record at the user's direction.

**Game.**
- **Jacksonville offense:** 227 yards on 51 plays, 1 of 9 on third down, 22:54 possession, three sacks allowed and one turnover.
  - Scoring: Scobee field goals of 36 and 51, and Shorts's 40-yard touchdown on Mesh at the end of a nine-pass, 80-yard drive.
  - After that touchdown, eight drives gained 62 yards in total.
  - Cousins: 18 of 29 for 155 yards, a touchdown, no interception.
  - Jones-Drew: 13 carries for 42.
- **Turnover:** Thielen's catch-and-fumble at the Jacksonville 18 with 6:13 left, forced and recovered by Patrick Bailey. It set up Bironas's 26-yarder for 20-13.
- **Tennessee:** 404 yards on 77 plays, 11 of 20 on third down, 37:06 possession.
  - Johnson: 24 carries for 103 and a touchdown. Bironas missed from 41 and 42 in the first half.
  - Britt: 8 catches on 12 targets for 58, longest 19, and the go-ahead 4-yard touchdown with 7:13 left.
- **Game management:** Stone entered no decision.

**Engine limitation (the Entry 60 limit; recorded here, not fixed).**
- **What happened:** trailing 20-13 with 2:22 left, Jacksonville faced fourth-and-10 at its own 30. The engine drew a punt from the real 2012 late-game cell (trailing by 4-8, 121-300 seconds). Tennessee's next possession ran from 2:00 to 0:07 on six snaps, and Jacksonville got one snap from its own 8.
- **Why it matters:** timeouts and the two-minute warning are not simulated snap by snap. A real punt from that cell assumes the trailing team still has timeouts, and the following clock runoff assumes it used none. Stone's spoken end-game check had no mechanical effect.
- **Status:** the user deferred this defect ("we're gonna fix the bug another day"). Under the label-swap rule a result is never voided because of who it favoured. The result stands as closed and nothing is rerun.

**Other Divisional games.**
- Minnesota 38, Dallas 10.
- Philadelphia 30, St. Louis 20.
- Buffalo 26, the Jets 24: Carpenter kicked a 51-yard field goal with 33 seconds left. E.J. Manuel was injured (lower extremity, long-term; projected absence 66 days).
- Roundup: `career/2013/league_results/week_19.md`.

**Conference championships (postseason week 20; the higher remaining seed hosts):**

| Date and kickoff (ET) | Game | Seeds |
|---|---|---|
| Sun. Jan. 19, 3:00 p.m., CBS | Buffalo at Tennessee | AFC 6 at 2 |
| Sun. Jan. 19, 6:30 p.m., FOX | Philadelphia at Minnesota | NFC 4 at 1 |

They are background games.

**Availability.**
- **Ryan Davis:** out, trunk, minor; projected return January 14, 2014.
- **Owens and Thielen:** cleared at their projected returns.
- No other Jacksonville status changed.

**Commit closed - Canonical update - January 12, 2014 - AFC Divisional at Tennessee closed - canonical through January 12, 2014, after the Divisional round**

## Entry 65: Conference championships closed (background)

**Effective canonical state:** January 19, 2014, after the conference championships
**Recorded:** September 28, 2026
**Checkpoint:** `Canonical update - January 19, 2014 - Conference championships closed`
**Preceding global package checkpoint:** `Canonical update - January 12, 2014 - AFC Divisional at Tennessee closed`

**Decision.** At the user's instruction ("Finish the playoffs"), the conference round (postseason week 20) closed as a background slate. Jacksonville was eliminated in Entry 64 and supplies no plan.

**Batch.** Both games closed once each under kernel 2013.10 as `postseason` games. They were drawn from the package frozen by `build_week_inputs.py 20` (sha256 `880c16de...`) after the two-game exclusivity gate passed: no Jacksonville-controlled player appeared in either TeamInput. Buffalo dressed Jeff Tuel as its only available quarterback after E.J. Manuel's Divisional injury, under the rule every club gets. Receipts (compact_stats) are in `career/2013/stats/postseason_receipts/`.

**Results.**
- **AFC:** Buffalo 34, Tennessee 3. Spiller ran 27 times for 214; Buffalo committed no turnover.
- **NFC:** Minnesota 20, Philadelphia 7. Philadelphia came away empty from the Minnesota 16, 20 and 8.
- **Roundup:** `career/2013/league_results/week_20.md`.

**Super Bowl XLVIII:** Minnesota (NFC 1) vs. Buffalo (AFC 6), Sun. February 2, 2014, 6:30 p.m. ET, FOX, MetLife Stadium. It is a neutral site, and Buffalo, as the AFC champion, is the designated home team. The user approved fixing the neutral-site home term before this game (Entry 66).

**Jacksonville.** The season is over. Ryan Davis's projected return (January 14, 2014) has passed, so he is cleared under the standard rule; no other status changed.

**Commit closed - Canonical update - January 19, 2014 - Conference championships closed - canonical through January 19, 2014**

## Entry 66: Kernel 2013.11 adopted (no home term at a neutral site)

**Effective canonical state:** January 19, 2014, after the conference championships
**Recorded:** September 28, 2026
**Checkpoint:** `Canonical update - January 19, 2014 - Kernel 2013.11 adopted (neutral site)`
**Preceding global package checkpoint:** `Canonical update - January 19, 2014 - Conference championships closed`

**Decision.** The user approved the fix before Super Bowl XLVIII. The instruction quoted Claude's offer, "The Super Bowl still carries the unfixed neutral-site issue ... I can fix that first if you approve it", as part of "Finish the playoffs". Kernel 2013.11 replaces 2013.10 from postseason week 21.

**Defect (Entry 45).** `kernel._edge` gave its 0.008 home term to the designated home team at any venue, so Minnesota (Week 4) and Jacksonville (Week 8) received it at Wembley.

**Fix.** The home term applies only when the packet venue is not `neutral`; the anchor term is unchanged.
- Source and tests: `runtime/README.md`, `tests/test_neutral_site.py`.
- The full suite passes.

**Scope.**
- Every home-venue game resolves exactly as under 2013.10. The only 2013 game this affects is Super Bowl XLVIII, where Buffalo is the designated home team.
- The decision is result-blind. It was taken before the Super Bowl pairing's draw, and it applies to whichever club is designated home.

**Closed results stand.** The Week 4 and Week 8 Wembley receipts are never rerun.

**Commit closed - Canonical update - January 19, 2014 - Kernel 2013.11 adopted (neutral site) - canonical through January 19, 2014**


## Entry 67: Super Bowl XLVIII closed; 2013 season archived

**Effective canonical state:** February 2, 2014, after Super Bowl XLVIII
**Recorded:** September 28, 2026
**Checkpoint:** `Canonical update - February 2, 2014 - Super Bowl XLVIII closed; 2013 season archived`
**Preceding global package checkpoint:** `Canonical update - January 19, 2014 - Kernel 2013.11 adopted (neutral site)`

**Result.** Buffalo 31, Minnesota 20, at MetLife Stadium on Sun. February 2, 2014 (neutral site; Buffalo the designated home team). The Buffalo Bills, the AFC's sixth seed, are the branch's 2013 champions.

**Batch.**
- **How it closed:** one game, closed once under kernel 2013.11 as a `postseason` game at venue `neutral`, from the package frozen by `build_week_inputs.py 21` (sha256 `737fd0b4...`) after the one-game exclusivity gate passed.
- **Home term:** neither team received it (Entry 66).
- **Receipt:** compact_stats in `career/2013/stats/postseason_receipts/`.
- **Roundup:** `career/2013/league_results/week_21.md`.

**Engine limitation (the Entry 60 limit; recorded, not fixed).** Late in the first half, an interception return put Buffalo at the Minnesota 1 with 51 seconds left. The engine drew a real 2012 end-of-half drive from the time cell, and it ended in two kneel-downs. Timeouts and end-of-half clock management are not simulated snap by snap, so the engine cannot tell a kneel-out from a scoring chance. The result stands as closed and nothing is rerun. The user has directed the timeout and fourth-down fixes before any 2014 game.

**Availability reconciled at the master date.**
- **Cleared at their projected returns:** Alan Ball (January 22, 2014) and C.J. Wilson (January 30, 2014).
- **Still out:** Paul Posluszny, on an independent medical hold, projected return April 5, 2014.
- **Limited:** Rackley (minor).

**Not run in the branch (recorded gaps, not simulated):**
- Pro Bowl selections (December 27, 2013) and AP All-Pro teams (January 3, 2014) were never drawn. They are behind this checkpoint and stay chronology gaps unless the user authorizes a retroactive draw.
- The Pro Bowl (January 26, 2014), the AP season awards and the Super Bowl MVP (NFL Honors, February 1, 2014) are not drawn. The branch has no season-award voting method; `library/2013_nfl_awards_structure.md` records only the structure.
- Exit interviews are held until the user asks.

### Phase archive | Jacksonville Jaguars | 2013 regular season | Closed December 29, 2013

This archive was appended late. It was written at this February 2, 2014 checkpoint from the closed records, with no event added or changed. No preseason archive was written at the preseason boundary; the preseason record is Entries 22-29 and Document 5 section 5.

- **Global package checkpoint:** `Canonical update - December 29, 2013 - Week 17 at Indianapolis closed`.
- **Governing documents:**
  - Documents 1-3: `358ccf4f`, `ab790f6e`, `38e0ce21` (Document 5 manifest).
  - Document 4: `JAX-2013-DEC29-WEEK17-REGISTER-29`.
  - Document 5: `JAX-2013-DEC29-WEEK17-STATE-36`.
- **Date range:** September 8 through December 29, 2013 (Week 9 bye November 3).
- **Record and standing:** 10-6 (356 points for, 346 against). Second in the AFC South: Tennessee also went 10-6 and won the division on division record, 4-2 to 3-3. Jacksonville was the AFC's fifth seed.
- **Schedule and results:** `career/2013/regular_season/README.md` and Entries 35-60.
- **Roster at close:** 53 active and 8 on the practice squad (Document 4 `REGISTER-29`).
- **Significant transactions:** Blackmon on Reserve/Suspended for Weeks 2-5 (Entry 36), then reinstated and activated October 7 (Entry 42). No trade and no reserve-list move during the season.
- **Significant injuries:**
  - Posluszny: Week 3, returned Week 5; head/neck independent medical hold from Week 13.
  - Meester and C.J. Wilson: Week 2.
  - Thielen: Week 5.
  - Ball: Week 10.
  - Bouye: Week 11.
  - Kelce: Week 13.
  - Pasztor and Mosley projections recovered (Entry 46).
- **Staff and authority:** unchanged. Stone called the offense, Tice coordinated it, Crennel called the defense and Lowry the special teams (`career/2013/coaching_staff.md`).
- **Verified statistics (from receipts):**
  - Cousins 357 of 564 for 3,981 yards, 23 touchdowns, 18 interceptions, 38 sacks.
  - Jones-Drew 1,334 rushing yards; Shorts 1,158 receiving yards.
  - Marks 8 sacks; Lowery 119 tackles; Scobee 36 of 41 field goals.
  - Team: 25 giveaways and 15 takeaways; 23 sacks for.
- **Material head-coach decisions:** Stone's weekly plans and frozen call sheets, the weekly inactive lists and the Blackmon activation. Every game ran in autonomous game-management mode, with no in-game decision entered.
- **Corrections and superseded records:**
  - Week 1 void and replay (Entries 30-35).
  - Week 14 generation void (Entry 57).
  - Kernels 2013.6-2013.10 (Entries 39, 48, 51, 54, 56).
  - Injury projection recovery (Entry 46).
- **Commitments carrying forward:**
  - Posluszny's hold, projected April 5, 2014.
  - Coaching contracts: Crennel and Tice through 2015, Lowry through 2014.
  - The engine limits listed in Entries 60, 64 and 67.
- **Information still uncertain:** exact cap working room (ranges in Document 4); the unresolved accounting named there.
- **Next phase and first event:** postseason, AFC Wild Card at Kansas City, January 4, 2014.

### Phase archive | Jacksonville Jaguars | 2013 postseason | Closed February 2, 2014

- **Global package checkpoint:** `Canonical update - February 2, 2014 - Super Bowl XLVIII closed; 2013 season archived`.
- **Governing documents:** Documents 1-3 unchanged. Document 4: `JAX-2014-FEB02-SEASON-CLOSE-REGISTER-34`. Document 5: `JAX-2014-FEB02-SEASON-CLOSE-STATE-43`.
- **Date range:** December 30, 2013 through February 2, 2014.
- **Record and status:** 1-1.
  - AFC Wild Card: won 38-14 at Kansas City (Entry 62).
  - AFC Divisional: lost 20-13 at Tennessee (Entry 64). Jacksonville was eliminated.
  - League champion: Buffalo (AFC 6).
  - Stone's NFL postseason head-coaching record is 2-2.
- **Format:** built in Entry 61. Kernel 2013.10 through the conference round; 2013.11 for the Super Bowl (Entry 66).
- **Schedule and results:** `career/2013/postseason/README.md`; roundups in `career/2013/league_results/week_18.md` through `week_21.md`.
- **Roster at close:** 53 active and 8 on the practice squad (Document 4 `REGISTER-34`).
- **Transactions:** none.
- **Injuries:** Owens and Thielen (Wild Card, minor) and Ryan Davis (Divisional, minor), all cleared at their projections.
- **Staff and authority:** unchanged.
- **Verified statistics (two games):** 51 points for and 34 against; 480 passing and 251 rushing yards; two giveaways and two takeaways.
- **Material head-coach decisions:**
  - Stone's Wild Card and Divisional plans (frozen call sheets); the established seven inactives.
  - Position-coach draft work frozen for the postseason by Stone.
  - No in-game decision entered.
- **Corrections during the phase:** none. The engine limits are listed above.
- **Commitments carrying forward:**
  - Kernel fixes for timeouts, the two-minute warning, kneel-downs and the fourth-down display before any 2014 game (user instruction).
  - Exit interviews held for the user.
  - The 2014 setup (Entry 68).
- **Information still uncertain:** the award gaps listed above.
- **Next phase and first event:** the 2014 offseason. The next league events are the franchise and transition tag window (February 17 to March 3, 2014), the Combine (February 19-25) and the opening of the 2014 league year on March 11, 2014 (`library/2014_league_calendar_and_financial_rules.md`, gated as recorded there).

**Commit closed - Canonical update - February 2, 2014 - Super Bowl XLVIII closed; 2013 season archived - canonical through February 2, 2014, after Super Bowl XLVIII**

## Entry 68: 2014 season set up (no clock advance)

**Effective canonical state:** February 2, 2014, after Super Bowl XLVIII (the master date does not move)
**Recorded:** September 28, 2026
**Checkpoint:** `Canonical update - February 2, 2014 - 2014 season set up`
**Preceding global package checkpoint:** `Canonical update - February 2, 2014 - Super Bowl XLVIII closed; 2013 season archived`

**Decision.** The user asked to "set up for 2014 season", and said not to run exit interviews yet. This entry creates the 2014 records. It advances no clock, changes no roster, contract or staff fact, and runs no phase.

**Created.**
- **`career/2014/README.md`:** the season index.
- **`career/2014/calendar.md`:** Jacksonville's 2014 calendar with each league date's public gate, from the new sourced library file `library/2014_league_calendar_and_financial_rules.md` (two-pass; WebFetch blocked, search-result text only; no real 2014 transaction or outcome; two outcome-bearing URL slugs withheld).
- **`career/2014/draft/draft_order.md`:** the 2014 draft order, generated from the closed receipts by `runtime/draft_order.py` and `scripts/render_draft_order.py`. `validate_repository.py` checks it is current; tests are in `tests/test_draft_order.py`.
- **`career/2014/schedule/opponents.md`:** Jacksonville's 2014 opponents, derived from the 2014 formula and the branch standings.
- **`career/2014/offseason/contract_status_register.md`:** each controlled player's status when the league year opens (two-pass research; branch contracts override real history; no real 2014 decision recorded).

**2014 draft order (branch).**
- **Jacksonville:** 26th in each round, as a Divisional loser (10-6, strength of schedule .477). Its second-round selection belongs to Washington (the Cousins trade).
- **Top and bottom:** San Francisco (2-13-1) holds the first selection; Buffalo, the champion, the 32nd.
- **Ties that survived strength of schedule:**
  - Oakland and Miami (both 7-9, .533): Miami wins the conference tiebreaker on conference record, so Oakland picks 11th and Miami 12th.
  - Green Bay and Indianapolis (both 8-8, .479, different conferences): a coin flip the league holds before the draft. It is pending and not invented.
- **Still open:** compensatory selections (gated to March 24, 2014) come from the branch's own 2014 free-agency cycle. Other clubs' traded 2014 selections are not reconciled.

**2014 opponents.**
- **Home:** Tennessee, Indianapolis, Houston, Cleveland, Pittsburgh, the Giants, Buffalo (AFC East second place), and Dallas (at Wembley Stadium, November 9).
- **Away:** Tennessee, Indianapolis, Houston, Baltimore, Cincinnati, Philadelphia, Washington, and San Diego (AFC West second place).
- **Dates:** gated to the April 23, 2014 schedule release.

**Contract status at the March 11, 2014 league-year turn (research register; Caldwell decides tenders and re-signings).**

| Status | Count | Players |
|---|--:|---|
| Under contract | 35 | |
| Unrestricted free agents | 8 | Henne, Jones-Drew, Monroe, Meester, Marks, C.J. Wilson, Ball, Brent Grimes |
| Restricted free agents | 3 | Bradfield, Reisner, Rutland |
| Exclusive-rights free agents | 3 | Clemons, Mike Brown, Pasztor |
| Practice-squad contracts expiring | 8 | |
| Unresolved | 4 | John Parker Wilson, Jonathan Grimes, Owens, Cain (contract lengths not recovered) |

**Held for the user.**
- End-of-season exit interviews.
- The 2014 phase plans.
- The 2014 free-agency, draft and trade boards (AGENTS.md "Run the [year] offseason cycle").
- The engine fixes for timeouts, the two-minute warning, kneel-downs and the fourth-down display, before any 2014 game.

**Commit closed - Canonical update - February 2, 2014 - 2014 season set up - canonical through February 2, 2014, after Super Bowl XLVIII**

## Entry 69: Kernel 2014.1 adopted (timeouts, kneel zones, goal to go)

**Effective canonical state:** February 2, 2014 (no clock advance)
**Recorded:** September 28, 2026
**Checkpoint:** `Canonical update - February 2, 2014 - Kernel 2014.1 adopted (timeouts)`
**Preceding global package checkpoint:** `Canonical update - February 2, 2014 - 2014 season set up`

**Decision.** The user's instruction was "The timeout and fourth-down fixes you deferred, before any 2014 games." Kernel 2014.1 replaces 2013.11 for every event from here on. No game has been drawn under it.

**Defects addressed.**
- **Week 17 (Entry 60):** a leading possession punted with 3 seconds left.
- **Divisional round (Entry 64):** after a trailing punt with 2:22 left, the opponent's clock ran down to 0:07.
- **Super Bowl XLVIII (Entry 67):** kneel-downs at the Minnesota 1 before halftime.
- **Fourth-down display:** yards to go beyond the goal line in three receipts (Weeks 11, 13, 16).

**Fix.** Documented in `runtime/README.md`; tests in `tests/test_timeouts.py`.
- **Timeout data:** the 2012 field-position data (schema v2) now carries each club's charged timeouts at every drive's start and the timeouts it used. The data was cross-checked against the second play-by-play file; the deviations are explained and recorded in the builder.
- **Timeout state:** the kernel tracks each club's timeouts: three per half, two in regular-season overtime, and three per two-period postseason overtime half (labelled inference).
- **Conditioned draws:** late, first-half-final and overtime draws follow a pre-registered ladder on those counts, and the counts reweight the choice between kneeling out, punting, a field goal or going.
- **Kneel start zone:** a kneel drive replays only from its own start zone.
- **End-of-half fallback:** a failed end-of-half draw first tries a same-bin drive that fits the time left.
- **Fourth-down records:** they publish goal-to-go distances.
- **New checks:** coherence classes check the timeout state and the goal line.

**Not modelled separately.** The two-minute warning and the play clock remain embedded in real 2012 drive durations. This is stated rather than claimed as fixed.

**Acceptance (250-game synthetic sample).** Zero coherence violations. Every graded band row is inside except the two clock rows registered as known detections since kernel 2013.7. FGM per team game moves back inside.
- **Touchdown share of drives:** 0.2100 against 0.1945 +/- 0.0155, at the band's ceiling (2013.11: 0.2090 on the same sample).
- **Trailing late punt share:** 0.062 against 0.119 +/- 0.064, inside but low.
- **Cause:** both come from the late cells' existing masking bias, not the timeout logic. Recalibrating it is a separate, larger change, not made here.
- **Effect on the defects:** a leading offence in its last two minutes punted 11 of 126 times, against 16 of 115 under 2013.11. With the defence out of timeouts it punted 1 of 50 times.

**Closed results stand.** No 2013 receipt is rerun. The Week 17, Divisional and Super Bowl results keep their recorded limitations.

**Commit closed - Canonical update - February 2, 2014 - Kernel 2014.1 adopted (timeouts) - canonical through February 2, 2014**

## Entry 70: Kernel 2014.2 adopted (late-game recalibration)

**Effective canonical state:** February 2, 2014 (no clock advance)
**Recorded:** September 28, 2026
**Checkpoint:** `Canonical update - February 2, 2014 - Kernel 2014.2 adopted (late-game recalibration)`
**Preceding global package checkpoint:** `Canonical update - February 2, 2014 - Kernel 2014.1 adopted (timeouts)`

**Decision.** The user's instruction was "do the late-game recalibration before 2014". Kernel 2014.2 replaces 2014.1 for every event from here on. No game has been drawn under 2014.1 or 2014.2.

**Defect.** Recorded at the 2014.1 acceptance (Entry 69): late categories with no drive feasible at the spot and clock were masked, and their weight went mostly to touchdowns. The late touchdown rate ran well above 2012 (expected 0.199 against 0.159), and trailing teams punted too rarely.

**Fix.** Documented in `runtime/README.md`; tests in `tests/test_timeouts.py`.
- **Start-zone weights:** late, first-half-final and overtime category weights are conditioned on the drive's start zone (Bayes, estimated on the need's larger pool).
- **Borrowing before masking:** a late cell with no feasible drive of a category borrows one from the same need's other time buckets under the same clock filters.

**Evidence.**
- **750 fresh games:** the expected late touchdown share is 0.170 (2014.1: 0.199; 2012: 0.159), and drive share: touchdown is 0.1991 (2014.1: 0.2027; centre 0.1945).
- **Expected late mix by score situation:** tracks 2012, with trailing punts at 0.173 and 0.129 against 0.179 and 0.135.

**Acceptance.** Zero coherence violations. Two rows were registered as known detections: field-goal attempts per team game (the first-half redirect) and the small late trailing punt row (0.087 inside tolerance on 750 games).
- **Who registered them:** Claude, not the user, while carrying out the request. They are reversible, graded and labelled, and tolerated only within twice their tolerance.
- **Still open, not late-game:** the field-goal and turnover shares of drives. Both trace to the first-half redirect.

**Closed results stand.** No 2013 receipt is rerun.

**Commit closed - Canonical update - February 2, 2014 - Kernel 2014.2 adopted (late-game recalibration) - canonical through February 2, 2014**

## Entry 71: 2013 season honours drawn (retroactive)

**Effective canonical state:** February 2, 2014 (no clock advance)
**Recorded:** September 28, 2026
**Checkpoint:** `Canonical update - February 2, 2014 - 2013 season honours drawn (retroactive)`
**Preceding global package checkpoint:** `Canonical update - February 2, 2014 - Kernel 2014.2 adopted (late-game recalibration)`

**Decision.** The user asked for a method and a draw for the 2013 Pro Bowl, AP All-Pro teams and AP season awards, which Entry 67 recorded as chronology gaps. That request authorizes this retroactive draw. It changes no game result, statistic, standing or roster fact.

**Method.** Fixed in `career/2013/awards/season_honours_method.json` and committed before the draw.
- **Structure:** slot counts and voting from `library/2013_season_honours_selection_structure.md` (new, two-pass sourced, no honourees).
- **Evidence:** regular-season receipts only; Weeks 1-17 for the AP ballots, Weeks 1-16 for the Pro Bowl (its vote closed December 26). Eligibility and line starts come from `season_honours_evidence.json`: pre-2013 public facts (experience, 2011 and 2012 games, 2012 records, opening-day head coaches) and the frozen weekly TeamInputs, each checked against its receipts.
- **Selection:** All-Pro and Pro Bowl slots are formula ranks per position; each AP award is drawn 6:3:1 from a three-name shortlist with the private service's entropy, as the weekly awards are.
- **Linemen:** the receipts hold no individual line evidence, so a starter earns his club's line output and a club places at most one lineman per position. The one-per-club rule was added after a dry run showed one club's five starters tied across all three line positions; it applies to every club and was fixed before the draw.
- **Author's view:** the method was written after the season closed, so the standings were visible to its author. Every rule applies to every club alike.

**AP awards.**
- MVP: Jamaal Charles, Kansas City.
- Offensive Player of the Year: Daryl Richardson, St. Louis.
- Defensive Player of the Year: David Harris, New York Jets.
- Offensive Rookie of the Year: Geno Smith, New York Jets.
- Defensive Rookie of the Year: Kiko Alonso, Buffalo.
- Comeback Player of the Year: **Maurice Jones-Drew, Jacksonville**.
- Coach of the Year: Rex Ryan, New York Jets. Alex Stone led the shortlist on improvement (plus 8 wins); the panel drew the third name.

**All-Pro and Pro Bowl.** Full tables in `career/2013/awards/season_honours.md`.
- No Jaguar made either All-Pro team.
- Marcedes Lewis plays in the Pro Bowl, replacing Buffalo's Scott Chandler (Super Bowl club). Sen'Derrick Marks is the first alternate at defensive tackle.
- The Pro Bowl coaches are the Jets' and Rams' staffs (highest-seeded Divisional losers); Stone does not coach it.

**Not generated.**
- The two special teamer slots: no coverage-unit evidence.
- The coach-appointed need players.
- The Pro Bowl draft and game.
- The Super Bowl MVP.

**Commit closed - Canonical update - February 2, 2014 - 2013 season honours drawn (retroactive) - canonical through February 2, 2014**

## Entry 72: Kernel 2014.3 adopted (credit rules, Pro Bowl game type)

**Effective canonical state:** February 2, 2014 (no clock advance)
**Recorded:** September 28, 2026
**Checkpoint:** `Canonical update - February 2, 2014 - Kernel 2014.3 adopted (credit rules, Pro Bowl game type)`
**Preceding global package checkpoint:** `Canonical update - February 2, 2014 - 2013 season honours drawn (retroactive)`

**Decision.** The user asked for an assessment of what must be fixed so games have no bugs, and for the gaps recorded in Entry 71 to be built out. They confirmed that the engine change ships as kernel 2014.3 and that 2013's closed receipts are not rerun. Kernel 2014.3 replaces 2014.2 for every event from here on. No game has been drawn under 2014.2 or 2014.3.

**Credit rules (credit only; every result identical to 2014.2).** Documented in `runtime/README.md`.
- **Sacks allowed:** charged to the on-field lineman facing the rusher (edge rushers beat a tackle, interior rushers a guard or the center). The five on the field earn line starts.
- **Coverage tackles:** one per returned kickoff or punt, from the kicking club's coverage unit.
- **Long snaps:** credited on every punt, field goal and try.
- **Returners:** one club returner per game when none is designated.
- **Coverage units and returners:** Jacksonville's depth chart designates none, so they follow the same mechanical rule as every club until Stone designates them.

**Pro Bowl game type.** `game_type="pro_bowl"` plays the 2014 Pro Bowl structure: no kickoffs, the ball at the 25 to start every quarter and after every score, and possession ending at every quarter. Regular and postseason games never reach it.

**Acceptance.**
- **Replay:** 1,090 games (the frozen Weeks 11-17 TeamInputs, ten fresh seeds each) are identical to 2014.2 in score, possessions, kickoffs, injuries and team counters, with zero validation errors and zero coherence violations.
- **Pro Bowl:** 300 synthetic Pro Bowl games, with zero errors.
- **Views:** the 2013 stat views and box scores render unchanged. `season_totals.json` gains only the declared names of the three new counters.

**Assessment.** `runtime/defect_register.md` ranks the open defects. The most important is that every club carries the same Average strength, so each game is close to a coin flip.
- **Tier 1:** results integrity, recommended before any 2014 game. It includes half-final drives taking the whole clock, fourth-down distances and first downs contradicting the yardage, and players never leaving a game.
- **Tier 2:** visible play-by-play and decision bugs.
- **Tier 3:** realism gaps.
- **No fixes yet:** none of these fixes is made here. Each changes results, so each needs the user's decision.

**Unrecorded 2013 defect, now recorded.** Week 9, San Diego 20, Washington 20 (kernel 2013.7): San Diego's nine-play, 66-yard overtime drive, which ended on downs, was clocked from 13:25 to 0:00. That is the whole-period overtime defect Entry 50 records for Week 10, and kernel 2013.8 fixed it. Neither Entry 49 nor the Week 9 roundup noted it. The result stands, as the Week 10 one does.

**Commit closed - Canonical update - February 2, 2014 - Kernel 2014.3 adopted (credit rules, Pro Bowl game type) - canonical through February 2, 2014**

## Entry 73: Super Bowl MVP and Pro Bowl drawn (retroactive)

**Effective canonical state:** February 2, 2014 (no clock advance)
**Recorded:** September 28, 2026
**Checkpoint:** `Canonical update - February 2, 2014 - Super Bowl MVP and Pro Bowl drawn (retroactive)`
**Preceding global package checkpoint:** `Canonical update - February 2, 2014 - Kernel 2014.3 adopted (credit rules, Pro Bowl game type)`

**Decision.** The user asked for the Super Bowl MVP and the Pro Bowl need players, draft and game to be built out and finished (Entry 71 recorded them as not generated). That authorizes this retroactive draw.
- **Methods:** both were merged in Entry 72, before any draw: `career/2013/awards/super_bowl_mvp_method.json` and `career/2013/pro_bowl/method.json`, on `library/2013_super_bowl_mvp_and_pro_bowl_procedure.md`.
- **Scope:** no game result, statistic, standing or roster fact changes.

**Super Bowl XLVIII MVP: C.J. Spiller, Buffalo.**
- **Shortlist:** from the winning club's players on the closed Super Bowl receipt, by the weekly award formulas: Spiller, Leodis McKelvin and Jeff Tuel.
- **Draw:** the private service's 6:3:1 panel drew the first name.

**Pro Bowl draft (January 21-22).**
- **Captain groups:**
  - Team One: Jamaal Charles and David Harris.
  - Team Two: Vontaze Burfict and Philip Rivers.
- **Coin toss:** the private service's toss gave Team Two the first pick on both days.
- **Coaches:** the pairing put Jeff Fisher's Rams staff with Team One and Rex Ryan's Jets staff with Team Two.
- **Need players:** each staff appointed its own long snapper, Jake McQuaide (Rams) and Tanner Purdum (Jets).
- **Picks:** alternated straight, taking the highest vote-rank player left at each position. A team with its quota filled had the rest assigned to it.
- **Jacksonville:** Marcedes Lewis was drafted by Team One.

**Pro Bowl game (January 26): Team One 9, Team Two 6 in overtime.**
- **Rules:** played under the kernel 2014.3 Pro Bowl rules: no kickoffs, the ball at the 25 each quarter and after scores, and possession alternating each quarter.
- **Scoring:** four regulation field goals, then Team One's overtime field goal.
- **Records:** the receipt is `career/2013/pro_bowl/receipt.json`, apart from the season receipts, and counts toward no statistic, standing, award or band. The record is `career/2013/pro_bowl/README.md`.

**Receipt audit.** The first audit of the published receipt showed that its compact drive summary omits the quarter. `check_ledger` now derives the quarter from the drive's clock, since no Pro Bowl possession crosses a quarter. The receipt audits clean, and `tests/test_pro_bowl.py` now audits Pro Bowl receipts. This is a checking change only; no result depends on it.

**Still not generated.** The two 2013 special-teamer slots (no coverage-unit evidence in the 2013 receipts).

**Commit closed - Canonical update - February 2, 2014 - Super Bowl MVP and Pro Bowl drawn (retroactive) - canonical through February 2, 2014**

## Entry 74: Season review with Khan and Caldwell; Stone retained

**Effective canonical state:** February 2, 2014 (no clock advance). The event is dated Wednesday January 15, 2014.
**Recorded:** September 28, 2026
**Checkpoint:** `Canonical update - February 2, 2014 - Season review with Khan and Caldwell (Stone retained)`
**Preceding global package checkpoint:** `Canonical update - February 2, 2014 - Super Bowl MVP and Pro Bowl drawn (retroactive)`

**Decision.** The user asked whether Stone's end-of-season meeting with the owner and general manager had been held, and whether he is retained. It had not been held. The user directed it:
- **Date:** Wednesday January 15, 2014, the day after the player exit interviews.
- **Stone's brief:** an honest season review and his 2014 direction, with no new asks.

**Record.** `career/2013/season_review/owner_and_gm_review.md`.
- **Entry 1:** the club's criteria freeze, committed before the meeting was written. It covers authority, the fully guaranteed contract, the hire criteria, Stone's own first-year standard, the 2013 record, and the unknown private weighting.
- **Entry 2:** the meeting.
- **Entry 3:** the club's decision.

**Decision: Alex Stone is retained as head coach for 2014, on his existing contract.** Khan and Caldwell hold this authority (Document 3, row 1), and resolved it from the frozen criteria.
- **The five criteria:** the Caldwell-Stone partnership, program leadership, the quarterback evaluation, staff construction and roster development all have 2013 evidence.
- **Stone's own standard:** the season met the first-year standard he set in his interview, which did not promise a playoff appearance.
- **Concerns raised:** the regular-season scoring margin (356-346), the three losses by 28 or more (six and four turnovers in two of them), and Cousins's 18 interceptions and 38 sacks. They are Caldwell's first measures for 2014, not grounds to end the contract.
- **Label-swap check:** any club with this record and a four-year, fully guaranteed contract in its first year retains its coach.
- **Unchanged:** Stone's contract, authority and staff.
- **Extension:** not raised by either side; remains unknown.

**Follow-ups.**
- **Caldwell's deadline:** Stone's written recommendations before February 17. They were delivered as the February 2 memo filed in `career/2014/offseason/`.
- **Khan's request:** prepare the November 9, 2014 Wembley game against Dallas on the 2013 London plan.
- **Open gap:** the league's post-2013 head-coaching changes are not simulated, so no other club has sought permission to interview a Jacksonville assistant. This is recorded for the user's decision.

**Exit interviews.** Stone's player exit interviews, dated January 13-14, are recorded separately when complete.

**Commit closed - Canonical update - February 2, 2014 - Season review with Khan and Caldwell (Stone retained) - canonical through February 2, 2014**

## Entry 75: January 2014 coaching carousel resolved (retroactive)

**Effective canonical state:** February 2, 2014 (no clock advance). The events are dated December 30, 2013 to February 2, 2014.
**Recorded:** September 28, 2026
**Checkpoint:** `Canonical update - February 2, 2014 - January 2014 coaching carousel resolved (Lowry to Atlanta)`
**Preceding global package checkpoint:** `Canonical update - February 2, 2014 - Season review with Khan and Caldwell (Stone retained)`

**Decision.** The user asked for the 2013-14 rules on other clubs interviewing Jacksonville's coordinators and position coaches to be researched and followed, and for the staff's exposure to be weighted and resolved without the user forcing each case. This closes the open gap recorded in Entry 74.

**Rules.** `library/2014_coaching_hiring_and_anti_tampering_rules.md`: two research passes, a calibration pass from the January 2013 cycle and a skeptical verification pass. Section 8 is enforced as written:
- only a head-coach job is a promotion;
- a head-coach interview cannot be refused once the employer's season is over;
- a Wild Card winner's assistants may be interviewed for head-coach jobs only from the evening of January 5 to January 12, 2014;
- every other request is lateral, waits for the employer's elimination and may be refused;
- no hire before the employer's elimination.
Whether a playoff club could refuse an in-window head-coach interview is Unverified (W11); the method sets a default policy there instead of a rule.

**Method.** `career/2014/offseason/staff_changes/carousel_method.json` and `scripts/coaching_carousel.py`, committed and pushed (35f1276) before the draw, with `tests/test_coaching_carousel.py`.
- **Head-coach changes:** each club's chance comes from real 2002-2012 club-seasons by wins, tenure and recent playoffs (`library/data/2012_hc_change_base_rates.json`), applied to the branch 2013 record. Hire days follow the January 2013 cycle.
- **Requests:** weighted by role, play-calling, club and unit rank for head-coach jobs, and by prior coordinator experience and room for coordinator jobs. Factors are normalized so they move interest without raising the league total.
- **Permission:** Jacksonville's default policy, set for the user and applied alike to any club, grants head-coach interviews and position-to-coordinator moves and refuses lateral moves.
- **Offers:** calibrated to the January 2013 cycle, in which sitting coordinators were 72.5 percent of named candidates and half of the hires.
The adversarial review of the method before the draw confirmed and fixed thirteen findings, among them double hires into one job, the hire date of a club that hires a Jacksonville coach, pending candidacies and the base-rate window.

**Draw.** One private packet (`coaching-carousel-2014-v1`, event `2014-coaching-carousel-v1`) committing the method, script, base-rate and input digests; result reference and digests in `carousel_results.json`. Rendered at `requests_and_outcomes.md`. The rendering fix to the page's table after the draw changed no draw; `code_sha256` in the results matches the script at 35f1276.

**Result.**
- **Head-coach changes by February 2 (five):** Atlanta (Mike Smith; 8-8; hired Alan Lowry, January 12), Cincinnati (Marvin Lewis; 5-10-1; external hire January 2), Denver (John Fox; 7-9; external hire January 2), Indianapolis (Chuck Pagano; 8-8; external hire January 14) and San Francisco (Jim Harbaugh; 2-13-1; external hire January 5). Every other club kept its coach. External hires are not named: the branch has no league-wide staff register.
- **Deferred:** Buffalo and Minnesota played Super Bowl XLVIII on February 2; their decisions are resolved by `2014-coaching-carousel-deferred-v1` when the clock passes that date.
- **Alan Lowry (special teams coordinator):** Atlanta asked on January 6, inside the Wild Card winners' window. The interview was granted under the default policy and held. Atlanta offered him the head-coach job on January 12, the first day a hire was allowed, and he accepted. **He leaves Jacksonville.**
- **Frank Bush (linebackers):** Atlanta's January 12 request for its linebackers job was refused (lateral). Indianapolis asked on January 14 for its defensive coordinator job; the request was granted (a step up in title) and he interviewed. He was not hired, and he stays.
- **The other ten assistants:** no request.

**State.**
- `career/2013/coaching_staff.md`: Lowry's departure and the vacancy. His 2014 salary ($625,000) is no longer scheduled; the eleven remaining coaches are scheduled at $6,950,000 for 2014 before any replacement.
- Document 4 (`JAX-2014-FEB02-COACHING-CAROUSEL-REGISTER-35`) and Document 5 (`JAX-2014-FEB02-COACHING-CAROUSEL-STATE-51`): the special teams coordinator job is vacant. Direction of the kicking game returns to Stone until a replacement is hired, as Document 3's special-teams rows provide for a material departure. Document 3 itself still names Lowry in its authority map; it is a foundation file and is not edited here (flagged for the user).
- `career/2013/season_review/owner_and_gm_review.md`: Entry 2's staff answer is corrected and Entry 4 appended, because the retroactive carousel places Lowry's departure and Bush's interview before the January 15 meeting. The retention decision is re-checked against the frozen criteria and stands.
- `career/2014/offseason/staff_changes/`: README, staff plan status and budget line; the first-pass interest assessment is kept as the ex-ante record.
- No player, roster, cap, calendar or draft-capital change.

**Label-swap check.** Every probability reads only the job, the coach's role and record, the clubs' branch records and the calendar. The permission policy applies alike to any asking club.

**Commit closed - Canonical update - February 2, 2014 - January 2014 coaching carousel resolved (Lowry to Atlanta) - canonical through February 2, 2014**

## Entry 76: 2013 exit interviews recorded (retroactive)

**Effective canonical state:** February 2, 2014 (no clock advance). The interviews are dated Monday January 13 and Tuesday January 14, 2014.
**Recorded:** September 28, 2026
**Checkpoint:** `Canonical update - February 2, 2014 - 2013 exit interviews recorded (January 13-14)`
**Preceding global package checkpoint:** `Canonical update - February 2, 2014 - January 2014 coaching carousel resolved (Lowry to Atlanta)`

**Decision.** The user asked for in-depth, comprehensive exit interviews and set the format:
- **Date:** January 13-14, 2014.
- **Tone:** an honest review with no promises.
- **Depth:** a full interview for the main core; a structured, in-depth report for the core; a summary for everyone else.

**Record.** `career/2013/exit_interviews/` holds 61 players: all 53 on the active roster and all 8 on the practice squad.
- **Main core** (13 full interviews, Monday January 13): `main_core/`.
- **Core** (27 structured reports, Tuesday January 14): `core/`.
- **Summaries** (21, Tuesday January 14): `summaries_offense.md`, `summaries_defense.md`, `summaries_practice_squad.md`.
- **Index:** `README.md` lists each player's date and the coaches present. It also collects the open program decisions for the user, the follow-ups and the staff findings.

**Method.**
- Each interview was written from the branch record only, then checked by a separate skeptical pass.
- The verification removed manufactured flaws, unsupported motives, draft and contract hints and misdated quotations. It also moved any live work out of Phase Two, where the CBA forbids it.
- No numeric rating appears. Statistics that the 2013 engine attributed at random are not used as evidence (sacks allowed by lineman, returners, coverage tackles).
- No real 2013 or later outcome was used.

**Reconciliation with Entry 75.** The carousel closed first and places Lowry's departure (January 12) and Bush's Indianapolis interview (January 14) before or inside the interview dates.
- Lowry attends no meeting. His follow-ups belong to the special teams coordinator, with Stone covering until the job is filled, and none is dated before February 2.
- Bush attends the Monday meetings but not Tuesday's.
- Stone told the specialists that Lowry had left and that his replacement was not decided.

**What changed.** Nothing in roster, role, contract, cap, medical or availability state:
- every exit physical is the medical staff's, and none recorded a finding;
- Stone promised no job, role, contract or roster spot;
- contract, tag, tender and roster questions were referred to Caldwell.
The user's February 2 memo to Caldwell (`career/2014/offseason/stone_to_caldwell_2014_offseason_decisions.md`) already answers the contract recommendations for the pending free agents, the futures and the trade candidates. The interviews disclosed none of them.

**Open for the user.**
- **Program decisions** for the 2014 phase plans, listed in the README: examples are the backup defensive caller, the long-term-injury plan, individual classified cutups, how rotation and depth-order evidence is communicated, and the end-of-half punt rules.
- **Follow-ups dated January 31, 2014:** individual film cutups from the position coaches. Their delivery is not recorded; whether the CBA lets staff send film before April 21 is unsourced.

**Companion manuscript.** The user's researched ownership review and press conference (`career/2013/season_review/stone_2013_review_and_exit_interview.md`, merged into this branch as pull request #122) was written before Entry 75. Its staff passages are corrected to Entry 75, with a dated note at the top: Lowry's departure, Bush's Indianapolis interview and the vacant special teams job. `owner_and_gm_review.md` remains the controlling record.

**Commit closed - Canonical update - February 2, 2014 - 2013 exit interviews recorded (January 13-14) - canonical through February 2, 2014**

## Entry 77: Special-teams authority and staff planning reconciled

**Effective canonical state:** February 2, 2014; the existing interim assignment applies from Lowry's January 12 departure. No clock advance.
**Recorded:** September 28, 2026
**Checkpoint:** `Canonical correction - February 2, 2014 - special-teams authority and staff planning reconciled`
**Preceding global package checkpoint:** `Canonical update - February 2, 2014 - 2013 exit interviews recorded (January 13-14)`

**Authority and scope.** The user requested assessment and improvement of the staff-change handoff, explicitly including Document 3's stale Lowry references, Stone's interim duties, the $6,950,000 payroll and the standing interview policy. This is an administrative correction of the Entry 75 dependency gap, not another carousel, appointment or delegation decision.

**Conflicting records and correction.** Entry 75, the current staff register and Document 4 already recorded Lowry's departure and Stone's interim control. Document 3 sections 4, 5 row 14 and 6.1 still named Lowry as current operator or incumbent. Those current references now reflect the vacant coordinator post and Stone's interim direction. Stone already held final authority under row 14; no new power is conferred. The generic phrase "material departures" concerned departures from an approved plan and did not itself appoint an emergency successor. Entry 75's express interim assignment is the controlling event. Emergency succession if Stone is unavailable remains unassigned.

**Payroll checked.** The eleven remaining 2014 contract rows sum to $6,950,000, also $7,575,000 less Lowry's removed $625,000. These are scheduled assistant salaries, not a spending ceiling, total football-operations cost or player-cap room. No numeric staff-budget ceiling or replacement salary has been established. The original contract schedule and Entry 75's treatment of Lowry's departure stand.

**Policy clarified, not changed.** For the January 2014 cycle, head-coach interview requests follow the applicable eligibility windows; Jacksonville grants them where required and voluntarily within a permitted playoff window. Position-to-coordinator interviews are voluntarily permitted after Jacksonville's season ends, even though they remain assistant-to-assistant moves under that era's rules. Same-job requests for contracted assistants are refused under the standing club policy. An expired or released contract is not a basis for Jacksonville to claim a veto. Interview permission is not an offer, a hire or the coach's acceptance. Other requests must be checked against the actual role and existing authority rather than assigned an invented permission decision. The frozen method and all closed requests, interviews and outcomes remain unchanged.

**Planning corrections.** `staff_plan.md` exists but has no selected targets or authorized offers. It now separates that missing decision from the existing role description, interim coverage, payroll commitments, unestablished hiring budget and candidate evidence. A current opening is not evidence that another club's coach is available; permission, contract status and availability must be checked at the actual approach date using branch records and permitted dated evidence.

**Dependency closure.** Document 3 becomes Rebuild draft 2.6; Document 4 becomes `JAX-2014-FEB02-STAFF-RECONCILIATION-REGISTER-36`; Document 5 becomes `JAX-2014-FEB02-STAFF-RECONCILIATION-STATE-53` with the exact new Document 3 Git-blob hash. Current staff prose and the staff-change README agree with those records. Earlier ledger entries, including the merged player exit interviews in Entry 76, and the frozen carousel artifacts are preserved verbatim. The corrected ownership/press manuscript is retained; section headings and index links make Alex Stone's press interview and the separate player interviews directly discoverable. No player, roster, cap, medical, calendar, draft-capital or game-result change; no replacement is selected or hired.

**Commit closed - Canonical correction - February 2, 2014 - special-teams authority and staff planning reconciled - canonical through February 2, 2014**

## Entry 78: Historical league rails adopted (2014 onward)

**Effective canonical state:** February 2, 2014 (no clock advance).
**Recorded:** September 28, 2026
**Checkpoint:** `Canonical update - February 2, 2014 - Historical league rails adopted (2014 onward)`
**Preceding global package checkpoint:** `Canonical correction - February 2, 2014 - special-teams authority and staff planning reconciled`

**Decision.** The user asked that the branch keep the same league of players as the real NFL. Other clubs' players should retire, sign and be drafted as they really were. The players Stone drafts come to Jacksonville, and the players the real Jaguars drafted go to the clubs that really drafted Stone's picks. Jacksonville's own contracts stay the branch's.

The user's choices:
- **Free agents Jacksonville pursues:** a market draw.
- **Retirements:** real dates apply league-wide, Jacksonville included.
- **Draft availability:** by real pick number.
- **Where the rule is written:** AGENTS.md and Document 2 both.

**Rule.**
- AGENTS.md, "Historical league rails", is the controlling text. Its hard-rule line now names this as the one standing exception to the no-hindsight rule.
- Document 2 adds §§4.3a and 4.5, and §12 notes the override for other clubs.
- Document 5 carries the new Document 2 hash.
- The 2013 background library already followed this pattern: real Week 1 charts, draft swaps, Jacksonville control first. The rule now states it in writing for 2014 onward.

**Method.** `career/2014/offseason/league_rails/method.md`:
- rails become usable only on their real public dates;
- Jacksonville control overrides every rail except retirement;
- market draw: the chance Jacksonville signs a free agent is 0 below a money index of 0.80, 0.50 at parity and at most 0.90, drawn through the private service at his real signing date;
- draft availability by real pick number, with Jacksonville's k-th selection paired with the real Jaguars' k-th selection.

The draw weights are a modelling choice and can be changed until the first draw.

**Built.** At the user's direction, the branch builds the structure and fills what it can; the user completes the rosters and contracts.
- `clubs/`: 31 draft club rosters, about 1,600 players, from the branch's 2013 Week 1 units, with contract years from Over The Cap data signed in 2013 or earlier. 316 players have no contract in the data, and every end year is unverified.
- `free_agent_pool.md`: 413 likely pending free agents.
- Empty records for retirements, the draft pairing and the market draws.
- No 2014 destination, term, trade or selection is recorded.

**Open check.** Whether any of Jacksonville's 61 controlled players announced a real retirement on or before February 2, 2014. A found retirement applies with its own ledger entry.

**What changed.** No roster, contract, cap, medical or result state.

**Commit closed - Canonical update - February 2, 2014 - Historical league rails adopted (2014 onward) - canonical through February 2, 2014**

## Entry 79: Meester retired; Allen retirement scheduled (league rails)

**Effective canonical state:** February 2, 2014 (no clock advance).
**Recorded:** September 28, 2026
**Checkpoint:** `Canonical update - February 2, 2014 - Meester retired; Allen retirement scheduled (league rails)`
**Preceding global package checkpoint:** `Canonical update - February 2, 2014 - Historical league rails adopted (2014 onward)`

**Decision.** The user asked to retire the confirmed players and to list the possible ones for verification. This is the retirement rule of the league rails (Entry 78).

**Research.** All 61 controlled players were searched in two passes for a real retirement announced from December 1, 2013 to December 31, 2014.

**Applied now.**
- **Brad Meester, C.**
  - He really announced on December 18, 2013 that he would retire at the end of the 2013 season. The date falls before the branch date, so the retirement applies now.
  - The branch weeks already closed are unchanged: he finished the season as reserve center.
  - He moves to Reserve/Retired and stays under control until his one-year contract expires March 11, 2014.
  - Active roster 52, controlled 53.
  - No cap effect.

**Scheduled.**
- **Russell Allen, LB.**
  - His real retirement is dated April 22, 2014 and applies when the clock passes that date.
  - Its real cause, a stroke in the real December 15, 2013 game, did not happen in the branch. The user chose to apply the retirement as the rule says.
  - The real April 17 release is a Jaguars move and does not apply.
  - The contract and cap effect is unresolved until verified.
  - Stone's trade package G (Allen for a 2015 seventh) cannot close after April 22.

**To verify (not applied).**
- Nwaneri, Rackley, Owens and Rutland are listed with "VERIFY" before their names in `career/2014/offseason/league_rails/retirements.md`.
- None has a dated public source.

**State.** Updated in the same commit: `career/2013/roster.md`, Document 4, Document 5, and `retirements.md`.

**Commit closed - Canonical update - February 2, 2014 - Meester retired; Allen retirement scheduled (league rails) - canonical through February 2, 2014**

## Entry 80: Cousins trade and draft capital reconciled

**Effective canonical state:** February 2, 2014 (no clock advance).
**Recorded:** September 28, 2026 (user's Eastern date; September 29 UTC).
**Checkpoint:** `Canonical correction - February 2, 2014 - Cousins trade and draft capital reconciled`
**Preceding global package checkpoint:** `Canonical update - February 2, 2014 - Meester retired; Allen retirement scheduled (league rails)`

**Controlling authority: explicit user correction.** The user clarified the original Cousins trade: Jacksonville sent its **2014 second and 2015 second**; Washington sent **Kirk Cousins and its original 2014 first**. This corrects the recorded compensation of the already-completed pre-draft 2013 trade. It is not a new negotiation, market draw, or transaction on February 2. Its exact original execution date remains unrecorded.

**Superseded claims.** Entry 5 and the prior completed-trade views recorded Cousins for Jacksonville's 2014 second alone. Entry 68's draft inventory omitted Washington's first. Those historical entries and the ex-ante authorization/recommendations remain intact; this correction controls current ownership. No revised offer, valuation, consultation, or acceptance dialogue is invented to make the earlier negotiation support the corrected terms.

| Stable asset | Correct current owner | Effect |
|---|---|---|
| Kirk Cousins | Jacksonville | Player control unchanged |
| Washington original 2014 Round 1 | Jacksonville | Branch overall No. 13 |
| Jacksonville original 2014 Round 1 | Jacksonville | Retained; branch overall No. 26 |
| Jacksonville original 2014 Round 2 | Washington | Branch overall No. 58; unconditional |
| Jacksonville original 2015 Round 2 | Washington | Unconditional; slot depends on the branch's 2014 season and is not known |

**Historical ownership exception, limited to this asset.** Washington had really transferred its 2014 first to St. Louis in the 2012 RGIII transaction, before branch divergence. This conflict was disclosed before the user's clarification. The user's corrected deal expressly controls the branch's Washington-origin 2014 first: Jacksonville owns it and St. Louis does not. This is a user-directed alternate-history ownership exception, not a claim that real Washington still owned the pick. No compensating Rams asset, rescission of the rest of the RGIII deal, or extra trade is invented. The source comparison and scope live in `library/2014_draft_order_verification.md`.

**Seven-round order.** All 224 ordinary slots are derived from the closed branch receipts. Equal-record clubs rotate within their elimination group, with the first club moving to the bottom each round. The Green Bay/Indianapolis coin flip stays unresolved in every affected round. Original club and recorded owner are separate. The verified pre-divergence Carolina 2014 seventh conveyed to San Francisco is carried forward; other clubs' unrecorded post-divergence transfers are not silently imported. Default original allocations are explicitly provisional for those clubs.

**Compensatory picks.** March 24 remains the announcement gate. Awards use **2013**, not 2014, qualifying free-agent activity. No real recipients or round counts are imported. Later overall numbers include explicit unknown compensatory offsets; no pending count is treated as zero. No forfeiture is recorded in the branch; a future recorded forfeiture needs reconciliation before the order can execute.

**Dependent records.** Completed trade views, the machine-readable pick register, generated seven-round order, 2014 index/calendar, rails order/pairing pointers and Documents 4/5 now agree. Documents 4/5 advance together to register 37 / state 56. Historical interview/review cost summaries remain dated evidence superseded by this entry. The user-authored draft board and trade offers are preserved: an extra first-round asset does not choose a prospect, and Seattle's own second now computes to No. 36 rather than the memo's No. 37; the precise intended asset must be reconciled before package A executes. No receiver trade is booked.

**Unchanged.** All seven exercised 2013 picks, player control, roles, contracts, cap charges, medical status, statistics, results, staff and the simulation clock. The existing Meester retirement leaves 52 active and 53 controlled, plus eight practice-squad players; stale active-count headers are reconciled to Entry 79 without a new roster event. The private snapshot must be advanced to the merged correction before any next simulated event; no private snapshot is advanced by this PR.

**Commit closed - Canonical correction - February 2, 2014 - Cousins trade and draft capital reconciled - canonical through February 2, 2014**


## Entry 81: Draft coin flip and league pick ownership reconciled

**Effective canonical state:** February 2, 2014 (administrative reconciliation; no clock advance).
**Recorded:** September 28, 2026 (Eastern; September 29 UTC).
**Checkpoint:** `Canonical correction - February 2, 2014 - Draft coin flip and league pick ownership reconciled`
**Preceding global package checkpoint:** `Canonical correction - February 2, 2014 - Cousins trade and draft capital reconciled`

**User authority and draw.** The user directed a website coin flip and a league-wide pick-ownership correction. Before drawing, heads was assigned to Green Bay and tails to Indianapolis. The one-coin RANDOM.ORG result was **0 obverse, 1 reverse (tails)** at **2026-09-29 01:42:47 UTC**. Indianapolis receives Round 1 slot **14**, Green Bay **15**. The locally committed protocol, structured result and screenshot are in `career/2014/draft/coin_flip.json` and `coin_flip_2026-09-29.jpg`. There was one draw, no reroll. This user-authorized administrative resolution is not a claim about an actual 2014 NFL ceremony. The recorded result now drives all seven rounds, preserving equal-record rotation and original-club asset identity.

**Ownership reconciliation.** The complete 224-asset audit is in `career/2014/draft/ownership_audit.md`, with dated source pairs and branch evidence. Pre-divergence consideration and consideration for trades already represented in the accepted 2013 background baseline are restored; this is bookkeeping for established acquisitions, not new negotiations. Closed branch receipts override conflicting historical midseason trades. The existing user exception for Washington's first remains controlling.

**Jacksonville correction.** The October 2012 Mike Thomas trade conveyed Detroit's original 2014 fifth to Jacksonville. That inherited asset was missing from Entry 80's inventory. Jacksonville now owns **eight ordinary 2014 picks**: Washington's first, its own first, its own third and fourth, Detroit's fifth, its own fifth, sixth and seventh. Washington still owns Jacksonville's 2014/2015 seconds. This adds no new trade or player movement. Donald remains Stone's recorded instruction for No. 13; the draft has not taken place.

**Branch conditions, not historical results.** Kansas City's closed 9-7 record satisfies the Alex Smith escalation, so its second goes to San Francisco and its third stays home. Arizona's QB1 and closed passing receipts support sixteen Palmer starts, satisfying the reported thirteen-start condition. Haralson and Shipley are in their receiving clubs' accepted opening rosters, satisfying the sourced roster conditions. Indianapolis keeps its first because Richardson remained in Cleveland; the historical Sopoaga, Beason, Levi Brown, Monroe and D'Anthony Smith transactions are not imposed on this branch.

**Three specific conditional claims remain open.** Revis requires one Tampa Bay pick, third if he is on its roster on March 13, otherwise fourth; neither alternative is free to spend pending resolution. Public sources do not disclose Benn's compensation round/threshold or Rosario's exact playing-time threshold. Philadelphia's original assets carry a single unresolved Benn claim, not seven debts; Chicago's seventh carries the Rosario claim. No historical injury, release or real-life non-conveyance is used to invent a branch outcome. Those affected assets are encumbered and blocked by the ownership guard. Every other ordinary allocation is reconciled; the old blanket outside-club warning is removed. Compensatory awards remain gated to March 24 and their offsets are preserved.

**Atomic closure.** The ownership register, renderer, seven-round order, ownership audit, 2014 calendar/index, rails pointers and Documents 4/5 now share this event. Register 38 / state 57 replace register 37 / state 56. Historical ledger entries and the frozen memo remain intact. Player control, contracts, cap charges, games, statistics, staff and the calendar do not change. Private snapshot binding must follow the merged correction before any simulated event; this PR does not advance that service.

**Commit closed - Canonical correction - February 2, 2014 - Draft coin flip and league pick ownership reconciled - canonical through February 2, 2014**


## Entry 82: 2014 operating handoff and readiness reconciled

**Effective canonical state:** February 2, 2014 (administrative correction; no clock advance).
**Recorded:** September 28, 2026 (Eastern; September 29 UTC).
**Checkpoint:** `Canonical correction - February 2, 2014 - 2014 operating handoff and readiness reconciled`
**Preceding global package checkpoint:** `Canonical correction - February 2, 2014 - Draft coin flip and league pick ownership reconciled`

**Authority.** The user requested the audited setup corrections and repair of PR #135's inconsistency. Its living coaching profiles and dated 2015 research are reconciled with the newer 2014 baseline. Research/preparation does not open a future information gate, execute a phase or confer an engine release.

**Corrections.** Five phase plans and their NOT_STARTED output/evidence records already exist; Stone is not assigned to write them. Bobby April is selected at the recorded offer limits, not hired. League research and dated roster preparation are operator work. Meester remains Reserve/Retired under Entry 79: the current baseline is 52 active plus one retired, and the contract register separates him from seven pending active UFAs. The eight legacy practice-squad names are retained as the prior closed baseline pending exact expiry/rights and actual futures reconciliation, not certified 2014 participants. No contract is silently ended or created here. The historical 2013 cap range is not 2014 spending authority; the new preparation worksheet stays UNRECONCILED. February 3's waiver/staff checkpoint precedes the February 17 tag window.

**Ownership and execution.** The repository map now distinguishes planning season 2014 from the still-current 2013 ledger/roster/staff/cap owners. New result-storage indexes contain no outcomes. Explicit season routing prevents new-season commands from silently selecting old inputs, caches, event identities or receipt destinations. The season-release gate separately blocks 2014 before private game closure while the documented engine, rules, financial/control, fixture, input and acceptance requirements remain open. The public free-agent record contains no private probability/draw fields. E1/E2 policy remains adopted; no result-changing kernel is released.

**Atomic closure.** Register 39 / state 58 replace register 38 / state 57. The live records and finance owner remain at their documented paths until a future audited 2014 activation. Earlier ledger entries, game receipts, statistics, ownership, actual contracts, staff appointments, roles and medical instructions remain unchanged. The clock is still February 2. No private snapshot is advanced from this branch; binding to the merged correction remains required before the next simulated event.

**Commit closed - Canonical correction - February 2, 2014 - 2014 operating handoff and readiness reconciled - canonical through February 2, 2014**


## Entry 83: February 2014 coaching exposure resolved (retroactive; no departures)

**Effective canonical state:** February 2, 2014 (no clock advance); events dated January 12 to February 17, 2014.
**Recorded:** September 29, 2026
**Checkpoint:** `Canonical update - February 2, 2014 - February 2014 coaching exposure resolved (no departures)`
**Preceding global package checkpoint:** `Canonical correction - February 2, 2014 - 2014 operating handoff and readiness reconciled`

**Authority.** Entry 75 declared a deferred procedure for Buffalo's and Minnesota's post-Super Bowl head-coach decisions. On September 29, 2026 the user asked, before any advance to February 17, for every resolvable poaching risk to Jacksonville's staff to be assessed, including coordinator openings at clubs that kept their head coach, which Entry 75 left unmodelled. The rules are `library/2014_coaching_hiring_and_anti_tampering_rules.md` section 8, as in Entry 75.

**Method, fixed before the draw.** `career/2014/offseason/staff_changes/carousel_deferred_method.json` was committed in b8812d2 before the draw, with `scripts/coaching_carousel_deferred.py`. Stage D1 used each Super Bowl club's recorded Entry 75 base-rate cell. Stage D2 used the sourced January 2013 cycle (`2013_retained_club_coordinator_turnover.md`, research and verification passes): 24 clubs that kept their head coach opened 5 offensive and 4 defensive coordinator jobs, and only 2 of 17 coordinator openings went to another club's sitting position coach. Every probability reads the job, the coach's role and record, the clubs' records and the calendar only; the same method for any employer gives the same probabilities. One private packet (event `2014-coaching-carousel-deferred-v1`, packet `27f11087`, result reference `20275e99`) drew every value in fixed structural order.

**Head coaches.** Buffalo kept Doug Marrone (change probability 4.2 percent, not drawn). Minnesota changed head coach (probability 2.5 percent, drawn); the vacancy opened February 3 and an external candidate was hired February 17. No real 2014 hire is imported and the new coach is not named.

**Coordinator openings.** Ten opened at clubs that kept their head coach: Chicago offense and defense (decided February 9), Cleveland offense (January 17), Dallas defense (February 9), Kansas City defense (January 18), New York Giants offense (January 17), New York Jets defense (January 18), Oakland offense (February 9) and defense (February 12) and Tennessee offense (January 18). Each could reach Jacksonville's staff.

**Requests for Jacksonville assistants.**
- **Frank Bush, Chicago defensive coordinator:** requested February 6; permission granted under Jacksonville's default policy (lateral under the 2013 rules but a step up in title); interviewed February 6; no offer. Chicago's February 9 decision went to another candidate. Bush stays.
- **Jeremy Bates, Minnesota quarterbacks coach:** requested February 17 by the new staff; refused as a move to the same job elsewhere (rule T3, default policy).
- **Mike Tice, Minnesota offensive coordinator:** requested February 17; refused on the same basis.

No other club asked for a Jacksonville assistant, and none left. Nothing was pending at February 17. Alan Lowry, already gone (Entry 75), was not a candidate.

**Atomic closure.** `requests_and_outcomes.md` (February section generated from `carousel_deferred_results.json`), the staff timeline and README, the staff register's Bush note, the 2014 calendar and Documents 4 and 5 now carry these outcomes. No contract, role, player, pick, cap figure or game record changes. The clock is still February 2, 2014.

**Commit closed - Canonical update - February 2, 2014 - February 2014 coaching exposure resolved (no departures) - canonical through February 2, 2014**


## Entry 84: Special teams coordinator hired (Mike Westhoff, February 11, 2014)

**Effective canonical state:** February 2, 2014 (no clock advance); events dated February 3 to February 11, 2014.
**Recorded:** September 29, 2026
**Checkpoint:** `Canonical update - February 2, 2014 - Special teams coordinator search resolved (Westhoff hired February 11)`
**Preceding global package checkpoint:** `Canonical update - February 2, 2014 - February 2014 coaching exposure resolved (no departures)`

**Authority.** Stone selected Bobby April on September 28, 2026 at a $700,000 opening and $800,000 ceiling (`career/2014/offseason/staff_changes/staff_plan.md`). On September 29, 2026 the user added the fallback order: Mike Westhoff, then Bruce DeHaven, each at a $625,000 opening and $750,000 ceiling on the common terms. Stone hires his own assistants within the funded staff budget (Document 3, authority row 2).

**Method, fixed before the draw.** `st_search_method.json` was committed in 10ba5f7 before the draw, with `scripts/st_coordinator_search.py`. One private packet (event `2014-st-coordinator-search-v1`, packet `599bb86f`, result reference `3ab39549`) drew in fixed order whatever the path. Each probability reads only the coach's employment status, the job and the calendar.

**April.** His January 2013 Oakland deal is treated as expiring after 2013, a labelled inference from ESPN's January 2014 report that assistants were offered one-year deals. Whether Oakland re-signed him before Jacksonville's approach was drawn at 13/16 = 0.8125, the retention rate of the other Oakland assistants whose decisions ESPN reported (his own outcome excluded): **re-signed**. Jacksonville requested permission on February 3; the lateral move (rule T3) was refused on February 4 under the symmetric default policy that applies to every club. He was not interviewed.

**Westhoff.** Retired from the Jets on December 30, 2012 and a 2013 media analyst, he was under no NFL contract, so no permission was needed. Contacted February 5. His willingness to return was drawn at a labelled 0.25 (no base rate was found; his one pre-cutoff statement left the door open): **willing**, February 7. Interviewed February 10. On February 11 Caldwell confirmed the allocation within the plan's ceiling, Jacksonville offered $625,000 a season, Westhoff countered for the ceiling, and the counter was met under Stone's instruction.

**Appointment.** Mike Westhoff is special teams coordinator effective **February 11, 2014**: **$750,000 a season for 2014 and 2015**, equal salaries, no signing bonus, first season guaranteed subject to offset, second season non-guaranteed, no added title, roster power or authority. DeHaven was not approached. Westhoff runs the kicking game (the role in `career/2013/coaching_staff.md` section 6) and reports to Stone, who keeps team priorities and consequential game management. Stone's interim special-teams direction (Entry 75) ends February 11. Existing player unit assignments stand until changed through the ordinary process. Emergency succession for a caller remains unassigned.

**Money.** Scheduled 2014 assistant salary becomes **$7,700,000** for twelve coaches ($6,950,000 plus $750,000); 2015 becomes $3,650,000 ($2,900,000 plus $750,000). Assistant pay is a club operating expense outside the player salary cap. Caldwell's confirmation covers this allocation only; no numeric staff-budget ceiling is established.

**Atomic closure.** `hires.md` (dated stages and the completed appointment), the staff timeline and README, the staff register (status, delegation, contract row, changes after execution, section 6), Document 3 (section 4, row 14, section 6.1, document control), Document 4 (register 40 replaces 39), Document 5 (state 59 at Entry 83, then 60 here, replacing 58), the 2014 calendar, README, readiness, operating baseline and the current-fact lines of the training plans now agree. Planning records keep their ex-ante content. No player, pick, cap or game record changes. The clock is still February 2, 2014; a later entry advances it to February 17. The private snapshot is not advanced from this branch.

**Commit closed - Canonical update - February 2, 2014 - Special teams coordinator search resolved (Westhoff hired February 11) - canonical through February 2, 2014**


## Entry 85: 2014 reserve/future contracts signed (six of eight)

**Effective canonical state:** February 2, 2014 (no clock advance); events dated February 3 to February 5, 2014.
**Recorded:** September 29, 2026
**Checkpoint:** `Canonical update - February 2, 2014 - 2014 reserve/future contracts signed (six of eight)`
**Preceding global package checkpoint:** `Canonical update - February 2, 2014 - Special teams coordinator search resolved (Westhoff hired February 11)`

**Authority.** Stone's February 2 memo, section 1 (`career/2014/offseason/stone_to_caldwell_2014_offseason_decisions.md`), recommends reserve/future contracts for Tyler Bray, Richard Murphy, Antwon Blake, Jerome Long, D'Anthony Smith and Jerrell Jackson at the 2014 minimum for each player's credited seasons, no guarantee and no signing bonus, and letting Brandon King and Will Ta'ufo'ou go. On September 29, 2026 the user asked for the reserve/future contracts to be run before the clock advances to February 17. Caldwell executes: six minimum camp contracts are within the memo and cost nothing that counts before the league year. His agreement is a stated reading, not a draw.

**Method, fixed before the draw.** `career/2014/offseason/futures_method.json` and `scripts/futures_2014.py` were committed in 8f85462 before the draw. All six offers went out on February 3, 2014. Under league rails method section 3, a player Jacksonville offers follows his real next move only if it is a dated move of the same kind in the same window. One private packet (event `2014-futures-contracts-v1`, packet `9bc36abe`, result reference `c9e39398`) made the one draw the method needed.

**Uncontested signings, February 3.** Bray, Murphy, Blake, Long and Jerrell Jackson had no dated competing move and signed on February 3. Jackson's real 2014 Kansas City contract is undated, so it cannot enter the branch (rails method section 2).

**Market draw, D'Anthony Smith.** His real Seattle reserve/future contract is dated February 5, 2014. Both contracts are taken as the minimum for the same credited seasons with no guarantee (the Seattle terms are an inference), so the method's ratio is m = 1.0 and Jacksonville's chance is 0.50. Jacksonville won the draw, and Smith signed on February 5. The real Seattle move does not occur in the branch.

**Not offered.** King and Ta'ufo'ou left as free agents when their practice-squad contracts ended. No later destination is imported for either.

**Terms.** Each of the six contracts is the 2014 minimum for the player's credited seasons, with no guarantee and no bonus. Each takes effect at the 2014 league year (March 11, 4:00 p.m. ET) and counts toward the 90-player limit from then. These are camp places, not practice-squad places. Bray has 0 credited seasons, so his base is $420,000 (Confirmed). For the other five, credited seasons are not established in the branch record, so each salary is recorded as "minimum for credited seasons, figure unresolved".

**Atomic closure.** The following now agree: the roster (practice squad 0, six reserve/future contracts), the contract status register, the 2014 preparation worksheet, `free_agency/signings.md`, `league_rails/fa_draws.md`, Seattle's rails page, one-line pointers in the futures page and living profiles, the film queue, the calendar, the readiness and operating baseline pages, and Documents 4 (register 41) and 5 (state 61). The 53 controlled players do not change, and no cap figure is certified. The clock is still February 2, 2014.

**Commit closed - Canonical update - February 2, 2014 - 2014 reserve/future contracts signed (six of eight) - canonical through February 2, 2014**
