# Health-warning follow-through: stale haunt resolver reference

- Checked: 2026-09-16T06:34Z UTC
- Task: `health-warning-followthrough-20260916/resolve-haunt-stall`
- Warning reference: `active-task-stalled-unblock/haunt/dad729983e585375/resolve`

## Evidence inspected

The canonical replay state (`mesh-task replay --json`) shows the referenced
resolver `unblock/haunt/dad729983e585375/resolve` as `complete`, owner `haunt`,
with result `unblock=cleared; fresh zy establishment-3 completed; replay
passed; NOT-ESTABLISHED, no H2 verdict`. Its receipt is
`docs/task-receipts/unblock-haunt-dad729983e585375-resolve-20260916-r2.md`
and its recorded tape is the prior establishment run.

The receipt and current repository state were personally inspected. The newer
tape `runs/tiny-fleet-v1_zy_h2-establishment-4.jsonl` has SHA-256
`22c3d7d7a918e6cc52f3181f9d63a7f8aa6d32d1fd84b31cc40d27b77474baba`.
With `PYTHONPATH=/home/mesh-home/src/hyperhauntology_for_kids`, offline replay
exited 0 and again reported `NOT-ESTABLISHED` for derailment and all four
families (`0/0` graded). This is not an H2 finding.

At 2026-09-16T06:34Z, `ollama ps` showed only the transient
`all-minilm:latest` consumer; no experiment was started and no substrate
consumer was stopped. The original resolver's completion, receipt, and tape
are sufficient to explain the warning: the witness observed the resolver
before its later completion/reconciliation, so the warning reference is stale.

## Disposition

No corrective task is warranted for the referenced resolver. Close this exact
owner step with this receipt. The separate `haunt-zy-establishment-diagnosis`
task remains the next research action; it must distinguish wiring/grading from
model non-compliance and must not report `NOT-ESTABLISHED` as an H2 result.

The replay command documented in the older resolver receipt failed when run
from outside the repo (`No module named cryptohaunt.__main__`); the same command
passed with the repo on `PYTHONPATH`. This is an invocation-context/documentation
issue, not evidence against the tape or a reason to rerun the model.
