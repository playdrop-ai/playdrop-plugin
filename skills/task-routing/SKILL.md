---
name: task-routing
description: "Route PlayDrop requests to the smallest relevant builder v2 skill."
---

# Task Routing

- New game: `create-game`.
- Remix: `remix-game`.
- Existing game update: `update-game`.
- Working inside a PlayDrop worker task: the task-local PlayDrop context governs the lifecycle.
- Playtest or QA: `playtest-game`.
- Existing asset discovery and normal game assets: `discover-assets` then `make-assets`.
- Original consistent 2D packs, multi-item sheets, paired large/small variants, transparent sprite families, or extraction repairs: `make-2d-asset-pack`.
- Listing art/metadata: `make-listing`.
- Game review task (PlayDrop Cloud worker tasks only): `review-game`.
- Creator support: `creator-help`.
- Marketing follow-up: `market-game`.
