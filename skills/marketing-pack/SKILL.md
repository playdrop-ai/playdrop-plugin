---
name: marketing-pack
description: "Use when a PlayDrop creator asks to prepare marketing, make a launch kit, create promo assets, create social videos, create marketing screenshots, package listing media, or prepare a game for promotion."
---

# Marketing Pack

Use this skill for the single-prompt workflow:

```text
let's prepare the marketing for my game
```

This skill orchestrates specialist skills. It should not duplicate platform specs or rendering details.

## Workflow

1. Run `gameplay-review` first. If the game is not ready to market, hand off to `game-improvement` and edit by default.
2. Run `catalogue-preview` to make `catalogue.json` previewable, music-ready, and capture-ready.
3. Run `marketing-capture` to produce real local CLI captures under `assets/marketing/`.
4. Review the source captures before rendering assets. Reject any wrong-window capture, low-bitrate source, quiet audio, missing music, 30 fps source capture, menu/loading footage, or boring first seconds.
5. Run `marketing-screenshots`, `marketing-videos`, and `listing-art` after captures exist. These can run independently.
6. Run `store-listing` for Playdrop listing readiness.
7. Run `game-marketing` to write `MARKETING.md`.
8. Run `node <plugin>/scripts/validate-marketing-manifest.ts --root .`.
9. Re-run `playdrop project validate .`.

## Rules

- edit the creator project by default when the prompt asks to prepare marketing
- accepted assets live in `assets/marketing/`, not `output/`
- temporary files may live in `tmp/marketing/`
- update `catalogue.json` automatically after validation
- only touch creator project files while operating on a creator game
- keep fixing quality, preview, capture, audio, and surface issues by default
- stop only when a gate cannot be fixed clearly
- do not use hosted capture, server capture, or remote capture
- do not produce raw screenshots or raw videos as final marketing assets
- do not mark a marketing pack passed with caveats, warnings, rejected captures, or missing required assets
- do not accept browser-frame capture or manual capture as a substitute for `playdrop project marketing capture`
- do not accept quiet audio; default marketing previews should use background music plus SFX unless the game has a documented design reason not to
- do not accept screenshot composites as final Playdrop hero or icon art
- long-form YouTube is out of scope unless the user explicitly asks for longer capture

## Shared references

- `preview-guidelines.md`
- `marketing-capture.md`
- `marketing-platforms.md`
- `marketing-audio.md`
- `marketing-asset-quality.md`

## Handoff

- preview metadata or preview runtime hooks -> `catalogue-preview`
- local capture -> `marketing-capture`
- covers and screenshots -> `marketing-screenshots`
- social videos and thumbnails -> `marketing-videos`
- hero artwork and icon artwork -> `listing-art`
- Playdrop listing package -> `store-listing`
- copy and distribution plan -> `game-marketing`
