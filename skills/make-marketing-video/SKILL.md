---
name: make-marketing-video
description: "Capture and finish truthful gameplay marketing videos from a PlayDrop game. Use for App Store previews, Google Play videos, interstitial or rewarded ad creatives, trailers, and social clips that require external recording, a strong opening hook, platform-specific framing, editing, captions, or technical export validation."
---

# Make Marketing Video

Produce marketing video from real gameplay. Capture the game from the outside; never add a game-specific recorder or change normal gameplay to manufacture footage.

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
- Keep two reusable canonical gameplay captures when the game supports both orientations: a real 9:16 portrait capture and a real 16:9 landscape capture.
- Build channel exports from the nearest canonical capture only when a uniform crop removes unused scenery and preserves the complete action envelope. Recapture the destination surface when it does not.
- For board and puzzle games that fill the width, treat 3:4 Instagram and 2:3
  Pinterest as native capture surfaces by default. Use a 9:16 crop only after a
  complete-clip comparison proves that it removes empty margin and nothing
  else.
- Hide browser and host chrome while keeping only the real game surface visible.
- Record one clean take with enough lead-in and tail to select the strongest segment.
- Record the real game surface dimensions. Do not trust an output file's nominal dimensions as proof that the embedded game was captured without distortion.
- Preserve the source aspect ratio through every transform. Never scale width and height independently.
- When source and destination ratios differ, use a uniform crop only when it removes genuine empty scenery. Start centered, then move the crop anchor within empty margin when needed to preserve headlines, gameplay, touch guidance, and goals.
- Never use blurred gutters, duplicated-video backgrounds, plain side bars, pillarboxing, letterboxing, or decorative filler.
- If a uniform crop removes gameplay, touch guidance, important HUD, or the intended payoff, recapture or recompose at the destination ratio. Never repair the mismatch by stretching or padding.
- For Apple iPhone, Apple iPad, AppLovin, Pinterest, Instagram, and social exports, start from the nearest 9:16 or 16:9 canonical capture. Reuse it only when the destination crop preserves the complete board, touch cue, HUD that matters, and payoff for the entire clip.
- Capture separate orientations when the game layout materially changes. Do not crop away interaction context.
- Confirm audio is synchronized when the game uses sound.

### 4. Build the cut

- Show the core mechanic or primary payoff in the first seconds.
- When an exact protected hero exists at the output ratio and the campaign uses
  a hero opening, use that file unchanged for a short identity beat. Do not
  crop, extend, retype, decorate, or regenerate it. Open on real gameplay when
  no ratio-native protected hero exists.
- For paid app-video edits, prove the app experience in the first 2 to 3 seconds and use at least two meaningful visual changes in the first 5 seconds as a starting point. Do not force this cadence onto a store preview when it would make the real interaction harder to follow.
- Remove loading, menus, dead time, failed gestures, debug UI, and unrelated host UI.
- Prefer a continuous, understandable gameplay sequence for store previews.
- Keep one short creative focused on one mechanic and its payoff. Remove secondary progression or feature beats that dilute that story; give them their own creative when they are worth testing.
- For a mechanic-led puzzle ad, prefer a readable action-to-payoff arc: show one deliberate player action, show the release or commit, then let the resulting cascade accelerate. Do not speed up the gesture until its meaning becomes unclear.
- Split the edit into semantic phases: identity or hook, readable player input,
  repetitive or automatic payoff, and result or victory.
- Keep player input readable. Speed only the repetitive automatic phase when it
  improves momentum, then return to a readable result or victory speed. Do not
  apply one global speed merely to hit the target duration.
- Preserve synchronized audio per segment and record every phase speed in the
  edit manifest.
- Use cuts, captions, and effects only when they improve comprehension and remain honest about the game.
- Keep text out of the interaction area and make it readable without sound.
- Match caption treatment to the game's approved marketing art and cited
  campaign precedent. Follow the complete raster-plate process in
  `../../references/marketing-creative-production.md`. Do not ship generic
  drawtext, plain HTML captions, or placeholder typography when the campaign
  uses premium game-styled plates.
- Keep caption plates compact. Do not add a large opaque text region that masks empty scenery and changes the apparent framing of the gameplay.
- Time short three-to-five-word plates for roughly 2 to 2.6 seconds including transitions. Give opening hooks and final calls to action roughly 3 to 4 seconds when the edit permits.
- Use fast, smooth transitions around the readable hold. A practical default is a 200-millisecond fade in and a 200-millisecond fade out.
- Place each plate in the nearest genuinely quiet safe-area region. Prefer above
  a centered board. Use empty lower scenery for a top-aligned board. Never cover
  gameplay, touch guidance, moving objects, important HUD, or platform
  controls.
- Remove a plate when its message has landed. Do not leave copy covering a longer gameplay sequence merely because the underlying shot continues.
- Use a hand cue for every action when the raw gameplay does not otherwise make input timing and location obvious. Repetition should be fixed through varied pacing and stronger action selection, not by hiding the player input. When the game response already makes later input unambiguous, showing each control once can be enough.
- For a top-down hand cue, anchor the fingertip at the contact point. Show the press with a small scale compression into the screen plane and radial feedback from that exact point. Do not translate the whole hand vertically across the screen to represent a tap.
- Use a real transparent hand asset or an image-generated asset that has been visually approved. Do not draw a substitute hand from code. A simple aligned tap ring may be generated programmatically.
- For two-tap mechanics, show and validate both the source selection and destination placement. Derive cue timestamps from the exact raw take being edited; do not reuse timestamps from an older capture with a different preroll.
- Fade the hand in and out instead of popping it on screen. A practical starting point is 120 to 200 milliseconds per edge, shortened only when two distinct taps are close together.
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
- Confirm across the complete clip that cropping removed only empty scenery and that no interaction, moving object, payoff, caption, or touch cue is clipped. A clean first frame is not sufficient evidence.
- Generate a contact sheet at every input timestamp for touch-guided videos. Confirm the fingertip and feedback ring land on the control that the real game is using in that frame.
- Generate frames immediately before and after every speed boundary. Confirm
  that player input, automatic payoff, and victory were split at the intended
  semantic moments.
- For a multi-format campaign, create one review composite showing every final
  output in delivery order. Inspect captions, framing, action, payoff, and
  ending across ratios.
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

- The first seconds prove the strongest mechanic or payoff.
- All footage represents real gameplay.
- No loading, browser chrome, debug UI, or misleading edit remains.
- No nonuniform scaling, stretching, bars, blurred side fill, or padding remains.
- Protected identity assets are unchanged.
- Player interaction, automatic payoff, and victory use documented independent
  phase speeds.
- Caption plates match the approved game art and have verified copy and alpha
  edges.
- Every video uses square pixels with a `1:1` sample aspect ratio.
- Every requested orientation is framed intentionally.
- Technical validation passes for the destination.
- The user has reviewed the final video and poster frame.
