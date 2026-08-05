---
name: create-game
description: "Use for any PlayDrop game-building request, including creating, remixing, or updating a game. Introduces PlayDrop capabilities and routes setup, SDK, engines, assets, local testing, playtesting, validation, and listing work to the right specialized guidance."
---

# Create Games with PlayDrop

Requires the PlayDrop CLI. If the `playdrop` command is unavailable, follow the PlayDrop `setup` skill first.

Use this as the main entry point for PlayDrop game development:

- **New game:** follow the new-game rules below.
- **Remix:** read `../remix-game/SKILL.md`, then use the relevant capabilities and specialist skills below.
- **Update:** read `../update-game/SKILL.md`, then preserve working behavior while making the requested change.

## Capabilities

- **Templates:** Hosted HTML, Phaser 2D, and Three.js scaffolds. Learn more: `playdrop project create app --help`.
- **Platform SDK:** Host lifecycle, identity, saves, achievements, leaderboards, multiplayer, pause, audio, and preview. Learn more: `../../references/tech/playdrop-sdk.md`.
- **Phaser 2D:** Sprites, tweens, collisions, and continuous 2D gameplay. Learn more: `phaser-2d-game`.
- **Three.js:** Spatial 3D rendering, cameras, assets, and physics. Learn more: `three-js-game`.
- **Asset discovery:** Reusable games, packs, and individual assets. Learn more: `discover-assets`.
- **Asset creation:** Original gameplay art, audio, backgrounds, and listing art. Learn more: `make-assets`.
- **Custom content:** Creator or user-generated typed assets such as levels and tracks. Learn more: `sdk.assets.custom`.
- **Tweaks:** Creator-tunable runtime values for balance, colors, labels, booleans, and enums. Learn more: `tweaks`.
- **Playtest Notes:** Text, image, JSON, Markdown, log, or asset feedback captured inside the game. Learn more: `playtest-notes`.
- **Local development:** Run and inspect the hosted game locally. Learn more: `playdrop project dev --help`.
- **Playtesting:** Deterministic gameplay checks and self-review. Learn more: `playtest-game`.
- **Catalogue:** Surfaces, assets, metadata, Tweaks, listing, and upload declarations. Learn more: `../../references/catalogue-json.md`.
- **Listing:** Identity art, preview mode, metadata, and real gameplay video. Learn more: `make-listing`.

Open only the capabilities that improve the game. Never load both engine skills for one game. Read `make-assets` before any image-generation command; it routes transparent 2D art to `make-2d-asset-pack` when needed.

## New-game rules

1. Read `../../references/dimensions.md` and `../../references/quality-bars.md`. Keep the first version focused, fun, and shippable. When the core interaction is uncertain, prove a small playable version before polish; art-first or parallel art and code suit familiar or visually led games.
2. Search PlayDrop early for games, systems, packs, and assets worth reusing.
3. Choose the primary surface and engine before scaffolding. The single-file HTML template is only for turn-based or static-screen UI games. Continuous motion, physics, a moving camera, or spatial 2D gameplay requires `phaser-2d`; use Three.js for 3D. Never pick HTML because it is faster. One-thumb continuous arcade games normally use `MOBILE_PORTRAIT`, wide platformers and racers `MOBILE_LANDSCAPE`, and pointer- or keyboard-heavy games `DESKTOP`. Task `surfaceContext` describes the device that submitted the prompt, not a game-design requirement.
4. Claim the slug when required, then scaffold with `playdrop project create app <slug> --template <allowed-template-key>`. Do not create projects by hand or prefill a root catalogue before scaffolding.
5. Replace the sample loop. The finished game needs agency, feedback, challenge, visible progress or payoff, and a reliable restart. Use coherent finished assets, not emoji, basic shapes, or default engine primitives as its identity.
6. In `catalogue.json`, declare one honest `primarySurface`, only supported `surfaceTargets`, and one complete playtest tape per surface. Treat task `surfaceContext` as the submitting device, not a design requirement.
7. Create original expression. A referenced game may inform genre and function, never its name, characters, art, audio, text, level design, or presentation.
8. After the last runtime change, run the deterministic final check from `playtest-game`, complete the listing, validate, then deliver through the workflow that invoked this skill.

For macOS PlayDrop Cloud and Local Agent worker tasks, follow the native recorder contract in `make-listing` after the final runtime change. Windows Local Agent tasks use the supported external capture workflow described there.

Use `../../references/phases/new-game.md` for creator-facing progress vocabulary. Working notes such as `GAME.md`, `ART_DIRECTION.md`, and `AGENTS.md` are optional memory, never delivery gates.
