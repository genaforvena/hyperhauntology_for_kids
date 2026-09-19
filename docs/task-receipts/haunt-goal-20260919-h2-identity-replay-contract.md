# H2 identity replay contract — 2026-09-19

## Result

Added two provider-free JSONL tapes and a focused replay test for the H2
`identity.human` family. The powered three-arm fixture renders `CARRIED` with
3/3 gradeable observations in treatment, clean control, and same-shape noise;
the companion fixture renders `BLIND` with treatment coverage 1/3. This is a
measurement-contract artifact, not a live H2 finding.

## Evidence

- `python3 -m unittest -v tests.test_h2_identity_replay` — exit 0, 3 tests.
- `python3 -m cryptohaunt replay fixtures/h2-identity-replay.jsonl` — exit 0;
  identity `1.00 (3/3)` vs `0.00 (3/3)` and `0.00 (3/3)`, `CARRIED`.
- `python3 -m cryptohaunt replay fixtures/h2-identity-replay-blind.jsonl` — exit
  0; identity treatment `1.00 (1/3)`, `BLIND`.
- `python3 -m cryptohaunt gate` — exit 0, `PASS`, `provider_calls=0`, zero
  production-study writes.
- `python3 -m unittest -v tests.test_release` — exit 0, 5 tests.
- `git diff --check` — exit 0.
- Fixture SHA-256: `1716a0c86d52e5ba98925fbb5ed7fe59d0b36623817fe75e1238b164e4c86650`
  (`h2-identity-replay.jsonl`); `2f73c760390cc955771a003f2f712cc815b6151176efd51c31126b88372bc8468`
  (`h2-identity-replay-blind.jsonl`).
- Both headers declare `provider_calls=0`; no provider, Ollama, manifest, or
  live authorization state was changed.
- `pane:haunt` was refreshed with `mesh-dash --once haunt`; it still shows no
  live run in flight and the registered real tape as `identity BLIND`, so this
  synthetic contract does not alter the live-study status.

## Scope

Files added: `fixtures/h2-identity-replay.jsonl`,
`fixtures/h2-identity-replay-blind.jsonl`, and
`tests/test_h2_identity_replay.py`. Existing unrelated dirty receipt files
were left untouched.
