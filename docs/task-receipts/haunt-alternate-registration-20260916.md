# Alternate induction registration — 2026-09-16

This registration freezes one bounded, harmless establishment-only attempt after
four `zy` diagnostics reached `NOT-ESTABLISHED` with `0/0` gradeable answers.
It uses a newly scoped reversible `abcase` canary, the seed word `Abacus`, and
one repetition. The registration does not alter the failed tapes and does not
authorize persistence probes before establishment.

Registration: `protocol/alternate-induction-registration-20260916.json`

Planned tape: `runs/tiny-fleet-v1_o2cyrillic_alternate-establishment-20260916.jsonl`

Implementation gate: `abcase` and the establishment-only command path were
already present in committed `00bfc7a` (`feat: add bounded establishment-only
runner`); this was verified with `python3 -m unittest tests.test_establishment
-v` (exit 0). `ollama ps` showed no resident model before the provider call, so
the frozen command was run exactly once:

```text
python3 -m cryptohaunt establishment --model tiny-fleet-v1:latest --provider ollama --rule abcase --seed-word Abacus --turns 4 --reps 1 --temperature 0.7 --seed 19 --out runs/tiny-fleet-v1_o2cyrillic_alternate-establishment-20260916.jsonl
```

Result: `ESTABLISHED`. Tape:
`runs/tiny-fleet-v1_o2cyrillic_alternate-establishment-20260916.jsonl`,
SHA-256
`4767766e82b54482ad5dc0e9e8e2c298f6759e4c4fe95cdc57d1c63a5446a2cc`.
Offline replay with `python3 -m cryptohaunt replay
runs/tiny-fleet-v1_o2cyrillic_alternate-establishment-20260916.jsonl` exited
0 and returned `ESTABLISHED`. This clears the establishment gate only; no
three-arm persistence collection or H2 inference is claimed here.
