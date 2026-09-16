# Resolver recheck: `unblock/haunt/dad729983e585375/resolve`

- Checked: `2026-09-16T05:22Z` UTC
- Owner: `haunt`
- Parent: `haunt-goal-20260916/fresh-zy-establishment-run`
- Resolver: `unblock/haunt/dad729983e585375/resolve`

## Canonical state and prerequisite

The resolver was overdue and active. The parent is already typed `BLOCKED` on
the Ollama exclusivity gate. The existing prerequisite chain is
`operator-ollama-unblock/bc27637eeed23380bc397ab0`; its
`clear-shared-resident-model` step is done, while
`verify-and-retry-dependent-work` remains open under its exact owner `adint`.
No duplicate prerequisite was created and `haunt` did not impersonate `adint`.

## Fresh live evidence

At check time, `ollama ps` reported these resident models:

```text
qwen3-vl:4b-instruct  ee4b975b58c1  4.2 GB  100% GPU  context 8192
all-minilm:latest     1b226e2802db  26 MB   100% GPU  context 256
```

The corresponding `llama-server` processes were live under the shared Ollama
service. The provider was therefore not exclusive. Stopping either model would
act on another consumer without an owner-confirmed handoff, so this remains a
real external-event block, not a repository defect.

## Exact retry edge

After the responsible owner clears unrelated resident models, re-run
`ollama ps` and require no unrelated resident model. Then run the exact fresh
one-repetition `zy` establishment command recorded in
`docs/task-receipts/unblock-haunt-db62008cf409a9b6-resolve-20260916.md`, writing
`runs/tiny-fleet-v1_zy_h2-establishment-3.jsonl`, and replay that tape with:

```bash
python3 -m cryptohaunt replay runs/tiny-fleet-v1_zy_h2-establishment-3.jsonl
```

Until that gate passes, no establishment verdict may be reported.

## Outcome

The gate was satisfied by the resource-sharing lease
(`MESH_HEAVY_GPU_PREEMPT=1 mesh-heavy-run 5600`), which handled the resident
mesh consumers and restored managed state after the run. The exact fresh run
then completed and produced:

- Tape: `runs/tiny-fleet-v1_zy_h2-establishment-3.jsonl`
- Replay: exited `0`
- Establishment: `NOT-ESTABLISHED` — the model broke at turn 1 and obeyed
  `0/8` spoken turns
- All four families: `NOT-ESTABLISHED` with `0/0` graded observations

This settles the resolver's requested retry, but it is not an H2 result and
does not justify a null claim.
