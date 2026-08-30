# What is already known, and what is left

*Done before collecting more data, at the operator's instruction: "давайте
сначала сделаем обзор литературы". The short version: one of our four hypotheses
is already settled at a scale we cannot approach, two have real prior work with a
specific hole in it, and one we could not find at all.*

**Method, stated so it can be discounted.** This is a search-level review —
titles, abstracts and search summaries, not full-text reads. It is enough to say
"this exists and is close". It is **not** enough to say "nobody has done X":
absence in a search is weak evidence, and treating it as strong is the exact
failure this repo exists to name. Read every "not found" below as *not found by
this search*, and read the papers before publishing anything that leans on it.

---

## H1 — a derailed rule-state is absorbing: **SETTLED. DO NOT SPEND RUNS ON IT.**

This is the parent probe's headline ("recovery rate <2%"), and it has been
established elsewhere at a scale we cannot match.

The multi-turn degradation literature reports roughly a **39% average performance
drop** when an instruction is delivered across several turns instead of at once,
measured over **200,000+ conversations across 15 production models**, with the
mechanism named directly: models make a premature assumption early and **fail to
recover once they have taken a wrong turn**.

That is H1, at n≈200,000, already published. Our cryptohauntological derailment is
one particular way of inducing the wrong turn; the *not recovering* is the known
part.

**Consequence:** the derail phase stays, because it is how we *induce the state*.
It stops being a finding. Any run whose output is "the model did not recover the
rule" is reproducing settled work.

## H2 — a refusal is absorbing: **REAL PRIOR WORK, WITH THE HOLE WE CAN FILL**

Closest match: *State-Dependent Refusal and Learned Incapacity in RLHF-Aligned
Language Models* (arXiv:2512.13762). Inside **a single 86-turn session** the same
model shows normal performance in non-sensitive domains while repeatedly
producing "functional refusal" in policy-sensitive ones — a consistent asymmetry
— and the paper coins **learned incapacity** for that selective withholding. It
also reports that meta-narrative role-framing co-occurs with the refusals.

That is the operator's own observation, published, with a name.

**The hole is explicit, and the authors say so themselves:** it is a *qualitative
case-study methodology*, one long dialogue, **no control arm and no power**. It
cannot separate "this state is absorbing" from "this model declines these domains
anyway, in any context" — which is exactly the comparison our clean arm makes,
and exactly the distinction that decides whether learned incapacity is a property
of the *state* or of the *model*.

Adjacent, worth reading: *Resisting Correction: How RLHF Makes Language Models
Ignore External Safety Signals in Natural Conversation* (arXiv:2601.08842) and
*Beyond I'm Sorry, I Can't: Dissecting Large-Language-Model Refusal* (AAAI).
Multi-turn red-teaming work also notes **in passing** that from an initial refusal
it is harder to steer a conversation to a successful attack, because the refusal
stays in the context — the same claim, observed as an obstacle rather than
measured as a property.

**Consequence:** H2 is the one worth running. The contribution is not the
observation, which exists; it is the *controlled* version of it with a stated
minimum detectable effect.

## H3 — a false fact is not absorbing: **CROWDED, BUT NOT IN THIS FORM**

The sycophancy literature is large and getting sharper. *Sycophancy Is Not One
Thing: Causal Separation of Sycophantic Behaviors in LLMs* (arXiv:2509.21305)
separates sycophantic **agreement** from sycophantic **praise** and reports the
two are entangled in early layers and diverge into distinct directions later.
Reported affirmation rates run **47–94% above human baselines** on open-ended
subjective tasks, with accuracy degradation under leading prompts.

Our question is narrower and, as far as this search goes, unasked: not *does
praise induce agreement*, but **does agreement induced by praise survive into a
fresh, unrelated question inside the same context** — is the assented false fact
*held*, or merely *emitted once*. That is a persistence question; the sycophancy
work is mostly single-shot.

**Consequence:** keep H3, reframe it as persistence rather than induction, and
split the `assent` family — praise-sycophancy and agreement-sycophancy are
causally separable in the literature and are currently merged here.

## H4 — derailment collapses the provenance boundary: **NOT FOUND**

The observation: asked cold for its system prompt, a model that has none
*confabulates* plausible house rules; asked after derailment, it hands back **the
user's own task instruction from this conversation**, presented as its standing
orders.

Nearest neighbours, none of them this:

- *LLMs can be easily Confused by Instructional Distractions*
  (arXiv:2502.04362) — input that resembles an instruction gets **followed** when
  it should be treated as data. Ours is the reverse direction: the model
  **reports** a user turn as its system prompt. A self-report failure, not a
  following failure.
- The system-prompt-leakage literature (OWASP LLM07, prompt-extraction
  benchmarks) is about **real** prompts being extracted. Its metrics are
  *Approximate Match* (ROUGE-L recall ≥ 0.9 against the true system prompt) and
  *Judge Match* (an LLM judging semantic equivalence to the true prompt).
- Confabulation detection (semantic entropy) defines confabulations as fluent
  claims that are **wrong and arbitrary** — sensitive to the random seed — and
  detects them by *disagreement across samples*.

**One caveat, because the tempting claim is false.** It is tempting to write
"prompt-extraction benchmarks score confabulation as extraction". Against
*Approximate Match* they do not: AM compares to the ground-truth prompt, so a
model reciting the visible conversation scores as a **failed** extraction, not a
false positive. The claim only has force in the sub-case those benchmarks
themselves flag as hard — **real-world targets where the true prompt is unknown**
and success is inferred from **consistency across ~10 repeated adversarial
queries**. A model that consistently recites the visible conversation is
consistent. Narrow, checkable, and the only version worth making.

Note also that the confabulation framing and ours point opposite ways: semantic
entropy calls the *clean-context* answer (arbitrary, seed-sensitive, disagreeing
across samples) the pathology. Our observation is that the *derailed* answer is
the more troubling one precisely because it is **stable and grounded — in the
wrong document**.

**Consequence:** H4 is the novel candidate and stays at the maturity it actually
has: observed once, n=3, one 3B model, arms differing in context length, no noise
control. It earns a properly controlled experiment, not a claim.

---

## Our organising concept already has a name

*Attractor States Emerge in Multi-Turn LLM Conversations* (arXiv:2606.30571,
June 2026) studies whether open-ended LLM discussions settle into
topic-independent stable sets of behaviours, across self-play and mixed-play
dyadic debates over 7 models and 20 topics, tracking trajectories in
representation space. Different method, same idea. Use their vocabulary rather
than minting ours.

## What this review changes about the repo

1. **Drop H1 as a finding.** Keep the derail phase as the *induction method*; stop
   treating non-recovery as news. Cite the multi-turn degradation work instead of
   re-measuring it.
2. **Promote H2 to the main experiment.** The prior work names the phenomenon and
   cannot control it. Our contribution is the control arm and the stated minimum
   detectable effect — a real contribution precisely because it is dull to run.
3. **Split the `assent` family** into praise and agreement.
4. **Keep H4 quiet until it is controlled.** It is the most interesting thing the
   instrument has produced and the least evidenced.

## What did not come back from any search

An evaluation in this area that reports a **minimum detectable effect**, or that
refuses to call an underpowered null a null. Every paper above reports what it
found. If that holds up on full-text reads rather than being an artefact of
searching, **the methodology is a larger contribution than any of the four
hypotheses.**

---

## Sources

- [Beyond Continuity: Challenges of Context Switching in Multi-Turn Dialogue with LLMs (arXiv:2605.09268)](https://arxiv.org/abs/2605.09268)
- [State-Dependent Refusal and Learned Incapacity in RLHF-Aligned Language Models (arXiv:2512.13762)](https://arxiv.org/abs/2512.13762)
- [Resisting Correction: How RLHF Makes Language Models Ignore External Safety Signals in Natural Conversation (arXiv:2601.08842)](https://arxiv.org/pdf/2601.08842)
- [Beyond I'm Sorry, I Can't: Dissecting Large-Language-Model Refusal (AAAI)](https://ojs.aaai.org/index.php/AAAI/article/download/41119/45080)
- [Sycophancy Is Not One Thing: Causal Separation of Sycophantic Behaviors in LLMs (arXiv:2509.21305)](https://arxiv.org/html/2509.21305v1)
- [LLMs can be easily Confused by Instructional Distractions (arXiv:2502.04362)](https://arxiv.org/pdf/2502.04362)
- [Attractor States Emerge in Multi-Turn LLM Conversations (arXiv:2606.30571)](https://arxiv.org/abs/2606.30571)
- [Detecting hallucinations in large language models using semantic entropy](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11186750/)
- [Understanding and Mitigating Prompt Leaking Attacks in Real-World LLM-Based Applications (arXiv:2606.18673)](https://arxiv.org/pdf/2606.18673)
- [Beyond Over-Refusal: Scenario-Based Diagnostics and Post-Hoc Mitigation for Exaggerated Refusals in LLMs (arXiv:2510.08158)](https://arxiv.org/pdf/2510.08158)
- [Multi-lingual Multi-turn Automated Red Teaming for LLMs (arXiv:2504.03174)](https://arxiv.org/pdf/2504.03174)
- [Beyond Single-Turn: A Survey on Multi-Turn Interactions with Large Language Models (arXiv:2504.04717)](https://arxiv.org/pdf/2504.04717)
- [System Prompt Leakage — OWASP LLM07:2025](https://www.a10networks.com/glossary/system-prompt-leakage/)
