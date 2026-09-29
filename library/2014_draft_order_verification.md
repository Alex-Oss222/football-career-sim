# 2014 branch draft order: rule and ownership verification

**Current-status supplement, Entry 81:** the website coin flip is resolved (Indianapolis 14, Green Bay 15) and all 224 ordinary assets have been audited. Jacksonville now has eight ordinary picks, including the previously omitted Detroit fifth. [Current ownership audit](../career/2014/draft/ownership_audit.md) supersedes the coin/blanket-provisional status below. Three specific conditional claims remain, as do March 24 compensatory awards. The original research below is preserved as Entry 80 history.


Researched September 28–29, 2026; applied at the unchanged February 2, 2014 branch checkpoint, ledger Entry 80. This document verifies procedure and eligible historical ownership. It does not import the real 2013 standings, 2014 draft order, selections, compensatory recipients or post-divergence trades.

## Two-pass rule check

The first pass located the 2014-era NFL procedure; an independent second search located an earlier NFL bulletin and checked the direction of rotation. Both publications agree: two tied clubs alternate; in a larger tied segment the first club goes to the bottom and the others move up. Apply the rotation to equal winning percentages within the existing playoff-elimination grouping, not merely to clubs still tied on strength of schedule. A different elimination round remains a different priority group.

| Source | Publication | Finding used |
|---|---|---|
| [NFL bulletin on Titans.com, “Titans to Pick 11th in 2014 NFL Draft”](https://www.tennesseetitans.com/news/titans-to-pick-11th-in-2014-nfl-draft-12310955) | December 30, 2013 | Group ranges, SOS and division/conference sequence, coin flip, top-to-bottom rotation |
| [NFL bulletin on Raiders.com, “Preliminary Draft Order Announced”](https://www.raiders.com/news/preliminary-draft-order-announced-6732652) | January 2, 2012; updated February 28, 2012 | Independent pre-divergence confirmation of the same procedure |
| [Patriots.com, “2014 Patriots Draft 101”](https://www.patriots.com/news/2014-patriots-draft-101-197921) | 2014 draft explainer | Discrepancy: its bottom-to-top wording reverses the NFL bulletins. Not used for rotation direction |

No real club order printed alongside those rules enters the calculation. Runtime inputs are the branch's 256 regular-season and eleven postseason receipts. The currently unresolved Green Bay/Indianapolis tie stays a pair of mutually exclusive slot possibilities; alphabetical display order cannot settle it. Both possibilities rotate through the six-club non-playoff 8-8 segment in later rounds. No coin flip was drawn by this research.

## Compensatory boundary

[Steelers.com, “Compensatory picks: A mystery/history,” March 24, 2014](https://www.steelers.com/news/compensatory-picks-a-mystery-history-12801380) explicitly identifies **2013 offseason** qualifying losses/signings as the input year for 2014 awards. [The NFL announcement reproduced by Houston, March 24, 2014](https://www.houstontexans.com/news/texans-awarded-3-compensatory-picks-12804697) confirms the announcement date and the supplemental selections. Only procedure/date is used. The 32 supplemental choices, their allocation among rounds 3–7, and branch recipients are not filled from the real award list.

The old renderer's reference to 2014 free agency was wrong. In the generated table, `C3` means the still-unknown number appended after Round 3; later offsets accumulate only earlier rounds' compensatory choices. Thus Jacksonville's ordinary Round 3 pick is 90, while its Round 4 pick is `122 + C3`. These are explicit expressions, not estimates or zero-valued placeholders. There are no recorded branch forfeitures. Compensatory awards, forfeitures and any subsequent ownership changes must be reconciled before executing affected selections. The unpublished formula weights and fill mechanism remain unresolved in the original financial-rules library; this work does not invent them.

## Ownership evidence and the user correction

| Asset / claim | First pass | Independent check | Branch disposition |
|---|---|---|---|
| Washington's original 2014 first was sent to St. Louis before divergence | [NFL.com, “Teams finalize blockbuster deal for No. 2 pick,” March 14, 2012](https://www.nfl.com/_amp/teams-finalize-blockbuster-deal-for-no-2-pick-09000d5d827984a7) | [Washington team site, “No Insider Trading For No. 2 Overall Pick,” September 14, 2012](https://www.commanders.com/news/no-insider-trading-for-no-2-overall-pick-8264513) | **Explicit user exception:** Jacksonville now owns the Washington-origin 2014 first under the corrected Cousins deal; St. Louis cannot also own it. No other part of the historical RGIII trade is changed here |
| Carolina's original 2014 seventh was conveyed to San Francisco for Colin Jones | [NFL.com, August 31, 2012 report](https://amp.nfl.com/news/colin-jones-traded-by-san-francisco-49ers-to-carolina-panthers-0ap1000000057372), attributing the year/round to the Charlotte Observer | [49ers release, August 31, 2012](https://www.49ers.com/news/49ers-release-21-players-trade-s-jones-8133732) confirms the trade but calls the pick undisclosed; independent search of the [Panthers' 2013 media guide](https://library.sfo2.cdn.digitaloceanspaces.com/publications/football/yearbooks/FCARPMG-2013-carolina-panthers-media-guide.pdf), Colin Jones bio, explicitly identifies the 2014 seventh | Carry this pre-divergence ownership forward; no real overall number or eventual selected player imported |

Verification limits: the Panthers media-guide claim was available in indexed text; the full PDF reader rejected its size. The 49ers transaction index lists August 30 while the contemporaneous release/report and indexed guide say August 31. The register therefore identifies the reported date, not a newly certified execution timestamp. Other clubs' complete post-divergence pick-trade chains have not been reconciled. Their original allocations are labelled provisional, not asserted to be their real February 2014 holdings. The historical roster rails do not silently replace the branch draft order or authorize arbitrary pick transfers.

The completed Cousins deal is a branch fact established by the user's clarification, not an online historical fact: **Cousins plus Washington's 2014 first to Jacksonville, Jacksonville's 2014 and 2015 seconds to Washington**. The original pre-draft execution date remains unspecified. Earlier ledger entries, frozen strategy and interviews retain their historical text and are superseded as to acquisition cost by Entry 80. The current machine-readable ownership source is [pick_ownership.json](../career/2014/draft/pick_ownership.json); the renderer regenerates every current pick table from it.

## Planning implications, not executed transactions

Jacksonville has ordinary 2014 selections at 13 and 26, then its own Round 3–7 slots. Its original Round 2 at 58 belongs to Washington, as does its unnumbered 2015 second. Adding the first does not assign a prospect or rewrite Stone's frozen board. The draft pairing's `k` is the order of picks Jacksonville actually exercises; the second first-round selection is `k=2` if the inventory is unchanged at the draft.

The corrected Houston/Seattle rotation puts Seattle's original second at **36**, while Stone's preserved package A memo calls it **37**. These are competing identifiers in an unexecuted offer. Reconcile the intended asset with Stone before communicating/executing package A; this accounting correction neither changes the offer automatically nor books a return. The original asset, not a copied old overall number, must identify every pick in a future trade receipt.
