# Game Review Outcomes

Creator-facing outcomes:

- `Blocked`
- `Limited`
- `Passed`
- `Good`
- `Excellent`

Stored enum mapping:

- `Blocked` persists as `FAILED`
- `Limited` persists as `LOW_QUALITY`
- `Passed` persists as `PASSED`
- `Good` persists as `GOOD`
- `Excellent` persists as `EXCELLENT`

Use the creator-facing label in CLI review validation and submission commands. The CLI also accepts the stored enum for compatibility and always sends the canonical stored value to the platform.

Operational-only state:

- `ERROR` is reserved for tooling, access, or infrastructure failure
- `ERROR` never gets creator feedback

## Outcome rules

### Blocked

Use when:

- safety, compliance, deception, or malicious behavior makes the game unacceptable
- the runtime is so broken that there is no meaningful playable product for the current submission
- the declared or obvious primary interaction is absent, such as a darts game with no way to throw the dart
- the listing is materially deceptive or harmful

### Limited

Use when:

- the game is safe enough to remain accessible
- the submission is below the minimum quality bar for normal distribution
- major weaknesses are present in gameplay, onboarding, controls, metadata accuracy, or stability
- the primary interaction works but the core fantasy or production promise is far below the selected references

### Passed

Use when:

- the game clears the minimum quality bar for its current stage
- the listing and runtime are honest enough
- no major category is severely off bar
- no hard score cap from `game-review-score-caps.md` restricts the outcome to `Limited` or `Blocked`
- the scores support the outcome: average score is at least `6.0`, minimum score is at least `4`, and Gameplay, Controls, and Performance are each at least `5`

### Good

Use when:

- the game is clearly above the minimum bar for its current stage
- the loop, presentation, and usability feel deliberate
- there are still important improvements available, but the experience is already strong
- the scores support the outcome: average score is at least `7.5`, minimum score is at least `6`, and Gameplay, Controls, UX, Visuals, and Performance are each at least `7`
- if those score gates do not hold, use `Passed` unless the evidence justifies changing the underlying scores

### Excellent

Use when:

- the game stands out for its current stage
- quality is strong across most criteria with few notable weaknesses
- it is a credible input to future featuring or stronger recommendation treatment
- the scores support the outcome: average score is at least `8.5`, minimum score is at least `7`, Gameplay, Controls, UX, Visuals, and Performance are each at least `8`, and FTUE is at least `7`
- if those score gates do not hold, use `Good` or lower unless the evidence justifies changing the underlying scores
