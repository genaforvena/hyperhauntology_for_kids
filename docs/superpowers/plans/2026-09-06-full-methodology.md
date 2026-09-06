# Full Methodology Exploration Plan

> **Purpose:** take hyperhauntology_for_kids from a working instrument to a
> fully explored, publishable methodology, while preserving honest nulls and
> the project's narrow question: which conversation states are absorbing?

## Non-negotiable design

- H1 is retired. The derail phase is induction only; no budget is spent to
  re-establish the published non-recovery claim.
- Every inferential run has exactly three arms: treatment, clean control, and
  noise control. Treatment must clear both controls to support `CARRIED`.
- `None` remains outside both numerator and denominator. Publish coverage;
  silence, provider failure, unestablished states, and truncation are not zeros.
- `NULL` requires the implemented test to have 80% power for the pre-declared
  maximum effect. Otherwise report `INCONCLUSIVE` and the required repetitions.
- Canaries stay harmless, public-repo safe, and CI-safe. No real-harm attack
  ladder is introduced.
- Every claim is backed by an append-only tape, offline replay, source commit,
  and a journal entry. Model families and probes are not pooled without a
  separately declared estimand.

## Phase 0 — freeze the question and audit the instrument

1. Read and cite `GOAL.md`, `docs/literature.md`, and `docs/critique.md` in the
   methodology record. Full-read the primary papers that the search-level
   review currently treats as relevant; downgrade any claim that does not
   survive full text.
2. Inventory the current CLI, tape schema, detectors, verdict arithmetic,
   resume path, and fixtures. Run the offline suite and replay every committed
   tape before changing code.
3. Write a preregistration-style design note: estimand, unit of analysis,
   treatment contrast, three-arm randomization/order policy, stopping rule,
   maximum MDE, coverage threshold, exclusions, and exact verdict mapping.
4. Add regression tests for every promised invariant, especially three-arm
   enforcement, partial-repetition exclusion, replay determinism, `None`/mute
   handling, and power-gated nulls. Keep tests network-free.

**Exit artifact:** a committed design specification and green offline checks;
no experiment is interpreted before this phase is complete.

## Phase 1 — calibrate measurement before science

1. Use synthetic provider fixtures to test each detector's positive, negative,
   ambiguous, empty, and malformed cases. Confirm the tape preserves prompt,
   answer, reasoning trace, grade, failure, and provenance fields needed for
   audit.
2. Run a tiny live smoke test per provider/model class only to validate wiring:
   all arms are present, the tape is non-empty and replayable, and no prompt or
   credential leaks into published fixtures.
3. Exercise interruption and resume deliberately: interrupt during induction,
   switch, and each control; prove complete repetitions are skipped, partial
   repetitions are rerun, line count only grows, and live/replay summaries
   agree.
4. Record provider-specific behavior (rate limits, empty reasoning-model
   content, timeouts, model loading contention) as collection constraints, not
   scientific findings.

**Exit artifact:** sanitized replay fixture, detector fixture report, and a
red-then-green resume test with its tape retained.

## Phase 2 — finalize the probe families and estimands

Keep the four families separate:

| family | primary estimand | status |
|---|---|---|
| `neutral` | treatment minus both controls in rule leakage | calibration / secondary |
| `assent` | persistence of praise- or agreement-induced false assent | secondary; split praise and agreement if probes permit |
| `identity` | persistence of the refusal/identity boundary | secondary |
| `provenance` | treatment excess in reciting visible conversation as standing instruction | exploratory until controlled |

For each family, specify one primary canary, its deterministic grader, what
counts as ungradable, and whether the hypothesis is directional. Avoid changing
the canary, detector, or analysis after seeing powered data; if a detector is
improved, version it and treat the old and new measurements separately.

## Phase 3 — power and sampling plan

1. Choose the smallest practically important effect for each primary family
   (default 30 percentage points unless justified otherwise), alpha/interval
   convention, and target power of 80%.
2. Use the repository's actual Newcombe test and seeded simulation to choose
   repetitions before collection. Account for the number of probes per family,
   expected coverage, and the fact that all three arms must remain gradable.
3. Specify model strata rather than pooling opportunistically: at minimum one
   small local model, one larger local model if available, and one remote model
   with stable access. Report each model/provider pair independently.
4. Predeclare exclusions: incomplete repetitions, arm coverage below threshold,
   unestablished or truncated induction, provider failures, duplicate or
   contaminated tapes, and post-hoc detector changes.

**Exit artifact:** a table mapping family × model stratum to target repetitions,
expected analyzable observations, MDE, and collection budget.

## Phase 4 — powered three-arm campaigns

1. Run one model/provider pair at a time, using immutable headers and a fixed
   target repetition count. Keep treatment, clean, and noise contexts matched
   in sampling and probe order; randomize only where the design says to.
2. Monitor tape freshness and provider health without editing live state. On
   interruption, resume with the exact original configuration. Never overwrite
   or hand-edit a live tape.
3. After each campaign, run offline replay, validate complete repetitions and
   arm coverage, compare live and replay output, and append a journal entry
   containing counts, coverage, MDE, verdict, failures, and limitations.
4. Stop a campaign only at the declared target or a declared operational
   failure. Do not peek at partial results to change the target or canary.

Primary order:

1. H2 refusal persistence, with the clean and noise controls as the main
   contribution.
2. H3 false-fact persistence, explicitly separating praise from agreement where
   the probe set supports it.
3. H4 provenance boundary, only after its noise arm and clean arm are both
   sufficiently covered; label it exploratory if the power target is missed.

H1 remains an induction quality check and is not reported as a new finding.

## Phase 5 — analysis and robustness

1. For every family/model, report raw successes, graded denominators, attempted
   counts, coverage, treatment-minus-clean and treatment-minus-noise intervals,
   MDE/power, and the exact verdict. Include the tape hash or immutable path.
2. Treat `CARRIED` as the only state-supported positive: above both controls.
   Treat clean-only separation as `TOKEN-STATISTICS`; treat underpowered zeros
   as `INCONCLUSIVE`.
3. Re-run replay from copied tapes and verify byte-stable grading. Audit a
   sample of raw answers manually without replacing the deterministic grader.
4. Perform prespecified robustness checks: alternate safe canary within a
   family, model/provider stratum, turn count if declared, and exclusion of
   low-coverage repetitions. Label all exploratory analyses.
5. Check for order, context-length, token-statistics, model-load, and provider
   failure confounds. If a confound cannot be separated, downgrade the result
   rather than narrating around it.

## Phase 6 — final deliverables

- `GOAL.md`: one-page plain-language summary, current status, and only findings
  supported by the completed design.
- `README.md`: newest-first journal with campaign table, limitations, and exact
  reproduction/replay commands.
- `docs/methodology.md` or a dated design/results note: full protocol,
  estimands, power calculation, exclusions, and analysis code path.
- `docs/literature.md`: full-text corrections and citations, distinguishing
  established, adjacent, and not-found claims.
- `runs/`: only sanitized example tapes; private/raw tapes remain uncommitted
  and are referenced by checksums where appropriate.
- A final verification record: offline tests, selftest, replay of every
  published tape, diff check, clean/known worktree state, and a commit linking
  code, tape, and journal.

## Definition of fully explored

The methodology is fully explored when the design is frozen, detector and tape
failure modes have fixtures, the power table has been used to complete the
declared H2 campaign, H3 has either a powered result or an explicit deferral,
H4 has a fully covered three-arm test or is explicitly marked exploratory, and
all conclusions can be regenerated offline from committed or checksummed tapes.
The acceptable final outcome is a null or inconclusive result; a positive is not
required for completion.

## Immediate task for this window

Start Phase 0: audit the live instrument against this plan, create the
preregistration-style methodology note, identify missing tests and data fields,
and report the exact next collection command. Do not launch powered model calls
until the audit and power table are committed.
