# QuestForge — threat model and explicit limitations

## Protected by deterministic contract code

- Only the designated creator and accepted invited player can participate.
- A turn changes state only when the expected nonce and active player's wallet match.
- Energy, insight, threat and stage changes are numerical, deterministic and bounded.
- The LLM cannot name a winner or debit energy; it only returns a bounded SOLVE label.
- Invalid/unresolved AI classifications do not consume resources or turns.
- No reward, escrow or value transfer is possible.
- Turn timeouts prevent a non-responsive player from leaving a game forever active.

## Dependent on honest validator majority

- Stage semantics can be interpreted differently by AI models, particularly free-form phrasing.
- An attacker can inject instructions into PLAYER_MOVE text; prompts define this as untrusted data and validators rerun independently, but model reliability is not guaranteed.
- Semantic label mismatch can produce a transaction that fails consensus. This is preferable to quietly altering a game state.

## Explicit restrictions

- Two players only; three fixed puzzle stages; 12-turn limit; 128-game total cap.
- A public contract cannot keep clues secret. `get_stage` intentionally reveals stages.
- Game history stores SHA-256 of player narrative, not text itself; a hash is not strong privacy for low-entropy messages.
- No randomness claim, economic incentive or matchmaking; genesis ownership is not proof of personhood.
- Real GenVM lint/direct and Studionet consensus tests remain necessary.
