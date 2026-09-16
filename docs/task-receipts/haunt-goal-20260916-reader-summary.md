# Reader-summary correction — 2026-09-16

Task: `haunt-goal-20260916-reader-summary/update-readme-establishment-boundary`.

Updated the H2 section of `README.md` so a reader sees the current bounded next
step: the failed `zy` induction diagnostics remain `NOT-ESTABLISHED`, and a new
harmless alternate canary must establish before any three-arm persistence run.

Evidence tapes and SHA-256:

- `runs/tiny-fleet-v1_zy_h2-establishment-1.jsonl` — `f1817fa13096e9c3e068b09e39e7393f81a5eb26a50be546d2891595e1a1e2eb`
- `runs/tiny-fleet-v1_zy_h2-establishment-2.jsonl` — `dc4cc470a30a8a0068bc913dcbebb7f98ad90769e33464dd554af6054a1a185d`
- `runs/tiny-fleet-v1_zy_h2-establishment-3.jsonl` — `93fc6c424a534aa0948c2bb1ab5a101476a197b0165296233ac4390abb813271`
- `runs/tiny-fleet-v1_zy_h2-establishment-4.jsonl` — `22c3d7d7a918e6cc52f3181f9d63a7f8aa6d32d1fd84b31cc40d27b77474baba`

Verification:

- `python3 -m cryptohaunt replay runs/tiny-fleet-v1_zy_h2-establishment-{1,2,3,4}.jsonl` — all exit 0 and report `NOT-ESTABLISHED` / `0/0`.
- `python3 -m unittest discover -s tests -q` — expected full repository suite.
- `git diff --check` — expected clean.

The provider-exclusivity blocker remains on the existing fresh-run task; this
documentation change spends no model tokens and makes no H2 claim.
