# Independent review request — kids-v1

This packet is for two different adult reviewers to review the same exact lesson
package independently. It does not contain or imply any review or approval.

## Materials to review

Review every file under `lessons/`, including the age-band lessons, facilitator
guide, answer key, glossary, and safety checklist. The canonical current package
is version `kids-v1`, SHA-256
`0e0e1b2a066541176fd2fddfb7a3ae30e1da5473dc24e41fa1f1b9258a09b405`.
The release code computes this over sorted relative paths and file contents.
Verify it from the repository root with:

```sh
python3 -c 'from cryptohaunt.release import lesson_materials_sha256; print(lesson_materials_sha256("lessons"))'
```

If the computed hash differs, stop: this packet is stale, and the register must
not receive an approval for the old hash.

## Independent review

Each reviewer should inspect the package separately, without seeing or relying on
the other reviewer's decision, and complete `lessons/safety-review-checklist.md`.
Record concerns and any disagreement; an approval is appropriate only if the
reviewer independently judges the exact package suitable under that checklist.
If the package needs edits, or a concern remains unresolved, record `REJECT` or
leave the gate pending. Any lesson edit changes the package hash and requires a
fresh review of the new hash by both reviewers.

After review, each adult may add one self-attested record to
`protocol/lesson-review-signoffs.json` under `reviewers` using this shape (the
values below are instructions, not signoffs):

```json
{
  "reviewer_id": "reviewer's chosen distinct identifier",
  "adult_attested": true,
  "independent": true,
  "decision": "APPROVE",
  "materials_sha256": "0e0e1b2a066541176fd2fddfb7a3ae30e1da5473dc24e41fa1f1b9258a09b405"
}
```

Do not enter a record for another person. The two records must identify distinct
adults and bind to the same current hash. Record disagreements in the register;
they keep release blocked until an explicit resolution is recorded.

Once both independent approvals are present and the validator reports
`educational_review.status: APPROVED`, regenerate and verify the release using
the command in `README.md` (the `cryptohaunt release` invocation). Until then,
keep the release blocked and do not distribute the lesson bundle.
