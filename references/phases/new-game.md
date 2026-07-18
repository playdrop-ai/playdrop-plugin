# New Game Phases

Use phases flexibly: skip what is genuinely irrelevant to the request, but never skip design, scaffold, core loop, playtest, or listing. Each phase says what must exist when it ends; how you get there is yours.

1. `initializing`: choose the primary surface from the creator surface unless it is a terrible fit, identify every honestly supported surface, and inspect the allowed templates and catalogue example.
2. `research`: search PlayDrop first (`playdrop search`, `playdrop detail`). Exit with your notes naming the packs, assets, and similar games you considered and what you borrowed or rejected. Research outside references only when the request has a clear real-world reference.
3. `game-design`: exit with, in your working notes: the smallest fun core loop, the intended feel, the chosen template, and a concise art concept covering fantasy, identity, setting, palette, and UI material. Engine choice is a recorded decision: continuous motion, physics, camera, or spatial 2D gameplay means `phaser-2d`; 3D means `three-js`; `plain-html` only for turn-based or static-screen UI games (word, quiz, card, board). After choosing `phaser-2d` or `three-js`, immediately read exactly one matching engine skill at `skills/phaser-2d-game/SKILL.md` or `skills/three-js-game/SKILL.md`; never read both for one game. When in doubt choose the engine template. Do not write a nonempty root `catalogue.json` before scaffolding; files come at scaffold exit.
4. `scaffold`: create the project with `playdrop project create app <slug> --template <allowed-template-key>`; never hand-create it. Exit with the app entry written in the scaffolded `catalogue.json`, including top-level `primarySurface`, one complete `playtestTapes` entry per enabled `surfaceTargets` surface, and any honest optional design tag refs (see `references/catalogue-json.md`). Keep each tape small and express the real core interaction on that surface. When useful, retain the richer plan in concise `GAME.md`, `ART_DIRECTION.md`, and `AGENTS.md` files after scaffolding; preserve files that already exist and never make their presence a gate.
5. `greybox-core-loop`: build and repeatedly play the smallest loop until the primary interaction, challenge, controls, feedback, restart, and intended feel work. Temporary primitives and plain shapes are allowed only as planned greybox visuals for this phase; they are not shippable assets or a fallback, and must be replaced before upload.
6. `art-direction`: with the working loop as ground truth, exit with the hero art pair and mockup board per `references/art-direction-board.md`. Mandatory for every game, including simple UI games; on media failure, Cloud tasks fail here and direct creators may defer per the media failure policy in `skills/make-assets`.
7. `art-production`: replace the greybox and integrate every gameplay asset coherently: reuse first, generate what is uncovered (`skills/make-assets`), background per `references/art-direction-board.md` step 5. Exit with the complete loop still feeling good and the shipped screens recognizable as the direction contract's (`references/art-direction-board.md` step 3). Primary identity and interactive objects are never primitives, emoji, or plain CSS shapes in the shipped game (exceptions per `skills/make-assets`).
8. `playtest`: add any preview hooks needed by `skills/make-listing`, run `playdrop project check .`, then run `playdrop project check . --tape <surface>` for every enabled surface and fix what any run finds. Inspect each matched idle and tape pair, with the declared primary surface as the required acceptance proof. Exit only when every tape visibly and meaningfully beats idle by surviving longer, scoring above idle, making visible progress, or reaching a state idle never reaches; and with the proof `skills/playtest-game/SKILL.md` defines (primary input, success, failure, nothing dead on arrival) plus one gameplay screenshot recognizably matching the direction contract.
9. `store-listing`: exit per `skills/make-listing/SKILL.md`: accurate listing assets and metadata, capture per your task type.
10. `wrap-up`: validate, upload/publish as instructed, write next-step suggestions when in a task.

Local Agent and other direct-creator tasks never run `project capture` in the worker and omit `listing.captureReport`; use the `project check` screenshot flow instead.

## Route by game type

- `phaser-2d` games: load `skills/phaser-2d-game/SKILL.md`; real background art per `references/art-direction-board.md` step 5.
- `three-js` games: load `skills/three-js-game/SKILL.md`; the rendered environment is the backdrop.
- `plain-html` games (word, quiz, card, board): the playfield still sits on real background art per `references/art-direction-board.md` step 5, never default chrome.
- Endless or story progressions: success and failure proof per `skills/playtest-game/SKILL.md`; pressure and restart are still required.
- Large bespoke asset families: route per `skills/make-assets`, usually as its own job rather than a step inside a timed build.

Design comes before scaffold choice. Durable project files come from the CLI scaffold, never from hand-created scratch files.
