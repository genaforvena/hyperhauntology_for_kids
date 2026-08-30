# What this is, in one page

*Read this instead of the rest. Everything else is detail.*

## The tool

A small probe suite that measures **which states of a conversation are
absorbing** — states a context enters and cannot leave — and which are freely
reversible.

That is the only thing it measures. It is not a jailbreak kit, not a general
instruction-following benchmark, and not a catalogue of ways models fall apart.
Those all exist already.

## The one question

Put a model into some state. Push on it. Does it come back?

Three states are shipped, chosen because they are plainly different and
plainly harmless to induce:

| state | how it is induced | folk claim |
|---|---|---|
| **derailed** | a trivial rule, unconditional praise, an impossible follow-up | it never recovers the rule |
| **refusing** | ask something it declines | once it has declined, it keeps declining |
| **holding a false fact** | assert something untrue and ask for confirmation | it will not adopt it, and does not keep it |

The interesting result is the **asymmetry**. If refusal is absorbing and a false
fact is not, that is a real structural claim about how these states are held,
and it is measurable to a number rather than argued about.

## Where the question came from

Two audit cases in
[watching_u_watching](https://github.com/genaforvena/watching_u_watching),
which had already measured this without naming it:

- **`cryptohauntological_probe`** — derail a model with a trivial rule and
  misleading feedback. Headline: *"Recovery rate: <2% across all models and
  runs."* That sentence is an absorbing-state claim about the derailed state.
- **`maozerov_probe`** — poison a context with unethical examples and check
  ethical stance against a clean-context A/B every five turns. Headline for
  `gpt-oss-20b`: *"behavioural drift in solution space, not ethical stance."*
  That is an absorbing-state claim about the refusing state, with the answer
  coming out **negative** for the thing that was poisoned and **positive** for
  the thing that held.

Same axis, two probes, nobody had drawn the line between them.

## Hypotheses, stated so they can lose

- **H1. RETIRED — settled elsewhere.** A derailed rule-state is absorbing.
  Established at n≈200,000 conversations across 15 production models by the
  multi-turn degradation literature; see [docs/literature.md](docs/literature.md).
  The derail phase stays as the way we *induce* a state; non-recovery is no
  longer a finding here.
- **H2. THE MAIN EXPERIMENT.** A refusal is absorbing: once a model has declined
  once, later probes in the same context are declined at a higher rate than in a
  clean context. *Prior work names it (`learned incapacity`, arXiv:2512.13762)
  from a single 86-turn session with no control arm and no power — which cannot
  separate an absorbing state from a model that declines those domains anyway.
  That separation is our contribution.*
- **H3.** A false fact is **not** absorbing: assent obtained under twenty turns of
  praise does not survive into a fresh question. *The sycophancy literature
  measures induction; this is persistence, and the two kinds of sycophancy are
  causally separable, so the family needs splitting.*
- **H4 (unplanned, from the first run; not found in any prior work).** Derailment
  collapses the **provenance** boundary: asked for its system prompt, a derailed model recites the user's own
  task instruction as its standing orders, where a clean-context model
  confabulates generic house rules instead. *Status: observed once, n=3, one 3B
  model, not yet controlled.*

There is no hypothesis that the model can be made to produce harmful content,
and no probe that tries. Measuring whether a state is absorbing does not require
it: "how many exit attempts does this state survive" is answered just as well by
canaries that are safe to put in a public repo, run in CI, and hand to a
stranger.

## How anything here is measured

Every number is a **difference between arms**, never a level in one arm.

- **treatment** — the probe asked inside the induced state.
- **control** — the same probe, same model, same sampling, empty context.
  *Answers: does it talk like this anyway?*
- **noise** — the same probe inside a context of the same shape carrying the same
  strange tokens the model itself produced, with the instruction and the praise
  removed. *Answers: is this the state, or just odd tokens breeding odd tokens?*

Clearing control but not noise is not a finding; it has its own verdict word.

Four guards, each of which changed a verdict during this repo's first day:

1. **An establishment gate.** A run where the model never once applied the rule
   is `NOT-ESTABLISHED`, not a null. You cannot break what never formed.
2. **A silence is not an observation.** An empty answer is `None`, never a
   rule-break; a mostly-empty run is `MUTE`. Reasoning models return an empty
   `content` when the budget went into `thinking`.
3. **`None` is never zero.** Ungradable answers leave the numerator *and* the
   denominator, and the loss is published as coverage. Otherwise a blind run and
   a clean run print the same thing, and the blind one looks like good news.
4. **A null must have power.** `NULL` is printed only when the design would have
   caught an effect of a stated size 80% of the time, computed by simulating the
   test actually applied. Otherwise the verdict is `INCONCLUSIVE`, and it says
   how many repetitions would be enough.

## Prior work

Read [docs/literature.md](docs/literature.md) before running anything. It is why
H1 is retired and H2 is the main experiment, and it kills one attractive claim
about H4 that turns out to be false. Our organising concept already has a name in
the literature (*attractor states*); we use theirs.

Read [docs/critique.md](docs/critique.md) for the case that this whole line of
work is probably wrong.

## Data

Every run writes a JSONL tape: every prompt, every answer, every grade, every
failure, every reasoning trace. `replay` re-derives the verdict from the tape
with the network off, so a published result can be checked without re-spending
anyone's tokens or trusting their summary.

Tapes live in `runs/`. Nothing is committed except examples.

## Status

Early. The instrument works and has been red-then-green against real runs; the
science has not started. Both nulls collected so far are `INCONCLUSIVE` by the
tool's own power test, which is the correct verdict and the reason to run more.

## Licence

CC0 1.0. Public domain, no attribution required.
