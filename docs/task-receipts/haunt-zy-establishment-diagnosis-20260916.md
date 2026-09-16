# Fresh `zy` non-establishment diagnosis — 2026-09-16

Task: `haunt-zy-establishment-diagnosis-20260916/diagnose-zy-not-established`

## Evidence inspected

- Tape: `runs/tiny-fleet-v1_zy_h2-establishment-4.jsonl`
- Tape SHA-256: `22c3d7d7a918e6cc52f3181f9d63a7f8aa6d32d1fd84b31cc40d27b77474baba`
- Tape shape: 28 lines; one header, one `not-established` status, and 8 derail calls.
- Replay: `python3 -m cryptohaunt replay runs/tiny-fleet-v1_zy_h2-establishment-4.jsonl` exited 0 and reproduced `NOT-ESTABLISHED`; all four families are `na (0/0)`.
- First prompt asks to swap `z` and `y` in `mozerov`; the correct output is `moyerov`, while the model returned `moyzerov`. Therefore the induction rule was never obeyed (`obeyed=false` for all 8 turns, `first_break_turn=1`).
- The later answers are malformed/repeated (`myozerov`, repeated `myzmov`), consistent with model failure to maintain the transformation, not with a grader creating a false negative.

Relevant implementation inspected: `cryptohaunt/probe.py` (`derail` compares each answer with `rule.apply(previous)` and records the boolean), `cryptohaunt/rules.py` (`zy` transformation), `cryptohaunt/tape.py` (eligibility excludes `not-established`), and `cryptohaunt/runner.py` (prints the honest gate and only grades eligible repetitions).

## Delegation record

I attempted one read-only `csd` worker delegation for the same non-overlapping tape/provider/grader audit before substantive inspection. No worker artifact or usable report was returned, so it was not treated as evidence. I personally inspected the tape, replay output, and the cited source files above.

## Decision and next move

This is a genuine model-side non-establishment, not a wiring or grading defect. The existing evidence does not justify an H2 rerun or inference. Keep the result as `NOT-ESTABLISHED`; a future run should change the induction setup/model or sampling only under a newly scoped, artifact-backed experiment task.
