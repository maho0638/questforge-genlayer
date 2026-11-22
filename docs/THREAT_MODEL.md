# QuestForge — threat model and explicit limitations

## Protected by deterministic contract code

- Only the designated creator and accepted invited player can participate.
- A turn changes state only when the expected nonce and active player's wallet match.
- Energy, insight, threat and stage changes are numerical, deterministic and bounded.
- The LLM cannot name a winner or debit energy; it only returns a bounded SOLVE label.
- Invalid/unresolved AI classifications do not consume resources or turns.
- No reward, escrow or value transfer is possible.
- Turn timeout lets the non-stalling player claim a win after 48 hours. After 7 days of inactivity anyone may neutrally expire the session, freeing capacity without granting a winner.
- Active-game slots are released only once on terminal state transitions (win, loss, cancel, forfeit, neutral expiry).

## Dependent on honest validator majority

- Stage semantics can be interpreted differently by AI models, particularly free-form phrasing.
- An attacker can inject instructions into PLAYER_MOVE text; prompts define this as untrusted data and validators rerun independently, but model reliability is not guaranteed.
- Semantic label mismatch can produce a transaction that fails consensus. This is preferable to quietly altering a game state.

## Explicit restrictions

- Two players only; three fixed puzzle stages; 12-turn limit; **128 active games** maximum, not 128 historical games.
- Each creator can open up to two active games concurrently. Closed games retain their immutable IDs and readable history.
- Sybil wallets can still temporarily occupy the 128 active slots; eventual permissionless cleanup ensures this is not permanent after 7 days of inactivity.
- A non-stalling player must claim a forfeit between 48 hours and 7 days before an outsider can choose neutral expiry.
- A public contract cannot keep clues secret. `get_stage` intentionally reveals stages.
- Game history stores SHA-256 of player narrative, not text itself; a hash is not strong privacy for low-entropy messages.
- No randomness claim, economic incentive or matchmaking; genesis ownership is not proof of personhood.
- Real GenVM lint/direct and Studionet consensus tests remain necessary.
