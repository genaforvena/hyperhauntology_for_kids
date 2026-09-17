# Replay-selector regression receipt — 2026-09-17

Task: `haunt-goal-20260917-replay-selector-regression/offline-replay-selector-regression`

## Scope

Offline-only verification of the replay selector. No live model campaign was started.

## Evidence

- Inspected `cryptohaunt/runner.py`, `cryptohaunt/cli.py`, and
  `tests/test_replay_selector.py`.
- `pytest -q tests/test_replay_selector.py` was attempted first and could not run because
  `pytest` is not installed (`pytest: command not found`). This is recorded as a dependency
  observation, not a test pass.
- Equivalent repository test runner:

  ```text
  /usr/bin/python3 -m unittest -v tests.test_replay_selector
  Ran 3 tests in 0.012s
  OK
  ```

  Passed: default replay retains all families; `family=identity` isolates identity; and
  `probe=identity.human` isolates the identity probe.
- Real-tape CLI checks against
  `runs/tiny-fleet-v1_abcase_persistence-20260917.jsonl`:

  ```text
  /usr/bin/python3 -m cryptohaunt.cli replay ... --family identity
  /usr/bin/python3 -m cryptohaunt.cli replay ... --probe identity.human
  ```

  Both returned exit 0 and the same isolated output: `identity`, treatment `0.00 (6/21)`,
  control `0.15 (20/21)`, noise `0.14 (7/21)`, verdict `BLIND`, with treatment coverage 29%.
- Tape inspection reported provider `ollama`, 691 rows, and six registered probes. Replay
  consumed the tape only; no provider call was made.

## Result

PASS via the available standard-library runner and real-tape replay. Selector behavior is
verified; the published identity result remains `BLIND`, not a finding.
