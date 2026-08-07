# Security and data handling

The PlayDrop plugin is a skills-only package. It does not include an MCP server, background service, analytics client, or bundled credentials.

Some skills use the separately installed PlayDrop CLI to read or change the creator's PlayDrop projects. Commands that upload, publish, replace, or otherwise change remote state are described in the relevant skill. Authentication remains in the PlayDrop CLI session. The plugin instructs agents not to request, print, copy, or commit secrets.

The 2D asset-pack skill includes local scripts that read and write files inside the creator-selected working directory and can start a loopback-only review server. It does not accept non-loopback review endpoints.

Report suspected vulnerabilities privately to [support@playdrop.ai](mailto:support@playdrop.ai). Include the affected version, reproduction steps, and impact. For ordinary bugs and feature requests, use the public [issue tracker](https://github.com/playdrop-ai/playdrop-plugin/issues).
