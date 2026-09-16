# Haunt status audit — 2026-09-16

Task: `haunt-goal-20260916-status-audit/reconcile-newest-establishment-status`

## Evidence inspected

- Source task record: `~/.mesh/chat.log:75968-75977`; it was taken by `haunt`
  at `2026-09-16T12:12:45Z` and had no progress after that claim.
- Required research context: `GOAL.md`, `docs/literature.md`, and
  `docs/critique.md`, read in charter order.
- Frozen registration: `protocol/alternate-induction-registration-20260916.json`.
  It remains unchanged; its `establishment-only-pending-provider` status is the
  pre-run registration state, not the run result.
- Live tape: `runs/tiny-fleet-v1_o2cyrillic_alternate-establishment-20260916.jsonl`.
  It contains six rows (header, status, four calls), uses model
  `tiny-fleet-v1:latest` through provider `ollama`, and records `obeyed` as
  `[false, true, false, true]` with status `established`.
- Tape SHA-256: `4767766e82b54482ad5dc0e9e8e2c298f6759e4c4fe95cdc57d1c63a5446a2cc`.
- Offline verification: `python3 -m cryptohaunt replay runs/tiny-fleet-v1_o2cyrillic_alternate-establishment-20260916.jsonl`
  returned `ESTABLISHED`, exit 0.
- Resource check at reconciliation: `ollama ps` showed no resident model;
  `nvidia-smi` showed 1 MiB used and 11911 MiB free. No experiment was run by
  this audit.

## Reconciliation

The previous reader-facing status was incomplete: it described the failed `zy`
diagnostics and said the alternate design was still next, omitting the newer
successful establishment-only tape. `GOAL.md` now records both facts and points
to the actual next step. The alternate result clears only the establishment gate;
it does not establish H2 and does not authorize changing the predeclared
three-arm design.

The stale-status discrepancy is corrected in this audit, so it has no remaining
actionable follow-up task. No persistence probes were spent.
