---
name: task-routing
description: "Route ambiguous or multi-step public Playdrop creator requests to the right specialist skill. Use when the user asks for broad Playdrop help, does not know which creator workflow they need, or one request spans planning, scoping, mockups, improvement, listing, marketing, services, or porting."
---

# Task Routing

Use this skill only when the correct public Playdrop specialist skill is not already obvious.

## Route by intent

- idea, pitch, platform fit, roadmap -> `game-planning`
- cut scope, reduce feature creep, lock a smaller v1 -> `scope-control`
- gameplay mockups, HUD framing, visual build targets -> `gameplay-mockups`
- find references, assets, packs, reusable code -> `asset-discovery`
- update CLI, SDK, plugin, or project compatibility -> `project-updates`
- local validation, test accounts, multiplayer checks -> `dev-testing`
- pre-publish feel, desirability, session quality -> `gameplay-review`
- improve an existing game -> `game-improvement`
- screenshots, hero art, icon art, publish flow -> `store-listing`
- comments and community triage -> `comment-monitoring`
- visibility, GitHub SEO, boosts, distribution -> `game-marketing`
- auth, saves, realtime, monetization, AI assets -> `service-integration`
- Godot or starter-kit-based porting -> `engine-porting`
- stuck creator, escalation, support path -> `creator-support`

## Rules

- preserve coherence on multi-step requests
- route to more than one specialist when the task genuinely spans workflows
- use `playdrop documentation browse` and `playdrop documentation read <path>` when current public product guidance matters
- use shared reference filenames from `references/` only when the task needs them
