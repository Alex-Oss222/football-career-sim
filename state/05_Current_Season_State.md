# Current Season State

**Document status:** Mutable canonical snapshot; replace rather than append
**Version:** `JAX-2013-MAY15-OTA1-STATE-3`
**Supersedes:** `JAX-2013-MAY05-RECONCILED-STATE-2`
**Readiness:** OTA block 1 is closed with roster control, participation, provisional football evidence and availability synchronized. The unchanged May 5 Top-51 worksheet remains the financial authority.
**Must be read:** In full before every simulation response.
**Simulation status:** Jacksonville has completed all prior closed events plus May 13-15 OTA block 1. OTA block 2 has not begun.
**Snapshot effective:** May 15, 2013, after OTA block 1 and before the May 20 OTA opening.
**Last reconciled:** September 19, 2026; season-ledger Entry 10.
**Global package checkpoint:** `Canonical update - May 15, 2013 - OTA block 1 closed`.
**Preceding global package checkpoint:** `Canonical correction - May 5, 2013 - roster/cap/calendar reconciled`.

## Effective source-version manifest

| Canonical document | Effective version | Current pointer |
|---|---|---|
| Document 1 | `697208640886f9f63581f4b865f917f16007f036` | Project instructions unchanged |
| Document 2 | `4dcdaa9bb3812ffe47b1bc7007dda73204cbc170` | 2013 rules/sourcebook unchanged by this correction |
| Document 3 | `9538b8e4831eba1a407c394a37c21972f8b8e290` | Stone/Jacksonville authority map unchanged |
| Document 4 | `JAX-2013-MAY15-OTA1-STATE-3`; branch content closed by Entry 10 | 64-player control, OTA participation/availability and provisional role evidence |
| Document 6 | 2013 ledger through Entry 10 | OTA block 1 progression authority |

## 1. Master clock and competition position

| Field | Current canonical value |
|---|---|
| Master date/time | May 15, 2013, after OTA block 1 close |
| Time zone | America/New_York |
| League/season | NFL, 2013 |
| Team | Jacksonville Jaguars |
| Head coach | Alex Stone |
| Season phase | Offseason; OTA block 1 complete; OTA block 2 not begun |
| Record | 0-0; regular season not begun |
| Last football event | May 13-15 OTA block 1 |
| Last canonical update | Entry 10 OTA block 1 close |
| Next football event | **May 20-21 OTA block 2** |
| Current football focus | Refresh next-event medical communication, retain/re-teach OTA block 1 corrections, then execute only the May 20-21 portion of `offseason/otas/plan.md` |
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
| May 13-15 | OTA block 1 | Complete |

### Remaining offseason and preseason

| Date/window | Event |
|---|---|
| **May 20-21** | OTA block 2 |
| **May 23** | OTA day |
| **Jun. 4-7** | OTA block 3 |
| **Jun. 11-13** | Mandatory veteran minicamp |
| Jun. 14-Jul. 21 | Pre-camp individual preparation / no invented club practice |
| **Jul. 22** | Rookies and quarterbacks report; acclimation/physical/conditioning preparation |
| Jul. 23-24 | Rookie/QB preparation before full-team report |
| **Jul. 25** | Full team / veterans report to training camp |
| Jul. 26-Aug. 3 | Published opening full-team training-camp practice sequence and Aug. 3 stadium scrimmage |
| Aug. 5-8 | Verified post-scrimmage camp practice/walkthrough sequence |
| **Aug. 9, 7:30 p.m.** | Preseason 1 vs Miami |
| Aug. 12-14 | Verified training-camp practices |
| **Aug. 15** | Walkthrough; 2013 training camp concludes |
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

- Every controlled player has received the established welcome/standards material and complete active 2013 Iteration I playbook; required individual follow-up for veterans without a prior closed onboarding record was completed before participation.
- May 13-15 teaching was limited to common operation; Power, Inside Zone, Stick and Drive; base protection communication; base defensive fits/coverage exchange; and core special-teams language.
- Cousins, Meester, Shorts and Posluszny supplied the clearest unit-operation evidence. Johnson, Poyer and Moore carried useful rookie evidence into veteran work. Trawick and Thielen added provisional multi-unit special-teams evidence.
- Open corrections remain for Kelce's run-block fit, Bray's cadence/progression timing, Henne's changed-picture reset, Rambo's substitution call and the interior line's changed-presentation combinations. Tice simplified the relevant language; Crennel postponed added pressure disguise.
- No depth chart, quarterback order, workload/target share, package place, final special-teams assignment or roster outcome was awarded.
- The full-team OTA family dinner occurred May 15 under voluntary, private and non-evaluative rules.

## 7. Medical / availability boundary after OTA block 1

- Qualified staff cleared Daryl Smith for the May 13-15 assigned work; he completed it without a communicated restriction.
- Brent Grimes attended meetings and medically directed rehabilitation/individual work but was withheld from team periods. No new diagnosis or return date was communicated. Reassessment is due before the next block.
- Every other controlled player was cleared for assigned May 13-15 work and participated. No new injury or restriction was communicated.
- All participation clearance remains event-bounded; ordinary medical communication precedes May 20 work, and no coach may override it.

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
| May 13-15 OTA block 1 | Participation/availability and provisional football evidence closed; no transaction, permanent depth decision or cap change |

## 9. Live-game checkpoint

**Game underway:** No.

There is no score, possession, game clock, timeout, challenge, game-day active list or cumulative 2013 game statistic to resume.

## 10. Immediate next step

The simulation is positioned to enter the **May 20-21 OTA block 2** after ordinary next-event medical communication. May 20-21 has not been run.

No roster-control or cap-accounting uncertainty blocks the next OTA block.

## 11. Snapshot replacement rule

After any state-advancing transaction, medical event, OTA/camp event, roster decision or game:

1. write the event/result to its owning career file and season ledger;
2. update roster/control/cap/availability records affected by it;
3. recalculate Document 4;
4. replace this snapshot;
5. reconcile calendar and deadlines;
6. keep plan files durable rather than appending results to them;
7. run a contradiction scan before closing the new global checkpoint.
