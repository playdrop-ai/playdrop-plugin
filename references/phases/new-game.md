# New Game Phases

Use phases flexibly. Skip research that is irrelevant, but do not skip design, scaffold, core loop, playtest, or listing.

1. `initializing`: claim the slug when needed, choose the primary surface from the creator surface unless it is a terrible fit, and inspect the allowed templates and catalogue example.
2. `research`: ALWAYS search PlayDrop packs and assets: name at least 2 candidate packs and 2 individual catalogue assets that could fit this game in your notes, or state per need why none fit. ALWAYS browse 2 existing PlayDrop games or demos close to this genre (`./bin/playdrop search --kind app`, `./bin/playdrop detail <ref>`) and write one line each on what to borrow (controls, HUD, feedback, asset usage). Research outside references only when the request has a clear real-world reference.
3. `game-design`: decide the one-page game direction inside `catalogue.json.design`. Include genre, coreGameplay, render, camera, input, progression, artStyle, engine, assetStrategy, coreAssets, features, and references where applicable. Choose the template here. Engine choice is a recorded decision: continuous motion, physics, camera, or spatial 2D gameplay means `phaser-2d`; 3D means `three-js`; `plain-html` is allowed only for turn-based or static-screen UI games (word, quiz, card, board) that need no engine features. When in doubt choose the engine template. Record the reason in design.references.
4. `scaffold`: create the project with `./bin/playdrop project create app <slug> --template <allowed-template-key>`. Never hand-create the project.
5. `art-direction`: make a concrete visual target. Use real assets or screenshots as references for any generated hero/mockup art.
6. `art-production`: follow `skills/make-assets` preference order: PlayDrop packs and catalogue assets first per asset need, then CC0, then agent-native generation, then PlayDrop CLI AI generation. The mascot/hero and all primary interactive objects must be real image assets. Never ship primitive shapes, emoji, or plain CSS shapes as the primary identity.
7. `core-loop`: build the smallest loop that has action, challenge, feedback, scoring/progression, restart, and a visible payoff.
8. `playtest`: run the self-playtest checklist and fix broken controls, invisible entities, impossible goals, blank first frames, and console errors.
9. `store-listing`: create accurate listing assets and metadata in `catalogue.json`.
10. `wrap-up`: validate, upload/publish as instructed, write next-step suggestions when in a task.

Design comes before scaffold choice. Project files still come from the CLI scaffold, never from hand-created scratch files.
