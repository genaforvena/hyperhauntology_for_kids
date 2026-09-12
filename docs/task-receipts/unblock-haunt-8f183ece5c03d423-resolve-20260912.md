# Unblock resolution — lesson review safety gate

- Checked: 2026-09-12 UTC
- Unblock task: `unblock/haunt/8f183ece5c03d423/resolve`
- Result: **PREREQUISITE PREPARED; external reviews still required.**

## Current evidence

The assigned unblock task was open when checked and is now claimed. The parent
`crypthauntology-kids-followup-20260912` remains blocked at
`lesson-review-safety-gate`. `protocol/lesson-review-signoffs.json` has zero
reviewer records. The release manifest reports `educational_review.status:
PENDING`, `completed_reviews: 0`, `required_reviews: 2`, and
`disposition: BLOCKED`.

The release validator recomputed the lesson package hash as
`0e0e1b2a066541176fd2fddfb7a3ae30e1da5473dc24e41fa1f1b9258a09b405`, matching
the register. The validator therefore confirms a missing-review blocker, not a
stale-hash or release-code defect. The gate requires two distinct adults to
attest to their own independent review; no repository-only change can supply
those judgments honestly.

## Safe prerequisite prepared

Added `docs/lesson-review-request-kids-v1-20260912.md` as a reviewer handoff
outside the hash-covered `lessons/` directory. It identifies the exact package,
provides a hash check and checklist, specifies independent review and register
fields, and explicitly forbids entering attestations for someone else. No
lesson, signoff, or release data was changed, and no reviewer was contacted.

## Retry condition

Keep the safety gate blocked. Resume only after two distinct adult reviewers
independently record `APPROVE` for the current exact hash in
`protocol/lesson-review-signoffs.json`. Then regenerate the release using the
README command and verify the manifest is `APPROVED` for educational review
before any dependent closeout.

## Verification

- `mesh-task status crypthauntology-kids-followup-20260912` — parent gate blocked
  with the two-review retry condition.
- `cryptohaunt.release.evaluate_educational_review` — `PENDING`, 0/2 approvals;
  recomputed package hash matches the register.
- Archived `release/adult-study-2026-09-07-v1/release-manifest.json` — pending
  educational review and blocked disposition.
- `git diff --check` — no whitespace errors.
