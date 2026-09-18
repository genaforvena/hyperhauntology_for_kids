# H2 protocol readiness audit — 2026-09-18

Task: `haunt-goal-20260918-h2-readiness-audit/audit-h2-protocol-readiness`.

## Result

The registered H2 refusal-persistence path is locally executable and provider-free
up to its live safety boundary. The next authorized run remains the exact command
recorded in `docs/task-receipts/haunt-goal-20260917-h2-refusal-canary-registration.md`.
No live run was started because the manifest still has
`live_model_campaign_authorized=false`; the current `ollama ps` read returned only
the header, so there is no exclusive registered provider to authorize implicitly.

## Checks

All commands ran from the repository root:

```text
python3 -m cryptohaunt --help                         exit 0
python3 -m cryptohaunt selftest                      exit 0 (62 tests, OK)
python3 -m cryptohaunt gate                           exit 0
python3 -m cryptohaunt establishment --help           exit 0
ollama ps                                              exit 0 (no resident models)
```

The gate output reports `gate=PASS`, `provider_calls=0`, and
`production_study_writes=[]`. The frozen registration
`protocol/alternate-induction-registration-20260916.json` has SHA-256
`6718f04bafefaacaf93ac2e9a8f8c685b0a90c78bf9e44867bb9808e710982f5`.

The attempted historical path `python3 scripts/run_study_matrix.py --help`
returned exit 2 because that file is absent; it is not the registered runner and
was not substituted for `python3 -m cryptohaunt run`.

## Safety integrity

`protocol/design-manifest.json` SHA-256 was
`1558b4a8a879da6c3aa0f15e4b0fad4c78a553d10833f0a51c9935d6c9cdda8b` both before
and after the checks. No provider call, tape write, authorization mutation, or
model eviction occurred. The remaining retry edge is external authorization of
the live campaign followed by a fresh manifest hash and fresh `ollama ps` read;
only then may the registered three-arm run begin.
