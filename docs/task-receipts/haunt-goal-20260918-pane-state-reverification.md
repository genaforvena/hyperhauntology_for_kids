# Pane state reverification — 2026-09-18

Task: `haunt-goal-20260918-pane-state-reverification/pane-state-reverification`.

## Fresh evidence

- Tape: `runs/tiny-fleet-v1_abcase_persistence-20260917.jsonl`.
- SHA-256: `c6f70912682a4b7956cb94fb9c111e653c4b44c868469b08abbb0d39f279cbc5`.
- Command: `python3 -m cryptohaunt replay runs/tiny-fleet-v1_abcase_persistence-20260917.jsonl`.
- Replay: exit `0`; 30 complete repetitions; neutral `NULL` at 29% MDE;
  assent, identity, and provenance `BLIND`.
- Authorization boundary: `protocol/design-manifest.json` still records
  `live_model_campaign_authorized: false`; `ollama ps` returned an empty model table.
- Observed pane: `mesh-dash --once haunt` at `2026-09-18T21:50:28Z` showed no run
  in flight and the same four-family verdicts (`pane:haunt`).

This is provider-free verification only. No model call, authorization mutation,
or production-study write was made. The result remains bounded: it does not answer
H2 refusal persistence.
