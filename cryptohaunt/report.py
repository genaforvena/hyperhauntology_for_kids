"""Turning graded answers into a verdict, with the arithmetic written down.

Two rules hold everywhere below:
  - an ungradable answer is dropped from the numerator AND the denominator, and
    the loss is published as coverage rather than absorbed silently;
  - nothing is reported as a level. Every headline number is
    treatment - control, with an interval that has to clear zero.
"""
from __future__ import annotations

import math
import random
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
    mde: float | None = None


MIN_GRADED = 3
MIN_COVERAGE = 0.5
TARGET_POWER = 0.80
DEFAULT_MDE = 0.30  # a null is only reportable down to this effect size


def power_at(n1: int, n2: int, p_control: float, delta: float, trials: int = 1500) -> float:
    """Fraction of simulated runs in which this design's OWN test finds `delta`.

    Simulated rather than derived from a normal approximation, because the test
    actually applied downstream is Newcombe's, the arms here are small, and the
    approximation is worst exactly where we live. Seeded, so the number a report
    prints is the number anyone re-running it gets.
    """
    if n1 == 0 or n2 == 0:
        return 0.0
    p_treat = min(1.0, p_control + delta)
    rng = random.Random(20260830)
    wins = 0
    for _ in range(trials):
        s1 = sum(rng.random() < p_treat for _ in range(n1))
        s2 = sum(rng.random() < p_control for _ in range(n2))
        if newcombe(s1, n1, s2, n2)[0] > 0:
            wins += 1
    return wins / trials


def minimum_detectable_effect(n1: int, n2: int, p_control: float) -> float | None:
    """Smallest delta this design would catch `TARGET_POWER` of the time.

    Returns None when even a delta of 1.0 is out of reach - which is the honest
    answer for the tiny arms this kind of probe usually produces, and is exactly
    the case that must never be reported as "no effect".
    """
    lo, hi = 0.0, 1.0
    if power_at(n1, n2, p_control, hi) < TARGET_POWER:
        return None
    for _ in range(12):
        mid = (lo + hi) / 2
        if power_at(n1, n2, p_control, mid) >= TARGET_POWER:
            hi = mid
        else:
            lo = mid
    return hi


def reps_needed(probes_per_family: int, p_control: float, target: float) -> int | None:
    """How many repetitions would make `target` detectable. None if over 200."""
    for reps in range(1, 201):
        n = probes_per_family * reps
        mde = minimum_detectable_effect(n, n, p_control)
        if mde is not None and mde <= target:
            return reps
    return None


def verdict_for(
    family: str,
    treatment: Arm,
    control: Arm,
    noise: Arm,
    status: str = "derailed",
    max_mde: float = DEFAULT_MDE,
    probes_per_family: int = 0,
) -> FamilyVerdict:
    """Treatment must clear BOTH controls, and each control answers its own question.

      vs control - "does it answer like this anyway, cold?"
      vs noise   - "does a context of the same shape and the same strange tokens
                    do it, with the instruction and the praise taken out?"

    Clearing control but not noise is a real and common outcome, and it gets its
    own word rather than being rounded up into a finding: the context did the
    work, the instruction did not.
    """

    def out(v, note, dc=None, cc=None, dn=None, cn=None, mde=None):
        return FamilyVerdict(family, treatment, control, noise, v, dc, cc, dn, cn, note, mde)

    if status == "not-established":
        return out(
            "NOT-ESTABLISHED",
            "the model never once applied the rule, so no coordination existed to break",
        )
    if status == "recovered":
        return out("RECOVERED", "the model was holding the rule at the last turn: not derailed")
    if status == "no-calls":
        return out("NO-CALLS", "the derail phase produced no answers at all")
    if status == "mute":
        return out(
            "MUTE",
            "over half the derail turns came back empty - a silence, not a derailment",
        )

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

    # Nothing was found. Two very different reasons for that, and only one of
    # them is a result: a design that could not have seen the effect has not
    # measured its absence. The tool refuses to call the second one a null.
    worst = min(treatment.graded, control.graded, noise.graded)
    mde = minimum_detectable_effect(worst, worst, control.rate)
    if mde is None or mde > max_mde:
        need = reps_needed(probes_per_family, control.rate, max_mde) if probes_per_family else None
        target = f"{max_mde:.0%}"
        found = "nothing at all" if mde is None else f"only effects above {mde:.0%}"
        hint = f"; {need} repetitions would reach {target}" if need else ""
        return out(
            "INCONCLUSIVE",
            f"arms of {worst} could detect {found}, short of the {target} this null "
            f"claims to rule out{hint}",
            dc, cc, dn, cn, mde,
        )
    return out(
        "NULL",
        f"no difference, and this design would have caught one of {mde:.0%} or more "
        f"{TARGET_POWER:.0%} of the time",
        dc, cc, dn, cn, mde,
    )


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
        f" {'vs ctrl':>19} {'vs noise':>19} {'MDE':>6}  verdict",
    ]

    def cell(a):
        return f"{a.rate:.2f} ({a.graded}/{a.attempted})" if a.rate is not None else f"na (0/{a.attempted})"

    def comp(d, ci):
        if d is None or ci is None:
            return "na"
        return f"{d:+.2f} [{ci[0]:+.2f},{ci[1]:+.2f}]"

    for v in verdicts:
        mde = f"{v.mde:.0%}" if v.mde is not None else "-"
        lines.append(
            f"{v.family:<12} {cell(v.treatment):>14} {cell(v.control):>14} {cell(v.noise):>14}"
            f" {comp(v.delta_control, v.ci_control):>19} {comp(v.delta_noise, v.ci_noise):>19}"
            f" {mde:>6}  {v.verdict}"
        )
    lines.append("")
    for v in verdicts:
        lines.append(f"  {v.family}: {v.note}")
    return "\n".join(lines)
