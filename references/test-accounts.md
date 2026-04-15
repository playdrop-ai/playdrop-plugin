# Test Accounts

Use this for local multiplayer or auth-sensitive validation.

## Hosted dev modes

- `prompt` keeps the normal hosted `/dev` behavior and lets the browser session choose at auth time
- `anonymous` keeps the hosted session guest for login-wall and guest-flow testing
- `viewer` uses the real signed-in PlayDrop account when the app asks for auth
- `player` with `--player 1..4` uses one of the creator-owned sandbox players for deterministic multiplayer and persistence testing

## Practices

- test with more than one account when multiplayer or sharing matters
- separate anonymous, optional-auth, and required-auth flows
- validate reconnect and account-switch behavior
- for multiplayer, verify that more than one client can join and progress without desync

## Useful commands

- `playdrop project dev <app>`
- `playdrop project dev-browser <app> --dev-auth anonymous`
- `playdrop project dev-browser <app> --dev-auth viewer`
- `playdrop project dev-browser <app> --dev-auth player --player 1`
