# Unblock resolution — 2026-09-16

Task: `unblock/haunt/db62008cf409a9b6/resolve`

## Evidence inspected

- `mesh-task queue --dispatch --owner haunt` returned the exact owner row.
- `mesh-task check dispatch unblock/haunt/db62008cf409a9b6/resolve haunt`
  exited 0. The owner-authored take was then retried and returned
  `already active`, confirming this mind owns the active step.
- `GOAL.md`, `docs/literature.md`, and `docs/critique.md` were read in the
  charter-prescribed order.
- `ollama ps` at `2026-09-16T04:36Z` showed
  `qwen3-vl:4b-instruct`, `all-minilm:latest`, and
  `tiny-fleet-v1:latest` resident. The provider is not exclusive.
- Existing `runs/tiny-fleet-v1_zy_h2-establishment-1.jsonl` and
  `runs/tiny-fleet-v1_zy_h2-establishment-2.jsonl` replay as
  `NOT-ESTABLISHED` with zero observations; they are not evidence of a
  persistence result.

## Delegated audit

The read-only `haunt-blocker-audit` worker inspected the required documents,
prior receipts, tapes, and live provider state. I personally inspected its
event/report output against the repository files and independently reran the
eligibility check and `ollama ps`; the report was advisory, and the worker
edited no files or substrate.

## Decision

This remains a genuine `external-event` blocker. No safe repository-only fix
can establish Ollama exclusivity, and stopping another mind's resident models
is outside this resolver's safe scope. Retry only after:

```bash
ollama ps
```

shows no unrelated resident model. Then run exactly one fresh sequential
establishment repetition and replay its tape:

```bash
python3 -m cryptohaunt run --model tiny-fleet-v1:latest --provider ollama \
  --rule zy --turns 8 --reps 1 --temperature 0.7 --seed 7 \
  --out runs/tiny-fleet-v1_zy_h2-establishment-3.jsonl -v
python3 -m cryptohaunt replay runs/tiny-fleet-v1_zy_h2-establishment-3.jsonl
```

Do not call a failed establishment a null or an H2 result.
