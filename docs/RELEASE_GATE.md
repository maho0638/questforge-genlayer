# Release gate — explicit authorization required

- [x] Source committed to GitHub under user-authorized development task
- [x] Local fake-SDK regression 39/39
- [x] Python compilation and supplemental static checks
- [x] Official `genvm-lint check` PASS
- [x] Official GenLayer Direct Mode 7/7 PASS, including validator mismatch
- [x] Security audit: wallet permissions, replay, boundary times, retained ID history, terminal-state accounting
- [ ] Studionet deployment and independent real-chain read/write/finality
- [ ] Record real on-chain contract address, transaction hashes, leader/validator results, gas
- [ ] Verify on-chain source correspondence and finality from the Explorer/RPC
- [ ] Review latest Portal criteria and distinctness against live competing contributions
- [ ] **Reminder: Both private repositories must be made Public before Portal submission; verify logged-out access**
- [ ] User's separate explicit authorization for chain deployment/gas
- [ ] User's separate explicit authorization for Portal submission

Evidence of code-level checks: https://github.com/maho0638/questforge-genlayer/actions/runs/45056608635

No on-chain claim should be made before verified finalized transactions.
