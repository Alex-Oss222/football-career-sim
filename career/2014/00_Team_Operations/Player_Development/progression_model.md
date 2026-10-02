# 2014 offseason player-progression model

[Development index](README.md) · [Current progression cohort](progression_roster.json) ·
[2013 continuity index](2013_exit_player_index.json) ·
[Football-development research](../../../../library/player_development_research.md) ·
[Runtime primitives](../../../../runtime/player_progression.py)

## Purpose

The offseason progression system answers one question for every controlled
player:

> Based on who this player was in 2013, what could realistically be different
> about him when he reports for the 2014 season?

The answer is not an overall rating change. It is a collection of specific
physical, technical, processing, system, consistency, conditioning and role
changes, each with a football mechanism, evidence boundary and uncertainty.

The current roster is the eligibility authority. A player is not progressed
because he was drafted here, because he appeared in an old development file, or
because the staff remembers him. If he is controlled now, he belongs in the
cohort. If he has departed, his old development obligations remain historical
but he is not part of the live 2014 progression resolution.

## Current roster checkpoint

As of the current March 28, 2014 roster:

| Cohort | Count | Meaning |
|---|---:|---|
| Controlled players | 55 | Every live progression candidate at this checkpoint |
| Jacksonville 2013 continuity | 50 | Player appears in the frozen 2013 exit-review universe and remains controlled |
| Ordinary returning Jaguars | 44 | Returned from the 2013 roster/club-control group |
| Practice squad to reserve/future | 6 | Tyler Bray, Richard Murphy, Jerrell Jackson, D'Anthony Smith, Jerome Long and Antwon Blake |
| 2014 newcomers | 5 | Hakeem Nicks, Andrew Hawkins, Daniel Te'o-Nesheim, Alterraun Verner and Aqib Talib |

Kirk Cousins is explicitly in the returning cohort. The manifest is generated
from `career/2014/team/roster/roster.md`, not from the draft class.

Run:

```sh
python scripts/build_player_progression_roster.py --check
# after a roster/control change:
python scripts/build_player_progression_roster.py
```

A stale manifest is an error. Before progression is resolved for a later
offseason checkpoint, regenerate it after signings, releases, trades, tender
resolutions and draft additions.

## Player state is multidimensional

Every position uses the trait catalog in
`runtime/player_progression.py`. The catalog is divided into seven state
domains.

| Domain | What it represents | What it must not be confused with |
|---|---|---|
| Physical | Actual athletic/strength capacity relevant to the position | Technique, knowledge, anticipation |
| Technical | Learned movement and contact mechanics | Raw speed/strength |
| Processing | Recognition, diagnosis, decision speed and cue-to-response work | Playbook memorization alone |
| System | Terminology, rules, checks, communication and teammate timing | General football intelligence |
| Consistency | How reliably an existing ability appears across conditions | A higher peak ability |
| Conditioning | Work capacity, recovery and body-composition state | Generic toughness or motivation |
| Role | Responsibilities the staff is willing/able to assign | Better underlying ability |

The resolver itself still has no engine-wide overall value and no generic
awareness attribute. The separate annual personnel sheet may show a user-facing
`/10` summary grade, but that grade is not consumed by the resolver.

## Inherited player identity: start with the player he already is

A returning player does not become an unknown player because the season number
changed. The previous season's demonstrated capabilities are the default
starting state for the next season.

The runtime represents those with `EstablishedCapability` and
`PlayerIdentityState`. `carry_forward_identity()` preserves them before any
offseason transition is considered. A later development case is a delta from
that player, not a re-scout from zero.

Keep four ideas separate: capability, access/execution, consistency, and staff
certainty. A quarterback can retain the arm to drive a tight-window throw while
being late to recognize the window. A receiver can retain long speed while
running a poor route. A corner can retain recovery speed while recognizing the
route late. Those execution problems may change processing, technique or
consistency without rewriting the physical tool.

Established state changes only for a football reason with evidence. Missing new
evidence means **no demonstrated change**, not that the old capability vanished.
New acquisitions bring their established NFL football capabilities with them
when permitted evidence supports those capabilities; Jacksonville terminology,
teammate timing and role access may be new.

The annual history is stored in
[`career/YEAR/player_profiles/`](../../../player_profiles/README.md). Those
sheets make the 2013-to-2014-to-2015 progression readable without turning the
visible overall grade into an engine input.

## Whole-player context gate

Before any hidden trait change can be resolved, the runtime requires a complete
`PlayerDevelopmentContext`. It must explicitly consider all 15 categories
below for that player:

1. physical profile/development or decline;
2. technical state/development;
3. mental processing;
4. scheme and playbook familiarity;
5. position-specific skill;
6. previous-season experience gained;
7. consistency;
8. role;
9. conditioning and body composition;
10. age context;
11. coaching influence;
12. previous-season performance;
13. playing time and opportunity;
14. injuries and physical limitations;
15. existing strengths and weaknesses.

A category may be `unknown`, but it may not be omitted. Any supported
(non-unknown) assessment needs evidence identifiers. This makes missing
information explicit instead of silently replacing it with a generic average.
A trait-specific `DevelopmentCase` then references that whole-player context,
so the random transition cannot be resolved from age, draft status or one
highlight statistic in isolation.

## Evidence before change

Every player begins with an evidence packet. The packet is position-specific,
but the source hierarchy is common.

1. **2013 Jacksonville evidence for returners.** Exit-review observations,
   lawful practice/camp work, game-film locators, actual role and snap
   opportunities, medical restrictions and the player's own recorded
   perspective.
2. **Permitted pre-divergence public evidence.** Useful for establishing a
   physical/technical baseline where the branch has not observed the player
   directly.
3. **2013 branch experience.** A full season can establish situations
   encountered, role familiarity and shared language. The equal-strength
   engine's win totals and generated production do not establish talent.
4. **2014 transaction/medical facts.** They establish control, availability and
   contract/role context, not ability.
5. **Missing evidence remains missing.** It becomes uncertainty and an
   observation target, not an Average grade disguised as knowledge.

For 2014 newcomers, do not import their later real 2013 careers after the
branch divergence as an answer key. Their Jacksonville scheme familiarity
starts lower because they are new to this staff and terminology, but their
football ability is not reset to zero. Use the permitted baseline plus the
actual onboarding evidence the branch creates.

## Development case

A material trait change requires a `DevelopmentCase` with:

- player and position;
- one registered football trait;
- one or more mechanisms;
- dated/source evidence IDs;
- confidence;
- a football rationale;
- constraints or counterevidence where relevant.

Allowed mechanisms include deliberate practice, live reps, film study, scheme
continuity, coaching correction, strength/conditioning work, body-composition
change, injury recovery/limitation, accumulated mileage, role change, technique
transfer, game experience and player adaptation.

Age may be included as context. It cannot be the only mechanism.

Examples of legal causal statements:

- **QB:** 2013 exposure to the same protection language plus film work creates a
  plausible case for faster pressure identification. It does not create more
  arm strength.
- **WR:** repeated leverage/release work creates a plausible case for a better
  press-release plan. It does not imply more long speed.
- **CB:** improved route recognition can reduce reaction delay and make recovery
  look faster. It does not change the corner's true maximum speed.
- **DL:** better hand placement can improve shed efficiency or the long-arm
  without changing where the defender aligns.
- **OL:** improved twist recognition can reduce late exchanges while foot
  quickness stays the same.
- **Veteran:** age and mileage can raise concern about physical decline while
  film/system experience can still improve recognition or communication.

Illegal shortcuts include:

- age 30 therefore minus speed;
- second-year player therefore plus awareness;
- first-round pick therefore high potential;
- starter therefore better;
- 10 sacks therefore pass-rush technique improved;
- 12 interceptions therefore QB processing declined;
- same scheme therefore faster/stronger;
- new role therefore better player.

## Hidden state versus staff knowledge

The model has two different records.

### Private latent state

`PrivateTraitChange` is the resolved change in the simulation's hidden player
state. It can be substantial regression, slight regression, stable, slight
improvement or substantial improvement.

The repository code intentionally has **no default probability table**. A caller
must supply an externally calibrated `TransitionPrior` for the particular
case. This prevents arbitrary age curves, draft-status bonuses or hard-coded
"potential" from silently becoming canon.

The hidden change must not be written directly into coach-facing reports.

*Dated note (October 2, 2026):* by Stone's explicit decision, kernel 2014.6 adopts aging and experience curves pooled over 2010-2014, draft-slot starting estimates for players without a pre-2013 record, and a recorded once-per-season swing. They are fitted, externally calibrated priors on the engine's hidden player state, the calibrated-prior case this section requires, not a silent default. They are not transitions resolved by this model. They never enter coach-facing reports or staff grades, and no staff assessment reads them. See [Kernel 2014.6 decisions](../../../../runtime/2014_engine_decisions.md#kernel-20146-decisions-dated).

### Observed belief

`ObservedTraitUpdate` records what the staff/user can currently support. Its
visibility can be:

- unobserved;
- reported;
- non-contact observed;
- padded observed;
- game observed.

It also carries confidence and evidence locators.

This allows a player to have improved privately in March while the staff still
has low confidence in May. OTAs can raise confidence in processing, footwork,
communication or route rules. They still cannot certify a contact-dependent
skill that has not been tested in pads. Training camp and preseason can reveal
more. Regular-season evidence can change the belief again.

The observed direction can therefore differ from the hidden direction until
enough football evidence exists. That is uncertainty, not an error.

## Transition resolution

For each eligible player:

1. **Freeze the roster cohort** at the chosen offseason checkpoint.
2. **Build the 2013 evidence packet.**
3. **Create trait-specific development cases.** Most traits should remain
   stable unless there is a football reason to revisit them.
4. **Attach a calibrated transition prior** to each accepted case. Priors must
   be sourced/calibrated separately; the runtime supplies no invented default.
5. **Resolve private trait changes** with the common seeded random process.
6. **Do not reveal the private result.**
7. **Run actual offseason phases.** Record observations appropriate to that
   phase and its contact limits.
8. **Update staff beliefs** only from actual evidence.
9. **At camp/preseason handoff, compose the 2014 player profile** from the
   observed state and remaining uncertainty.
10. **Game integration uses the relevant job traits**, not an overall score.

A player with no accepted material-development case can still gain experience,
retain system knowledge or change role. That does not require inventing a trait
increase.

## Continuity

Continuity is a mechanism, not a reward.

For a returning player it can support:

- terminology retention;
- quicker recall of concept rules;
- protection/front/coverage communication;
- familiarity with teammate landmarks and timing;
- fewer assignment errors when the presentation is already known.

Continuity does not automatically improve:

- maximum speed;
- acceleration;
- change of direction;
- arm strength;
- anchor strength;
- catch radius;
- contact balance;
- any contact technique that was never corrected or successfully transferred.

A second-year player may recognize the same concept earlier and still execute
it poorly. The model records those as two different states.

## Age, mileage and injury

There is no fixed positional age multiplier in this layer.

Age affects the prior through relevant context:

- existing physical baseline;
- position and role;
- accumulated snaps/touches/contact exposure where supported;
- injury and surgery history actually known to the branch;
- current medical restriction;
- observed movement or strength change;
- recovery history;
- conditioning/body-composition evidence.

Mental and technical growth can coexist with physical decline. A veteran corner
may lose some true recovery speed while improving route-combination recognition
and leverage discipline. A veteran quarterback may gain protection/coverage
command while mobility or recovery capacity flattens. Neither side of that
statement is automatic.

Medical recovery is not player development. Clearance and limitation remain
medical facts. Technique can be re-taught around a restriction, but attendance
or work ethic cannot heal an injury by simulation fiat.

## Coaching

Coaching acts through mechanisms that can be observed:

- what the staff teaches;
- clarity of rules/cues;
- practice allocation;
- quality and timing of correction;
- whether the player receives appropriate reps;
- whether the correction survives changed presentations;
- whether the staff changes the job to fit the player.

There is no global coach-development bonus. A strong position coach can help
one specific technique while another unresolved shared rule remains a problem.
A bad initial teaching point can be corrected by the staff. Player development
and coach development are allowed to interact.

## Interconnected development

`INTERDEPENDENCIES` records football links, but a linked trait does not
automatically receive a rating change.

Examples:

- QB coverage-rotation confirmation can improve effective progression timing.
- QB drop footwork can improve placement without changing arm strength.
- WR leverage recognition can improve the release plan, stem and pacing.
- RB run-concept vision can improve patience and cut timing.
- OL twist recognition can improve exchange timing and reduce the need for
  late recovery.
- DL block recognition and hand placement can improve gap/shed execution.
- LB run-key recognition can improve pursuit and fit timing.
- CB route recognition can improve effective recovery while true speed is
  unchanged.
- Safety route-combination recognition can improve depth/angle decisions.
- Better conditioning can preserve late-rep execution without increasing peak
  ability.

Body-composition tradeoffs are conditional. Gaining functional strength does
not automatically cost speed or agility. If the player's actual body change or
movement evidence supports such a tradeoff, create a separate physical case for
it.

## Position-specific catalogs

The runtime registry contains separate catalogs for QB, RB/FB, WR, TE, OL,
DL, LB, CB, S, K, P and LS. The
[research note](../../../../library/player_development_research.md) explains the
coaching basis for those categories.

Important distinctions include:

- defensive-line alignment/role versus rush/block-defeat technique;
- corner hip-transition technique versus underlying hip mobility;
- quarterback system knowledge versus coverage processing versus throwing
  mechanics;
- offensive-line protection recognition versus foot/hand execution;
- running-back vision versus burst;
- receiver route craft versus speed;
- safety range expression versus true long speed;
- specialist operation timing versus raw leg strength.

## Consistency and role

Consistency is allowed to improve without changing peak ability.

Examples:

- a tackle repeats the same pass-set depth more often;
- a receiver hits the correct route depth more often;
- a QB's base remains intact on more pressure reps;
- a corner maintains leverage more consistently;
- a long snapper hits the target window more reliably.

Role can expand with or without ability growth. Coaches may trust a player with
more alignments because his assignment reliability improved. A roster shortage
may also expand his role without any development. The report must state which
one occurred.

## Required per-player answer

At the final offseason handoff, every controlled player's report must be able to
answer:

- What changed?
- Why is that change plausible?
- What stayed the same?
- What declined, if anything?
- What did the player actually work on?
- Which weakness remains?
- Did any new strength emerge?
- Did role scope change, and was that development or necessity?
- Did system understanding improve?
- Did the physical profile change?
- How confident is the staff?
- What 2013 evidence supports the case?
- What 2014 evidence has actually revealed the change?
- What should look different in games if the belief is correct?

If the evidence cannot answer one of those questions, the report says
**unknown** rather than filling the gap.

## Kirk Cousins

Cousins is not an exception to the roster rule; he is proof that the rule is
necessary. He appears in the live roster and the frozen 2013 exit universe, so
he is a returning progression candidate regardless of the original Jacksonville
draft class.

His existing 2013 film index provides the right starting questions. Candidate
development cases include:

- coverage-rotation confirmation;
- pressure and protection identification;
- progression timing;
- anticipation;
- decision quality under pressure;
- pocket movement;
- base/reset and its effect on placement;
- command of checks, cadence and receiver timing.

The system must not convert his interception or sack totals into causes. Review
the indexed plays, assignment and available answer. If the film supports a
processing issue, name the processing issue. If a protection failure was shared
or cannot be assigned, leave it unresolved. If he retained a corrected answer,
that is evidence of learning. Whether the offseason creates a further hidden
change is then resolved through the same calibrated transition process as every
other player.

## Release boundary

This commit creates the roster gate, trait taxonomy, causal validation,
uncertainty split and private transition interface. It does **not** complete E1
game-strength integration.

Before 2014 games can consume progression:

- calibrate position/trait transition priors without tuning to Jacksonville
  outcomes;
- create/store private per-player latent states outside public Git;
- build evidence coverage for the players/jobs actually used;
- connect relevant traits to lineup, assignment and matchup resolution;
- test that unrelated traits do not leak into a matchup;
- verify that hidden state is not exposed in coach-facing output;
- pass the existing E1 release gates.
