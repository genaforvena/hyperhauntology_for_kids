# Lesson review release gate — 2026-09-12

Task: `crypthauntology-kids-followup-20260912/lesson-review-safety-gate`

The adult-only study checks remain valid (`adult_only_gate: true`). Educational
release is now a separate gate bound to the SHA-256 of the exact `kids-v1`
lesson package. It requires two distinct reviewers who attest to adult status,
independent review, approval, and the same materials hash. Disagreements remain
in the review register and block release until a resolution is recorded.

No adult reviews have been received. The canonical register records zero
reviews for materials hash
`0e0e1b2a066541176fd2fddfb7a3ae30e1da5473dc24e41fa1f1b9258a09b405`; this is
PENDING, and the release disposition is BLOCKED. Lesson files were removed from
the archived generated bundle. No review was fabricated and no child-facing
pilot or deployment occurred.

Verification: `python3 -m unittest discover -s tests` — 57 tests passed. The
focused test was observed failing before implementation (`RELEASED` where
`BLOCKED` was expected). The regenerated archived manifest reports the pending
review and blocked disposition.

Remaining event: obtain and record two independent adult reviews of this exact
materials hash; rerun the release command after updating the register.
