# QA v3 — questforge-genlayer

Checked: 2026-11-22

- Contract SHA-256: `5fb1b313102cf54a4d0eb670bc494f14b92fa06aa9f0eb060856fd19c9aa3106`
- `python -m compileall -q contracts tests`: **PASS**
- `python scripts/static_contract_audit.py`: **PASS** (custom, NOT official GenVM lint)
- `PYTHONPATH=tests/local python -m pytest tests/local -q`: **34/34 PASS** (fake SDK, NOT GenVM)
- Official `genvm-lint check`: **NOT RUN** — runtime tooling unavailable; package network blocked
- Official Direct Mode with `genlayer-test`: **NOT RUN** — dependencies unavailable
- Studionet deployment, transactions, finality and validator consensus: **NOT RUN** — needs separate gas/chain authorization
- GitHub CI: **PENDING** — CI will execute after approved push

Local tests include parameter loops; loop iterations are not separately counted as pytest cases.

**Pre-submission reminder:** Both GitHub repositories currently Private; make both Public and verify anonymous access before Portal submission.
