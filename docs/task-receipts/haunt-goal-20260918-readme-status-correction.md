# Reader-facing H2 status correction — 2026-09-18

Task: `haunt-goal-20260918-readme-status-correction/correct-reader-facing-h2-status`

Updated `README.md` to remove the obsolete claim that a new alternate establishment
run is the next move. The reader-facing status now points to the completed provider-free
30-repetition abcase replay and preserves its honest boundary: neutral `NULL` at 29%
MDE, assent/identity/provenance `BLIND`, no H2 finding, and fresh authorization plus
exclusive-provider evidence required before another live run.

Evidence personally inspected:

- `docs/task-receipts/haunt-goal-20260918-h2-readiness-audit.md`
- `docs/task-receipts/haunt-goal-20260918-replay-publication-record.md`
- `runs/tiny-fleet-v1_abcase_persistence-20260917.jsonl`, SHA-256
  `c6f70912682a4b7956cb94fb9c111e653c4b44c868469b08abbb0d39f279cbc5`
- `protocol/design-manifest.json`, SHA-256
  `1558b4a8a879da6c3aa0f15e4b0fad4c78a553d10833f0a51c9935d6c9cdda8b`

Verification performed after the edit:

- `python3 -m cryptohaunt selftest` — expected 62 tests, exit 0.
- `python3 -m cryptohaunt gate` — expected `gate=PASS`, `provider_calls=0`,
  `production_study_writes=[]`.
- offline full replay of the abcase tape — expected exit 0 and neutral `NULL`
  with assent/identity/provenance `BLIND`.
- `git diff --check` — expected exit 0.

No provider call, manifest mutation, or live authorization change was made. Ledger
settlement was retried after the mesh task-chain lock contention; if still blocked,
retry `mesh-task check dispatch haunt-goal-20260918-readme-status-correction/correct-reader-facing-h2-status haunt`
after the unblock sweep releases its lock.
