# QuestForge — Consensus-Refereed Cooperative Strategy (GenLayer)

**Python GenLayer Intelligent Contract only — no website. Live-verified on Studionet (chain ID 61999).**

## Implemented contract

Source: `contracts/quest_forge.py`. One standalone `gl.Contract` with persistent GenLayer storage.

- Two wallet-authenticated players, three immutable puzzle stages and a 12-turn maximum
- AI classifies SOLVE moves; validator independently checks the decisive label
- Deterministic energy, insight, threat, turn nonce, victory and loss accounting
- Two concurrent games per creator; no globally exhaustible 128-game lifetime or active ceiling
- 48-hour forfeit to the non-stalling player; permissionless neutral expiry after 7 days
- Terminal-state slot recovery, immutable game IDs, no wagering, transfers, or website

## Independent verification (2026-11-22)

- **39/39** local logic tests PASS (fake SDK, not chain).
- **7/7** official GenLayer Direct Mode tests PASS (SDK storage, mock LLM, validator reruns).
- **GenVM lint PASS**, including official validation checks.
- Python compilation and supplemental AST audit PASS.
- [Canonical successful GitHub Actions run](https://github.com/maho0638/questforge-genlayer/actions/runs/45056608635)
- Verified source SHA-256: `1527dca395726d9b7495f9af6ec1ef4bb3be6354d40eb24e29aac5a110d72d84`
- Verified source commit: `7d85ba25b6ddc68674aaafa482c40eb99470377b`
- **Studionet LIVE VERIFIED:** 0x0362B282B2389B8AE1D609a845b32986675573b3; four transactions FINALIZED; semantic PASS; 3 Agree / 2 Idle votes.

For reproducibility:

```bash
python -m pip install -r requirements.txt
genvm-lint check contracts/quest_forge.py
PYTHONPATH=tests/local python -m pytest tests/local -q
pytest tests/direct -v
```

Full security limitations: `docs/THREAT_MODEL.md`. Latest exact test evidence: `docs/QA_STATUS.md` and `docs/LOCAL_PROOF_MANIFEST.json`.

## Publication gate

**BEFORE PORTAL SUBMISSION: Change both GitHub repositories from PRIVATE to PUBLIC and verify logged-out access.**
Chain deployment/gas, Portal submission, and any other external action need separate explicit user authorization.

## Final live consensus record — 2026-11-22

- [Live GenLayer Studionet test](https://github.com/maho0638/questforge-genlayer/actions/runs/45057554737): **PASS**.
- [Independent six-transaction RPC finality and voting audit](https://github.com/maho0638/chartercycle-genlayer/actions/runs/45057971178): **PASS**.
- `docs/STUDIONET_PROOF.json` contains source SHA-256, contract address, all transaction hashes, real validator vote tally (3 Agree / 2 Idle), and observed outcomes.
- No website/Vercel deployment. Portal not submitted. Both private repositories must be changed to Public before Portal.
