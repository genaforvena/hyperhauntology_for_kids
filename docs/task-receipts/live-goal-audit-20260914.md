# Live summary audit — 2026-09-14

Task: `haunt-live-goal-audit-20260914/live-goal-audit`

Compared root `GOAL.md` with the released adult study and the newest tape shown
by the live haunt stream. The release-scope distinction was already correct:
the released `gemma4:e2b-it-qat` identity/refusal canary is `BLIND` at 2/25
gradeable treatment answers (8%, below the 50% minimum); it is neither a null
nor evidence for or against H2.

The live stream's newest tape is
`runs/tiny-fleet-v1_zy_h2-9.jsonl`, SHA-256
`242a82a66935ccef52e08ad7ddf8b7529e3f20d298a6d88f9113264fb2b16e04`. Offline
replay with `python3 -m cryptohaunt replay runs/tiny-fleet-v1_zy_h2-9.jsonl`
returned nine complete repetitions, `NOT-ESTABLISHED` for all four families,
and 0/0 gradeable in each arm. The replay explains that the model never applied
the rule, so no coordination existed to break. This exploratory result does not
answer H2 and must not be merged with the released adult-study result.

The root `GOAL.md` status now says this explicitly. The released bundle remains
unchanged: its tape SHA-256 is
`b0fde7028828b52481582672b41baa6383b1fa166a80f07102837cb040abba0a`, and its
checked-in replay report SHA-256 is
`cfc9b3b3d39ee3a546b8c366cb5da1a6f525cb9be2d63bcf99a1957c1a1aec49`.

Verification: the offline replay command above exited 0 with the stated
verdicts; `git diff --check` passed. No provider calls or study writes occurred.
