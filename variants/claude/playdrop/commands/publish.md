---
description: Publish this game on PlayDrop and get its playable link
argument-hint: "[private|unlisted|public]"
---

Publish the game in this project on PlayDrop and give me its playable link.

Read `get_documentation({topic:"publishing"})`. Use `upload_game` for a self-contained HTML game up to 10 MiB
without PlayDrop SDK features. For multiple files, listing media, SDK features or a server, use
`prepare_catalogue_upload` and `complete_catalogue_upload` with a built folder; unpack a ZIP or `.play` locally first.
Keep the source project here.

Find an existing game with `list_games` and preserve its identity on updates. If the arguments name a visibility
(arguments: $ARGUMENTS), use it exactly: `private` for owner-only testing, `unlisted` for anyone with the link,
`public` for discovery. Otherwise a new game takes my saved setting (`get_account` shows
`publishing.defaultVisibility`) and an update keeps the game's current `gameVisibility` from `list_games`;
`upload_game` does both when visibility is left out.
Return the receipt's `shareUrl` for a public or unlisted game, or the private exact-version `url`.

If PlayDrop's tools are unavailable, ask me to run `/mcp`, select `plugin:playdrop:playdrop` and choose Authenticate.
