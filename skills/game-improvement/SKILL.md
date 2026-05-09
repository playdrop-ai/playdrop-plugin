---
name: game-improvement
description: "Improve an existing Playdrop game's visuals, audio, controls, performance, and feel. Use when the user already has a project and wants iteration, polish, or stronger runtime quality before publishing or republishing."
---

# Game Improvement

Use this skill for focused iteration on an existing Playdrop project.

## Workflow

1. Log in, initialize, and validate the project
2. Inspect 2 to 3 strong references before making major changes
3. Improve visuals, animation, audio, controls, feel, or performance
4. Verify portrait, landscape, and desktop surfaces when the game supports them
5. Re-test locally
6. Capture and validate before publish or marketing

## Rules

- do not polish around a broken or confusing core loop
- if the strongest raw moment is still not worth clicking, step back before more surface polish
- use this skill to improve a viable game, not to rescue a concept that never worked
- add or fix background music and SFX before marketing unless `preview.audioPolicy` intentionally declares `silent`
- make the first preview scene visually active enough for capture before generating assets
- keep changes in the creator project; do not change PlayDrop platform code for game-specific polish

## Shared references

- `existing-projects.md`
- `assets-and-generation.md`
- `audio.md`
- `performance-debugging.md`
- `gameplay-review.md`
- `marketing-audio.md`
- `preview-guidelines.md`

## Handoff

- pre-listing desirability review -> `gameplay-review`
- visual direction rethink before polishing assets -> `art-direction`
- concept or scope rethink -> `game-planning`
- new listing assets or publish prep -> `store-listing`
- full marketing preparation -> `marketing-pack`
