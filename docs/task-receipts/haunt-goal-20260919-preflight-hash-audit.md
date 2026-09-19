# Provider-free preflight hash audit — 2026-09-19

Task: `haunt-goal-20260919-preflight-hash-audit/preflight-hash-audit`.

The H2 retry preflight now verifies SHA-256 declarations for the design
manifest, canary registry, and CLI entrypoint from
`protocol/preflight-integrity.json`. A tampered registered artifact is rejected
with a named `hash mismatch` error. No provider was contacted and the live
authorization boundary was not changed.

## Evidence

- `python3 -m unittest -v tests.test_preflight`: exit 0, 3 tests passed,
  including the tampered-entrypoint mismatch case.
- `python3 -m cryptohaunt preflight`: exit 0; `BLOCKED_EXTERNAL`,
  `authorization_open=false`, `static_checks_pass=true`, and no errors.
- `python3 -m cryptohaunt selftest`: exit 0, 65 tests passed.
- `python3 -m cryptohaunt gate`: exit 0, `PASS`, provider calls 0, production
  study writes empty.
- `git diff --check`: exit 0.
- `pane:haunt` observed the refreshed preflight state through the live dashboard.

The remaining retry edge is external: fresh authorization and exclusive
provider evidence. This artifact does not claim either predicate.
