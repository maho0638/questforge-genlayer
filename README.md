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
| Official GenLayer Direct Mode tests | **5/5 PASS** (GitHub Actions; actual SDK fixture, not Studionet) |
| `genvm-lint check` | **PASS** (GitHub Actions, official linter) |
| Studionet deploy / on-chain finality | **NOT RUN** — requires separate chain/gas approval |
| Reviewer/portal submission | Not submitted |

`PYTHONPATH=tests/local python -m pytest tests/local -q` runs the isolated fake-SDK logic tests. The repository includes a non-deploying GitHub Actions workflow, verified successful.

With GenLayer tooling installed, run:

```bash
python -m pip install -r requirements.txt
genvm-lint check contracts/quest_forge.py
pytest tests/direct/ -v
```

GitHub Actions verified these commands against the actual SDK and official linter: https://github.com/maho0638/questforge-genlayer/actions/runs/45045352664. See `docs/THREAT_MODEL.md` and `docs/RELEASE_GATE.md`.

## Release control

Before Portal submission, **REMIND OWNER TO CHANGE BOTH PRIVATE GITHUB REPOSITORIES TO PUBLIC** and verify access while logged out. GitHub source push was separately authorized and completed. Chain deploy, gas spending and Portal submission require separate explicit user permission.

Official Direct Mode tests passed in GitHub Actions, with mocked LLMs and validator reruns; these are NOT finalized on-chain consensus or Studionet transactions.

## QA v3 update (2026-11-22)

- Supplemental negative tests now reject Unicode bidi/zero-width display spoofing in signed charter/move text.
- Canonicalizes wallet address case before constructing SDK Address.
- QuestForge rejects boolean turn nonce before type conversion.
- CharterCycle covers quorum acceptance/rejection for all configured member counts 3..15.
- QuestForge runs 100 reproducible seeded game traces with bounds assertions.
- Official GenVM lint and Direct Mode passed in GitHub Actions (5/5 Direct Mode); live Studionet proof has NOT been claimed.
- Verified exact source SHA-256: `da662f7678b6bc24670be20485f1811033af359e46eb5c86a6529e84598c70ee`; canonical CI: https://github.com/maho0638/questforge-genlayer/actions/runs/45045352664.
