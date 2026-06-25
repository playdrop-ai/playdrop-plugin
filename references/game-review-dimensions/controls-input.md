# Controls / Input

Controls are where player intention meets the game. This dimension is not just about whether buttons technically work. It is about whether the game reads player intent reliably, responds with the expected speed, and teaches the player the input language it expects.

## Comparison discipline

Choose references based on genre and primary control surface.

- precision platformers compare against games like `Celeste`, `Super Meat Boy`, or `N++`
- twin-stick or top-down combat compares against games like `Hades`, `Nuclear Throne`, or `Enter the Gungeon`
- driving and drift games compare against the steering readability of games like `Mario Kart`, `art of rally`, or `Rocket League`
- touch-native games should be judged against strong mobile clarity, not against desktop tolerance for clutter

The question is simple: on the intended surface, does this control scheme feel worse, comparable, or stronger than credible peers?

## What to inspect

- input latency and responsiveness
- dead zones, oversensitivity, and accidental actions
- button mapping clarity
- prompt accuracy
- camera and perspective support for aim, distance, timing, and spatial judgment
- consistency between menu controls and gameplay controls
- support for the surfaces declared in the listing

## Evidence to gather

- test the primary supported path first
- if multiple surfaces are declared, spot-check the others when practical
- verify that prompts match actual input devices
- verify that the primary action can actually be performed
- note whether the player can discover controls naturally, or only by trial and error

## Questions to answer

- Does the game do what the player intended at the moment they intended it?
- Can a first-time player discover and execute the primary action without external explanation?
- Are the most common actions comfortable and legible?
- Does the camera or perspective make the intended input readable?
- Are there hidden or overloaded inputs that create confusion?
- Does the game demand precision that its input model does not support?
- Are declared controller, mouse, keyboard, or touch claims actually true?

## Common failure modes

- acceptable movement, but unreadable action inputs
- the primary action is missing, such as no working throw in a darts game
- perspective makes a skill action impossible to judge, such as aiming from an angle that hides direction or distance
- controller support claimed, but missing prompts or broken focus states
- touch input added superficially and not actually tuned
- menus navigable with one device and gameplay with another, creating mismatch
- jump, dodge, aim, or drag actions that feel inconsistent under repeated use

## Stage-aware interpretation

At prototype stage, placeholder prompts are forgivable. Unreliable control feel is not. By `Demo`, the main control path should already support the game's intended fantasy. By `First Release`, control mismatches and metadata lies become serious trust problems.

An unavailable primary action is not a controls polish issue. Cap `Controls / Input` at `2/10` and cap `Gameplay / Core Loop` at `1/10` when the missing action removes the loop.

## What strong feedback looks like

- "The movement response is quick enough, but jump buffering and coyote time feel absent, so the game reads as harsher and less fair than the precision-platformer references it invites."
- "Mouse aiming is the clearly supported path, but the listing claims controller support and the controller path currently feels second-class."
