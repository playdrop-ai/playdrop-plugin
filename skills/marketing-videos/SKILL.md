---
name: marketing-videos
description: "Use when a PlayDrop game needs TikTok, Instagram, YouTube Shorts, Snapchat, Pinterest, YouTube, X, Reddit, Facebook, LinkedIn, social video variants, covers, captions, or thumbnails."
---

# Marketing Videos

Use this skill after `marketing-capture` has produced source videos.

## Workflow

1. Read `assets/marketing/capture-manifest.json`.
2. Inspect the source captures before editing. Reject captures that are 30 fps, shorter than 12 seconds, visually wrong, low quality, missing music when expected, or too quiet.
3. Select key moments from the actual capture before rendering. Look for visible fail, recovery, reward, combo, win, danger, timer, score, unlock, progression, or a surprising interaction. If the promised moment is not visible, recapture or improve the preview.
4. Create vertical, landscape, feed portrait, square, and Pinterest variants around those moments.
5. Put the strongest gameplay moment at timestamp 0. Do not open with a title card, logo card, menu, static board, or explanation.
6. Use full-bleed or close-up gameplay with dynamic camera movement. The game action should dominate the frame, not sit as a small panel inside a graphic template.
7. Use short overlay hooks tied to the visible moment. Keep the copy out of the main action and avoid generic CTA-first text.
8. Preserve and normalize captured game audio unless the platform export is intentionally silent.
9. Render separate thumbnails where needed. Thumbnails must be gameplay-first stills from the selected moment, not poster layouts.
10. Render source moment, final video, and cover/thumbnail contact sheets under `assets/marketing/review/`.
11. Inspect the contact sheets before setting any gate to passed.
12. Update `asset-manifest.json`, `marketing-report.json`, and `MARKETING.md`.

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
- do not put gameplay inside a centered phone/card frame for short-form game video; crop into the action instead
- do not use large empty backgrounds, static side text, or CTA bars that compete with gameplay
- do not render text-dominant thumbnails or covers for videos; the selected gameplay moment must stay primary
- do not use brand + headline + subtitle poster layouts as video covers
- do not use decorative callouts unless they point to the exact action the hook promises
- gameplay should fill at least 65% of the useful frame in final videos
- short-form video should feel native to a scrolling feed: full-screen, immediate motion, minimal text, and a payoff loop
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
  --moment-description "The hazard triggers and the recovery starts immediately" \
  --viewer-promise "The viewer understands the risk and payoff in one glance" \
  --selected-moment-reason "The first second contains the player action, hazard, and consequence" \
  --composition action-closeup \
  --gameplay-fill 0.78 \
  --audio-policy music-and-sfx \
  --text "Short hook" \
  --font <font.ttf> \
  --zoom 1.18 \
  --pan-strength 0.04 \
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
