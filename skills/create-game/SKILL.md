---
name: create-game
description: "Create, remix, update, test, or publish a PlayDrop web game. Routes game-building work to the appropriate engine, assets, SDK, multiplayer, playtesting, and listing guidance."
---

# Create Games with PlayDrop

Requires the PlayDrop CLI. If the `playdrop` command is unavailable, follow the PlayDrop `setup` skill first.

Read `../../references/game-quality.md` before creating, remixing, or updating a game. It is the canonical quality target for every game workflow.

Use this as the main entry point for PlayDrop game development:

- **New game:** follow the new-game rules below.
- **Remix:** read `../remix-game/SKILL.md`, then use the relevant capabilities and specialist skills below.
- **Update:** read `../update-game/SKILL.md`, then preserve working behavior while making the requested change.

## Capabilities

- **Templates:** Hosted HTML, Phaser 2D, and Three.js scaffolds. Learn more: `playdrop project create app --help`.
- **Platform SDK:** Host lifecycle, identity, simple client saves, achievements, leaderboards, friends and messages, pause, audio, and preview. Legacy `sdk.rooms` and `sdk.me.joinRoom()` multiplayer are deprecated. Use `sdk.me.appData` only for simple saves that do not need authoritative server state. Learn more: `../../references/tech/playdrop-sdk.md`.
- **Game servers:** The default for every new multiplayer or server-authoritative game, and the only supported way for a game to run custom server-side code. PlayDrop Cloud provides standard Colyseus rooms, trusted player identity, and app-scoped MongoDB. Learn more: `../../references/tech/game-servers.md`.
- **Phaser 2D:** Sprites, tweens, collisions, and continuous 2D gameplay. Learn more: `phaser-2d-game`.
- **Three.js:** Spatial 3D rendering, cameras, assets, and physics. Learn more: `three-js-game`.
- **Asset discovery:** Reusable games, packs, and individual assets. Learn more: `discover-assets`.
- **Asset creation:** Original gameplay art, audio, backgrounds, and listing art. Learn more: `make-assets`.
- **Procedural 3D and avatars:** Source-bundled Three.js models, VFX, and characters with typed parameters, parts, sockets, animations, and reusable skins. Learn more: `../../references/tech/three-js.md`.
- **Custom content:** Creator or user-generated typed assets such as levels, tracks, procedural configurations, and avatar skins. Pair compact custom data with a shared procedural runtime instead of duplicating geometry or code. Learn more: `sdk.assets.custom` and `../../references/tech/three-js.md`.
- **Tweaks:** Creator-tunable runtime values for balance, colors, labels, booleans, and enums. Learn more: `tweaks`.
- **Playtest Notes:** Runtime-created artifacts and structured creator context, with an optional message, sent from the game to an agent. Learn more: `playtest-notes`.
- **Editor:** An optional owner-only creator surface built for this specific game. Learn more: `editor`.
- **Local development:** Run and inspect the hosted game locally. Learn more: `playdrop project dev --help`.
- **Playtesting:** Deterministic gameplay checks and self-review. Learn more: `playtest-game`.
- **Catalogue:** Surfaces, assets, metadata, Tweaks, listing, and upload declarations. Learn more: `../../references/catalogue-json.md`.
- **Listing:** Accurate metadata, required new-game identity art, and optional creator-requested media. Learn more: `make-listing`.

Open only the capabilities that improve the game. Never load both engine skills for one game. Read `make-assets` before any image-generation command; it routes transparent 2D art to `make-2d-asset-pack` when needed.

### Procedural 3D and avatars

Prefer a suitable PlayDrop procedural asset over rebuilding the same configurable model, VFX, or character. Pin and bundle its exact source revision, then use its controls, named parts and sockets, timeline, and character capabilities when present. Store creator or player variations as typed custom assets containing an exact procedural asset reference plus compact parameters. The official avatar follows this pattern: one extensible procedural humanoid runtime from `sdk.libs.avatar`, with appearance supplied by an exact `asset-spec:playdrop/avatar-skin` custom asset. Use the avatar runtime's rendering options, sockets, and available animations instead of copying its geometry, rig, or animation code.

## New-game rules

1. Keep the first version focused, fun, and shippable. When the core interaction is uncertain, prove a small playable version before polish; art-first or parallel art and code suit familiar or visually led games.
2. **Do not reinvent the wheel.** Before scaffolding, follow `../discover-assets/SKILL.md`: run three game or demo searches using different keywords or tags and download the two best sources to a temporary directory. Separately run three asset or pack searches. Strongly prefer procedural 3D assets and always download and bundle their exact source; reference other assets and packs by exact ref.
3. Choose the primary surface and engine before scaffolding. The single-file HTML template is only for turn-based or static-screen UI games. Continuous motion, physics, a moving camera, or spatial 2D gameplay requires `phaser-2d`; use Three.js for 3D. Never pick HTML because it is faster. One-thumb continuous arcade games normally use `MOBILE_PORTRAIT`, wide platformers and racers `MOBILE_LANDSCAPE`, and pointer- or keyboard-heavy games `DESKTOP`. Task `surfaceContext` describes the device that submitted the prompt, not a game-design requirement.
4. Claim the slug when required, then scaffold with `playdrop project create app <slug> --template <allowed-template-key>`. Do not create projects by hand or prefill a root catalogue before scaffolding.
5. Replace the sample loop. The finished game needs agency, feedback, challenge, visible progress or payoff, and a reliable restart. Use coherent finished assets, not emoji, basic shapes, or default engine primitives as its identity.
6. In `catalogue.json`, declare one honest `primarySurface`, only supported `surfaceTargets`, and one complete playtest tape per surface. Treat task `surfaceContext` as the submitting device, not a design requirement.
7. Create original expression. A referenced game may inform genre and function, never its name, characters, art, audio, text, level design, or presentation.
8. Read `../make-listing/SKILL.md` before creating the required new-game identity trio: a square app icon, portrait hero, and landscape hero. Its title, composition, file-size, production-owner, inspection, and manifest rules are mandatory. Keep screenshots, gameplay video, capture reports, and social packages absent unless the creator explicitly requests them.
9. After the last runtime change, run the deterministic final check from `playtest-game`, verify the listing metadata, validate, then deliver through the workflow that invoked this skill.

Use `../../references/phases/new-game.md` for creator-facing progress vocabulary. Working notes such as `GAME.md`, `ART_DIRECTION.md`, and `AGENTS.md` are optional memory, never delivery gates.
