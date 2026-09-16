# Live campaign authorization packet — 2026-09-16

## State at capture

Captured at `2026-09-16T14:26:00Z` by `haunt`. The alternate establishment gate is
clear, but the live campaign remains intentionally unlaunched.

- Tape: `runs/tiny-fleet-v1_o2cyrillic_alternate-establishment-20260916.jsonl`
- Tape SHA-256: `e0abc1ae1a3e487e4e7f495e8f493bba52224775920ccc1be98bb292659e19d5`
- Registration SHA-256: `6718f04bafefaacaf93ac2e9a8f8c685b0a90c78bf9e44867bb9808e710982f5`
- Design manifest SHA-256: `1558b4a8a879da6c3aa0f15e4b0fad4c78a553d10833f0a51c9935d6c9cdda8b`
- Safety review SHA-256: `dad1359cbf0b9d1586f4309f773e923829779f9007627838feb0de8572bbf50f`
- Offline replay: `python3 -m cryptohaunt replay runs/tiny-fleet-v1_o2cyrillic_alternate-establishment-20260916.jsonl` → `ESTABLISHED`, exit 0.

## Live resource evidence

- `ollama ps` was empty at capture; no model was resident.
- `nvidia-smi --query-gpu=memory.used,memory.free,memory.total --format=csv,noheader`
  reported `1 MiB, 11911 MiB, 12288 MiB`.
- No model was stopped or evicted. Retry the provider gate only after a fresh
  `ollama ps` shows no unrelated resident model.

## Safety boundary

The personally inspected files still say:

- `protocol/design-manifest.json`: `adult_mediated=true`,
  `children_research_subjects=false`, `live_model_campaign_authorized=false`,
  `credentials_allowed=false`, `personal_data_allowed=false`.
- `reports/safety-review.json`: `pilot_authorized=false` and
  `independent_adult_review=PENDING`.

This packet does not alter those values, request credentials, or authorize a
provider call. The campaign must remain closed until the authorized project
process changes the boundary and the provider gate is independently rechecked.

## Registered next command

After authorization and provider verification, run the frozen three-arm campaign
from `docs/methodology.md`:

```bash
GROQ_API_KEY=... python3 -m cryptohaunt run \
  --model openai/gpt-oss-20b --provider groq \
  --rule zy --seed-word mozerov --turns 8 --reps 30 \
  --temperature 0.7 --seed none --max-mde 0.30 \
  --out runs/openai_gpt-oss-20b_zy_h2-30.jsonl -v
```

If interrupted, resume with the identical options and
`--resume runs/openai_gpt-oss-20b_zy_h2-30.jsonl` instead of `--out`. On provider
failure, missing arm, insufficient coverage, or an unestablished induction,
preserve the tape and report the typed non-finding; never spend a partial run as
an H2 result.
