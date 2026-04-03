# Test Accounts

Use this for local multiplayer or auth-sensitive validation.

## Practices

- test with more than one account when multiplayer or sharing matters
- separate anonymous, optional-auth, and required-auth flows
- validate reconnect and account-switch behavior
- for multiplayer, verify that more than one client can join and progress without desync
