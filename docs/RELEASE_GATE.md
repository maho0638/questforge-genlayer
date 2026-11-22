# Hard release gate — action requires user approval

- [ ] Official `genvm-lint check` PASS on exact source hash, evidence captured.
- [ ] Official GenLayer Direct Mode tests PASS, including validator disagreements.
- [ ] Studionet deployments and real write/read finalization PASS; record addresses and TX hashes.
- [ ] Source SHA-256 equals deployed proof manifest; preserve validator/leader results.
- [ ] Security review: auth, replay, duplicate IDs, ranges, time windows and terminal states.
- [ ] Review external duplicate projects / reviewer criteria one last time.
- [ ] **Explicit user permission for GitHub push** before creating commits on the remote.
- [ ] **REMIND USER: make BOTH GitHub repositories Public before Portal submission**, then verify unauthenticated read access.
- [ ] **Explicit user permission for chain deploy / gas and Portal submission.**

Source code, tests, mock simulation and successful CI are distinct from real finalized GenLayer transactions.
