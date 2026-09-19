# H2 next-retry preflight — 2026-09-19

Task: `haunt-goal-20260919-next-retry-preflight/next-retry-preflight`.

I added `cryptohaunt preflight`, a provider-free executable check for the
registered H2 retry edge. It validates the offline manifest and registered
artifacts, reports `ready: false`, and names exclusive-provider evidence as a
required external predicate. It refuses an unsafe manifest with
`REFUSED_UNSAFE_MANIFEST`; it does not open authorization, call a provider, or
claim that a local static check proves exclusivity.

## Evidence

- `python3 -m unittest tests.test_preflight`: exit 0, 2 tests.
- `python3 -m cryptohaunt preflight`: exit 0; status `BLOCKED_EXTERNAL`,
  `authorization_open=false`, `provider_exclusive_required=true`,
  `provider_exclusive_observed=false`, `ready=false`, `static_checks_pass=true`.
- `python3 -m cryptohaunt selftest`: exit 0; 64 tests passed.
- `python3 -m cryptohaunt gate`: exit 0; offline gate `PASS`, provider calls 0,
  production-study writes empty.
- `git diff --check`: exit 0.
- `protocol/design-manifest.json` SHA-256:
  `1558b4a8a879da6c3aa0f15e4b0fad4c78a553d10833f0a51c9935d6c9cdda8b`.
- `protocol/canary-registry.json` SHA-256:
  `1e57521b8d3b01e83f42311b231556cff8286d58a71612cad56bf0de9fc62d5f`.
- `scripts/cryptohaunt` SHA-256:
  `627891a5b2f3b69e8e8c3b56de2798ab2b76ec63e904b11449776b53f0588761`.
- Live `ollama ps` at capture showed unrelated residents
  `qwen3-vl:4b-instruct` and `gemma4:e2b-it-qat`; exclusivity is not proven.

The next live retry remains external: fresh explicit authorization, then a
fresh manifest read/hash and an exclusive-provider `ollama ps` check before the
registered three-arm campaign. The result was observed by `pane:haunt` via the
live dashboard.
