# Live Ops

Use this when managing a game after launch.

Typical tasks:
- check your creations and release state
- review comments and current release status
- answer comments
- prepare and publish updates

Workflow:
- review current creations with `playdrop creations browse --kind app --creator me --json`
- review comments with `playdrop comments browse <ref>`
- review release history with `playdrop versions browse <ref>`
- identify the next change worth shipping
- update app metadata with `playdrop creations apps update <name>` when needed
- validate and publish the update when ready
