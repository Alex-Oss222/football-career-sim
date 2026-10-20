# NFL head-coach career simulator: May–June and training-camp design handoff

**Design packages, not execution.** GitHub `Alex-Oss222/football-career-sim` was inspected read-only at `75fd41fbfc5ed0363d9f6cb68b5bef37a6583f24` on October 20, 2026. The career still stands at October 5, 2014 after the Week 5 game. Weeks 6–17 and any 2014 postseason results remain future, and neither 2015 spring nor 2015 camp was simulated. No GitHub change is included or recommended as already applied.

## Findings to enforce first

1. **2011 CBA, not a modern rewrite.** In the 2014–15 era, Phase Three OTC/OTA and mandatory veteran minicamp activities are non-contact. Seven-on-seven, nine-on-seven and eleven-on-eleven against an opposing group are lawful without contact; opposed one-on-ones and shells are not. The voluntary OTA and mandatory veteran camp rules differ. The actual 2011 CBA has separate daily-duration rules for ordinary non-OTA activity, Appendix G OTAs and Article 22 minicamp. Training camp begins with restricted day one and no pads/contact on days two and three, followed by one legal padded session per day under Article 23 time/rest limits. See both source registers.
2. **Use actual historical Jacksonville dates, not their outcomes.** 2015 OTAs were announced for May 26–28; June 1–2 and 4; June 8–9 and 11–12, with June 16–18 mandatory minicamp. The real club ultimately held nine OTAs, but Stone's simulated completed count is unknown. The initial 2015 camp public announcement on July 7 provides July 31 first practice, August 5 first full pads and August 8 scrimmage; the remaining exact daily camp sessions are not supplied by that publication. On October 5, 2014 Stone has not received a July 2015 public announcement.
3. **One observed source, one authority owner.** `Offseason_Training/OTAs/training_report.md` and `.../Mandatory_Minicamp/training_report.md` own their separately conducted football work; new `OTA_Report.md` summarizes and links without duplicating assessments. `Training_Camp_and_Preseason/Training_Camp/training_report.md` and game outputs own camp/game evidence. Each genuine battle card owns its own comparisons and eventual dated result. The team's current depth data own the chart, which the phase `Depth_Chart.md` renders. A staff recommendation is never a transaction.
4. **Authority is not optional.** Stone chooses practice, group opportunities, depth and staff under his contract and standing instructions. Caldwell chooses contracts, cuts, trades, acquisitions and the draft. Medical staff determine diagnosis and clearance. The 2014 staff list and player assignments cannot simply be projected into 2015 without the intervening career results.
5. **Events never aggregate.** An active phase briefing can receive several inserts, which can be answered on one shared response journal, but every separately concluded trade inquiry, rejected offer, unsuccessful hiring pursuit, player transaction or independent battle closure must have its one correct dated readable result at its own department/position-card owner. The phase view only links these files.
6. **No practice-result magic.** The repo contains detailed already-completed 2014 sessions, not a validated general procedure for generating future 2015 on-field observations. An approved protagonist-blind method or actual recorded inputs are required before any new result. No arbitrary scores, role promotions, guaranteed improvement, coach dialogue or medical clearance are allowed.

## What the two new design packages contain

- `01_OTAs_and_Minicamp/`: `OTA_Brief`, `My_Install_Plan`, `OTA_Report`, an event-result reference, a full integration contract with **58 proposed tests**, evidence-anchored 2014 three-page Jacksonville illustration, source register, repository assessment and README.
- `02_Training_Camp_Position_Battles/`: `Position_Battle_Report`, `My_Depth_Calls`, `Depth_Chart`, an individual battle-result reference, integration contract with **68 proposed tests**, 2014 six-battle illustration, source register, repository assessment and README.

All placeholders in the coach-page templates are *authoring instructions* only. A deployed page includes actual verified and relevant football facts, not template brackets, technology labels or unknown figures disguised as facts. The specs are technical and intentionally separate.

## Precise six-workflow checklist

| # | Workflow | Research/template status | GitHub deployment |
|---|---|---|---|
| 1 | April Offseason Program | Previously completed design package | Not established by this work |
| 2 | NFL Draft | Previously completed design package | Not established by this work |
| 3 | May–June OTAs and mandatory minicamp | **Design package complete here** | Not installed here |
| 4 | Training Camp Position Battles | **Design package complete here** | Not installed here |
| 5 | Each Preseason Game | **Still remaining** | Separately design briefing, Stone's game plan, per-game report |
| 6 | Final Roster Cuts | **Still remaining** | Separately design Caldwell's roster-cut report, Stone's recommendations and Final 53 |

**Quality gate:** Both packages need dedicated runtime implementations and their proposed tests run on a separate, explicitly approved future GitHub change. Their current contents do not authorize the next simulation event.
