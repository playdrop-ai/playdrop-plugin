---
name: make-marketing-screenshots
description: "Create polished, truthful game marketing screenshots from real gameplay and reference research. Use for App Store, Google Play, paid acquisition, social, or campaign stills that need strong concepts, professional composition and copy, multiple creative directions, or device-specific exports. Use make-listing instead for raw PlayDrop catalogue captures."
---

# Make Marketing Screenshots

Create conversion-focused campaign art without inventing gameplay. Treat the playable game and its accurate PlayDrop listing as the source of truth.

## Preconditions

- Inspect the playable game, current listing, hero art, icon, and real gameplay captures.
- If the listing or capture state is inaccurate or missing, use `../make-listing/SKILL.md` first.
- Know the target channel, language, device class, and orientation before composing.
- For Apple exports, read `references/app-store-screenshots.md` and verify the current official specifications before export.

Fail clearly with `marketing_screenshot_source_missing` rather than fabricating a board, feature, enemy, score system, or interface.

## Workflow

### 1. Research the category

- Study five successful, directly comparable games on the target storefront or ad channel.
- Capture the real reference assets, their exact phrases, composition, information hierarchy, and the gameplay promise each frame makes.
- Use references to understand proven structure. Never copy another game's characters, art, branding, or distinctive layout verbatim.
- Present references next to proposed work when asking for a creative decision.

### 2. Define the screenshot story

Write one truthful sentence for each of these beats the game actually supports:

1. Core action: what the player does.
2. Tension: what pushes back.
3. Payoff: what feels spectacular or satisfying.
4. Goal: what the player pursues or improves.

Use three strong frames when only three beats are real. Use four when all four are compelling. Do not add a filler fifth frame.

Give every frame one job and a short headline, normally two to six words. Make the sequence understandable without reading body copy.

### 3. Develop complete concepts

- Start from real gameplay captures or deterministic preview states.
- For any uncertain frame, produce three materially different whole-image concepts. Change gameplay state, composition, camera emphasis, effects, and hierarchy, not just the headline.
- Keep the board, controls, primary entities, and rules recognizable.
- Decorative worlds, lighting, and effects may heighten the fantasy, but cannot imply unavailable mechanics or content.
- Use different gameplay states and color balance across the set. Repeating the same board with new text is not a new concept.
- Make the player's action visually obvious. Hands, arrows, or motion lines may clarify a real gesture, but cannot conceal or replace the game.

### 4. Finish the art

- Use built-in image generation with the real capture and approved game art as references when it materially improves the composition.
- Generate the whole composition when pursuing an image-generated direction, including typography. Verify every requested word exactly.
- If using conventional compositing, use deliberate final typography. Never ship temporary, script-drawn, or placeholder text.
- Keep headlines inside safe areas and legible at App Store thumbnail size.
- Recompose for a different aspect ratio or orientation. Do not mechanically crop a portrait campaign image into a landscape layout.
- Keep platform chrome, browser chrome, debug controls, and unrelated PlayDrop UI out of the gameplay focal area.

### 5. Review before export

Show a contact sheet containing, for each frame:

- the closest reference,
- the current candidate,
- any proposed revision.

Inspect every final at full size and thumbnail size. Reject it if the copy is misspelled, gameplay is confusing, a feature is invented, important content is clipped, or two frames communicate the same idea.

### 6. Package the approved set

- Keep editable sources separate from final exports.
- Name files by order and message, for example `01-core-action.png` and `02-enemy-pressure.png`.
- Record the channel, locale, pixel dimensions, orientation, headline, source capture, and ordering in a small manifest or handoff note.
- Keep rejected generations, debug captures, contact sheets, and temporary exports outside the game repository unless the user explicitly asks to preserve them.
- Do not upload or submit media as part of this skill.

## Completion bar

- Every frame has a distinct marketing job.
- The set is truthful to actual gameplay.
- Copy and typography look finished.
- Gameplay remains legible behind the marketing treatment.
- Every requested device layout is composed and inspected independently.
- The user has reviewed the final contact sheet.
