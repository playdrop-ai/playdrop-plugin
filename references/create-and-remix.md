# Create And Remix

Use this when starting a new project or when a public Playdrop app is already close to the target.

Start with:
- `playdrop browse --kind app --app-type template --json`
- `playdrop project create app <name> --template <ref>`
- `playdrop project create app <name> --remix <ref>`
- `playdrop detail <ref> --json`

Decision rule:
- use a template when starting a new app
- align with a starter when the fit is partial
- remix when the fit is already strong

Before remixing:
- inspect the reference first
- confirm that the art, controls, systems, and packaging direction are close enough
