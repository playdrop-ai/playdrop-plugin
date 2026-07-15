# New Game Phases

Use phases flexibly: skip what is genuinely irrelevant to the request, but never skip design, scaffold, core loop, playtest, or listing. Each phase says what must exist when it ends; how you get there is yours.

1. `initializing`: choose the primary surface from the creator surface unless it is a terrible fit, and inspect the allowed templates and catalogue example.
2. `research`: search PlayDrop first (`playdrop search`, `playdrop detail`). Exit with your notes naming the packs, assets, and similar games you considered and what you borrowed or rejected. Research outside references only when the request has a clear real-world reference.
3. `game-design`: exit with the one-page direction, the chosen template, and the concept block decided: fantasy, identity, setting, palette, UI material. Engine choice is a recorded decision: continuous motion, physics, camera, or spatial 2D gameplay means `phaser-2d`; 3D means `three-js`; `plain-html` only for turn-based or static-screen UI games (word, quiz, card, board). When in doubt choose the engine template. Do not write a nonempty root `catalogue.json` before scaffolding.
4. `scaffold`: create the project with `playdrop project create app <slug> --template <allowed-template-key>`; never hand-create it. Exit with the app entry written in the scaffolded `catalogue.json`, including the concept block fields (see `references/catalogue-json.md`).
5. `art-direction`: exit with the hero art pair and the mockup board per `references/art-direction-board.md`. Mandatory for every game, including simple UI games.
6. `art-production`: exit with every gameplay asset real and coherent: reuse first, generate what is uncovered (`skills/make-assets`), background per `references/art-direction-board.md` step 5. Primary identity and interactive objects are never primitives, emoji, or plain CSS shapes.
7. `core-loop`: exit with the smallest loop that has action, challenge, feedback, scoring or progression, restart, and a visible payoff. A valid board is the screen contract: the shipped screens must be recognizable as the board's. How you build them is yours.
8. `playtest`: run `playdrop project check .` with focused-frame actions; fix what it finds. Exit only with the proof `skills/playtest-game/SKILL.md` defines (primary input, success, failure, nothing dead on arrival) and one gameplay screenshot recognizably matching the board's gameplay screen (or the hero direction when the board is advisory).
9. `store-listing`: exit per `skills/make-listing/SKILL.md`: accurate listing assets and metadata, preview hooks, capture per your task type.
10. `wrap-up`: validate, upload/publish as instructed, write next-step suggestions when in a task.

## Route by game type

- 2D action, physics, or spatial play: `phaser-2d` template; engine mechanics live in `references/tech/phaser-2d.md`; real background art per the direction.
- 3D: `three-js` template (`references/tech/three-js.md`, plus `references/tech/rapier.md` for physics); the rendered environment is the backdrop.
- Turn-based or static-screen UI games (word, quiz, card, board): `plain-html` allowed; the playfield surface is still designed art, not default chrome.
- Endless or story progressions: the success proof is the designed milestone or chapter moment; pressure or failure and restart are still required.
- Large bespoke asset families (multi-family packs, paired size variants): the `make-2d-asset-pack` skill, usually as its own job rather than a step inside a timed build.

Design comes before scaffold choice. Durable project files come from the CLI scaffold, never from hand-created scratch files.
