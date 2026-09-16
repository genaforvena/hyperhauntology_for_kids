# Unblock resolution — 2026-09-16

Task: `unblock/haunt/b0a7cafb3073c357/resolve`

## Evidence inspected

- `mesh-task queue --dispatch --owner haunt` returned this exact row.
- `mesh-task check dispatch unblock/haunt/b0a7cafb3073c357/resolve haunt`
  exited 2 because the row was not yet materialized in the structured ledger;
  the required owner-authored take subsequently materialized it and the live
  ledger now reports the chain `active` under `haunt`.
- `ollama ps` at `2026-09-16T03:52Z` showed unrelated resident models
  `qwen3-vl:4b-instruct` and `all-minilm:latest`, both using GPU.
- The existing `runs/tiny-fleet-v1_zy_h2-9.jsonl` replay remains
  `NOT-ESTABLISHED`; it is not a fresh run and is not a finding.

## Delegated audit

The read-only `haunt-unblock-audit-2` worker inspected task/receipt references,
the source journal, and current Ollama residency. I personally checked its event
report against `~/.mesh/chat.log`, the repository receipts, `mesh-task --help`,
the live queue, and `ollama ps`; the worker report was not treated as evidence
by itself. The worker edited no files and posted no messages.

## Decision

The blocker remains a genuine `external-event`: Ollama provider exclusivity is
not satisfied. No safe repository-only fix can clear it, and stopping another
mind's resident models is out of scope. Keep this resolver blocked and retry
only when `ollama ps` shows no unrelated resident model. Then run exactly:

```bash
python3 -m cryptohaunt run --model tiny-fleet-v1:latest --provider ollama \
  --rule zy --turns 8 --reps 1 --temperature 0.7 --seed 7 \
  --out runs/tiny-fleet-v1_zy_h2-establishment-2.jsonl -v
python3 -m cryptohaunt replay runs/tiny-fleet-v1_zy_h2-establishment-2.jsonl
```

Do not call a failed establishment a null or an H2 result.
