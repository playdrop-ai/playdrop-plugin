# AppLovin portrait video ads

Use this reference only for AppLovin video-ad work. Verify the official specification again immediately before export or upload.

## Official source

- Creative specifications and guidelines: https://support.applovin.com/en/growth/promoting-your-apps/welcome-to-applovin/creative-specs-and-guidelines

## Current technical contract

- Supported containers: MP4 or MOV.
- Required orientation: 9:16 portrait.
- Maximum file size: 1 GB.
- Maximum duration: 60 seconds.
- AppLovin reprocesses uploaded video for mobile playback.

Fail with `applovin_video_spec_mismatch` when the inspected export disagrees with the current official requirements.

## PlayDrop first-test defaults

These are creative defaults, not AppLovin requirements:

- Export 1080 x 1920 H.264 MP4 at 30 fps with AAC stereo audio.
- Use roughly 8 to 15 seconds for a focused mechanic-to-payoff creative. Use longer cuts only when the extra time proves another meaningful beat.
- Make the first player action understandable within 2 to 3 seconds.
- Hold short caption plates for roughly 2 to 2.6 seconds, including a 200-millisecond fade in and fade out.
- Create one separate clean branded end card. Keep its lower area visually quiet for AppLovin's own CTA and app metadata.
- Do not bake a fake install button, store badge, rating, network chrome, or duplicate app metadata into that end card.
- Keep the story understandable with sound muted.
- Create materially different creatives around different promises or payoffs instead of cosmetic variations of the same edit.

## Geometry contract

Never stretch gameplay to fill the destination.

For a source size `(sourceWidth, sourceHeight)` and destination `(targetWidth, targetHeight)`:

1. Compute `scale = max(targetWidth / sourceWidth, targetHeight / sourceHeight)`.
2. Scale both dimensions by that single value.
3. Center-crop only the overflow.
4. Verify that the crop removes empty scenery rather than interaction context.

Example:

- Source: 886 x 1920.
- Destination: 1080 x 1920.
- Uniform scale: `1080 / 886`.
- Rendered source: approximately 1080 x 2340.
- Center crop: approximately 210 pixels from both the rendered top and bottom.

Prefer this clean crop over side blur, duplicated footage, pillarboxing, or decorative filler. If the crop removes important content, recapture for 9:16 instead.

## Recommended mechanic-led structure

1. Show the game's identity and a compact promise above the action.
2. Show one deliberate player input with the fingertip anchored to the real contact point.
3. Show the release or commit.
4. Let the real payoff accelerate naturally.
5. Hold the strongest result briefly.
6. Supply a separate matching branded end card for the network's end-card stage.

Use premium caption plates derived from the game's approved visual language when plain typesetting looks generic. Keep plates outside the interaction area and validate their transparent edges on the final background.

For a two-tap mechanic, cue both the source and destination. Validate the final video with a contact sheet sampled at every cue timestamp so an old preroll or trimmed raw take cannot silently desynchronize the hand from the gameplay.

## Final review

- Inspect the file with `ffprobe`.
- Require a `1:1` sample aspect ratio so the ad renderer cannot deform the frames.
- Verify exact 9:16 dimensions, duration, H.264 video, AAC audio, frame rate, and file size.
- Compare source and output frames for geometry drift.
- Review the first 3 seconds, the action-to-payoff transition, the strongest payoff frame, and the end card.
- Preview once with sound and once muted.
- Keep the video and matching end-card asset separate for upload.
