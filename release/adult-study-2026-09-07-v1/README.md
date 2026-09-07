# Adult-only absorbing-state study bundle

This bundle is a reproducibility and educational artifact. It contains one
append-only model tape, its SHA-256 in `release-manifest.json`, two independent
offline replay results, the disjoint calibration/holdout report, and copies of
the public educational materials.

Scope: local model only, harmless canaries, adult operator, no children and no
human research participants. The study target was 30 complete repetitions;
recovered inductions remain in the tape and are excluded from inferential
denominators.

The verifier was run with:

```bash
python3 -m cryptohaunt release \
  --manifest protocol/adult-study-manifest.json \
  --out release/adult-study-2026-09-07-v1 \
  runs/adult-study-gemma4-e2b-zy-30.jsonl
```

See `witness-report.json` for the explicit gate and disposition.
