# QuestForge — Security/liveness changes (v4)

Exact contract source SHA-256: `1527dca395726d9b7495f9af6ec1ef4bb3be6354d40eb24e29aac5a110d72d84`.

- Two concurrent games per creator; no globally exhaustible 128-game lifetime or active ceiling
- 48-hour forfeit to the non-stalling player; permissionless neutral expiry after 7 days
- Terminal-state slot recovery, immutable game IDs, no wagering, transfers, or website

- Official CI: **SUCCESS**, local 39/39 PASS, Direct Mode 7/7 PASS, GenVM lint PASS.
- Run: https://github.com/maho0638/questforge-genlayer/actions/runs/45056608635
- No live transaction; Studionet requires explicit permission.
