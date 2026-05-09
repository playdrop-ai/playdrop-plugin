---
name: marketing-videos
description: "Use when a PlayDrop game needs TikTok, Instagram, YouTube Shorts, Snapchat, Pinterest, YouTube, X, Reddit, Facebook, LinkedIn, social video variants, covers, captions, or thumbnails."
---

# Marketing Videos

Use this skill after `marketing-capture` has produced source videos.

## Workflow

1. Read `assets/marketing/capture-manifest.json`.
2. Inspect the source captures before editing. Reject captures that are 30 fps, shorter than 12 seconds, visually wrong, low quality, missing music when expected, or too quiet.
3. Create vertical, landscape, feed portrait, square, and Pinterest variants for every relevant surface.
4. Put the strongest gameplay moment at timestamp 0. Do not open with a static title card.
5. Use short, direct overlay hooks tied to visible action: fail, recovery, reward, combo, win, danger, timer, score, unlock, or progression.
6. Preserve and normalize captured game audio unless the platform export is intentionally silent.
7. Render separate thumbnails where needed.
8. Update `asset-manifest.json` and `MARKETING.md`.

## Rules

- final social videos are not raw captures
- short vertical covers TikTok, Instagram Reels, Instagram Stories, YouTube Shorts, Snapchat, and Pinterest
- short landscape covers YouTube, X, Reddit, and web embeds
- long-form YouTube is out of scope unless the user explicitly asks for a longer capture
- text overlays must work when muted
- do not add unlicensed commercial music or platform-trending audio
- use captured game music and SFX from the preview whenever the audio policy allows it
- do not start with the game title unless the title appears over immediate gameplay action
- do not reuse the same generic template for every game; the first hook must describe this game and this visible moment
- do not accept audio that feels nearly silent; final social videos should be normalized for social playback
- do not use source captures as final social videos
- do not mark the video gate passed if any required platform family is missing

## Scripts

Use:

```bash
node <plugin>/scripts/render-marketing-video.ts \
  --root . \
  --input <capture.mp4> \
  --out assets/marketing/social/<platform>.mp4 \
  --width 1080 --height 1920 \
  --first-second-action \
  --audio-policy music-and-sfx \
  --text "Short hook" \
  --font <font.ttf> \
  --thumbnail-out assets/marketing/thumbnails/<platform>.png \
  --manifest assets/marketing/asset-manifest.json
```

## Shared references

- `marketing-platforms.md`
- `marketing-audio.md`
- `marketing-asset-quality.md`

## Handoff

- cover images -> `marketing-screenshots`
- social copy -> `game-marketing`
