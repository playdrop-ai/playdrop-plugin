---
name: make-marketing-screenshots
description: "Create polished, truthful game marketing screenshots from real gameplay and reference research. Use for App Store, Google Play, paid acquisition, social, or campaign stills that need strong concepts, professional composition and copy, multiple creative directions, or device-specific exports. Use make-listing instead for raw PlayDrop catalogue captures."
---

# Make Marketing Screenshots

Create conversion-focused campaign art without inventing gameplay. Treat the playable game and its accurate PlayDrop listing as the source of truth.

## Preconditions

- Read `../../references/marketing-creative-production.md`. It defines the
  mandatory protected-art, gameplay-truth, typography, geometry, and review
  contract.
- Inspect the playable game, current listing, hero art, icon, and real gameplay captures.
- Inspect the approved positioning brief and any previous campaign the operator
  names. Reuse its established art and production system when requested.
- Inventory the icon, title, subtitle, hero, and end card as protected or
  editable before opening an image tool.
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

Lock the exact headline, spelling, punctuation, and line breaks before
generating finished art. Make the visible state prove its headline at a glance.
If the first frame must establish a familiar category such as Classic Klondike,
say that before introducing the differentiator.

### 3. Lock real gameplay states

- Choose a distinct real capture or deterministic playable state for every
  frame.
- Preserve the exact gameplay region as a locked truth layer. Never ship an
  image-generated board, card layout, HUD, score, control, or result.
- Audit rules-dense states object by object. Confirm every highlighted move is
  legal and obviously sensible; prefer the strongest available move when
  viewers can judge the board immediately.
- Capture the source state, legality evidence, and intended action in the
  handoff before adding decorative treatment.

### 4. Develop complete concepts

- Build around the locked real gameplay state.
- Create two canonical masters for every approved campaign frame: a native 9:16 portrait composition and a native 16:9 landscape composition.
- Compose both masters independently from the same approved gameplay truth. Do not obtain one master by cropping or stretching the other.
- In a PlayDrop game package, use `playdrop/screenshots/portrait/` and `playdrop/screenshots/landscape/` as the canonical master locations. Do not duplicate them into another source folder.
- For any uncertain frame, produce three materially different whole-image concepts. Change gameplay state, composition, camera emphasis, effects, and hierarchy, not just the headline.
- Keep the board, controls, primary entities, and rules recognizable.
- Decorative worlds, lighting, and effects may heighten the fantasy, but cannot imply unavailable mechanics or content.
- Use different gameplay states and color balance across the set. Repeating the same board with new text is not a new concept.
- Make the player's action visually obvious. Hands, arrows, or motion lines may clarify a real gesture, but cannot conceal or replace the game.
- Do not modify a protected icon, title, subtitle, hero, or end card. If a
  protected hero does not fit the destination ratio exactly, use a
  ratio-native gameplay composition instead of cropping, padding, or extending
  it.

### 5. Finish the art

- Use built-in image generation with the real capture and approved game art as
  references when it materially improves the creative layer.
- Image generation may create backgrounds, lighting, effects, interaction
  guidance, and finished typography. Restore the exact locked gameplay layer
  before export if a generation redraws any part of it.
- Generate complete creative concepts when useful, but never accept an
  AI-interpreted gameplay state as final.
- Follow the caption-plate procedure in
  `../../references/marketing-creative-production.md` for game-styled raster
  headlines. Verify every requested word exactly.
- If using conventional compositing, use deliberate final typography. Never ship temporary, script-drawn, or placeholder text.
- Keep headlines inside safe areas and legible at App Store thumbnail size.
- Do not add an outer decorative frame when the destination applies a rounded
  mask. Avoid generic gold, metallic trim, or other stock "premium" effects
  unless they belong to the approved game art direction.
- Treat Apple iPhone, Apple iPad, Pinterest, Instagram, and other non-master ratios as channel derivatives of the nearest canonical master.
- Create a destination-native derivative with image editing or recomposition when the ratio changes enough to remove meaningful content. Preserve the approved headline, gameplay state, mechanic, art direction, and object proportions.
- Recompose for a different aspect ratio or orientation. Do not mechanically crop a portrait campaign image into a landscape layout.
- For nearby portrait ratios, use a uniform crop only when it removes genuine empty margin. Move the crop anchor within that margin to preserve the entire headline, gameplay action, and goal.
- Never use non-uniform scaling, plain bars, blurred side fill, letterboxing, pillarboxing, or duplicated imagery to fill a destination.
- If a crop clips meaningful content, recompose for the destination instead of stretching or padding.
- Keep platform chrome, browser chrome, debug controls, and unrelated PlayDrop UI out of the gameplay focal area.

### 6. Review before export

Show a contact sheet containing, for each frame:

- the closest reference,
- the current candidate,
- any proposed revision.

Inspect every final at full size and thumbnail size. Reject it if the copy is misspelled, gameplay is confusing, a feature is invented, important content is clipped, or two frames communicate the same idea.

Compare every derivative beside its canonical master. Dimensions and aspect ratio alone do not prove that the composition is valid. Confirm that the complete semantic content, including the lowest gameplay row and every moving object, remains visible.

For rules-dense games, include the gameplay-state audit in the review. Do not
approve a plausible-looking board without verifying its actual rules.

### 7. Package the approved set

- Keep editable sources separate from final exports.
- Name files by order and message, for example `01-core-action.png` and `02-enemy-pressure.png`.
- Record the channel, locale, pixel dimensions, orientation, headline, source capture, and ordering in a small manifest or handoff note.
- Record protected assets, gameplay-state evidence, highlighted move, and any
  AI-generated creative layers separately from the locked real gameplay layer.
- Record which 9:16 or 16:9 canonical master each derivative came from and whether it was recomposed or safely cropped.
- Keep rejected generations, debug captures, contact sheets, and temporary exports outside the game repository unless the user explicitly asks to preserve them.
- Do not upload or submit media as part of this skill.

## Completion bar

- Every frame has a distinct marketing job.
- The set is truthful to actual gameplay.
- Copy and typography look finished.
- Protected identity assets are unchanged.
- Every visible gameplay state and highlighted move has been audited.
- Gameplay remains legible behind the marketing treatment.
- Every requested device layout is composed and inspected independently.
- No stretching, bars, blurred side fill, or clipped headline remains.
- The user has reviewed the final contact sheet.
