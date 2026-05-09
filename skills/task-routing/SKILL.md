---
name: task-routing
description: "Route ambiguous or multi-step public Playdrop creator requests to the right specialist skill. Use when the user asks for broad Playdrop help, does not know which creator workflow they need, or one request spans planning, art direction, scoping, mockups, improvement, listing, marketing, services, or porting."
---

# Task Routing

Use this skill only when the correct public Playdrop specialist skill is not already obvious.

## Saved Game Ideas

If the user says "my game idea", "the idea I created", "that game idea", or gives a likely game idea name, first check saved ideas:

```bash
playdrop creations ideas browse --state all --json
```

When a saved GameIdea matches, route the work using that record as the source of truth. If the task creates the app, use `playdrop project create app <name> --game-idea <id-or-slug>` so the CLI infers the stored remix source or default TypeScript template. If the task publishes it, pass `--game-idea <id-or-slug>` to `playdrop project publish <app-name>`.

## Route by intent

- idea, pitch, platform fit, roadmap -> `game-planning`
- visual style, mood, palette, mascot feel, icon or hero concepts, art mockups -> `art-direction`
- cut scope, reduce feature creep, lock a smaller v1 -> `scope-control`
- gameplay mockups, HUD framing, visual build targets -> `gameplay-mockups`
- find references, assets, packs, reusable code -> `asset-discovery`
- update CLI, SDK, plugin, or project compatibility -> `project-updates`
- local validation, test accounts, multiplayer checks -> `dev-testing`
- pre-publish feel, desirability, session quality -> `gameplay-review`
- improve an existing game -> `game-improvement`
- prepare marketing, launch kit, promo assets, social assets, marketing screenshots, social videos -> `marketing-pack`
- preview metadata, preview hook, no-HUD autoplay preview, capture scene -> `catalogue-preview`
- local marketing capture, source capture videos, capture manifest -> `marketing-capture`
- marketing screenshots, social covers, platform screenshots -> `marketing-screenshots`
- TikTok, Reels, Shorts, Snapchat, Pinterest, YouTube, X, Reddit, Facebook, or LinkedIn videos -> `marketing-videos`
- final hero art, final icon art, title typography compositing -> `listing-art`
- PlayDrop listing readiness, listing media refs, publish flow -> `store-listing`
- comments and community triage -> `comment-monitoring`
- `MARKETING.md`, listing copy, social copy, GitHub SEO, boosts, distribution -> `game-marketing`
- auth, saves, realtime, monetization, AI assets -> `service-integration`
- Godot or starter-kit-based porting -> `engine-porting`
- stuck creator, escalation, support path -> `creator-support`

## Rules

- preserve coherence on multi-step requests
- route to more than one specialist when the task genuinely spans workflows
- use `playdrop documentation browse` and `playdrop documentation read <path>` when current public product guidance matters
- use shared reference filenames from `references/` only when the task needs them
