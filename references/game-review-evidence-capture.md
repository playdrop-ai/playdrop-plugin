# Game Review Evidence Capture

Evidence capture is mandatory. This workflow reviews gameplay quality, not whether a page launches.

## Primary review surface

Choose exactly one primary scored surface from the claimed version's `surfaceTargets`, in this priority order:

1. `MOBILE_PORTRAIT`
2. `MOBILE_LANDSCAPE`
3. `DESKTOP`

Use that surface for the scored review, screenshots, and score comments. Do not average across surfaces.

If `surfaceTargets` is missing or empty in the claimed payload, stop with `ERROR`; do not guess. If the chosen surface fails because the game falsely declares support for it, score the failure on that surface. You may do small smoke checks on other declared surfaces only to document metadata problems, not to rescue the score.

## Browser lifecycle

Every capture run must close its browser resources. Use the PlayDrop CLI capture command instead of importing Playwright directly.

Required cleanup order:

1. stop tracing or video if enabled
2. close the page if it exists
3. close the context if it exists
4. close the browser if it exists

If cleanup itself fails, report the cleanup error in the run output. Do not leave a Chrome instance running.

## Gameplay screenshots

Capture screenshots at gameplay moments. Loading screens, title screens, splash screens, menus, and static launch proof do not count.

Required screenshots:

- `core`: a real core gameplay moment after the reviewer performs the primary action
- `win`: a win, completion, level clear, success, or meaningful progression moment
- `loss`: a fail, loss, timeout, mistake, blocked state, or evidence that the game has no reachable failure condition

Do not burn the review trying to force a true win in a non-deterministic, long-running, or deduction-heavy game. If a true win is not quickly reachable through normal player inputs, use the best meaningful progression or near-completion screenshot as `win.png`, then state that limitation in `Primary interaction evidence`, `Challenge evidence`, and `Score caps applied` when it affects quality.

If a required moment is impossible because the game has no working primary interaction, no success state, or no loss state, capture the clearest evidence of that absence and label it with the missing moment. The absence itself must affect scoring.

For the core screenshot, record the exact input sequence in the internal assessment's `Primary interaction evidence` line. The evidence must state what the reviewer did and what changed in gameplay. If a darts or throwing game only allows the reviewer to drag or place a dart at the final hit location, that is evidence that the throw verb is absent, even if the game shows hit, clear, or fail modals.

Also record `Challenge evidence`. This must state what made play interesting or what failed to do so. If the reviewer can complete the captured core, win, or progression moments without timing, planning, aim, risk, pressure, or meaningful decisions, that absence is evidence against gameplay quality.

Write screenshots under `.tmp/game-review/<version-id>/` using stable names:

- `.tmp/game-review/<version-id>/core.png`
- `.tmp/game-review/<version-id>/win.png`
- `.tmp/game-review/<version-id>/loss.png`

Build the composite:

```bash
playdrop review compose-evidence \
  --core .tmp/game-review/<version-id>/core.png \
  --win .tmp/game-review/<version-id>/win.png \
  --loss .tmp/game-review/<version-id>/loss.png \
  --out .tmp/game-review/<version-id>/composite.png
```

The composite is required evidence. Do not post it to Slack yourself. `playdrop task submit-review` sends it to the PlayDrop API, and the API uploads it to the review Slack thread.

## Rating card image

After writing and validating the internal review message, create a final ratings image:

```bash
playdrop review rating-card \
  --review-message-file <INTERNAL.txt> \
  --out .tmp/game-review/<version-id>/rating-card.png \
  --title "<game display name> v<version>"
```

The rating card uses the 10 criterion ratings, the `Outcome` line, and the `Punchline assessment` line from the internal review message.

The rating card is required evidence. Do not post it to Slack yourself. `playdrop task submit-review` sends it to the PlayDrop API, and the API uploads it after the gameplay evidence composite.
