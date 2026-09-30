# Player-development research for the progression model

This note supports the football taxonomy in
[`runtime/player_progression.py`](../runtime/player_progression.py) and the 2014
[progression model](../career/2014/offseason/player_development/progression_model.md).
It is research about football development mechanisms, not an import of later
real-world player outcomes into the branch.

## Research boundary

The simulation's player-specific evidence rules still control. Later coaching,
biomechanics and analytics material may help name a technique or separate two
football mechanisms. It may not be used to say that a branch player later
became good or bad at that skill, suffered a future injury, changed body type,
or followed his real career.

The current roster determines who receives a progression case. The prior
season supplies experience, roles, dated practice observations and film
questions. Draft status, salary, age, box-score production and later reputation
do not substitute for those observations.

## General findings

### Offseason evidence has phase limits

The NFL/NFLPA offseason structure is deliberately teaching-heavy. Phase One is
limited to meetings, strength/conditioning and rehabilitation. Phase Two adds
individual/group instruction and perfect-play work but prohibits offense versus
defense and live contact. Phase Three permits OTAs, including 7-on-7, 9-on-7 and
11-on-11, but still prohibits live contact.

That makes the observation context part of the state model. A spring rep can
support learning, communication, footwork, route/coverage rules, movement
quality or retention. It cannot by itself certify a tackle, an NFL-caliber
press jam, a live pass-protection anchor, double-team survival, contested catch,
or other contact-dependent transfer.

Sources:

- [NFLPA: Offseason Rules](https://nflpa.com/active-players/off-season-rules)
- [NFL Football Operations: offseason workout program phases](https://operations.nfl.com/updates/football-ops/2023-nfl-offseason-workout-program-dates-announced)

### Separate athletic capacity, technique, processing and knowledge

Modern tracking and coaching analysis increasingly separates the assignment
from the result. NFL Next Gen Stats, for example, distinguishes run concepts,
individual blocking matchups, route/release classifications, pass rush and
protection rather than treating yards or a final outcome as a sufficient
description of player ability.

For this simulation, the important consequence is conceptual: a player can
know the rule and fail the technique; execute the technique and lose to a
better physical matchup; recognize the play early and therefore appear faster;
or possess unusual athletic tools while processing too late to use them.

Source:

- [NFL Next Gen Stats: expanded run, route, coverage, rush and protection
  modeling](https://www.nfl.com/news/next-gen-stats-new-advanced-metrics-you-need-to-know-for-the-2026-nfl-season)

### Age is a prior, not a verdict

Aggregate aging and learning curves are useful context, but they are vulnerable
to survivorship and selection bias. PFF's positional aging work explicitly
warns that older samples are dominated by players good enough to remain in the
league, while its learning-curve work finds substantial variation around the
average developmental path. Linemen, for example, can improve later than some
other positions, but no player inherits an automatic calendar upgrade or cliff.

The engine therefore uses age together with mileage, injury/medical evidence,
position, prior physical profile, role, workload and observed movement. Age
alone is not a legal mechanism for a trait change.

Sources:

- [PFF: positional aging curves and survivorship
  bias](https://www.pff.com/news/nfl-investigating-positional-aging-curves-with-pff-war)
- [PFF: athleticism and learning/aging variation](https://www.pff.com/news/nfl-investigating-athleticism-and-its-effect-on-aging-curves)

## Position research and model implications

### Quarterback

Quarterback development must split diagnosis from execution. Coverage
identification is not a single awareness value. A passer can improve at the
pre-snap structure, post-snap confirmation after rotation, pressure
identification, protection calls, progression timing and anticipation at
different rates.

USA Football's quarterback material treats pre-snap and post-snap thinking,
progression movement, footwork and release timing as connected but distinct.
Its coverage-identification teaching also emphasizes that a pre-snap picture is
only an indication and must be confirmed after the snap.

Progression traits therefore include:

- pre-snap structure identification;
- coverage-rotation confirmation;
- pressure and protection identification;
- hot/blitz answers;
- progression timing and anticipation;
- decision quality under pressure;
- drop, base/reset, sequencing and pocket movement;
- ball placement by throw area;
- terminology, concept rules, checks, cadence and receiver timing.

A faster mental answer can improve effective play speed without changing actual
running speed or arm strength. Cleaner feet can improve placement without
creating more arm talent.

Sources:

- [USA Football: pass-coverage identification](https://blogs.usafootball.com/blog/697/follow-this-formula-to-identify-pass-coverages)
- [USA Football: QB release, footwork, vision and decision
  grading](https://blogs.usafootball.com/blog/1292/an-objective-system-for-naming-a-starting-qb)
- [USA Football: progression reads](https://blogs.usafootball.com/blog/7291/basic-knowledge-about-reads)

### Running back and fullback

Running-back vision is teachable in relation to the blocking concept. Outside
zone, for example, can be coached through explicit reads of the blocker/defender
surface, track discipline, press-and-dip or press-and-cut answers and the timing
of the vertical cut. Pass protection adds separate balance, footwork, scan and
strike problems.

Progression traits therefore include:

- run-concept vision and blocker-surface reads;
- track discipline, patience and tempo;
- cut efficiency;
- contact balance and short-yardage body position;
- protection recognition, scan order, base and strike;
- route detail, catch technique and coverage adjustment;
- ball-security technique;
- conditioning and role breadth.

A runner can become a better decision-maker without getting faster. Strength or
body-composition change may help contact balance or protection, but an agility
tradeoff is not automatic and must have its own evidence.

Sources:

- [USA Football: developing outside-zone running-back
  vision](https://blogs.usafootball.com/blog/1618/here-s-a-strategy-to-help-running-backs-improve-vision-on-the-outside-zone-play)
- [USA Football/Miami Dolphins: running-back pass-protection
  drills](https://blogs.usafootball.com/blog/854/miami-dolphins-pass-blocking-drills-for-running-backs)
- [NFL.com: Rashad Jennings on offseason film review tied to runs, catches,
  blocks and system-specific cuts](https://www.nfl.com/news/rashad-jennings-offseason-training-rundown-0ap3000000468997)

### Wide receiver

Receiver development is leverage- and route-dependent. Beating press is not
simply winning the first yard. Release choice must fit the defender's leverage
and the route. Route pacing, stem manipulation and break efficiency are
different from long speed.

Progression traits therefore include:

- press-release plan, footwork and hand combat;
- leverage recognition;
- stem manipulation, pacing, depth and break efficiency;
- coverage recognition, zone spacing and route adjustments;
- catch technique, contested-catch technique and ball tracking;
- sideline technique;
- stalk/crack blocking;
- quarterback timing and formation/motion knowledge.

A receiver may become much more difficult to cover with unchanged timed speed
because his release plan, pacing and leverage manipulation improve.

Sources:

- [USA Football: press-release leverage and
  planning](https://blogs.usafootball.com/blog/7121/coaching-the-wide-receiver-the-press-release)
- [USA Football: press-release footwork and
  base](https://blogs.usafootball.com/blog/7150/coaching-the-wide-receiver-the-press-release-part-2)

### Tight end

The tight end is not one generic hybrid rating. NFL usage can require the same
player to execute in-line run blocks, move blocks, chips/protection and detached
receiver work. Development must preserve those jobs separately.

Progression traits therefore include:

- releases, route detail, coverage recognition and catch technique;
- in-line base, hand placement and leverage;
- move and second-level blocking;
- pass-protection set and chip/release timing;
- front/block-target recognition;
- alignment, motion, route and protection knowledge;
- the ability to carry multiple alignments without confusing role breadth with
  better execution.

Sources:

- [NFL.com: tight-end receiving/blocking and multi-alignment
  demands](https://www.nfl.com/news/q-a-delanie-walker-explains-the-rise-of-tight-ends-0ap3000000737655)
- [NFL.com: in-line blocking technique remains a distinct pro tight-end
  skill](https://www.nfl.com/news/pipelines-to-the-pros-tight-ends)

### Offensive line

Offensive-line development is highly technical and shared. USA Football
resources separate kick-slide footwork, lateral recovery against stunts, hand
accuracy, independent hand strikes, zone-combination work, double teams and
second-level blocking.

Progression traits therefore include:

- pass-set angle and kick-slide efficiency;
- lateral recovery, balance and anchor;
- hand placement, punch timing and independent hands;
- drive, reach, combination, pull and second-level techniques;
- front, protection, twist/stunt and blitz-exchange recognition;
- protection and combination communication;
- conditioning and positional versatility.

A sack cannot identify which one failed. A guard can know the twist exchange
and still lack the foot quickness to recover. A tackle can improve his hands
while the same edge speed remains difficult.

Sources:

- [USA Football: offensive-line technique resources](https://blogs.usafootball.com/blog/7315/resources-to-help-you-learn-offensive-line-play)
- [USA Football: zone combination footwork, aiming points and
  communication](https://blogs.usafootball.com/blog/1344/answering-the-5-most-common-questions-in-zone-combinations)

### Defensive line

Alignment and technique are separate. A 3-technique, nose, 5-technique or wide
alignment describes where a defender is placed and usually implies assignment
rules. It is not a pass-rush move.

Defensive-line coaching material separates get-off, hand placement, gap
control, block shedding, footwork, rush progression and combinations of rush
moves.

Progression traits therefore include:

- stance/get-off, strike timing, hands, pad level and leverage;
- block recognition, run/pass key and gap discipline;
- shed and double-team technique;
- rush plan and protection-tendency recognition;
- bull rush, speed-to-power, rip, swim, club, chop, long arm and counters;
- rush-lane/contain discipline;
- conditioning and alignment/role scope.

Sources:

- [USA Football: pass rush, gap control, hand placement and
  shedding](https://blogs.usafootball.com/blog/7869/podcast-pass-rush-gap-control-and-hand-placement-e-j-whitlow-defensive-line-coach-at-miami-university-ohio)
- [USA Football: defensive-line get-off and hand
  placement](https://blogs.usafootball.com/blog/583/streaming.usafootball.com)

### Linebacker

Linebacker play combines key-reading with block destruction and coverage.
Running-back flow and guard action can establish the fit; the defender still
has to stay square, destroy the block and finish. Coverage adds drops, matching,
route recognition and communication.

Progression traits therefore include:

- run keys and backfield-flow reads;
- gap-fit discipline and pursuit angles;
- hand use and block destruction;
- tackling;
- zone-drop and pattern-match rules;
- man technique and route recognition;
- play-action recognition;
- blitz timing and pass-rush hand use;
- front/coverage/pressure checks and communication.

Source:

- [USA Football: inside-linebacker flow reads and block
  destruction](https://blogs.usafootball.com/blog/5988/teaching-running-back-flow-reads-to-inside-linebackers)

### Cornerback

Corner development requires distinct press, off and bail solutions. Press
teaching includes stance/alignment, leverage, patient feet, eyes, hand timing
and the transition once the receiver declares. Route recognition can reduce
reaction delay, but it does not increase true long speed.

Progression traits therefore include:

- press stance, footwork, jam timing and mirror technique;
- off-man and bail footwork;
- hip-transition technique versus underlying hip mobility;
- leverage and eye discipline;
- route and receiver-tendency recognition;
- pattern matching, zone landmarks and checks;
- recovery technique, playing through the hands and ball tracking;
- tackling and block defeat;
- outside/slot/travel role scope.

Source:

- [USA Football: press-corner stance, leverage, eyes, footwork and hand
  technique](https://blogs.usafootball.com/blog/952/training-the-eyes-of-a-defensive-back-in-press-coverage)

### Safety

Safety development depends on formation and route-combination recognition,
rotation and match rules, communication, spacing and angles. Pattern-match
systems illustrate why the safety must recognize receiver distribution and make
or receive calls before the route becomes a simple one-on-one assignment.
Play-action discipline can be taught through explicit keys.

Progression traits therefore include:

- formation and route-combination recognition;
- rotation rules and deep-field positioning;
- pattern matching and zone spacing;
- man technique;
- angles, range expression and ball tracking;
- play-action recognition;
- communication and checks;
- run support, block defeat and tackling;
- post, split-field, box and slot role scope.

Sources:

- [USA Football: pattern-match Cover 3, safety rotation, calls and play-action
  keys](https://blogs.usafootball.com/blog/5615/blank)
- [USA Football: match-coverage communication and leverage
  rules](https://blogs.usafootball.com/blog/7313/setting-the-front-in-match-coverage-man-free-with-zone-principles)

### Specialists

Specialists need their own mechanics and operation relationships.

For punters, the drop, steps/get-off, contact point, hangtime-distance tradeoff,
directional location and plus-territory control are separate skills. For long
snappers, peer-reviewed biomechanics research links release mechanics and body
positioning to snap velocity and accuracy. Kicker evaluation similarly needs to
separate leg strength from approach, plant, swing/contact, launch control and
the snap-hold operation.

Progression traits therefore include:

- **K:** approach, plant, swing path, contact, launch/trajectory control,
  directional kickoff, operation timing and pressure repeatability.
- **P:** catch/mold, drop location, steps/get-off, contact, hangtime-distance
  control, directional and plus-territory placement.
- **LS:** set position, release mechanics, velocity, target accuracy,
  spiral/rotation, punt versus placekick trajectory, protection transition and
  coverage work.

Sources:

- [USA Football: punter mechanics, quick release, directional and hang-time
  considerations](https://blogs.usafootball.com/blog/5400/how-to-guide-for-punters-and-special-teams-coaches)
- [Journal of Strength and Conditioning Research/PubMed: long-snap
  biomechanics](https://pubmed.ncbi.nlm.nih.gov/26203735/)
- [Earlier long-snap biomechanics and accuracy study](https://pubmed.ncbi.nlm.nih.gov/16287369/)

## Modeling consequences

The research supports five rules used by the implementation:

1. **No overall progression number.** Change occurs per football trait and job.
2. **No automatic age curve.** Age changes the prior only alongside real
   physical, medical, mileage and performance evidence.
3. **No automatic transfer.** A linked trait can change effective execution
   without changing the underlying athletic trait. Related effects remain
   hypotheses until observed.
4. **No spring overclaim.** Evidence is tagged by observation context. Contact
   transfer waits for padded/game evidence.
5. **No result-as-cause shortcut.** A sack, interception, completion, rush
   average or tackle can locate a review play. It does not identify the
   technical or cognitive mechanism by itself.
