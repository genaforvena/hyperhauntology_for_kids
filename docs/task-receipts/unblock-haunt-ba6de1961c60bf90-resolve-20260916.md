# Unblock receipt — alternate establishment provider gate — 2026-09-16

Task: `unblock/haunt/ba6de1961c60bf90/resolve`

## Result

The capability prerequisite is present in the committed implementation (`f05973b`
and its prerequisite history). The live provider gate is still blocked: `ollama ps`
reports unrelated resident model `qwen3-vl:4b-instruct` using `100% GPU`. No model
was stopped, and the frozen establishment command was not run.

## Artifact inspected

- `protocol/alternate-induction-registration-20260916.json` — frozen one-repetition
  `abcase` establishment registration; requires provider exclusivity.
- `docs/task-receipts/unblock-haunt-0cb2bab533cb6f88-resolve-20260916.md` — prior
  capability-clearance receipt and verification record.
- `ollama ps` — live exclusivity check, predicate false.

## Delegation decision

No subagent was launched: the remaining work is a tightly coupled live-provider
gate plus owner-authored execution, and an independent report cannot establish
provider exclusivity or safely alter the resident external process. The decision
and live output were inspected directly in this mind.

## Exact retry edge

When `ollama ps` shows no unrelated resident model, rerun the exclusivity check,
execute the exact frozen command from the registration JSON, replay the resulting
tape offline with exit 0, and stop immediately on `NOT-ESTABLISHED`. Do not spend
treatment, clean-control, or noise-control probes unless the establishment gate is
`ESTABLISHED`.
