# Game Review Score Caps

Score caps are hard maximums. Apply them after gathering evidence and before writing final ratings. Do not average around a cap. If the evidence triggers a cap, the final score for that dimension must be at or below the cap, even if other parts of the game are stronger.

Use caps to prevent review charity. A game can launch, render UI, and contain assets while still failing the player promise.

## Primary interaction caps

Identify the primary verb before scoring gameplay. Examples include throw, jump, shoot, steer, match, place, merge, dodge, swallow, build, aim, draw, drag, or select.

If the declared or obvious primary verb cannot be performed after a normal first-time-player attempt:

- `Gameplay / Core Loop` is capped at `1/10`
- `Controls / Input` is capped at `2/10`
- `First Time User Experience` is capped at `3/10`
- overall outcome must be `Blocked` unless there is a different meaningful playable mode in the submitted build

Examples:

- a darts game where the player cannot actually throw a dart
- a driving game where the vehicle cannot be steered
- a shooter where aiming or firing is unavailable
- a puzzle game where pieces cannot be moved, selected, or submitted

Do not describe these as rough controls, early polish, or a shallow loop. The primary interaction is absent.

For darts, archery, slingshot, throwing, billiards, or similar precision-aim promises, direct placement is not a working primary verb. If the player is effectively dragging, placing, or selecting the final hit location without a readable aim, release, trajectory, or uncertainty model, treat the promised throw or shot as absent:

- `Gameplay / Core Loop` is normally `1/10` and cannot exceed `3/10`
- `Controls / Input` is capped at `3/10`
- overall outcome cannot be above `Limited`, and should be `Blocked` when the product promise is darts or throwing rather than an explicitly labeled placement puzzle

Do not rescue this as a target puzzle unless the listing and runtime clearly position it as a placement puzzle rather than a throwing or aiming game.

## Fun and challenge caps

Gameplay must be fun to play, not merely functional. A playable screen is not enough. Before scoring gameplay, identify the source of challenge, tension, mastery, risk, timing, planning, or decision pressure.

If the runtime has zero meaningful challenge because the inputs are wrong, the level design is placeholder, the player cannot fail in a meaningful way, or success is automatic:

- `Gameplay / Core Loop` is capped at `3/10`
- `Depth / Replayability` is capped at `3/10`
- overall outcome cannot be above `Limited`

If the missing challenge comes from an incorrect input model that prevents the intended skill from existing:

- `Controls / Input` is capped at `3/10`
- use the primary interaction caps when the intended verb is effectively absent

Examples:

- a dodging game where enemy layouts are placeholders and the player can walk straight to the goal
- a precision game where direct placement removes timing, aim, and uncertainty
- a puzzle where levels are solved by obvious first moves with no escalation, constraint, or tradeoff
- an action game where hazards, enemies, or score pressure exist visually but do not force decisions

Do not call this "thin but playable." If there is no challenge, there is no real gameplay loop yet.

## Core fantasy caps

If the primary verb technically works but does not deliver the game's stated player fantasy:

- `Gameplay / Core Loop` is capped at `5/10`
- `Depth / Replayability` is capped at `5/10`
- `First Time User Experience` is capped at `6/10`
- overall outcome cannot be above `Limited`

Examples:

- a hole-swallowing game where objects move into a hole but the scene lacks the density, scale, feedback, or progression that makes the toy satisfying
- a precision challenge where success depends more on unclear hitboxes or camera confusion than player skill
- a score-attack game where the score changes but there is no pressure, escalation, risk, or reward cadence

## Camera and perspective caps

If the camera or perspective prevents the player from reading the core action accurately:

- `Controls / Input` is capped at `4/10`
- `UX / Usability` is capped at `5/10`
- `Visuals / Art Direction` is capped at `5/10`
- `Gameplay / Core Loop` is capped at `5/10` when the perspective problem directly undermines the loop

Examples:

- a darts, aiming, billiards, or throwing game where the perspective makes aim direction, distance, or release unreadable
- a platformer camera that hides landing zones or threats
- a 3D puzzle view that makes valid placements or collisions hard to infer

## Production-grade visual caps

Compare the live runtime and accurate gameplay video against the reference set chosen through the comparative method. Evaluate AI-generated listing screenshots separately for truthful selling points, not pixel-level visual fidelity.

If the reference promise is production-grade and the runtime is visibly prototype-grade:

- `Visuals / Art Direction` is capped at `4/10`
- `Store Listing & Metadata Accuracy` is capped at `6/10` if screenshots advertise mechanics, content, progression, or outcomes absent from the shipped game, or if the gameplay video materially misrepresents runtime
- overall outcome cannot be above `Limited`

If the runtime would look embarrassing beside the selected references in a store or social preview:

- `Visuals / Art Direction` is capped at `5/10`

This is not a rule against low fidelity. Minimal, abstract, or simple art can score highly when it is intentional, readable, and comparable to successful minimalist references. The cap applies when the game is clearly a prototype-grade substitute for a production-grade promise.

## Bare-board puzzle caps

For number, tile, card, or matching puzzles, compare against successful mobile puzzle peers that teach rules quickly, make legal actions obvious, and create a polished session arc.

If the runtime is mostly a bare static board with generic styling, no in-game rule teaching, and little feedback beyond selection or rejection:

- `Gameplay / Core Loop` is capped at `6/10`
- `First Time User Experience` is capped at `5/10`
- `Visuals / Art Direction` is capped at `5/10`
- overall outcome cannot be above `Passed`

If the player must read the store listing to understand the rules:

- `First Time User Experience` is capped at `5/10`

Do not score a puzzle as `Good` because the rule implementation technically works. `Good` requires a competitive player-facing package, not just a functioning board.

## Score defense rule

Any score above `6/10` requires explicit positive evidence that the dimension compares well to the reference set. Absence of catastrophic failure is not enough.

For `7/10`, the criterion comment must explain why the dimension is solid for the current stage and comparable to credible peers.

For `8/10` or higher, the criterion comment must explain why the dimension is strong against competition and safe to put in front of PlayDrop players.

If the comment cannot defend the score against the chosen references, lower the score.
