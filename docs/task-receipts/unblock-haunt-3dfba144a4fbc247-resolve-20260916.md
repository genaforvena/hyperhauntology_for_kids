# Unblock receipt — alternate establishment provider gate — 2026-09-16

Task: `unblock/haunt/3dfba144a4fbc247/resolve`

## Result

At `2026-09-16T11:34:39Z`, the exact-owner resolver was checked and recorded as
`blocked` with typed blocker `capability`. The live Ollama exclusivity predicate
is false: `qwen3-vl:4b-instruct` (`100% GPU`) and `qwen2.5:3b` (`17%/83% CPU/GPU`)
were both resident. The frozen registration forbids evicting unrelated resident
models, so no model was stopped and no establishment run was started.

## Evidence personally inspected

- `protocol/alternate-induction-registration-20260916.json`: one-repetition,
  `abcase`, establishment-only registration with the no-unrelated-resident
  provider constraint.
- `ollama ps`: the exclusivity predicate was false at the timestamp above.
- `mesh-task status unblock/haunt/3dfba144a4fbc247`: resolver is `[blocked]`,
  owner `haunt`, blocker `capability`.

## Delegation decision

No subagent was launched. Provider exclusivity, exact-owner task settlement, and
the safety decision about resident processes are tightly coupled live operations;
an independent report could not establish the required predicate. The live output,
task status, and registration were inspected directly in this mind.

## Exact retry edge

When `ollama ps` shows no unrelated resident model, rerun the exclusivity check,
then execute exactly:

```bash
python3 -m cryptohaunt establishment --model tiny-fleet-v1:latest --provider ollama \
  --rule abcase --seed-word Abacus --turns 4 --reps 1 --temperature 0.7 --seed 19 \
  --out runs/tiny-fleet-v1_o2cyrillic_alternate-establishment-20260916.jsonl
python3 -m cryptohaunt replay runs/tiny-fleet-v1_o2cyrillic_alternate-establishment-20260916.jsonl
```

Stop immediately on `NOT-ESTABLISHED`; do not spend treatment, clean-control,
or noise-control probes unless the establishment gate is `ESTABLISHED`.
