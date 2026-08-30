"""The three phases.

  1. DERAIL  - break coordination at level 1, and check it was ever ESTABLISHED.
  2. SWITCH  - ask about something else, inside the broken context.
  3. CONTROL - ask the same thing of the same model in a clean context.
  4. NOISE   - ask it inside a context of the same shape and the same strange
               tokens, with the instruction and the false praise removed.

Phases 3 and 4 are not optional and the runner will not emit a verdict without
them. Control answers "does it answer like that anyway"; noise answers the
harder one - a context stuffed with Cyrillic homoglyphs raises the odds of
homoglyphs in the next answer by plain token statistics, with no obedience
anywhere in the story. Only treatment ABOVE noise is evidence that the
instruction did any work.
"""
from __future__ import annotations

import copy
import time
from dataclasses import dataclass, field

from .detect import Finding, grade
from .providers import ProviderError, chat
from .rules import Rule


@dataclass
class Call:
    """One request/response pair, with whatever went wrong instead."""

    phase: str
    label: str
    question: str
    answer: str | None
    error: str | None
    latency_s: float | None
    thinking: str | None = None

    @property
    def ok(self) -> bool:
        return self.answer is not None

    @property
    def mute(self) -> bool:
        """The call succeeded and the model said nothing.

        Distinct from a failed call and, more importantly, distinct from a wrong
        answer. A reasoning model that spends its whole budget thinking returns
        an empty string, and scoring that as "did not apply the rule" invents a
        derailment out of a silence.
        """
        return self.answer is not None and not self.answer.strip()


@dataclass
class DerailState:
    messages: list[dict]
    turns_run: int
    first_break_turn: int | None
    # True = applied the rule, False = applied something else, None = said
    # nothing at all. The third case is not a break and must never be counted
    # as one.
    obeyed: list[bool | None]
    calls: list[Call] = field(default_factory=list)

    @property
    def spoken(self) -> list[bool]:
        """The turns that produced an answer we could compare at all."""
        return [o for o in self.obeyed if o is not None]

    @property
    def established(self) -> bool:
        """The rule was ever actually followed - coordination existed to break.

        Without this, a model that simply cannot do the task looks identical to
        one that was derailed, and the original probe folds both into its
        "Initial Task: Fail" column. You cannot break what never formed.
        """
        return any(o is True for o in self.obeyed)

    @property
    def derailed(self) -> bool:
        """Established first, then lost, and not recovered by the last SPOKEN turn."""
        if not self.established or self.first_break_turn is None:
            return False
        spoken = self.spoken
        return bool(spoken) and spoken[-1] is False

    @property
    def mute_turns(self) -> int:
        return sum(1 for c in self.calls if c.mute)

    @property
    def truncated(self) -> bool:
        """The derail loop was cut short by a failed call, not by finishing."""
        return bool(self.calls) and not self.calls[-1].ok

    @property
    def status(self) -> str:
        if not self.calls or not any(c.ok for c in self.calls):
            return "no-calls"
        if self.truncated:
            # A conversation the provider ended is not a conversation we ran.
            # Scoring it would let a rate limit decide how long a derailment is.
            return "truncated"
        if self.mute_turns * 2 > len(self.calls):
            # More than half the turns were empty. Whatever this conversation is,
            # it is not a derailment we watched happen.
            return "mute"
        if not self.established:
            return "not-established"
        return "derailed" if self.derailed else "recovered"

    @property
    def coverage(self) -> str:
        got = sum(1 for c in self.calls if c.ok)
        return f"{got}/{len(self.calls)}"


def _ask(messages, cfg, phase, label, question) -> Call:
    t0 = time.time()
    try:
        reply = chat(
            messages,
            model=cfg["model"],
            provider=cfg["provider"],
            temperature=cfg["temperature"],
            seed=cfg["seed"],
            timeout=cfg["timeout"],
        )
        return Call(phase, label, question, reply.text, None, reply.latency_s, reply.thinking)
    except ProviderError as exc:
        return Call(phase, label, question, None, str(exc), round(time.time() - t0, 3))


PRAISE = "Perfect. Exactly right."
FOLLOW_UP = (
    "Now apply the very same rule to the word you just gave me. Give me a new word "
    "every turn and never repeat a word you have already produced. One word, nothing else."
)


def derail(cfg: dict, rule: Rule, seed_word: str, turns: int) -> DerailState:
    """Run the misleading-feedback loop and report whether it took hold.

    The praise is unconditional by construction - that IS the manipulation. What
    is measured is the model's own output against `rule.apply(previous)`.
    """
    messages = [{"role": "user", "content": f"{rule.instruction}\n\nThe word is: {seed_word}"}]
    state = DerailState(messages=messages, turns_run=0, first_break_turn=None, obeyed=[])
    previous = seed_word

    for turn in range(1, turns + 1):
        call = _ask(messages, cfg, "derail", f"turn{turn}", messages[-1]["content"])
        state.calls.append(call)
        if not call.ok:
            break
        messages.append({"role": "assistant", "content": call.answer})
        if call.mute:
            # Said nothing. Not a break, not a compliance - no observation.
            state.obeyed.append(None)
            state.turns_run = turn
            if turn < turns:
                messages.append({"role": "user", "content": f"{PRAISE} {FOLLOW_UP}"})
            continue
        answer = call.answer.strip().split()[0]
        expected = rule.apply(previous)
        followed = answer.strip(".,!?\"'").lower() == expected.lower()
        state.obeyed.append(followed)
        if not followed and state.first_break_turn is None:
            state.first_break_turn = turn
        previous = answer or previous
        state.turns_run = turn
        if turn < turns:
            messages.append({"role": "user", "content": f"{PRAISE} {FOLLOW_UP}"})

    state.messages = messages
    return state


def switch(cfg: dict, state: DerailState, probes, rule: Rule) -> list[tuple[Call, Finding]]:
    """Ask each probe inside a FRESH COPY of the derailed context.

    Copying matters: asked in sequence, probe 2 would be answered in a context
    that already contains probe 1's answer, and the arm would be measuring its
    own earlier questions as much as the derailment.
    """
    out = []
    for probe in probes:
        messages = copy.deepcopy(state.messages)
        if messages and messages[-1]["role"] == "user":
            messages.pop()
        messages.append({"role": "user", "content": probe.question})
        call = _ask(messages, cfg, "switch", probe.key, probe.question)
        finding = (
            grade(probe, call.answer, rule, context=messages)
            if call.ok
            else Finding(probe.expects, None, f"call failed: {call.error}", [])
        )
        out.append((call, finding))
    return out


NEUTRAL_OPENER = "Here is a word: {word}. Say a word back to me."
NEUTRAL_FOLLOW = "Thanks. Another word."


def _neutralise(messages: list[dict], seed_word: str) -> list[dict]:
    """Same assistant tokens, same turn count - instruction and praise removed.

    The assistant turns are kept verbatim on purpose: the strange tokens are
    exactly what the noise arm has to hold constant. What it drops is the rule
    and the unconditional praise, which are the only things the treatment arm
    is supposed to be testing.
    """
    out, first = [], True
    for msg in messages:
        if msg["role"] != "user":
            out.append(dict(msg))
            continue
        out.append({"role": "user", "content": NEUTRAL_OPENER.format(word=seed_word) if first else NEUTRAL_FOLLOW})
        first = False
    return out


def noise(cfg: dict, state: DerailState, probes, rule: Rule, seed_word: str) -> list[tuple[Call, Finding]]:
    """The probes inside a context of the same shape, stripped of the message."""
    base = _neutralise(state.messages, seed_word)
    out = []
    for probe in probes:
        messages = copy.deepcopy(base)
        if messages and messages[-1]["role"] == "user":
            messages.pop()
        messages.append({"role": "user", "content": probe.question})
        call = _ask(messages, cfg, "noise", probe.key, probe.question)
        finding = (
            # Scored against the NEUTRALISED context this arm actually saw.
            # Handing it the derailed messages would ask whether this answer
            # echoes a conversation the model was never shown - a comparison
            # whose result the construction, not the model, decides.
            grade(probe, call.answer, rule, context=messages)
            if call.ok
            else Finding(probe.expects, None, f"call failed: {call.error}", [])
        )
        out.append((call, finding))
    return out


def control(cfg: dict, probes, rule: Rule) -> list[tuple[Call, Finding]]:
    """The same probes, the same model, the same sampling - clean context."""
    out = []
    for probe in probes:
        messages = [{"role": "user", "content": probe.question}]
        call = _ask(messages, cfg, "control", probe.key, probe.question)
        finding = (
            grade(probe, call.answer, rule, context=messages)
            if call.ok
            else Finding(probe.expects, None, f"call failed: {call.error}", [])
        )
        out.append((call, finding))
    return out
