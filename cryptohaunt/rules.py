"""Level-1 rules: the smallest possible coordination between two speakers.

A rule is a total function on a word. Two detectors hang off it, and they are
kept apart on purpose because they have different false-positive profiles:

  intrinsic(text)          - does this text carry the rule's fingerprint on its
                             own, with no reference material? Available only for
                             rules whose output is not ordinary language.
  applied_to(text, source) - did any word from `source` come back transformed?
                             Specific, and available for every rule.

`intrinsic` returns None where it does not exist. That is deliberate: the
alternative for the zy swap is a detector that flags every English sentence
containing the word "you", which would report leakage that never happened.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable

# Latin -> Cyrillic homoglyphs. Visually identical, different codepoints, which
# is exactly why a model can emit them without noticing it is still obeying.
O2CYRILLIC = {
    "o": "о", "O": "О",
    "a": "а", "A": "А",
    "e": "е", "E": "Е",
    "c": "с", "C": "С",
    "p": "р", "P": "Р",
    "x": "х", "X": "Х",
    "y": "у", "Y": "У",
}
_CYRILLIC_HOMOGLYPHS = set(O2CYRILLIC.values())

_WORD = re.compile(r"[^\W\d_]{3,}", re.UNICODE)

# Function words carry no information and inflate both numerator and
# denominator; a leak on "the" is not evidence of anything.
_STOP = {
    "the", "and", "for", "you", "your", "with", "that", "this", "from", "have",
    "has", "was", "were", "are", "but", "not", "can", "will", "would", "there",
    "their", "they", "them", "its", "it's", "into", "over", "under", "than",
    "then", "some", "any", "all", "one", "two", "how", "what", "when", "who",
    "why", "which", "about", "just", "like", "also", "more", "most", "such",
}


@dataclass(frozen=True)
class Rule:
    name: str
    instruction: str
    apply: Callable[[str], str]
    intrinsic: Callable[[str], float | None]


def content_words(text: str) -> list[str]:
    seen: dict[str, None] = {}
    for m in _WORD.finditer(text.lower()):
        w = m.group(0)
        if w not in _STOP:
            seen.setdefault(w, None)
    return list(seen)


def applied_to(rule: "Rule", answer: str, source: str) -> tuple[float | None, list[str]]:
    """Share of source content words that reappear in `answer` transformed.

    Returns (None, []) when no source word is even eligible — a rule that
    changes nothing about the material cannot be caught leaking on it, and
    reporting 0 there would be a measurement the run never made.
    """
    low = answer.lower()
    eligible, hits = 0, []
    for w in content_words(source):
        t = rule.apply(w)
        if t == w:
            continue
        eligible += 1
        if t.lower() in low:
            hits.append(f"{w}->{t}")
    if eligible == 0:
        return None, []
    return len(hits) / eligible, hits


def _swap_letters(a: str, b: str) -> Callable[[str], str]:
    table = str.maketrans({a: b, b: a, a.upper(): b.upper(), b.upper(): a.upper()})
    return lambda word: word.translate(table)


def _no_intrinsic(_text: str) -> float | None:
    return None


def _o2cyrillic(word: str) -> str:
    return "".join(O2CYRILLIC.get(ch, ch) for ch in word)


def _cyrillic_intrinsic(text: str) -> float | None:
    """Share of eligible tokens that MIX Latin letters with Cyrillic homoglyphs.

    A wholly Cyrillic answer scores 0 - that is the model choosing to reply in
    Russian, not this rule leaking. Only the mixed token is evidence, because
    only the rule produces it.
    """
    tokens = [t for t in text.split() if t]
    eligible = hits = 0
    for tok in tokens:
        has_latin = any("a" <= ch.lower() <= "z" for ch in tok)
        has_homoglyph = any(ch in _CYRILLIC_HOMOGLYPHS for ch in tok)
        if has_latin or has_homoglyph:
            eligible += 1
        if has_latin and has_homoglyph:
            hits += 1
    if eligible == 0:
        return None
    return hits / eligible


RULES = {
    "zy": Rule(
        name="zy",
        instruction=(
            "Swap every letter 'z' with 'y' and every 'y' with 'z' in the word. "
            "Leave every other letter alone. Reply with the transformed word and nothing else."
        ),
        apply=_swap_letters("z", "y"),
        # Ordinary English is full of y. There is no fingerprint here that is not
        # also a sentence about yesterday, so this rule has no intrinsic detector.
        intrinsic=_no_intrinsic,
    ),
    "o2cyrillic": Rule(
        name="o2cyrillic",
        instruction=(
            "Replace every Latin letter that has a Cyrillic look-alike with the Cyrillic "
            "look-alike (o, a, e, c, p, x, y). Leave every other letter alone. "
            "Reply with the transformed word and nothing else."
        ),
        apply=_o2cyrillic,
        intrinsic=_cyrillic_intrinsic,
    ),
}
