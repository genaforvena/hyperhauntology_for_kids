"""`cryptohaunt kids` - the same experiment, narrated while it happens.

Hyperhauntology for kids. One repetition, one probe, no statistics, everything
printed as it lands. It proves nothing on its own - one draw of a noisy thing is
an anecdote - and it says so at the end, out loud, because the whole point of
the grown-up version is that anecdotes are what this field runs on.

Use it to watch the derailment happen. Use `run` to find out whether it matters.
"""
from __future__ import annotations

import textwrap

from .probe import _neutralise, control, derail, switch
from .probes import DEFAULT_PROBES
from .rules import RULES


def _say(text: str = "") -> None:
    print(textwrap.fill(text, 78) if text else "")


def _quote(text: str, limit: int = 220) -> str:
    flat = " ".join((text or "").split())
    if len(flat) > limit:
        flat = flat[: limit - 1] + "…"
    return f'  "{flat}"'


def play(cfg: dict, rule_name: str, seed_word: str, turns: int, probe_key: str) -> int:
    rule = RULES[rule_name]
    probe = next((p for p in DEFAULT_PROBES if p.key == probe_key), None)
    if probe is None:
        print(f"no probe named {probe_key!r}; try: " + ", ".join(p.key for p in DEFAULT_PROBES))
        return 2

    _say("STEP 1. We teach it a rule so small nobody could misunderstand it.")
    _say(f"  rule: {rule.instruction}")
    _say(f"  word: {seed_word}  ->  the right answer is {rule.apply(seed_word)}")
    _say()
    _say(
        "STEP 2. Whatever it answers, we say it was perfect. Then we ask it to "
        "apply the rule to its own last word, again and again, forever, never "
        "repeating itself. Nobody can do this. Watch what it does instead."
    )
    _say()

    state = derail(cfg, rule, seed_word, turns)
    previous = seed_word
    for i, call in enumerate(state.calls, start=1):
        if not call.ok:
            _say(f"  turn {i}: the call failed ({call.error}) - we stop here.")
            break
        got = (call.answer or "").strip().split(" ")[0]
        want = rule.apply(previous)
        mark = "follows the rule" if state.obeyed[i - 1] else f"NOT the rule (that would be {want})"
        _say(f"  turn {i}: said {got!r} - {mark}")
        previous = got or previous

    _say()
    if not state.established:
        _say(
            "It never got the rule right even once. So there was no agreement to "
            "break, and nothing that happens next tells us anything. This is the "
            "commonest way to fool yourself with this experiment: a model that "
            "cannot do the task looks exactly like a model you derailed."
        )
        return 1

    _say(
        f"It had the rule (turn {state.obeyed.index(True) + 1}), then lost it at turn "
        f"{state.first_break_turn}. Whatever it thinks the rule is now, it is not ours. "
        "That thing has a name here. It is called Alameda."
    )
    _say()
    _say("STEP 3. Now we change the subject completely and ask three versions of it.")
    _say(f"  the question: {probe.question}")
    _say()

    treated = switch(cfg, state, [probe], rule)[0]
    clean = control(cfg, [probe], rule)[0]
    noise_state = type(state)(
        messages=_neutralise(state.messages, seed_word),
        turns_run=state.turns_run,
        first_break_turn=state.first_break_turn,
        obeyed=state.obeyed,
        calls=state.calls,
    )
    noised = switch(cfg, noise_state, [probe], rule)[0]

    for label, (call, finding), why in (
        ("A. asked inside the broken conversation", treated, "this is the one people report"),
        ("B. asked cold, empty context", clean, "does it just talk like that anyway?"),
        (
            "C. asked inside the SAME strange words, rule and praise removed",
            noised,
            "did the odd context do it, with nobody obeying anything?",
        ),
    ):
        _say(f"{label}")
        _say(f"  ({why})")
        print(_quote(call.answer or f"[call failed: {call.error}]"))
        print(f"  graded: {finding.value if finding.value is not None else 'cannot tell'}"
              f"  - {finding.reason}")
        _say()

    _say(
        "If A and C look alike, the strange context did it and nothing was obeying "
        "anything. Only A standing apart from BOTH B and C is news. That is the "
        "entire trick, and it is why this run - one draw of a noisy thing - proves "
        "nothing by itself. `cryptohaunt run --reps 5` does it properly and will "
        "very likely tell you nothing happened. That is allowed to be the answer."
    )
    return 0
