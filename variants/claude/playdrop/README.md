# PlayDrop for Claude Code

Publish, test and share the browser games you build with Claude Code on PlayDrop. This plugin adds the
`playdrop-ai` skill and a connection to PlayDrop's remote MCP server. After installing, run `/mcp`, select `plugin:playdrop:playdrop` and choose Authenticate to sign in to your PlayDrop
account; there is no CLI or package to install. Then run `/playdrop:publish` or ask Claude Code to publish your game.

Your agent can publish `index.html` with listing images, videos and localized art, upload privately to test first,
add the optional PlayDrop SDK, upload a Colyseus `server.js` for free hosted multiplayer with MongoDB, and send
feedback to the PlayDrop team.

- Setup guide: https://www.playdrop.ai/docs/connectors
- Documentation: https://www.playdrop.ai/docs
- Source and other clients: https://github.com/playdrop-ai/playdrop-plugin
- Support: support@playdrop.ai

MIT licensed. The PlayDrop service is operated separately under its own terms and privacy policy.

## Privacy and data handling

This package runs no local commands, hooks or background jobs. It supplies a skill and an HTTPS connection to
`https://mcp.playdrop.ai/mcp`. After you sign in and authorize PlayDrop, tool calls can read your account and games,
fetch documentation, submit feedback, and upload the game files and listing metadata you ask to publish. Uploads
may include source code, images, videos and optional game-server code. Public uploads are visible to others;
private uploads are for testing. The plugin does not collect conversation transcripts itself.

See the [PlayDrop privacy policy](https://www.playdrop.ai/legal/privacy) for service data handling and contact
support@playdrop.ai for help or data requests. The bundled [PlayDrop icon](assets/playdrop-icon-large.png) is a
512×512 PNG.
