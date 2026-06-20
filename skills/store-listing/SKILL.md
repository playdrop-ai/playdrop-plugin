---
name: store-listing
description: "Use when a PlayDrop game needs PlayDrop listing readiness, listing metadata, listing media references, tags, validation, or publish-ready listing conventions."
---

# Store Listing

Use this skill for the PlayDrop listing itself. Full social launch kits route to `marketing-pack`; final hero and icon production routes to `listing-art`.

## Workflow

1. Confirm accepted listing assets exist under `assets/marketing/`.
2. Confirm `catalogue.json` references the final PlayDrop listing media.
3. Improve tags and listing copy that explain the input, goal, and stakes.
4. Confirm listing media matches the current runtime.
5. Run `playdrop project validate .` before publish. Inside server-assigned task workspaces, run the staged command as `./bin/playdrop project validate .`.

## Rules

- use versioned assets from `assets/marketing/`, not temporary output folders
- never ship a raw crop as the final icon or hero
- icon and hero must be purpose-built marketing assets that match actual gameplay
- hero art must show the exact game name front and center as large readable title/logo text
- icon and hero must come from Playdrop AI-generated or AI-edited base artwork with real-font title compositing
- do not reuse social covers, thumbnails, or gameplay screenshots as Playdrop hero/icon assets
- listing media must match the actual runtime
- include real high-quality CLI gameplay videos before treating the release as listing-ready
- copy should explain the core input and the success or fail rule when it could be misread
- pick gameplay moments, not menus or loading states
- update `catalogue.json` automatically when listing metadata or media paths are validated
- inside server-assigned task workspaces, do not run `playdrop project publish`; use the task-scoped upload/done/fail commands from the server prompt after validation

## Shared references

- `publish-and-listing.md`
- `marketing-asset-quality.md`

## Handoff

- full marketing pack, social videos, covers, and `MARKETING.md` -> `marketing-pack`
- final icon or hero artwork -> `listing-art`
- PlayDrop listing copy, social copy, tags, and posting guidance -> `game-marketing`
- early icon, hero, or visual direction before final listing media -> `art-direction`
- daily feedback triage after publish -> `comment-monitoring`
