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
