# Unblock resolution — 2026-09-16

Task: `unblock/haunt/9c0c70fc948b5120/resolve`

## Evidence inspected

- Owner queue returned this exact row; dispatch validation exited 0.
- Owner-authored take succeeded; chain status reports `active`, lease until
  `2026-09-16T04:12:41Z`.
- `ollama ps` at `2026-09-16T03:41Z` showed unrelated resident models
  `qwen3-vl:4b-instruct`, `gemma4:e2b-it-qat`, and `all-minilm:latest`.
- Prior receipt: `docs/task-receipts/haunt-zy-establishment-run-20260916.md`.
  It records that a fresh run must wait for an exclusive provider and gives the
  exact retry edge.
- Existing tape replay remains `NOT-ESTABLISHED`, not a finding:
  `python3 -m cryptohaunt replay runs/tiny-fleet-v1_zy_h2-9.jsonl`.

## Delegated audit

The read-only `haunt-unblock-audit` worker inspected the repository task/receipt
references and relevant command semantics. Its report was checked against the
receipt, tape, live queue, and `mesh-task --help` locally; no worker artifact was
treated as evidence by itself. No files were edited by the worker.

## Decision

The blocker is a genuine `external-event`: provider exclusivity is not yet
satisfied. No safe repository-only prerequisite or scientific interpretation can
clear it. Keep the resolver blocked and retry only when `ollama ps` shows no
unrelated resident model. Then run exactly one fresh sequential repetition:

```bash
python3 -m cryptohaunt run --model tiny-fleet-v1:latest --provider ollama \
  --rule zy --turns 8 --reps 1 --temperature 0.7 --seed 7 \
  --out runs/tiny-fleet-v1_zy_h2-establishment-2.jsonl -v
python3 -m cryptohaunt replay runs/tiny-fleet-v1_zy_h2-establishment-2.jsonl
```

Do not call a failed establishment a null or an H2 result.
