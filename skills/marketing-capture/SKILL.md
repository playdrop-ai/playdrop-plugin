---
name: marketing-capture
description: "Use when a PlayDrop game needs local marketing capture, capture manifests, surface-specific gameplay videos, high-framerate source footage, captured game audio, or capture validation."
---

# Marketing Capture

Use this skill to run local marketing capture through the Playdrop CLI.

## Workflow

1. Run `playdrop project marketing doctor .`.
2. Fix any missing local prerequisites, preview metadata, or audio policy issues.
3. Run `playdrop project marketing capture .`.
4. Confirm `assets/marketing/capture-manifest.json` and `assets/marketing/marketing-report.json` exist.
5. Inspect captured videos for real gameplay, motion, music/SFX, correct surfaces, and correct window content.
6. Reject and rerun capture when the capture is 30 fps, shorter than 12 seconds, from the wrong screen, quiet, missing music for `music-and-sfx`, visually boring, or not produced by the public CLI command.

## Rules

- capture runs on the creator's computer
- supported high-quality capture platforms are macOS and Windows
- Linux marketing capture must fail clearly in v1
- ffmpeg and ffprobe are required system installs
- do not use hosted capture, remote capture, or Playdrop server capture
- do not use hidden capture commands or native Apple listing recorders
- captures must be real preview gameplay, not menus or loading states
- `music-and-sfx` and `sfx-only` require captured audio
- accepted captures live under `assets/marketing/captures/`
- accepted source captures must come from `playdrop project marketing capture`, not browser screenshots, Playwright video, manual recordings, or hidden/internal capture commands
- default source capture quality is 60 fps and at least 12 seconds so downstream edits have enough real gameplay
- `music-and-sfx` is the default marketing policy; `sfx-only` needs a game-design reason, not missing music tooling
- a wrong-window capture is a hard failure even if a later manual capture exists
- a passed marketing report must not contain rejected captures, warning gates, or "pass with caveat" language

## Shared references

- `marketing-capture.md`
- `preview-guidelines.md`
- `marketing-audio.md`

## Handoff

- failed preview contract -> `catalogue-preview`
- weak visuals or audio -> `game-improvement`
- valid captures -> `marketing-screenshots` and `marketing-videos`
