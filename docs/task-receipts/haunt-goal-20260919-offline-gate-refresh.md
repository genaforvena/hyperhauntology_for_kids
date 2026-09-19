# Offline gate refresh — 2026-09-19

Task: `haunt-goal-20260919-offline-gate-refresh/offline-gate-refresh`

This was a provider-free refresh of the registered offline path. It is not a
new experiment and makes no H2 claim.

## Fresh artifact identity

- `protocol/design-manifest.json` — SHA-256 `1558b4a8a879da6c3aa0f15e4b0fad4c78a553d10833f0a51c9935d6c9cdda8b`
- `protocol/canary-registry.json` — SHA-256 `1e57521b8d3b01e83f42311b231556cff8286d58a71612cad56bf0de9fc62d5f`
- `protocol/preflight-integrity.json` — SHA-256 `dbf5ee35a4e6819497111e176ca0e72007b5d868ca49901369c2fa3283784a4f`
- `runs/tiny-fleet-v1_abcase_persistence-20260917.jsonl` — SHA-256 `c6f70912682a4b7956cb94fb9c111e653c4b44c868469b08abbb0d39f279cbc5`

## Verified commands

- `python3 -m cryptohaunt gate` — exit `0`, `gate: PASS`, both mutation fixtures failed as expected, `provider_calls: 0`, and `production_study_writes: []`.
- `python3 -m unittest -v tests.test_release` — 5 tests passed.
- `python3 -m unittest -v tests.test_preflight` — 3 tests passed.
- `python3 -m cryptohaunt replay runs/tiny-fleet-v1_abcase_persistence-20260917.jsonl` — exit `0`; neutral is powered `NULL` at 29% MDE, while assent, identity, and provenance remain `BLIND` for insufficient coverage.
- `ollama ps` — no resident provider model.

The manifest still has `status: offline-gate-only` and
`safety_boundary.live_model_campaign_authorized: false`. No provider call,
authorization mutation, or production-study write occurred. The exact retry
edge remains fresh external authorization plus exclusive-provider evidence
before any live H2 campaign.

Observed after refresh by `pane:haunt` through `mesh-dash --once haunt`.
