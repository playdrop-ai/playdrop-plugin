---
name: playdrop-publish
description: Upload, update and share an HTML game on PlayDrop using its remote MCP tools.
---

PlayDrop hosts AI-coded games on the web and native iOS, Android, Windows and Mac apps.
Use the connected PlayDrop MCP tools when the user wants to publish or update a game.

1. Read `get_documentation` and `get_account` for the current catalogue format and quotas.
2. Supply one `index.html` and `catalogue.json`; minimal catalogue: `{"apps":[{"name":"my-game"}]}`.
   Keep HUD and controls inside mobile safe areas. Rich metadata and localization improve presentation and reach.
3. Use `upload_game` for content you can reliably supply in tool arguments. For larger local files, compute hashes,
   call `prepare_game_upload`, stream to its signed PUT URL with all required headers, then `complete_game_upload`.
   The environment needs network permission for that upload host. Both paths publish publicly.
4. Keep the same request ID and exact content when retrying. Updates require the existing game ID and matching slug.
   Use a new request ID for edits; cancel only your obsolete unfinished upload. Return the playable URL.

OAuth connection is the one-time browser step. Publishing needs no browser tool, page visit or full PlayDrop CLI.
Studio-created games are separate and cannot be modified here. Consult MCP documentation for new capabilities,
including the forthcoming SDK; do not assume SDK support is available now.
