# QuestForge — Consensus-Refereed Cooperative Strategy (GenLayer)

**Python Intelligent Contract only — no frontend or Vercel project. Not deployed on Studionet.**

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
- **No Studionet transaction, contract deployment, on-chain finalization or real validator vote has been executed for this project.**

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
