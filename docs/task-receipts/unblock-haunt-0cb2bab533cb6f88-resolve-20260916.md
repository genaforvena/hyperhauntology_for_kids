# Unblock receipt — alternate establishment prerequisite — 2026-09-16

Task: `unblock/haunt/0cb2bab533cb6f88/resolve`

## Result

The reported capability blocker is already cleared in committed `00bfc7a`
(`feat: add bounded establishment-only runner`). The live provider blocker is
not cleared: `ollama ps` reports unrelated resident model
`qwen3-vl:4b-instruct` at `100% GPU`. The frozen establishment command was not
run, and no establishment or persistence result is claimed.

## Artifact inspected

- `cryptohaunt/rules.py`: registered harmless `abcase` canary.
- `cryptohaunt/runner.py`: induction-only `establishment()` and offline replay.
- `cryptohaunt/cli.py`: `cryptohaunt establishment` command.
- `tests/test_establishment.py`: provider-free tape/replay regression.
- `protocol/alternate-induction-registration-20260916.json`: frozen registration,
  SHA-256 `6718f04bafefaacaf93ac2e9a8f8c685b0a90c78bf9e44867bb9808e710982f5`.

## Verification

- `python3 -m unittest tests.test_establishment -v` — exit 0.
- `python3 -m unittest discover -s tests -q` — 58 tests, exit 0.
- `python3 -m cryptohaunt --help` — exit 0; lists `establishment`.
- `git diff --check` — exit 0.
- `ollama ps` — unrelated resident remains; exclusivity predicate false.

Delegation decision: one read-only capability-audit subagent was attempted,
but the relay returned no worker shim or artifact; no report was used as
evidence. The files and test results above were inspected directly in this
mind.

## Exact retry edge

After `ollama ps` shows no unrelated resident model, run the exact frozen
one-repetition command in `protocol/alternate-induction-registration-20260916.json`.
Write the planned tape, replay it offline with exit 0, and stop on
`NOT-ESTABLISHED`; do not spend three-arm persistence probes unless the gate is
`ESTABLISHED`.
