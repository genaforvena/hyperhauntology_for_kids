# Review-packet preflight — 2026-09-18

Task: `haunt-goal-20260918-review-packet-preflight/review-packet-preflight`

## Scope

Verified the current `kids-v1` lesson-review packet and its offline release
gate. This did not edit `protocol/lesson-review-signoffs.json`, call a model,
or change the release disposition.

## Evidence

- `python3 -c 'from cryptohaunt.release import lesson_materials_sha256; print(lesson_materials_sha256("lessons"))'`
  returned `0e0e1b2a066541176fd2fddfb7a3ae30e1da5473dc24e41fa1f1b9258a09b405`,
  matching `protocol/lesson-review-signoffs.json`.
- `python3 -m unittest -v tests.test_release` — exit 0; 5 tests passed.
- The live evaluator returned `status: PENDING`, `completed_reviews: 0`,
  `required_reviews: 2`, and `issues: two distinct independent adult approvals
  are required; 0 recorded`.

## Disposition

The packet is ready for the already-registered external review gate. No
approval was invented; release remains correctly pending until two distinct
adult independent approvals are recorded.
