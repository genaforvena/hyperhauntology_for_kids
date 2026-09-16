# Alternate induction registration — 2026-09-16

This registration freezes one bounded, harmless establishment-only attempt after
four `zy` diagnostics reached `NOT-ESTABLISHED` with `0/0` gradeable answers.
It uses a newly scoped reversible `abcase` canary, the seed word `Abacus`, and
one repetition. The registration does not alter the failed tapes and does not
authorize persistence probes before establishment.

Registration: `protocol/alternate-induction-registration-20260916.json`

Planned tape: `runs/tiny-fleet-v1_o2cyrillic_alternate-establishment-20260916.jsonl`

Implementation gate: `abcase` is not yet present in `cryptohaunt.rules.RULES`,
and the runner currently has no establishment-only command path. Implement and
test that bounded path before any provider call. Then verify Ollama provider
exclusivity; if it is not true, leave this task pending and retry only on that
event. If run, the tape must replay offline with exit 0 and its status must be
reported as `ESTABLISHED` or `NOT-ESTABLISHED`; the latter is not H2 evidence
and triggers no three-arm persistence collection.
