# Questforge — liveness/security regression v4

Scope: contract code and tests only; no website, deploy or transactions.

- Removed the permanent global lifetime limit on historical objects.
- Added bounded live-operation controls and eventual capacity recovery.
- Kept prior stored IDs and records immutable; newly added public methods only.
- Expanded fake-SDK negative/invariant cases and official Direct Mode tests.
- Real chain finality remains NOT VERIFIED pending separate authorization.

CI status: pending current code push and GitHub Actions results.

Controls: 128 concurrent games, 2 active per creator; slot returned on every terminal result; neutral expiry after 7 inactive days.
