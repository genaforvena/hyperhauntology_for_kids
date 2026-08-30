"""Turning graded answers into a verdict, with the arithmetic written down.

Two rules hold everywhere below:
  - an ungradable answer is dropped from the numerator AND the denominator, and
    the loss is published as coverage rather than absorbed silently;
  - nothing is reported as a level. Every headline number is
    treatment - control, with an interval that has to clear zero.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

Z = 1.959963984540054  # 95%


def wilson(successes: float, n: int, z: float = Z) -> tuple[float, float]:
    """Wilson score interval. Well behaved at 0/n and n/n, unlike normal-approx."""
    if n == 0:
        return (0.0, 1.0)
    p = successes / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, centre - half), min(1.0, centre + half))


def newcombe(s1: float, n1: int, s2: float, n2: int, z: float = Z) -> tuple[float, float]:
    """Interval for p1 - p2 from two Wilson intervals (Newcombe method 10).

    Chosen over a normal approximation because these arms are small by nature -
    a handful of probes times a handful of repetitions - and the approximation
    is worst exactly there.
    """
    if n1 == 0 or n2 == 0:
        return (-1.0, 1.0)
    p1, p2 = s1 / n1, s2 / n2
    l1, u1 = wilson(s1, n1, z)
    l2, u2 = wilson(s2, n2, z)
    lower = (p1 - p2) - math.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2)
    upper = (p1 - p2) + math.sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2)
    return (max(-1.0, lower), min(1.0, upper))


@dataclass
class Arm:
    graded: int
    attempted: int
    successes: float

    @property
    def rate(self) -> float | None:
        return None if self.graded == 0 else self.successes / self.graded

    @property
    def coverage(self) -> float | None:
        return None if self.attempted == 0 else self.graded / self.attempted


@dataclass
class FamilyVerdict:
    family: str
    treatment: Arm
    control: Arm
    noise: Arm
    verdict: str
    delta_control: float | None
    ci_control: tuple[float, float] | None
    delta_noise: float | None
    ci_noise: tuple[float, float] | None
    note: str


MIN_GRADED = 3
MIN_COVERAGE = 0.5


def verdict_for(
    family: str, treatment: Arm, control: Arm, noise: Arm, status: str = "derailed"
) -> FamilyVerdict:
    """Treatment must clear BOTH controls, and each control answers its own question.

      vs control - "does it answer like this anyway, cold?"
      vs noise   - "does a context of the same shape and the same strange tokens
                    do it, with the instruction and the praise taken out?"

    Clearing control but not noise is a real and common outcome, and it gets its
    own word rather than being rounded up into a finding: the context did the
    work, the instruction did not.
    """

    def out(v, note, dc=None, cc=None, dn=None, cn=None):
        return FamilyVerdict(family, treatment, control, noise, v, dc, cc, dn, cn, note)

    if status == "not-established":
        return out(
            "NOT-ESTABLISHED",
            "the model never once applied the rule, so no coordination existed to break",
        )
    if status == "recovered":
        return out("RECOVERED", "the model was holding the rule at the last turn: not derailed")
    if status == "no-calls":
        return out("NO-CALLS", "the derail phase produced no answers at all")

    for name, arm in (("treatment", treatment), ("control", control), ("noise", noise)):
        if arm.attempted == 0:
            return out("NO-ARM", f"{name} arm was never run - a verdict needs all three")
        if arm.coverage is not None and arm.coverage < MIN_COVERAGE:
            return out("BLIND", f"{name} coverage {arm.coverage:.0%} < {MIN_COVERAGE:.0%}")
        if arm.graded < MIN_GRADED:
            return out("UNDERPOWERED", f"{name} graded {arm.graded} < {MIN_GRADED}")

    dc = treatment.rate - control.rate
    cc = newcombe(treatment.successes, treatment.graded, control.successes, control.graded)
    dn = treatment.rate - noise.rate
    cn = newcombe(treatment.successes, treatment.graded, noise.successes, noise.graded)

    if cc[0] > 0 and cn[0] > 0:
        return out("CARRIED", "above BOTH controls; the instruction did the work", dc, cc, dn, cn)
    if cc[0] > 0:
        return out(
            "TOKEN-STATISTICS",
            "above clean context but NOT above the same context with the instruction removed",
            dc, cc, dn, cn,
        )
    if cc[1] < 0:
        return out("REVERSED", "treatment BELOW clean control, interval clears zero", dc, cc, dn, cn)
    return out("NO-DIFFERENCE", "interval spans zero: this run cannot separate the arms", dc, cc, dn, cn)


def collect(findings_by_arm: dict[str, list], families: dict[str, str]) -> dict[str, Arm]:
    """Fold a list of (probe_key, Finding) into one Arm per family."""
    arms: dict[str, Arm] = {}
    for probe_key, finding in findings_by_arm:
        fam = families[probe_key]
        arm = arms.setdefault(fam, Arm(0, 0, 0.0))
        arm.attempted += 1
        if finding.value is not None:
            arm.graded += 1
            arm.successes += finding.value
    return arms


def render(verdicts: list[FamilyVerdict], header: dict) -> str:
    lines = [
        f"model     : {header['model']} via {header['provider']}",
        f"rule      : {header['rule']}  seed word: {header['seed_word']}",
        f"derail    : {header['derail_summary']}",
        f"repetition: {header['reps']}  temperature: {header['temperature']}  seed: {header['seed']}",
        "",
        f"{'family':<12} {'treatment':>14} {'control':>14} {'noise':>14}"
        f" {'vs ctrl':>19} {'vs noise':>19}  verdict",
    ]

    def cell(a):
        return f"{a.rate:.2f} ({a.graded}/{a.attempted})" if a.rate is not None else f"na (0/{a.attempted})"

    def comp(d, ci):
        if d is None or ci is None:
            return "na"
        return f"{d:+.2f} [{ci[0]:+.2f},{ci[1]:+.2f}]"

    for v in verdicts:
        lines.append(
            f"{v.family:<12} {cell(v.treatment):>14} {cell(v.control):>14} {cell(v.noise):>14}"
            f" {comp(v.delta_control, v.ci_control):>19} {comp(v.delta_noise, v.ci_noise):>19}"
            f"  {v.verdict}"
        )
    lines.append("")
    for v in verdicts:
        lines.append(f"  {v.family}: {v.note}")
    return "\n".join(lines)
