# Game Review Rating Scale

Use only integer ratings from `1/10` through `10/10`.

Anchor scale:

- `1`: absent, fundamentally broken, deceptive, unsafe, or not meaningfully reviewable
- `2`: barely present, with severe issues that block the player promise
- `3`: present but poor, with major quality failures a normal player would reject
- `4`: weak, incomplete, or clearly below the bar for the current stage
- `5`: functional but mediocre, visibly behind credible peers
- `6`: acceptable for the stage, with clear weaknesses still holding it back
- `7`: solid for the stage and broadly comparable to credible peers
- `8`: strong, polished, and competitive for the stage
- `9`: excellent, clearly above the expected bar and close to best comparable examples
- `10`: exceptional and rare; defensible against best-in-class peers for the chosen promise and stage

Scoring rules:

- Scores are relative to the game's current stage, but the benchmark is still real competition and player expectations.
- A higher stage does not excuse broken basics in safety, usability, controls, gameplay, or runtime stability.
- Do not use half points.
- Each dimension must receive exactly one rating and exactly one comment.
- Before scoring, apply the comparison method in [game-review-comparative-method.md](game-review-comparative-method.md).
- Before finalizing scores, apply hard maximums from [game-review-score-caps.md](game-review-score-caps.md). Caps override normal stage-aware scoring.

## How to calibrate a score

Think like a studio QA lead or a serious games reviewer, not like a supportive friend.

For every score, decide:

- what successful games are setting the quality bar for the submitted player promise
- what quality is required at this stage of development
- whether the game is below bar, at bar, or above bar on this dimension
- whether exposing this game to PlayDrop players would increase or damage trust

That means a `5/10` is not a polite score. It means the dimension works but is mediocre and visibly behind the competition. A `7/10` means the dimension is genuinely solid for the stage. An `8/10` or higher requires strong positive evidence. A `10/10` should be extremely rare.

Any score above `6/10` must be defended with positive evidence from the selected comparison set. Do not give high scores because the game merely launches, has visible UI, has assets, or contains the rough shape of a mechanic.

The CLI validator rejects outcomes when the scores do not support them. Do not fight that gate by inflating individual scores. Lower the outcome or explain the actual weaknesses.

Outcome score gates:

- `Passed`: average at least `6.0`, minimum at least `4`, and Gameplay, Controls, and Performance each at least `5`.
- `Good`: average at least `7.5`, minimum at least `6`, and Gameplay, Controls, UX, Visuals, and Performance each at least `7`.
- `Excellent`: average at least `8.5`, minimum at least `7`, Gameplay, Controls, UX, Visuals, and Performance each at least `8`, and FTUE at least `7`.

## What different scores usually mean in practice

### `1/10`

Use when the dimension is absent or failing at a level that breaks trust, basic playability, or product viability.

Examples:

- the game's primary verb is unavailable, such as a darts game with no way to throw the dart
- the core loop is functionally absent
- the controls are so unreliable that the game cannot be meaningfully judged
- the listing is deceptive about what the player will receive
- the safety or compliance issue is severe

### `2/10` to `3/10`

Use when the dimension technically exists but is clearly unacceptable for normal players.

Examples:

- the loop exists only as a toy interaction with almost no consequence, reward, pressure, or progression
- the camera or perspective prevents accurate play in a skill-based game
- first-session friction is high enough that many players would quit before meaningful play
- visuals are prototype-grade while the player promise is production-grade

### `4/10` to `5/10`

Use when the dimension is functional but below bar.

Examples:

- the controls work but lack precision, discoverability, or comfort
- the FTUE gets players in, but leaves the goal or primary action unclear
- the store listing is mostly honest, but metadata or media quality is sloppy
- the audio is serviceable but weak in communicating state or reward

### `6/10` to `7/10`

Use when the dimension is acceptable to solid for the current stage.

Examples:

- the game launches quickly, feels stable, and supports the declared input path
- the UI hierarchy is readable and supports play
- the core loop is understandable and satisfying enough for the intended session length
- the runtime holds up reasonably against direct peers, even with visible improvement areas

### `8/10` to `10/10`

Use only when the dimension is strong to exceptional against credible competition.

Examples:

- the controls and feedback feel genre-appropriate and highly tuned
- the FTUE communicates the promise with almost no wasted motion
- the listing and runtime align with unusual clarity and trustworthiness
- the game would be credible to feature or recommend based on this dimension
