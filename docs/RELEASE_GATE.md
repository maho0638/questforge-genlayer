# Release gate — explicit authorization required

- [x] Source committed to GitHub under user-authorized development task
- [x] Local fake-SDK regression 39/39
- [x] Python compilation and supplemental static checks
- [x] Official `genvm-lint check` PASS
- [x] Official GenLayer Direct Mode 7/7 PASS, including validator mismatch
- [x] Security audit: wallet permissions, replay, boundary times, retained ID history, terminal-state accounting
- [x] Studionet deployment and independent real-chain read/write/finality
- [x] Record real on-chain contract address, transaction hashes, leader/validator results (gas not independently measured)
- [x] Verify on-chain source correspondence via SHA-256 and finality via RPC
- [ ] Review latest Portal criteria and distinctness against live competing contributions
- [ ] **Reminder: Both private repositories must be made Public before Portal submission; verify logged-out access**
- [ ] User's separate explicit authorization for chain deployment/gas
- [ ] User's separate explicit authorization for Portal submission

Evidence of code-level checks: https://github.com/maho0638/questforge-genlayer/actions/runs/45056608635

No on-chain claim should be made before verified finalized transactions.

## Finalized live proof

- `docs/STUDIONET_PROOF.json`; https://github.com/maho0638/questforge-genlayer/actions/runs/45057554737
- Validator votes: 3 Agree / 2 Idle; all four txs FINALIZED.
