---
name: make-marketing-screenshots
description: "Create fully AI-generated promotional screenshots for PlayDrop listings, App Store, Google Play, paid acquisition, social, and campaigns. Use when final stills need short marketing messages, strong selling-point concepts, professional composition, and truthful game-inspired art rather than literal gameplay captures."
---

# Make Marketing Screenshots

Create conversion-focused marketing art without inventing what the game offers. Treat the playable game and accurate gameplay video as the truth source, not as pixels that must appear in the final still.

## Non-negotiable media model

- **Gameplay video is the literal representation of the shipped game.** Produce or verify it with `../make-marketing-video/SKILL.md` or the listing capture workflow.
- **Marketing screenshots are fully AI-generated promotional images.** Generate the content, composition, effects, and rendered headline as one finished image.
- **Raw gameplay screenshots and recorder posters are reference inputs only.** Never publish them as the final marketing screenshot set.
- Default to four screenshots. Give each image one truthful selling point and one headline of two to four words.
- Screenshot truth is semantic, not pixel-identical. The art may idealize presentation, but it must not imply unavailable mechanics, characters, environments, progression, rewards, or outcomes.

When the intended result is unclear, find the approved Starfold PlayDrop listing package in the available workspace. Inspect its current screenshot exports, four-part selling-point story, marketing README, catalogue, source assets, and production handoff. Use it as the PlayDrop quality and structure reference without copying its branding or game art.

## Preconditions

- Read `../../references/marketing-creative-production.md`.
- Inspect the playable game, accurate listing, real gameplay video, source stills, hero art, and icon.
- Inspect the approved positioning brief. If it is missing, use `../market-game/SKILL.md` first.
- Inventory the icon, title, subtitle, hero, and end card as protected or reference-only inputs.
- Know the target channel, language, supported orientation, and destination dimensions before generation.
- For Apple exports, read `references/app-store-screenshots.md` and verify the current official specifications.

Fail with `marketing_screenshot_source_missing` when the game, listing, or gameplay video is too incomplete to verify the proposed selling points.

## Workflow

### 1. Research the category

- Study five successful, directly comparable games on the target storefront or ad channel.
- Record the exact phrases, composition, hierarchy, and player promise of the strongest references.
- Use references to understand proven structure. Never copy another game's characters, branding, or distinctive layout.
- Include Starfold whenever a PlayDrop listing precedent is useful or the operator asks for it.

### 2. Define four selling points

Choose four distinct truths the game can support. A strong default sequence is:

1. Core action: what the player does.
2. Twist or tension: what makes the action interesting.
3. Payoff: what feels satisfying or surprising.
4. Goal: what the player tries to achieve.

Use fewer than four only when the game genuinely has fewer distinct truthful promises. Never add a filler frame.

Lock one headline of two to four words for every image before generation. Make it player-facing, specific, and understandable without body copy. Record the exact spelling, punctuation, capitalization, and line breaks.

### 3. Write the truth brief

For each screenshot, record:

- the selling point;
- the game, video moment, or source still that proves it;
- the entities, environment, action, and outcome that may appear;
- the features, characters, rewards, controls, and claims that must not appear;
- the final two-to-four-word headline.

The final image does not need to preserve a real screenshot or exact gameplay geometry. It must remain recognizably about the actual game and communicate only supported promises.

### 4. Generate complete marketing images

- Use built-in image generation for the complete image, including scene content, composition, lighting, effects, and headline typography.
- Use the real game, gameplay video, source stills, hero, icon, and palette as visual references.
- Generate native 9:16 portrait and 16:9 landscape compositions when both orientations are supported or requested. Compose each orientation independently.
- In a PlayDrop game package, save approved masters under `assets/marketing/playdrop/screenshots/portrait/` and `assets/marketing/playdrop/screenshots/landscape/`.
- Give every image a different focal state and color balance. Changing only the headline does not create a distinct concept.
- Make the advertised action or benefit visually obvious at thumbnail size.
- Do not add browser chrome, platform chrome, debug controls, or unrelated PlayDrop UI.
- Do not add generic text with scripts, HTML, or temporary typography after generation. Regenerate until the AI-rendered headline is exact and visually finished.
- For an uncertain frame, generate three materially different whole-image concepts before choosing one.

### 5. Review the set

Create a contact sheet containing, for each image:

- the closest reference;
- the current candidate;
- the locked selling point and headline;
- the game or video evidence that supports the promise.

Inspect every final at full size and listing-card size. Reject and regenerate it when:

- any headline word is misspelled, malformed, missing, duplicated, or unreadable;
- the image does not communicate its selling point immediately;
- the image implies unsupported game content;
- two frames communicate the same idea;
- important content or text is clipped;
- the image feels materially weaker than the Starfold listing precedent when that precedent is available.

Do not reject an image merely because it is more polished, dramatic, or idealized than runtime footage. The accurate video owns literal gameplay representation.

### 6. Package the approved set

- Name files by order and message, such as `01-core-action.png` and `02-beat-the-clock.png`.
- Record the destination, locale, dimensions, orientation, headline, selling point, truth evidence, generation prompt, and ordering in a small manifest or handoff note.
- Keep source stills, rejected generations, contact sheets, and temporary exports outside the final screenshot directories.
- Do not upload or submit media as part of this skill.

## Completion bar

- The set normally contains four distinct selling points.
- Every headline contains two to four correctly rendered words.
- Every final screenshot is a complete AI-generated marketing composition.
- Every promise is supported by the shipped game and accurate gameplay video.
- No unavailable mechanic, character, environment, reward, or outcome is advertised.
- Each requested orientation is composed natively and inspected independently.
- The set is legible at listing-card size and meets the Starfold quality bar when that reference is available.
- The user has reviewed the final contact sheet.
