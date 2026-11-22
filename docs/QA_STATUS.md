# QA verified — questforge-genlayer

Checked: 2026-11-22

- Contract: `contracts/quest_forge.py`
- Contract SHA-256: `da662f7678b6bc24670be20485f1811033af359e46eb5c86a6529e84598c70ee`
- Python syntax: **PASS**, verified GitHub Actions
- Supplemental AST audit: **PASS**, custom only
- Fake-SDK local pytest: **34/34 PASS** (NOT chain proof)
- Official `genvm-lint check contracts/*.py`: **PASS** (3 checks + validation)
- Official GenLayer Direct Mode (`genlayer-test==0.29.2`): **5/5 PASS** including validator mismatch scenarios
- CI run for exact contract version: https://github.com/maho0638/questforge-genlayer/actions/runs/45045352664
- CI job ID: `137278653715`; contract commit: `e3f9aaac07b03296423ccb2862b6e28fba788227`
- Studionet deploy, actual write/read, transaction finality and live validator consensus: **NOT RUN** (separate chain/gas authorization required)
- Portal submission: **NOT AUTHORIZED**

The CI pipeline copies the official `genvm-runners-all.tar.xz` bundle cached by `genvm-linter` into the legacy `gltest-direct` cache filename to fix the upstream missing `genvm-universal.tar.xz` release asset. It does NOT bypass GenVM testing.

**Before Portal submission:** change **BOTH** private GitHub repositories to Public; verify anonymous access. The successful CI is not evidence of on-chain deployment.
