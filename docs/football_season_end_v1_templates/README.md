# Season ends: ownership review and club decision

**Design proposal, not installed in the repository.** Applies after Jacksonville's **actual final game of an NFL season**, whether that is Week 17 or a postseason game. No 2014 ending has been played or presumed by these documents.

## Reader-facing files

| Proposed file | Owner | What it does |
|---|---|---|
| `Season_Review_Briefing.md` | Khan and Caldwell, with evidence supplied by the football department | Gives Stone their communicated concerns and the questions they want answered. It does **not** announce a decision they have not made. |
| `My_Response.md` | Stone | Holds Stone's actual account of the football year and any request he deliberately makes. |
| `Club_Decision.md` | Khan and Caldwell | Records the club's completed employment decision and its actual consequences. |

The existing `career/YEAR/Season_Review/season_review.md` **is a different document**, the football-department's team season report. It remains in place and owns the detailed offensive, defensive, special-teams, player-development and coaching review. The proposed `Season_Review_Briefing.md` deliberately has a different filename to avoid a case-insensitive clash with that established owner. Alter the registry and links together when implemented.

## Supporting files

- `Implementation_Spec.md` gives the decision gates, authority boundaries, chronology, independent ownership decision method, validation and regression tests.
- `2013_Precendent_and_2014_Setup.md` shows what can be stated from the closed 2013 review and 2014 evidence **without fabricating a 2014 outcome or owner conversation**.

## Governing distinctions

1. The **club** decides whether Stone stays, with which existing terms, and whether it wishes to make a new offer. Stone does not decide his own retention.
2. A **meeting** is not mandatory. The owner may issue a lawful employment decision before meeting the coach. In that case record the real decision, do not generate fake prior discussion or an answered `My_Response.md`.
3. Being **retained** does not mean getting a raise, extension, new authority or guaranteed employment for another year. Such changes need real offers, approval and signatures.
4. A separate extension negotiation, hiring request, staff appointment, assistant exit, trade or player contract is a **separate event** with its **own dated output**, even if introduced in this briefing and answered through `My_Responses.md`.
5. If employment ends, stop showing confidential Jacksonville briefings to Stone and route the next genuine career decisions to his agent/career view.
6. The existing 2013 closed decision must not be revised and the 2014 outcome must not be preselected.

Read the implementation specification before attempting to use these Markdown files with the current parsers. This is a template design only; it does not advance game time or alter any canonical record.
