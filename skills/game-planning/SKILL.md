---
name: game-planning
description: "Plan and validate a Playdrop game from concept to production roadmap. Use when the user needs concept validation, platform fit, a GDD, art direction, technical design, scope shaping, or phased milestones for a new Playdrop game."
---

# Game Planning

Use this skill for pre-build planning when the concept still needs to prove it deserves implementation.

## Saved Game Ideas

If the user says "my game idea", "the idea I created", "that game idea", or gives a likely game idea name, first run:

```bash
playdrop creations ideas browse --state all --json
```

When a saved GameIdea matches, treat it as the source of truth for the plan. Use its display name, input mode, tags, input data, and generated data before adding new assumptions.

For implementation handoff, use `playdrop project create app <name> --game-idea <id-or-slug>`. The CLI reads the saved idea and uses the stored remix source for remix ideas, or the default TypeScript template for non-remix ideas.

## Workflow

1. Check saved game ideas first when the user references one
2. Inspect 2 to 3 relevant Playdrop references with `playdrop search` and `playdrop detail`
3. Write the concept pitch, target player, best platform, and first-15-second hook
4. Confirm the concept is built on a proven core loop and has a real reason to exist beyond a skin or vibe shift
5. Define the GDD: loop, controls, progression, success and failure states
6. Define art direction, content strategy, and technical design
7. Produce a phased roadmap and identify the smallest slice worth building

## Rules

- the concept should answer why this game beats or differs from the strongest game in the same lane
- keep gameplay audience, fantasy, and marketing promise aligned
- if a saved GameIdea matched, preserve it, pass its id or slug through create and publish, and clearly call out any proposed changes
- if the core loop is weak, unfamiliar, or only exciting after packaging, stop and reshape before implementation
- plan the first 15 seconds as a desire-creating beat, not just an explanation beat

## Outputs

- pitch
- feasibility note
- first-15-second beat
- GDD
- TDD
- phased roadmap
- saved GameIdea id or slug when used

## Shared references

- `pitch-and-validation.md`
- `game-design-document.md`
- `art-direction.md`
- `technical-design.md`
- `roadmap-phases.md`
- `discovery.md`
- `platform-capabilities.md`
- `scope-cutting.md`
- `gameplay-mockups.md`

## Handoffs

- visual direction, style exploration, or art mockups -> `art-direction`
- cut the plan to the smallest strong v1 -> `scope-control`
- turn the locked plan into visual build targets -> `gameplay-mockups`
- listing and media prep -> `store-listing`
- visibility and distribution -> `game-marketing`
