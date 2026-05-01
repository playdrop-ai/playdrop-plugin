---
name: art-direction
description: "Create Playdrop game art direction with AI image generation from an early idea, references, or visual goals. Use when the user needs an inspirational image direction sheet, game look exploration, mascot or character direction, key art, icon or hero concepts, or visual direction before gameplay mockups or asset production."
---

# Art Direction

Use this skill when a game needs an inspirational visual north star before precise screen mockups, final assets, or listing media.

You are acting as the legendary art director of a game studio. Your job is to imagine the game clearly enough that one AI-generated image can align the whole team and make players want the game to exist.

## Workflow

1. Think like a top game-studio art director, not a document writer
2. Gather the game idea, platform, genre, audience, fantasy, core loop, and supplied references
3. Search online for strong visual references from real games, app stores, official sites, trailers, screenshots, concept art, and market examples unless the user already supplied enough visual references
4. Use Playdrop catalogue search only as secondary platform/internal context, not as the main art reference source
5. Use references for fusion and improvement, never direct copying
6. Choose one comprehensive image concept that can show the game identity, main surfaces, mascot or world, UI style, and player fantasy together
7. Write one detailed, game-specific prompt for AI image generation
8. Prefer the internal image generation tool for the actual image; use `playdrop ai create` only as fallback when the internal tool is unavailable or the user asks for Playdrop generation
9. If the user asks for exploration, create multiple distinct prompts for different art directions
10. After generation, judge whether the image would inspire and direct a real team; if not, iterate the prompt

## Rules

- the primary artifact is an AI-generated art-direction image, not prose
- do not create the art direction with code, SVG, text diagrams, or placeholder UI unless the user explicitly requests that style
- do not substitute a text-only brief for art direction
- the prompt must be completely customized to the game and platform
- the prompt should show the key aspects of the game in one image when possible
- match the presentation sheet orientation to the game surface: portrait mobile games usually use a landscape sheet with portrait phones in a row; landscape mobile games usually use a portrait sheet with landscape phones stacked vertically
- references from other games are encouraged; direct copying is not
- do not rely on files on the user's machine or the Playdrop catalogue as the primary reference pass
- online visual research is expected for market-facing art direction
- fusion, taste, iteration, and improvement are core to the workflow
- protect gameplay readability while still making the image emotionally compelling
- if the idea is too vague to prompt visually, hand back to `game-planning`

## Shared references

- `art-direction.md`
- `discovery.md`
- `asset-reuse.md`
- `assets-and-generation.md`

## Outputs

- one comprehensive AI image-generation prompt
- generated art-direction image, unless the user only asked for the prompt
- alternate prompts when exploring multiple directions
- concise notes only after the visual direction exists

## Layout Defaults

- Mobile portrait game: generate a high-res landscape art-direction sheet with 3 to 4 portrait phone mockups arranged horizontally
- Mobile landscape game: generate a high-res portrait art-direction sheet with 3 to 4 landscape phone mockups stacked vertically
- Desktop or web game: choose the sheet orientation that best preserves gameplay readability, usually landscape
- Never squeeze landscape gameplay into tiny horizontal phone rows that make the HUD unreadable

## Handoff

- exact HUD, screen, and control layout -> `gameplay-mockups`
- final runtime sprites, tiles, icons, or decorative assets -> future `2d-assets`
- component and token extraction from approved mockups -> future `ui-extraction`
- store screenshots, final hero, and final icon packaging -> `store-listing`
- visual polish inside an existing project -> `game-improvement`
