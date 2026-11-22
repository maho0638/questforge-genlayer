# QuestForge — Consensus-Refereed Cooperative Strategy (GenLayer)

**Contract only — no frontend. Development draft; not deployed or audited.**

## What is actually implemented

- `contracts/quest_forge.py`: one standalone `gl.Contract`, version-pinned.
- Two authenticated wallet addresses per game; invitee must accept before play.
- One actor per turn, monotonic turn nonce, immutable hashed move receipts.
- Three frozen cooperative puzzle stages with bounded semantic `SOLVE` criteria.
- Leader and validators independently label a proposed `SOLVE` move `PASS` / `FAIL` / `UNDETERMINED` against the *same static goal*. A disagreement prevents consensus.
- Deterministic `SCOUT`, `FORTIFY`, `REST`; energy/insight/threat, progression, victory, loss, and timeout applied by code, not LLM text.
- `UNDETERMINED` reverts without resources or turn consumed; game supports a no-stall forfeit path and expired lobby cancellation.
- No wagers, assets, oracle dependency, off-chain server, or value transfer.

## Code surface

- `QuestForge()`
- `create_game(game_id, invited_player)` / `join_game(game_id)` / `cancel_lobby(game_id)`
- `act(game_id, expected_turn, action, narrative)` / `claim_timeout(game_id)`
- `get_game(id)`, `get_turn(id, index)`, `get_stage(index)`, `get_game_count()`, `get_game_id(i)`

## Verification matrix

| Stage | Status |
|---|---|
| Python compile | PASS (locally) |
| Supplementary AST audit (NOT official lint) | PASS (locally) |
| Pure-Python contract-logic simulation | PASS (34 tests, fake SDK and fake LLM) |
| Official GenLayer Direct Mode test source | Prepared, **not executed** |
| `genvm-lint check` | **Not executed** (linter unavailable in authoring runtime) |
| Real GenVM / Studionet | **Not executed** |
| Reviewer/portal submission | Not submitted |

`PYTHONPATH=tests/local python -m pytest tests/local -q` runs the isolated fake-SDK logic tests. The repo also contains non-deploying GitHub Actions checks, but they have NOT run because no push is authorized.

With GenLayer tooling installed, run:

```bash
python -m pip install -r requirements.txt
genvm-lint check contracts/quest_forge.py
pytest tests/direct/ -v
```

These commands are documentation only until the checks are run and captured with exact tool versions. See `docs/THREAT_MODEL.md` and `docs/RELEASE_GATE.md`.

## Release control

Before Portal submission, **REMIND OWNER TO CHANGE BOTH PRIVATE GITHUB REPOSITORIES TO PUBLIC** and verify access while logged out. No git push/merge, chain deploy, gas spending or Portal submission without separate explicit user permission.

The official Direct Mode tests are authored but **not independently verified** in this local environment. Current CI and test results must never be represented as finalized on-chain consensus.

## QA v3 update (2026-11-22)

- Supplemental negative tests now reject Unicode bidi/zero-width display spoofing in signed charter/move text.
- Canonicalizes wallet address case before constructing SDK Address.
- QuestForge rejects boolean turn nonce before type conversion.
- CharterCycle covers quorum acceptance/rejection for all configured member counts 3..15.
- QuestForge runs 100 reproducible seeded game traces with bounds assertions.
- No real GenVM lint, Direct Mode execution or live chain proof has been claimed.
