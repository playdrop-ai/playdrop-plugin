---
name: gameplay-mockups
description: "Create or review gameplay mockups as literal build targets. Use when the user needs HUD framing, screen layouts, control affordances, or shipping-resolution mockups that implementation can follow directly."
---

# Gameplay Mockups

Use this skill when a game needs visual implementation targets before coding or before a visual rework.

## Workflow

1. Start from the simplified plan, not the full wish list
2. Define the required screens and supported surfaces
3. Create or inspect shipping-resolution mockups for the best platform first
4. Check framing, control affordances, HUD density, signifiers, and small-screen readability
5. Approve the mockups only if they can act as the visual contract for implementation

## Rules

- gameplay mockups are build targets, not mood boards
- show the actual control surface for frequent actions
- avoid explanation text unless it would ship in the product
- if the mockups expose a planning problem, hand back to `game-planning` or `scope-control`

## Shared references

- `gameplay-mockups.md`
- `art-direction.md`

## Handoff

- planning changes exposed by the mockups -> `game-planning`
- simplifying the plan before more mockup work -> `scope-control`
- integrating approved mockups into an existing project -> `game-improvement`
