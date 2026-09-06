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


def validate_resume_header(header: dict, args, probe_keys: list[str]) -> None:
    from .runner import ConfigError

    expected = {
        "model": args.model,
        "provider": args.provider,
        "rule": args.rule,
        "seed_word": args.seed_word,
        "turns": args.turns,
        "reps": args.reps,
        "probes": probe_keys,
    }
    for key, value in expected.items():
        if header.get(key) != value:
            raise ConfigError(
                f"cannot resume: {key} differs (tape={header.get(key)!r}, requested={value!r})"
            )
