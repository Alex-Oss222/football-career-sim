# 2013 Jacksonville player-sheet research

All 61 final 2013 sheets retain the January 14, 2014 exit-review cutoff and
position-specific baseline format. Kirk Cousins remains the previously reviewed
worked example. The remaining 60 now have completed branch-source reviews,
recorded regular-season and separate playoff production, qualified historical
production context, and a separate same-player comparison where identity can
be established. At the user's subsequent explicit request, each remaining
overall and position-trait row now has an exact theoretical staff grade. The
number states the evaluator's view of the 2013 player; it does not claim a
verified physical measurement, a historical film score or a future ceiling.

## Evidence and reproducibility

The [frozen exit index](../career/2014/team/player_development/2013_exit_player_index.json)
owns membership, position and source paths. The [branch findings](../career/2013/player_profiles/review_findings.json)
preserve conclusions from those exit interviews, independently of historical
counterparts. Individual strengths and unresolved corrections keep the scope
of the recorded work: a retained spring correction is not a full-season grade,
and a practice-squad or inactive decision is not an observed talent finding.
The staff-view descriptions are separately identified hypotheses. Exact grades
live in the final sheets. The renderer reads those entered grades and preserves
them; it does not calculate them from box scores, workouts or real counterparts.

The [historical research artifact](data/2013_player_sheet_benchmarks.json)
preserves player identifiers, 2013 regular-season totals, derived rates,
qualified means and tied extremes, filtered workouts, and source URLs with
SHA-256 hashes of the downloaded files. These are research data, never runtime
rating inputs. Rebuild with `python scripts/research/build_2013_player_sheet_benchmarks.py SOURCE_DIR`
after downloading the four named CSV files; then run
`python scripts/research/complete_2013_player_sheets.py`.
Use the latter's `--check` mode to verify the reviewed sheets without editing.

Sources are the [nflverse player-stat release](https://github.com/nflverse/nflverse-data/releases/tag/stats_player),
[2013 rosters](https://github.com/nflverse/nflverse-data/releases/tag/rosters),
[snap counts](https://github.com/nflverse/nflverse-data/releases/tag/snap_counts)
and [archived workouts](https://github.com/nflverse/nflverse-data/releases/tag/combine).
Field definitions are documented in the [player-stat dictionary](https://nflreadr.nflverse.com/articles/dictionary_player_stats.html)
and [snap-count dictionary](https://nflreadr.nflverse.com/articles/dictionary_snap_counts.html).
Only season 2013 / REG statistical rows enter the references. Postseason rows
do not enter regular-season means or the same-player comparator.

## Qualified production references

These opportunity thresholds define this research sample. Except for the NFL
passing qualification, they are disclosed analytical cutoffs, not claims about
official leaderboard rules. Average means the unweighted mean of qualifying
individual-player rates or counts, not the league's opportunity-weighted total.
Top and low preserve ties. Passing rating uses the standard clipped four-component
formula. Ratios use their recorded opportunities; a zero denominator is missing
rate evidence, never a zero rate.

| Position | Metric | Minimum regular-season opportunity |
| --- | --- | --- |
| QB | CMP%, Y/A, passer rating | 224 attempts (14 per scheduled team game) |
| RB | Yards/carry | 100 carries |
| RB | Catch rate, yards/catch | 20 targets |
| FB | Catch rate, yards/catch | 10 targets |
| WR | Catch rate, yards/catch | 40 targets |
| TE | Catch rate, yards/catch | 30 targets |
| K | Field-goal make rate | 20 attempts |
| P | Gross average, inside-20 percentage | 40 punts |
| DE, DT, LB, CB, S | Sack, interception and pass-defense counts | 300 defensive snaps |
| OT, G, C | Participation context only | 300 offensive snaps |
| LS | No comparable snap-quality pool recovered | Unassessed |

Position grouping follows the historical source, with T/OT, NT/DT,
ILB/OLB/MLB/LB and FS/SS/S normalized. Historical DB rows enter CB or S only
when the name and snap-position join resolves uniquely. The LB group mixes
off-ball and edge roles; defensive counts are not role-adjusted rates or
individual coverage/rush grades. The same-name C.J. Wilson DE and CB are
resolved by position; Mike Brewster's historical name is Michael Brewster.
Linemen absent from the outcome dataset may have participation-only rows
recovered through roster identity and a unique position/name snap join. Outcome
counters in those rows stay missing; offensive snaps are not blocking grades.
Where present, counterpart birth dates are checked against the verified index.
An absent or ambiguous counterpart means no historical participation claim.
Antwon Blake's historical CB classification does not overwrite his branch S role.

Branch samples below the relevant threshold have no qualified peer standing.
Branch defensive snaps were not preserved, so defensive qualification is
unknown even where counts can be displayed descriptively. Branch G means
game-day active, not starts or measured snaps. Historical participation
definitions may differ. A receiver's catch rate depends on targets and throws;
yards/catch depends on routes and opportunity. Neither is a hands, separation
or route-running grade. All-distance field-goal percentage is not accuracy by
distance, and gross punt average is not hang time, net control or direction.

The archived 40-yard-dash subset requires real 2013 roster membership and a
test year no later than 2013. Position is the testing archive's position, which
may differ from the player's 2013 role. Testing methods and years vary, roster
coverage is incomplete, and these measurements do not establish current
branch speed, post-injury recovery, football quickness or absolute league
fastest/slowest players. They appear only when at least eight tests exist.

## Limits of the branch evidence

The 2013 engine assigned sacks allowed randomly among dressed linemen and
defensive credit through role/depth shares. It sampled punting outcomes from
a historical field-position pool. Those totals remain recorded history but
cannot establish individual blocking, tackling, coverage or punting technique.
Cause-unclassified fumbles, intercepted targets and kick misses stay cause
questions; they cannot automatically be assigned to carriage, receiver or
snap/hold flaws. Current physical measurements and comparable position-specific
trait-film scales were not recovered in this research pass. Consequently the
60 newly reviewed cards label their exact numerical entries as theoretical
staff judgments. Their technical comparison yardsticks are personnel standards:
6.0 viable starter, 9.0 elite and 3.0 low-end trait. Those standards are not
measured historical peer means or scores. The number is definite; the judgment's
confidence and the recorded facts remain distinct.

Regular-season production comes from the existing club statbook. Playoff
production is independently aggregated from Jacksonville's Wild Card and
Divisional receipts, using the existing statbook formatter. Returns and other
recorded counters stay descriptive and do not establish a specialist role.
No current roster, contract, medical state or career date changes in this pass.

## Format from 2014 onward

The restored [2014-onward template](../foundation/templates/player_sheet_2014_onward_template.md)
retains the earlier overall card and **vs. Average / vs. Best / vs. Worst**
comparisons, established state and year-over-year change. It carries separate
full position-specific regular-season and playoff statistics tables at the
bottom, starting with 2014 and appending 2015, 2016 and each later season.
Missing data stays Unrecorded; future play stays Not played. Only recorded
branch statistics enter those yearly rows. The 2013 baseline template and
completed-season timing rule remain in force.
