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
- Listing art/metadata and raw gameplay capture: `make-listing`.
- Game review task (PlayDrop Cloud worker tasks only): `review-game`.
- Creator support: `creator-help`.
- Marketing positioning, research, and asset planning: `market-game`.
- Promotional screenshots, store images, social carousels, and paid-acquisition stills: `make-marketing-screenshots`.
- App previews, trailers, gameplay ads, and social video: `make-marketing-video`.
- Complete YouTube, TikTok, Instagram, Pinterest, and X delivery package: `make-social-media-package`.
