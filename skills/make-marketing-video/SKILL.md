---
name: make-marketing-video
description: "Capture and finish truthful gameplay marketing videos from a PlayDrop game. Use for App Store previews, Google Play videos, interstitial or rewarded ad creatives, trailers, and social clips that require external recording, a strong opening hook, platform-specific framing, editing, captions, or technical export validation."
---

# Make Marketing Video

Produce marketing video from real gameplay. Capture the game from the outside; never add a game-specific recorder or change normal gameplay to manufacture footage.

## Non-negotiable media model

- **Video is the literal representation of gameplay.** Every gameplay frame must come from the shipped game.
- **Optional listing screenshots are separate AI-generated marketing artwork.** Only when screenshots are explicitly requested, use `../make-marketing-screenshots/SKILL.md` for still images and never turn recorder posters into the final screenshot set.
- Source stills and recorder posters are review evidence and image-generation references, not final marketing screenshots.
- Editing may improve clarity and pacing, but it must not change the mechanic, entities, environment, controls, reward, difficulty, score behavior, or outcome shown.

## Preconditions

- Read `../../references/marketing-creative-production.md`. It defines the
  mandatory protected-art, gameplay-truth, caption, interaction, phase-edit,
  geometry, and review contract.
- Inspect the playable game, supported surfaces, listing, and existing capture report.
- Inspect the approved positioning brief and every previous campaign the
  operator names. Review its finals, handoff, source assets, and render scripts
  before choosing a production method.
- Inventory the icon, title, subtitle, hero, and end card as protected or
  editable. Never infer permission to change a protected identity asset.
- If deterministic preview states or clean raw capture are missing, use `../make-listing/SKILL.md` to add the standard preview contract and capture them.
- Define the destination, orientation, duration, locale, and whether the deliverable is an app preview, paid ad, or social clip.
- For Apple App Preview work, read `references/app-store-previews.md` and recheck the official specifications before export.
- For AppLovin video-ad work, read `references/app-lovin-video-ads.md` and recheck the official specifications before export.

Fail with `marketing_video_source_missing` when real, clean footage is unavailable.

## Workflow

### 1. Write the video brief

- State the one mechanic or payoff the opening must prove.
- Define the intended player action, tension, payoff, and closing goal.
- Lock the exact caption copy, line breaks, protected assets, forbidden
  treatments, destinations, aspect ratios, and durations.
- Choose the strongest truthful gameplay sequence before recording.
- Use reference videos from successful comparable games to study pacing and clarity, not to copy their art or branding.
- When the operator cites an approved PlayDrop campaign, reproduce its
  established caption and interaction system unless the new game's visual
  language requires a documented adaptation.

### 2. Prepare a real gameplay state

- Use the game's normal preview phase and `window.__listingCapture.prepare(sceneId)` when deterministic setup is needed.
- Keep the preview state playable and representative of the shipped game.
- Use a fixed seed and a truthful scripted preview sequence when a specific real payoff must be reproducible. Prefer the strongest representative sequence first instead of recording weak footage and trying to manufacture excitement in the edit.
- When the creative must finish on a win or large payoff, record the complete
  real run first. Select the opening, late-game action, automatic payoff, and
  victory from that verified take.
- A standard listing preview may omit irrelevant HUD and add honest touch guidance. It must not change game rules, rewards, difficulty, or the resulting gameplay.
- Do not branch gameplay on recording flags, validation routes, query markers, or hidden marketing modes.
- Do not modify the existing PlayDrop recording pipeline unless the recording pipeline itself is the requested task.

### 3. Record externally

- Prefer the existing PlayDrop native capture output when it contains the required surface and moment.
- Otherwise record the game preview from outside the iframe or app at the exact target dimensions.
- Keep two reusable canonical gameplay captures when the game supports both orientations: a real 9:16 portrait capture and a real 16:9 landscape capture. Build channel exports from the nearest canonical capture only when its crop passes the geometry contract; otherwise recapture the destination surface. Capture separate orientations when the game layout materially changes.
- Hide browser and host chrome while keeping only the real game surface visible.
- Record one clean take with enough lead-in and tail to select the strongest segment.
- Record the real game surface dimensions. Do not trust an output file's nominal dimensions as proof that the embedded game was captured without distortion.
- Apply the geometry contract in `../../references/marketing-creative-production.md` to every crop and export: uniform scale only, empty-margin crops only, no bars, gutters, stretching, or fill, and native 3:4 and 2:3 capture for width-filling board and puzzle games.
- Confirm audio is synchronized when the game uses sound.

### 4. Build the cut

- Show the core mechanic or primary payoff in the first seconds. For paid app videos, prove the app experience in the first 2 to 3 seconds and use at least two meaningful visual changes in the first 5 seconds; do not force this cadence onto a store preview.
- Remove loading, menus, dead time, failed gestures, debug UI, and unrelated host UI. Prefer a continuous, understandable gameplay sequence for store previews.
- Keep one short creative focused on one mechanic and its payoff. Give secondary beats their own creative when they are worth testing.
- Edit by semantic phase per the reference: keep player input readable, accelerate only the repetitive automatic phase, return to readable speed for the result, keep audio synchronized per segment, and record every phase speed in the edit manifest.
- Build captions and hand cues per the reference's typography and interaction sections: game-styled raster plates with verified copy, compact placement in quiet safe areas, and fingertip-anchored cues with timestamps derived from the exact raw take being edited. Never ship generic drawtext, code-drawn hands, or timestamps reused from an older capture.
- Use a protected hero opening only per the reference's identity rules.
- Do not advertise a feature, enemy, reward, score, or control that the player cannot encounter.

### 5. Adapt by channel

- Treat each orientation as its own edit when composition or UI changes.
- For paid ads, make the hook and game identity clear immediately and provide a channel-compliant end card. Keep a separate matching end-card asset when the channel accepts one.
- For store previews, prioritize an uninterrupted demonstration of the advertised experience.
- For social clips, keep the same truthful footage while adapting pacing, captions, and safe areas to the platform. Use `../make-social-media-package/SKILL.md` when packaging the complete cross-platform set.

### 6. Validate and review

- Inspect the opening, middle, ending, and proposed poster frame visually.
- Use `ffprobe` or the platform's authoritative media inspector to verify dimensions, duration, frame rate, codec, bitrate, audio channels, sample rate, and a `1:1` sample aspect ratio.
- Compare representative source and final frames. Square tiles, circles, hands, logos, and other known shapes must retain their proportions.
- Produce the review evidence set in the reference: complete-clip crop confirmation, contact sheets at every input timestamp, frames around every speed boundary, and one delivery-order composite for multi-format campaigns.
- Confirm the edit remains understandable with audio muted.
- Compare the finished video with the real game and the brief.
- Show the final video and poster frame to the user before delivery.
- Fail with `marketing_video_export_invalid` on any specification mismatch rather than uploading an uncertain file.

### 7. Package the approved video

- Keep raw captures, project files, final exports, and poster frames separate.
- Name outputs by channel, device, orientation, and locale.
- Record source capture, time range, dimensions, duration, codec, frame rate, audio, and poster timestamp in a handoff note.
- Record the protected hero or end card used, caption-plate sources, cue
  timestamps, crop policy, semantic segments, and playback speed of every
  segment.
- Keep temporary renders and capture diagnostics out of the game repository.
- Do not upload, submit, fund, or launch a campaign as part of this skill.

## Completion bar

- The first seconds prove the strongest mechanic or payoff, and all footage represents real gameplay with no loading, chrome, debug UI, or misleading edit.
- The reference's geometry, typography, phase-edit, and protected-asset contracts all hold.
- Every video uses square pixels with a `1:1` sample aspect ratio and passes technical validation for its destination.
- Every requested orientation is framed intentionally.
- The user has reviewed the final video and poster frame.
