"""JSONL tape parsing and safe repetition accounting."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class TapeData:
    header: dict
    rows: list[dict]


def read_tape(path: str | Path) -> TapeData:
    """Read a tape and require exactly one header record."""
    with open(path, encoding="utf-8") as fh:
        rows = [json.loads(line) for line in fh if line.strip()]
    headers = [row for row in rows if row.get("kind") == "header"]
    if len(headers) != 1:
        from .runner import ConfigError

        raise ConfigError(f"{path} must contain exactly one header")
    return TapeData(headers[0], rows)


def expected_graded_count(probe_keys: list[str], arm_names: list[str]) -> int:
    return len(probe_keys) * len(arm_names)


def completed_repetitions(
    tape: TapeData, probe_keys: list[str], arm_names: list[str]
) -> set[int]:
    """Return reps with a status and every expected arm/probe grade."""
    statuses = {row["rep"] for row in tape.rows if row.get("kind") == "status"}
    expected = {(arm, probe) for arm in arm_names for probe in probe_keys}
    graded: dict[int, set[tuple[str, str]]] = {}
    for row in tape.rows:
        if row.get("kind") == "graded":
            graded.setdefault(row["rep"], set()).add((row["arm"], row["probe"]))
    return {rep for rep in statuses if graded.get(rep, set()) >= expected}


def inferentially_eligible_repetitions(tape: TapeData) -> set[int]:
    """Return complete repetitions whose induction actually established a state.

    The tape retains every completed repetition for audit, but only a completed
    ``derailed`` induction is eligible for the absorbing-state contrasts.
    ``not-established``, ``recovered``, ``mute``, ``truncated``, and failed
    inductions must never become inferential denominator rows.
    """
    complete = completed_repetitions(
        tape,
        tape.header.get("probes", []),
        ["switch", "control", "noise"],
    )
    derailed = {
        row["rep"]
        for row in tape.rows
        if row.get("kind") == "status" and row.get("status") == "derailed"
    }
    return complete & derailed


def validate_resume_header(header: dict, args, probe_keys: list[str]) -> None:
    from .runner import ConfigError
    from .report import DEFAULT_MDE

    expected = {
        "model": args.model,
        "provider": args.provider,
        "rule": args.rule,
        "seed_word": args.seed_word,
        "turns": args.turns,
        "reps": args.reps,
        "probes": probe_keys,
        "max_mde": getattr(args, "max_mde", DEFAULT_MDE),
    }
    for key, value in expected.items():
        tape_value = header.get(key, DEFAULT_MDE) if key == "max_mde" else header.get(key)
        if tape_value != value:
            raise ConfigError(
                f"cannot resume: {key} differs (tape={tape_value!r}, requested={value!r})"
            )
