# Haunt readiness audit — 2026-09-15

## Acceptance evidence

- Tape: `/home/mesh-home/src/hyperhauntology_for_kids/runs/tiny-fleet-v1_zy_h2-9.jsonl`
- Replay command: `python3 -m cryptohaunt replay runs/tiny-fleet-v1_zy_h2-9.jsonl`
- Tape SHA-256: `242a82a66935ccef52e08ad7ddf8b7529e3f20d298a6d88f9113264fb2b16e04`
- Tape size: 244 JSONL lines; header declares 9 repetitions, 8 derail turns, and three arms.

## Observed result

Offline replay reports `derail: replayed from tape (9 complete rep(s)): not-established`.
All four families (`neutral`, `assent`, `identity`, `provenance`) are
`NOT-ESTABLISHED`, with treatment/control/noise coverage `0/0` and no MDE.
The source tape's first repetition confirms `obeyed` is false for all eight
derail turns and `first_break_turn` is 1.

This is not an H2 result: the induction state never formed, so there is no
absorbing state to test. The evidence is consistent with the project's
establishment gate and does not justify spending tokens on a replay or calling
the result a null.

## Next bounded action

Before another controlled H2 run, obtain a fresh, sequential provider run whose
induction establishes the `zy` rule in at least one repetition; only then use
the three-arm persistence comparison. This receipt is the artifact for the
readiness decision; no provider call was made by this audit.
