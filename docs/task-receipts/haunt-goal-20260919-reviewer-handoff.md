# Adult reviewer handoff — kids-v1

Task: `haunt-goal-20260919-reviewer-handoff/reviewer-handoff`

## Packet identity

- Materials version: `kids-v1`
- Materials SHA-256: `0e0e1b2a066541176fd2fddfb7a3ae30e1da5473dc24e41fa1f1b9258a09b405`
- Signoff record: `protocol/lesson-review-signoffs.json`
- Offline validator: `python3 -m unittest -v tests.test_release`

## Reviewer action

Two distinct independent adult reviewers must inspect the current `lessons/`
packet and record an independent `APPROVE` or `REJECT` against the hash above.
An approval is valid only for this exact hash; a later lesson change requires
fresh review. Disagreements remain recorded rather than silently resolved.

## Current gate state

The signoff record contains zero reviewers and zero approvals. The release is
therefore `PENDING`, not approved. This handoff does not edit signoffs, change
the release disposition, or call a model.

## Verification

The packet hash matched the signoff record, and the existing release test
passed with 5 tests. The next state transition is external: two independent
adult signoffs, followed by rerunning the offline release gate.
