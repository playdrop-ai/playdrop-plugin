---
name: make-marketing-video
description: "Capture and finish truthful gameplay marketing videos from a PlayDrop game. Use for App Store previews, Google Play videos, interstitial or rewarded ad creatives, trailers, and social clips that require external recording, a strong opening hook, platform-specific framing, editing, captions, or technical export validation."
---

# Make Marketing Video

Produce marketing video from real gameplay. Capture the game from the outside; never add a game-specific recorder or change normal gameplay to manufacture footage.

## Preconditions

- Inspect the playable game, supported surfaces, listing, and existing capture report.
- If deterministic preview states or clean raw capture are missing, use `../make-listing/SKILL.md` to add the standard preview contract and capture them.
- Define the destination, orientation, duration, locale, and whether the deliverable is an app preview, paid ad, or social clip.
- For Apple App Preview work, read `references/app-store-previews.md` and recheck the official specifications before export.

Fail with `marketing_video_source_missing` when real, clean footage is unavailable.

## Workflow

### 1. Write the video brief

- State the one mechanic or payoff the opening must prove.
- Define the intended player action, tension, payoff, and closing goal.
- Choose the strongest truthful gameplay sequence before recording.
- Use reference videos from successful comparable games to study pacing and clarity, not to copy their art or branding.

### 2. Prepare a real gameplay state

- Use the game's normal preview phase and `window.__listingCapture.prepare(sceneId)` when deterministic setup is needed.
- Keep the preview state playable and representative of the shipped game.
- Do not branch gameplay on recording flags, validation routes, query markers, or hidden marketing modes.
- Do not modify the existing PlayDrop recording pipeline unless the recording pipeline itself is the requested task.

### 3. Record externally

- Prefer the existing PlayDrop native capture output when it contains the required surface and moment.
- Otherwise record the game preview from outside the iframe or app at the exact target dimensions.
- Hide browser and host chrome while keeping only the real game surface visible.
- Record one clean take with enough lead-in and tail to select the strongest segment.
- Capture separate orientations when the game layout materially changes. Do not stretch footage or crop away interaction context.
- Confirm audio is synchronized when the game uses sound.

### 4. Build the cut

- Show the core mechanic or primary payoff in the first seconds.
- For paid app-video edits, prove the app experience in the first 2 to 3 seconds and use at least two meaningful visual changes in the first 5 seconds as a starting point. Do not force this cadence onto a store preview when it would make the real interaction harder to follow.
- Remove loading, menus, dead time, failed gestures, debug UI, and unrelated host UI.
- Prefer a continuous, understandable gameplay sequence for store previews.
- Keep one short creative focused on one mechanic and its payoff. Remove secondary progression or feature beats that dilute that story; give them their own creative when they are worth testing.
- Use cuts, captions, and effects only when they improve comprehension and remain honest about the game.
- Keep text out of the interaction area and make it readable without sound.
- Time short three-to-five-word plates for roughly 2 to 2.6 seconds including transitions. Give opening hooks and final calls to action roughly 3 to 4 seconds when the edit permits.
- Use fast, smooth transitions around the readable hold. A practical default is a 200-millisecond fade in and a 200-millisecond fade out.
- Place each plate in the nearest quiet safe-area region that does not cover gameplay, touch guidance, or platform controls. For a portrait puzzle game with a centered board, prefer above the board. Use below-gameplay placement for a dedicated end-card call to action, not for instructions.
- Remove a plate when its message has landed. Do not leave copy covering a longer gameplay sequence merely because the underlying shot continues.
- Use a hand cue for every action when the raw gameplay does not otherwise make input timing and location obvious. Repetition should be fixed through varied pacing and stronger action selection, not by hiding the player input. When the game response already makes later input unambiguous, showing each control once can be enough.
- For a top-down hand cue, anchor the fingertip at the contact point. Show the press with a small scale compression into the screen plane and radial feedback from that exact point. Do not translate the whole hand vertically across the screen to represent a tap.
- Do not advertise a feature, enemy, reward, score, or control that the player cannot encounter.

### 5. Adapt by channel

- Treat each orientation as its own edit when composition or UI changes.
- For paid ads, make the hook and game identity clear immediately and provide a channel-compliant end card when requested.
- For store previews, prioritize an uninterrupted demonstration of the advertised experience.
- For social clips, keep the same truthful footage while adapting pacing, captions, and safe areas to the platform.

### 6. Validate and review

- Inspect the opening, middle, ending, and proposed poster frame visually.
- Use `ffprobe` or the platform's authoritative media inspector to verify dimensions, duration, frame rate, codec, bitrate, audio channels, and sample rate.
- Compare the finished video with the real game and the brief.
- Show the final video and poster frame to the user before delivery.
- Fail with `marketing_video_export_invalid` on any specification mismatch rather than uploading an uncertain file.

### 7. Package the approved video

- Keep raw captures, project files, final exports, and poster frames separate.
- Name outputs by channel, device, orientation, and locale.
- Record source capture, time range, dimensions, duration, codec, frame rate, audio, and poster timestamp in a handoff note.
- Keep temporary renders and capture diagnostics out of the game repository.
- Do not upload, submit, fund, or launch a campaign as part of this skill.

## Completion bar

- The first seconds prove the strongest mechanic or payoff.
- All footage represents real gameplay.
- No loading, browser chrome, debug UI, or misleading edit remains.
- Every requested orientation is framed intentionally.
- Technical validation passes for the destination.
- The user has reviewed the final video and poster frame.
