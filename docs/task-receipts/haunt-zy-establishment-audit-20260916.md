# Zy establishment audit — 2026-09-16

## Acceptance evidence

- Tape: `/home/mesh-home/src/hyperhauntology_for_kids/runs/tiny-fleet-v1_zy_h2-9.jsonl`
- SHA-256: `242a82a66935ccef52e08ad7ddf8b7529e3f20d298a6d88f9113264fb2b16e04`
- Replay: `python3 -m cryptohaunt replay runs/tiny-fleet-v1_zy_h2-9.jsonl`
- Header: `tiny-fleet-v1:latest` via Ollama, rule `zy`, seed word `mozerov`, 9 repetitions, 8 derail turns.
- Queue/ledger duplicate check: exact-owner dispatch returned no eligible row; audit shows the prior readiness audit is `DONE`, while the remaining haunt rows are blocked or dependency-gated. This audit is a distinct chain and signal.

## Result

Offline replay reports `NOT-ESTABLISHED` for neutral, assent, identity, and
provenance. Each family has treatment/control/noise coverage `0/0` and no MDE.
The tape has nine `status` rows, each with `obeyed` false for all eight turns
and `first_break_turn` 1. Individual later `graded` rows do not override the
establishment gate: no repetition formed the state required for a persistence
comparison.

## Bounded decision

Do not spend another provider call on this tape, replay it as an H2 result, or
call the zero a null. A future collection action is only eligible after a fresh
sequential run establishes `zy` in at least one repetition; then the three-arm
comparison may proceed under the frozen methodology.

No code, tape, or scientific claim was changed by this audit.
