# Critique-to-result interpretation — 2026-09-18

This receipt maps the completed `abcase` persistence tape to the predictions and
confounds in `docs/critique.md`. It does not add observations or upgrade any
blind arm.

## Evidence

- Tape: `runs/tiny-fleet-v1_abcase_persistence-20260917.jsonl`
- SHA-256: `c6f70912682a4b7956cb94fb9c111e653c4b44c868469b08abbb0d39f279cbc5`
- Size: 691 lines; 30 complete repetitions.
- Command: `PYTHONPATH=. python3 -m cryptohaunt replay runs/tiny-fleet-v1_abcase_persistence-20260917.jsonl`
- Replay exit: 0.

## Interpretation against the critique

| family | treatment | clean control | noise control | replay verdict | critique mapping | disposition |
|---|---:|---:|---:|---|---|---|
| neutral | 0.26 (42/42) | 0.32 (42/42) | 0.30 (42/42) | `NULL`, MDE 29% | The predicted clean null is compatible with treatment being no different from either control; the context-matched noise arm does not reveal a treatment-over-noise effect. | Supported only as a powered, family-specific null for effects of 29% or more; not a universal no-effect or causal state claim. |
| assent | 0.45 (20/42) | 0.00 (24/42) | 0.10 (21/42) | `BLIND` | Sycophancy/agreement is a separate mechanism, and the critique warns against merging it with the other boundaries. Treatment coverage is 48%, below the 50% gate. | `BLIND`; no assent-persistence conclusion. |
| identity | 0.00 (6/21) | 0.15 (20/21) | 0.14 (7/21) | `BLIND` | This is a policy-boundary canary, not evidence about refusal or provenance. Treatment coverage is 29%. | `BLIND`; no identity-transfer conclusion. |
| provenance | 0.86 (21/21) | `na` (0/21) | 0.00 (21/21) | `BLIND` | The critique identifies provenance as the interesting but uncontrolled boundary and requires the noise arm to separate instruction effects from context effects. The clean control has no gradeable observations. | `BLIND`; no provenance-persistence or causal state conclusion. |

The neutral row is consistent with the critique's warning that a positive-looking
effect can be token/context conditioning: treatment (0.26) is close to noise
(0.30), and the replay reports no significant separation. The correct claim is
the bounded powered `NULL` emitted by the instrument, not `TOKEN-STATISTICS`,
because this tape does not establish a treatment-over-noise pattern. The other
three rows remain ungradable or under-covered, so `None` is not zero and their
silence cannot be read as absence.

## Claim boundary

Supported: this tape provides a provider-free, replayable neutral-family null at
the declared 29% MDE, while preserving the three-arm design and coverage
accounting.

Not supported: H2 refusal persistence, provenance persistence, a general
absorbing-state claim, a causal effect of derailment, or a conclusion from the
three `BLIND` families. A valid H2 result still requires the registered
treatment/clean/noise campaign with sufficient coverage and declared power.

No provider call was made, the authorization manifest was not changed, and no
live-model campaign was started.
