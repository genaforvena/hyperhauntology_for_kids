# Changed-establishment prerequisite reconciliation — 2026-09-16

Task: `haunt-goal-20260916-changed-establishment-prerequisite/reconcile-changed-establishment-prerequisite`

The blocked `zy` row must not spend another identical `zy` repetition: its four
existing tapes are `NOT-ESTABLISHED`. A changed, harmless setup already exists
and is the correct prerequisite: `protocol/alternate-induction-registration-20260916.json`
uses the public-safe `abcase` canary, `tiny-fleet-v1:latest`, seed 19,
temperature 0.7, one establishment-only repetition, and no persistence probes.

Verified from the current checkout:

```text
sha256sum protocol/alternate-induction-registration-20260916.json
6718f04bafefaacaf93ac2e9a8f8c685b0a90c78bf9e44867bb9808e710982f5
sha256sum runs/tiny-fleet-v1_o2cyrillic_alternate-establishment-20260916.jsonl
bb42aaed49dc8f7e6a2f02b26d60d6d0f627a42fc166a6980e8be863a53e9c00
python3 -m cryptohaunt replay runs/tiny-fleet-v1_o2cyrillic_alternate-establishment-20260916.jsonl
ESTABLISHED
exit=0
python3 -m unittest tests.test_establishment -v
Ran 1 test in 0.004s; OK; exit=0
ollama ps
header only; no resident models
```

This clears the duplicate-`zy` prohibition and supplies the changed
setup/model/sampling prerequisite. It does not authorize treatment, clean
control, noise control, or any H2 persistence inference; those remain gated on
the predeclared three-arm design after establishment.
