# Offline identity replay selector — 2026-09-17

Task: `haunt-goal-20260917-replay-selector/implement-identity-replay-selector`

## Change

`cryptohaunt replay` now accepts mutually exclusive `--family` and `--probe`
selectors. The selector filters graded rows before repetition accounting and
reporting; default replay remains unchanged. The implementation is provider-free
and does not write tapes or alter the live authorization boundary.

Files:

- `cryptohaunt/runner.py`
- `cryptohaunt/cli.py`
- `tests/test_replay_selector.py`

## Delegation record

Delegated `haunt-readonly-audit` to independently inspect `GOAL.md`,
`docs/literature.md`, `docs/critique.md`, and the newest tape. The worker
registered but produced no readable artifact before its relay disappeared; its
report is therefore not used as evidence. I personally inspected the durable
artifact `/tmp/haunt-goal-audit.md` and the existing receipt
`docs/task-receipts/haunt-goal-20260917-identity-canary-coverage-audit.md`,
which identify this replay-selector action and its duplicate exclusions.

## Verification

- `python3 -m unittest discover -s tests`: 62 tests, exit 0.
- `python3 -m unittest tests.test_replay_selector tests.test_establishment tests.test_tape`: 12 tests, exit 0.
- `python3 -m cryptohaunt replay --family identity runs/tiny-fleet-v1_abcase_persistence-20260917.jsonl`: exit 0; output contains only `identity`, with `BLIND` and `0.00 (6/21)` treatment coverage.
- Unfiltered replay of the same tape: exit 0; output contains `neutral`, `assent`, `identity`, and `provenance`.
- `python3 -m cryptohaunt gate`: exit 0; `gate: PASS`, `provider_calls: 0`, `production_study_writes: []`.
- The live tape was inspected before and after replay; no tape write or provider call occurred.

The result is an executable offline artifact, ready for the registered H2
identity-family analysis; it does not turn the current `BLIND` result into a
finding.
