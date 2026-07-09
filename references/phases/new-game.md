# New Game Phases

Use phases flexibly. Skip research that is irrelevant, but do not skip design, scaffold, core loop, playtest, or listing.

1. `initializing`: claim the slug when needed, choose the primary surface from the creator surface unless it is a terrible fit, and inspect the allowed templates and catalogue example.
2. `research`: ALWAYS search PlayDrop packs and assets: name at least 2 candidate packs and 2 individual catalogue assets that could fit this game in your notes, or state per need why none fit. ALWAYS browse 2 existing PlayDrop games or demos close to this genre (`./bin/playdrop search --kind app`, `./bin/playdrop detail <ref>`) and write one line each on what to borrow (controls, HUD, feedback, asset usage). Research outside references only when the request has a clear real-world reference.
3. `game-design`: decide the one-page game direction and choose the template before scaffolding. Do not write a nonempty root `catalogue.json` before `project create app`; the scaffold command owns initial project registration and folder creation. Engine choice is a recorded decision: continuous motion, physics, camera, or spatial 2D gameplay means `phaser-2d`; 3D means `three-js`; `plain-html` is allowed only for turn-based or static-screen UI games (word, quiz, card, board) that need no engine features. When in doubt choose the engine template.
4. `scaffold`: create the project with `./bin/playdrop project create app <slug> --template <allowed-template-key>`. Never hand-create the project. Immediately after scaffolding, write the durable app entry in the scaffolded app's `catalogue.json`, then run `./bin/playdrop task report-catalogue --file <app-folder>/catalogue.json --message "Planned the version"`.
5. `art-direction`: Generate the art-direction board per `references/art-direction-board.md` and extract the palette into the design. This is mandatory for every game, including simple UI games.
6. `art-production`: Follow `skills/make-assets` preference order against the board: packs and catalogue assets first per asset need; for uncovered needs use `references/asset-sheet.md`. The mascot/hero and all primary interactive objects must be real image assets consistent with the board. Never ship primitive shapes, emoji, or plain CSS shapes as the primary identity.
7. `core-loop`: build the smallest loop that has action, challenge, feedback, scoring/progression, restart, and a visible payoff.
8. `playtest`: run `./bin/playdrop project check .` with focused-frame actions when input is needed, then fix broken controls, invisible entities, impossible goals, blank first frames, renderer failures, and console errors.
9. `store-listing`: follow `skills/make-listing/SKILL.md`; create accurate listing assets and metadata in `catalogue.json`, implement recorder-ready preview hooks, run native capture with the final build hash, and store `listing.captureReport`.
10. `wrap-up`: validate, upload/publish as instructed, write next-step suggestions when in a task.

Design comes before scaffold choice. Durable project files still come from the CLI scaffold, never from hand-created scratch files.
