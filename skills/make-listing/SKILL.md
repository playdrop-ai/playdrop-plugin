---
name: make-listing
description: "Create PlayDrop listing assets and metadata that match the real game and upload cleanly."
---

# Make Listing

## Required For New Games

- App icon PNG when available.
- Portrait and landscape hero PNG.
- Screenshots for supported surfaces.
- Accurate title, description, tags, surfaces, `previewable`, `uses`, and `design` in `catalogue.json`.

## Rules

- Base hero art on real screenshots, runtime assets, and final art direction.
- Hero art may be more polished than gameplay, but it must depict the actual game fantasy and key entities.
- Prefer built-in agent image generation for hero/icon art when available. Use PlayDrop CLI AI generation only when the agent has no native capability for that asset type.
- Do not use misleading stock-like art, raw screenshots as hero art, or title text that gets clipped in common listing crops.
- Store listing work is not optional polish; it is part of the shipped draft.
- Worker-scope listing does not include video capture in this round.

## Screenshot Command

Use a gameplay screenshot, not a loading screen. Store it under a path upload validation expects:

```sh
./bin/playdrop project check . --timeout 30 --screenshot assets/marketing/playdrop/screenshots/landscape/01-core.png
```

Then list the files in `catalogue.json` under `listing.screenshotsPortrait` and `listing.screenshotsLandscape`.
