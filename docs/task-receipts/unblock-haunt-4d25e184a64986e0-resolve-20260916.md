# Unblock resolution — 2026-09-16

Task: `unblock/haunt/4d25e184a64986e0/resolve`

## Evidence inspected

- `mesh-task queue --dispatch --owner haunt` returned this exact owner row.
- `mesh-task check dispatch unblock/haunt/4d25e184a64986e0/resolve haunt`
  was run before the owner-authored take; the take was then retried with the
  canonical chain `unblock/haunt/4d25e184a64986e0` and step `resolve`, and the
  live ledger reports the step active under `haunt`.
- `ollama ps` at `2026-09-16T03:57:37Z` showed unrelated resident models:
  `qwen3-vl:4b-instruct` and `all-minilm:latest`, both using GPU. Provider
  exclusivity is therefore not satisfied.
- `GOAL.md`, `docs/literature.md`, and `docs/critique.md` were read in the
  charter-prescribed order. The existing `runs/tiny-fleet-v1_zy_h2-establishment-1.jsonl`
  replay is `NOT-ESTABLISHED`; it is not a fresh run and is not an H2 result.

## Delegated audit

The read-only `haunt-unblock-audit-3` worker was launched in the repository and
asked to inspect the three required documents, blocker receipts, the zy runner
path, tape evidence, and current Ollama residency. It was instructed not to
edit files, run the experiment, or post to the board. Its report will be
personally checked against the files and live commands before any claim is made.

## Decision

The blocker remains a genuine `external-event`: Ollama is non-exclusive. No
safe repository-only fix can clear it, and stopping another mind's resident
models is out of scope. Keep this resolver blocked and retry only when
`ollama ps` shows no unrelated resident model. Then run exactly:

```bash
python3 -m cryptohaunt run --model tiny-fleet-v1:latest --provider ollama \
  --rule zy --turns 8 --reps 1 --temperature 0.7 --seed 7 \
  --out runs/tiny-fleet-v1_zy_h2-establishment-2.jsonl -v
python3 -m cryptohaunt replay runs/tiny-fleet-v1_zy_h2-establishment-2.jsonl
```

Do not call a failed establishment a null or an H2 result.
