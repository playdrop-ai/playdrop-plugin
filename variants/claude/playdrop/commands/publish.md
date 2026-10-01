---
description: Publish this game on PlayDrop and get its public link
argument-hint: "[private]"
---

Publish the game in this project on PlayDrop and give me its public link.

- Package it as one self-contained `index.html` of up to 5 MiB, and give it a clear title in the catalogue.
- If it is already on PlayDrop, update that game with its `gameId` from `list_games` and the same catalogue name, so
  its link stays the same.
- If the arguments say private (arguments: $ARGUMENTS), upload it with `visibility: "private"` so only I can open
  it for testing.

Use PlayDrop's `upload_game` tool, or `prepare_game_upload` and `complete_game_upload` to include listing images
and videos. Reply with the returned `shareUrl` (or `url` for a private upload). If PlayDrop's tools are not available, tell me to run `/mcp`, select `plugin:playdrop:playdrop` and
choose Authenticate.
