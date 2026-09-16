# Unblock receipt — alternate establishment path — 2026-09-16

Task: `unblock/haunt/b267f1773ecb7139/resolve`

## Result

`unblock=cleared` for the missing implementation prerequisite. The registered
`abcase` rule and establishment-only runner path now exist and are covered by a
provider-free regression. The provider boundary remains pending: this receipt
does not claim an Ollama run, establishment, or any persistence result.

## Changes inspected

- `cryptohaunt/rules.py`: registered the harmless alternating-case `abcase`
  canary and its total transformation.
- `cryptohaunt/runner.py`: added `establishment(args)`, which writes only a
  header, one gate status, and induction calls; it never invokes switch,
  clean-control, or noise probes. `replay()` recognizes its
  `establishment_only` tape and returns the recorded gate offline.
- `cryptohaunt/cli.py`: added the `cryptohaunt establishment` command with the
  frozen registration defaults.
- `tests/test_establishment.py`: regression proves induction-only tape shape,
  `ESTABLISHED` result, and offline replay.

## Verification

- `python3 -m unittest tests.test_establishment -v` — exit 0.
- `timeout 120s python3 -m unittest discover -s tests -q` — 58 tests, exit 0.
- `python3 -m cryptohaunt --help` — exit 0; lists `establishment`.
- `git diff --check` — exit 0.

Delegation decision: no subagent was launched because this was one tightly
coupled local implementation and test edge; splitting it would duplicate the
same task/runner contract. The registration personally inspected was
`protocol/alternate-induction-registration-20260916.json`.

## Exact next event

Verify live Ollama exclusivity and run the frozen one-repetition command from
that registration only when no unrelated resident model is present. If the
gate is `NOT-ESTABLISHED`, replay offline and stop; do not spend three-arm
persistence probes.
