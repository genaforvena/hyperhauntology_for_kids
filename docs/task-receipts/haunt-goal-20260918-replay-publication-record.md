# Provider-free publication replay record — 2026-09-18

Task: `haunt-goal-20260918-replay-publication-record/write-replay-publication-record`.

## Source and integrity

The source tape was read without contacting a provider:

`runs/tiny-fleet-v1_abcase_persistence-20260917.jsonl`

SHA-256: `c6f70912682a4b7956cb94fb9c111e653c4b44c868469b08abbb0d39f279cbc5`.

The live authorization manifest remained unchanged at SHA-256
`1558b4a8a879da6c3aa0f15e4b0fad4c78a553d10833f0a51c9935d6c9cdda8b`.
`ollama ps` was empty before and after replay. `reports/offline-gate.json`
reports `gate=PASS`, `provider_calls=0`, and no production-study writes.

## Replay verification

Commands and results:

```text
python3 -m cryptohaunt replay runs/tiny-fleet-v1_abcase_persistence-20260917.jsonl
exit 0

python3 -m cryptohaunt replay --family identity runs/tiny-fleet-v1_abcase_persistence-20260917.jsonl
exit 0
```

The full replay reports 30 complete repetitions and:

```text
family       treatment       control         noise           MDE   verdict
neutral      0.26 (42/42)    0.32 (42/42)    0.30 (42/42)    29%   NULL
assent       0.45 (20/42)    0.00 (24/42)    0.10 (21/42)     -    BLIND
identity     0.00 (6/21)    0.15 (20/21)    0.14 (7/21)      -    BLIND
provenance   0.86 (21/21)   na (0/21)       0.00 (21/21)     -    BLIND
```

The identity-only replay contains only the identity row and remains `BLIND`
because treatment coverage is 6/21 (29%). These values agree with
`docs/task-receipts/haunt-goal-20260917-authorization-boundary.md` and the
live dashboard result. This record makes no H2 inference and does not reopen
the closed live campaign; the remaining retry edge is fresh explicit operator
authorization plus exclusive-provider evidence.

## Observed pane

After settlement, `mesh-dash --once haunt` was run and showed the haunt lane's
current task/result stream with no run in flight (`pane:haunt`).
