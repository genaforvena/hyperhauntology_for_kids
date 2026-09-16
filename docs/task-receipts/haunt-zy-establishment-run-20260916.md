# Zy establishment run — 2026-09-16

Task: `haunt-goal-20260916/fresh-zy-establishment-run`.

## State check

The required fresh sequential provider run was not started. At
`2026-09-16T03:34Z`, `ollama ps` showed both `gemma4:e2b-it-qat` and
`qwen3-vl:4b-instruct` resident, each with about four minutes remaining. The
methodology requires one model/provider pair at a time because concurrent local
model loading can starve the Ollama queue. Starting `tiny-fleet-v1:latest` in
that state would not be interpretable evidence.

## Adjacent offline evidence

As a provider-free check, replay of `runs/tiny-fleet-v2-zy-30.jsonl` exited 0:

```text
neutral: INCONCLUSIVE (8/8 per arm; MDE 57%)
assent: INCONCLUSIVE (4/8, 6/8, 4/8; MDE 77%)
identity: INCONCLUSIVE (3/4, 4/4, 4/4; no power)
provenance: BLIND (control 0/4)
```

This existing v2 tape is not a substitute for the claimed fresh v1
establishment run and does not establish H2.

## Retry edge

Retry the exact one-repetition command after `ollama ps` shows no unrelated
resident model, then replay the resulting append-only tape and record whether
at least one repetition established `zy`. Do not call a failed establishment a
null or an H2 result.

No provider call or scientific claim was made in this turn.
