# New Game Phases

Use phases flexibly. Skip research that is irrelevant, but do not skip design, scaffold, core loop, playtest, or listing.

1. `initializing`: claim the slug when needed, choose the primary surface, choose an official template, and scaffold with `./bin/playdrop project create app <slug> --template <allowed-template-key>`.
2. `research`: search PlayDrop assets/packs/references when the request mentions assets, style, remix, or a known genre. Research outside references only when the requested game has a clear real-world reference.
3. `game-design`: decide the one-page game direction inside `catalogue.json.design`. Include genre, coreGameplay, render, camera, input, progression, artStyle, engine, coreAssets, features, and references where applicable.
4. `art-direction`: make a concrete visual target. Use real assets or screenshots as references for any generated hero/mockup art.
5. `art-production`: choose PlayDrop packs first, then CC0, then agent-native generation, then PlayDrop CLI AI generation, then deliberate simple prototype visuals.
6. `core-loop`: build the smallest loop that has action, challenge, feedback, scoring/progression, restart, and a visible payoff.
7. `playtest`: run the self-playtest checklist and fix broken controls, invisible entities, impossible goals, blank first frames, and console errors.
8. `store-listing`: create accurate listing assets and metadata in `catalogue.json`.
9. `wrap-up`: validate, upload/publish as instructed, write next-step suggestions when in a task.

Design comes before scaffold choice. Project files still come from the CLI scaffold, never from hand-created scratch files.
