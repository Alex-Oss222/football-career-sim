# Current Season State

**Document status:** Mutable canonical snapshot; replace rather than append  
**Version:** `JAX-2013-MAY05-RECONCILED-STATE-2`  
**Supersedes:** `JAX-2013-ROOKIE-MINICAMP-SNAPSHOT-1`  
**Readiness:** Roster control, current contracts, May 5 Top-51 planning room and the full 2013 calendar are reconciled. Current OTA participation still requires ordinary medical communication.  
**Must be read:** In full before every simulation response.  
**Simulation status:** Jacksonville has completed free agency, two pre-draft trades, the seven-pick draft, four UDFA signings, all seven drafted-rookie contracts, and May 3-5 rookie minicamp. OTAs have not begun.  
**Snapshot effective:** May 5, 2013, after rookie minicamp and before the May 13 OTA opening.  
**Last reconciled:** September 19, 2026; season-ledger Entry 9.  
**Global package checkpoint:** `Canonical correction - May 5, 2013 - roster/cap/calendar reconciled`.  
**Preceding global package checkpoint:** `Canonical update - May 5, 2013 - rookie minicamp closed`.

## Effective source-version manifest

| Canonical document | Effective version | Current pointer |
|---|---|---|
| Document 1 | `697208640886f9f63581f4b865f917f16007f036` | Project instructions unchanged |
| Document 2 | `4dcdaa9bb3812ffe47b1bc7007dda73204cbc170` | 2013 rules/sourcebook unchanged by this correction |
| Document 3 | `9538b8e4831eba1a407c394a37c21972f8b8e290` | Stone/Jacksonville authority map unchanged |
| Document 4 | `JAX-2013-MAY05-CONTROL-RECON-2`; branch content `027f793aca2a90400f53302473888e7b8601fc58` | 64-player current control, contracts and cap reconciliation |
| Document 6 | 2013 ledger through Entry 9 | Correction/supersession authority |

## 1. Master clock and competition position

| Field | Current canonical value |
|---|---|
| Master date/time | May 5, 2013, after rookie minicamp close |
| Time zone | America/New_York |
| League/season | NFL, 2013 |
| Team | Jacksonville Jaguars |
| Head coach | Alex Stone |
| Season phase | Offseason; rookie minicamp complete; OTAs not begun |
| Record | 0-0; regular season not begun |
| Last football event | May 3-5 rookie minicamp |
| Last canonical update | Entry 9 roster/cap/calendar correction; no new football event |
| Next football event | **May 13-15 OTA block** |
| Current football focus | Verify current medical participation status, complete onboarding for the corrected 64-player roster, then execute `offseason/otas/plan.md` |
| Current calendar | `career/2013/calendar.md` |
| Historical calendar source | `library/2013_jacksonville_master_calendar.md` |

## 2. Calendar control

The controlling Jacksonville calendar is now built through the entire 2013 season and conditional postseason.

### Completed / historical checkpoints

| Date | Event | Branch status |
|---|---|---|
| Jan. 15 | Stone accepts Jacksonville job | Complete |
| Late Jan. | Staff build | Complete |
| Mar. 12 | League year / branch FA batch | Complete |
| **Apr. 2** | Official offseason program begins | Historical date corrected; phase was not separately simulated |
| Apr. 16-18 | Additional voluntary veteran minicamp | **Missed branch phase; do not retroactively simulate** |
| Apr. 25-27 | NFL Draft | Complete |
| May 2 | Seven drafted-rookie contracts executed | Complete |
| May 3-5 | Rookie minicamp | Complete |

### Remaining offseason and preseason

| Date/window | Event |
|---|---|
| **May 13-15** | OTA block 1 |
| **May 20-21** | OTA block 2 |
| **May 23** | OTA day |
| **Jun. 4-7** | OTA block 3 |
| **Jun. 11-13** | Mandatory veteran minicamp |
| Jun. 14-Jul. 21 | Pre-camp individual preparation / no invented club practice |
| **Jul. 22** | Rookies and quarterbacks report; acclimation/physical/conditioning preparation |
| Jul. 23-24 | Rookie/QB preparation before full-team report |
| **Jul. 25** | Full team / veterans report to training camp |
| Jul. 26-Aug. 3 | Published opening full-team training-camp practice sequence and Aug. 3 stadium scrimmage |
| **Aug. 9, 7:30 p.m.** | Preseason 1 vs Miami |
| **Aug. 17, 7:30 p.m.** | Preseason 2 at New York Jets |
| **Aug. 24, 7:30 p.m.** | Preseason 3 vs Philadelphia |
| **Aug. 27, 4:00 p.m.** | Reduce roster to 75 maximum |
| **Aug. 29, 7:30 p.m.** | Preseason 4 at Atlanta |
| **Aug. 31, 6:00 p.m.** | Reduce Active/Inactive list to 53 |
| **Sep. 1, noon** | Waiver-claim window closes; eight-player practice squads may begin |
| **Sep. 4** | Regular-season cap compliance; offseason Top-51 treatment ends |

### Regular season

| Week | Date/time | Jacksonville game |
|---:|---|---|
| 1 | Sep. 8, 1:00 p.m. | vs Kansas City |
| 2 | Sep. 15, 4:25 p.m. | at Oakland |
| 3 | Sep. 22, 4:25 p.m. | at Seattle |
| 4 | Sep. 29, 1:00 p.m. | vs Indianapolis |
| 5 | Oct. 6, 1:00 p.m. | at St. Louis |
| 6 | Oct. 13, 4:05 p.m. | at Denver |
| 7 | Oct. 20, 1:00 p.m. | vs San Diego |
| 8 | Oct. 27, 1:00 p.m. ET | vs San Francisco, Wembley Stadium |
| 9 | Nov. 3 | BYE |
| 10 | Nov. 10, 1:00 p.m. | at Tennessee |
| 11 | Nov. 17, 1:00 p.m. | vs Arizona |
| 12 | Nov. 24, 1:00 p.m. | at Houston |
| 13 | Dec. 1, 1:00 p.m. | at Cleveland |
| 14 | Dec. 5, 8:25 p.m. | vs Houston |
| 15 | Dec. 15, 1:00 p.m. | vs Buffalo |
| 16 | Dec. 22, 1:00 p.m. | vs Tennessee |
| 17 | Dec. 29, 1:00 p.m. | at Indianapolis |

**Trade deadline:** Oct. 29, 4:00 p.m. ET.

Conditional postseason dates are Jan. 4-5, Jan. 11-12, Jan. 19 and Feb. 2, 2014. Jacksonville reaches them only if branch results qualify the club.

Historical schedule dates/opponents are rails only. No real 2013 Jaguars score or outcome is imported.

## 3. Current roster control

Authoritative current player detail: `state/04_Roster_and_Staff_Register.md`.  
Readable roster: `career/2013/roster.md`.

| Reconciliation step | Count |
|---|---:|
| Correct Jan. 15 inherited control | 67 |
| March 12 free agents not retained | -15 |
| Branch releases | -4 |
| Branch outside FA additions | +4 |
| Post-FA controlled roster | **52** |
| Cousins acquisition | +1 |
| Gabbert-for-C.J. Wilson | 0 net |
| Pre-draft controlled roster | **53** |
| Seven draftees | +7 |
| Four UDFAs | +4 |
| **Current May 5 controlled roster** | **64** |
| Offseason maximum | 90 |
| **Open offseason places** | **26** |

The old 75-player working count and the old inherited-control uncertainty bucket are superseded.

### Contract/right corrections

Four pre-divergence December 30 reserve/future contracts are included in inherited control:
John Parker Wilson, Ryan Davis, Brandon King and Will Ta'ufo'ou.

Fifteen old 2012 roster names are no longer Jacksonville-controlled because their prior rights/contracts expired March 12 and this branch did not tender or re-sign them:
Kyle Bosworth, Eben Britton, John Chick, Derek Cox, Greg Jones, Terrance Knighton, Rashean Mathis, Antwaun Molden, Jordan Palmer, Jalen Parmele, Zach Potter, George Selvie, Jordan Shipley, Keith Toston and Steve Vallos.

No later real destination is imported.

## 4. Current contracts and cap

### Branch veteran agreements

The six March agreements remain:

- Sen'Derrick Marks: 1 year, $1.50M.
- Alan Ball: 1 year, $1.00M.
- Brad Meester: 1 year, $1.50M.
- Roy Miller: 2 years, $5.00M.
- Daryl Smith: 2 years, $6.00M.
- Brent Grimes: 1 year, $5.50M fully guaranteed.

Gross scheduled 2013 cap for those six: **$13.75M**.

### Drafted rookies

All seven signed May 2.

| Player | Pick | 2013 cap |
|---|---:|---:|
| Lane Johnson | #2 | $3,854,836 |
| Travis Kelce | #33 | $994,382 |
| Jordan Poyer | #64 | $572,794 |
| Sio Moore | #98 | $529,257 |
| Lavar Edwards | #135 | $458,403 |
| Bacarri Rambo | #169 | $437,205 |
| Tyler Bray | #208 | $422,225 |
| **Gross** | | **$7,269,102** |

Net May 5 drafted-rookie Top-51 effect: **$4,134,102**.

### UDFAs

Brynden Trawick, A.J. Bouye, Adam Thielen and C.J. Anderson each have a three-year minimum contract:

- 2013: $405,000;
- 2014: $495,000;
- 2015: $585,000;
- signing bonus: $0;
- additional guarantee: $0.

Current Top-51 effect: **$0**.

### Current room

The current transaction-aware worksheet includes:

- final 2013 league cap normalization;
- March free-agent contracts and Top-51 displacement;
- four branch releases;
- Cousins;
- Gabbert bonus acceleration;
- C.J. Wilson;
- all seven drafted contracts;
- four UDFA contracts.

**May 5 Top-51 planning room: approximately $7.0M-$7.4M.**

The old `~$8.35M` figure is stale and must not be used as current room.

The range is the correct precision. Do not invent an exact dollar where the historical starting club-room source and Aaron Ross branch timing do not support it.

Recalculate on any transaction and at the August 27, August 31 and September 4 accounting checkpoints.

## 5. Staff and authority

Current staff register: `career/2013/coaching_staff.md`.

| Function | Current owner |
|---|---|
| Head coach / team football authority | Alex Stone |
| Offensive coordinator | Mike Tice |
| Offensive play caller | Alex Stone |
| Defensive coordinator / caller | Romeo Crennel |
| Special teams coordinator | Alan Lowry |
| Personnel / contracts / cap / draft | David Caldwell, with Stone consultation as established in Document 3 |
| Depth chart / football roles | Stone within eligibility and medical limits |
| Medical diagnosis and clearance | Qualified medical personnel |

No staff authority or contract changed in Entry 9.

## 6. Football development state

- Every current Jacksonville player may receive and study the complete active 2013 Iteration I playbook.
- "Installed" means formally taught/repped team football, not hidden pages.
- Rookie minicamp installed only the bounded work recorded in its output.
- OTAs must use `career/2013/offseason/otas/plan.md`.
- Personnel use, reps, touches, roles and eventual roster outcomes are determined by football evidence, health, matchup and coaching judgment, never by preset playbook percentages.
- Family-inclusive team events follow the established phase plans and remain non-evaluative.

## 7. Medical / availability boundary before OTAs

The eleven drafted/UDFA rookies completed May 3-5 rookie minicamp without a new communicated restriction. That event-specific status is not permanent clearance.

Before May 13 OTA participation:
- medical staff communicate current football-use status for the controlled roster;
- Smith's signing medical review is not practice clearance;
- Grimes retains Achilles uncertainty and requires current participation status;
- no coach can override medical restrictions.

This is the remaining immediate operational gate. It is not a roster-control or cap-legality gap.

## 8. Controlling decisions

| Decision/event | Current effect |
|---|---|
| Stone accepts Jacksonville offer | Head coach / authority unchanged |
| Staff hired | Current operating staff continues |
| March FA batch | Six agreements, two declines, four releases |
| Cousins acquisition | Cousins controlled; 2014 second belongs to Washington |
| Gabbert/Wilson trade | Gabbert out, C.J. Wilson in |
| Seven-pick 2013 draft | All seven selected players signed May 2 |
| Four UDFAs | All four under three-year minimum contracts |
| May 3-5 rookie minicamp | Event results preserved; no depth job awarded |
| Entry 9 correction | Calendar, roster control, rookie contracts and May 5 cap state corrected without rerunning football |

## 9. Live-game checkpoint

**Game underway:** No.

There is no score, possession, game clock, timeout, challenge, game-day active list or cumulative 2013 game statistic to resume.

## 10. Immediate next step

The simulation is positioned to enter the **May 13-15 OTA block** after current medical participation communication and normal onboarding/contact for the corrected 64-player controlled roster.

No roster-control or cap-accounting uncertainty now blocks onboarding or OTA planning.

## 11. Snapshot replacement rule

After any state-advancing transaction, medical event, OTA/camp event, roster decision or game:

1. write the event/result to its owning career file and season ledger;
2. update roster/control/cap/availability records affected by it;
3. recalculate Document 4;
4. replace this snapshot;
5. reconcile calendar and deadlines;
6. keep plan files durable rather than appending results to them;
7. run a contradiction scan before closing the new global checkpoint.
