# Create And Remix

Use this when starting a new project or when a public Playdrop app is already close to the target.

Start with:
- `playdrop creations ideas browse --state all --json` when the user mentions a saved game idea or likely idea name
- `playdrop browse --kind app --app-type template --json`
- `playdrop project create app <name> --template <ref>`
- `playdrop project create app <name> --remix <ref>`
- `playdrop detail <ref> --json`

Decision rule:
- use a saved GameIdea as the source of truth when one matches the user's request
- when creating from a saved GameIdea, run `playdrop project create app <name> --game-idea <id-or-slug>` and let the CLI infer the stored remix source or the default TypeScript template
- use a template when starting a new app
- align with a starter when the fit is partial
- remix when the fit is already strong
- pass `--game-idea <id-or-slug>` to `playdrop project publish <app-name>` when shipping the saved idea

Before remixing:
- inspect the reference first
- confirm that the art, controls, systems, and packaging direction are close enough
