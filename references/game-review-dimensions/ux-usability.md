# UX / Usability

This dimension covers the player's ability to understand and operate the product around the game loop. A lot of otherwise promising games lose players through unnecessary friction in menus, flow, navigation, HUD hierarchy, pause behavior, restart behavior, and settings clarity. Good UX makes the game easier to trust and easier to stay inside.

## Comparison discipline

Compare against games with similar information density and play tempo.

- high-action games should be compared against fast-readable HUD patterns
- tactical or card-heavy games should be compared against excellent information hierarchy
- cozy or slower games should still be compared against clean, low-friction flow rather than being excused for clutter

References may include games like `Slay the Spire`, `Balatro`, `Into the Breach`, `Hades`, or `Vampire Survivors`, depending on what the game is trying to communicate.

## What to inspect

- menu structure
- clarity of buttons and labels
- start, pause, restart, and quit behavior
- settings discoverability
- HUD readability under pressure
- error recovery and confirmation behavior

## Evidence to gather

- navigate the game as a new player would
- intentionally make small mistakes and see how recoverable they are
- check whether menus waste time before returning the player to action
- note whether the game hides important actions behind unclear labels or iconography

## Questions to answer

- Can the player quickly understand where they are and what they can do?
- Is important gameplay information visible at the moment it matters?
- Are restart and retry flows fast enough for the genre?
- Does the UI create friction unrelated to challenge?
- Can a player recover from confusion without leaving the game?

## Common failure modes

- too much visual weight on low-priority UI
- unclear button hierarchy or duplicate actions
- pause and restart flows that are slower than genre expectations
- settings that matter, but are buried or missing
- menus designed for desktop hover while claiming controller or touch support

## Stage-aware interpretation

At `Gameplay Prototype`, UX can be sparse, but it should not actively block testing. At `Vertical Slice`, the structure should already communicate competence. At `Mature Live Version`, avoidable UX friction is a meaningful quality failure even if the core game is strong.

## What strong feedback looks like

- "The combat HUD is understandable, but restart friction is too high for a score-attack loop. Stronger arcade references return the player to action much faster."
- "The challenge is fair, but the UI does not explain state changes clearly enough, so players are learning the interface instead of learning the game."
