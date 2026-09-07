"""Build and verify the provider-free pilot artifacts."""
from __future__ import annotations

import json
from pathlib import Path

from .detect import Finding
from .probes import load_probes
from .report import minimum_detectable_effect, reps_needed
from .runner import replay

ROOT = Path(__file__).resolve().parents[1]


def _read(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def validate_splits() -> dict:
    registry = _read("protocol/canary-registry.json")
    split = _read("protocol/split-manifest.json")
    registered = {row["id"] for row in registry["canaries"]}
    calibration = set(split["calibration"])
    holdout = set(split["holdout"])
    if calibration & holdout:
        raise ValueError("calibration and holdout overlap")
    if calibration | holdout != registered:
        raise ValueError("split does not cover the registry exactly")
    return {"registered": sorted(registered), "calibration": sorted(calibration), "holdout": sorted(holdout)}


def _finding(probe) -> Finding:
    if probe.expects == "assent":
        return Finding("assent", 0.0, "synthetic correction", [probe.truth or ""])
    if probe.expects == "declined":
        return Finding("declined", 1.0, "synthetic refusal", ["not a human"])
    return Finding(probe.expects, 0.0, "synthetic clean answer", [])


def build_pilot_tape(path: Path) -> None:
    probes = load_probes(None)
    rows = [{
        "kind": "header", "version": "0.1.0", "schema_version": "1.0.0",
        "model": "offline-synthetic", "provider": "offline", "rule": "zy",
        "seed_word": "mozerov", "turns": 8, "reps": 2, "temperature": 0.0,
        "sampling_seed": 0, "max_mde": 0.30, "probes": [p.key for p in probes],
        "provider_calls": 0, "production_study_writes": []
    }]
    for rep in (1, 2):
        rows.append({"kind": "status", "rep": rep, "status": "derailed", "obeyed": [True, False], "first_break_turn": 2})
        for arm in ("switch", "control", "noise"):
            for probe in probes:
                rows.append({
                    "kind": "graded", "rep": rep, "arm": arm, "probe": probe.key,
                    "family": probe.family, "question": probe.question, "answer": "synthetic",
                    "finding": _finding(probe).as_dict(), "provider_calls": 0
                })
    path.write_text("\n".join(json.dumps(row, sort_keys=True) for row in rows) + "\n", encoding="utf-8")


def power_worksheet() -> dict:
    return {
        "method": "seeded Newcombe simulation",
        "target_effect": 0.30,
        "target_power": 0.80,
        "rows": [{
            "assumed_clean_rate": baseline,
            "probes_per_family": 2,
            "repetitions_needed": reps_needed(2, baseline, 0.30),
            "mde_at_2_repetitions": minimum_detectable_effect(4, 4, baseline),
        } for baseline in (0.0, 0.1, 0.3, 0.5)]
    }


def run() -> dict:
    split = validate_splits()
    manifest = _read("protocol/pilot-manifest.json")
    tape = ROOT / manifest["tape"]
    build_pilot_tape(tape)
    live = replay(str(tape))
    replay_again = replay(str(tape))
    if live != replay_again:
        raise AssertionError("replay is not deterministic")
    transcript = {
        "schema_version": "1.0.0", "tape": manifest["tape"], "provider_calls": 0,
        "production_study_writes": [], "split": split,
        "holdout_separation": not (set(split["calibration"]) & set(split["holdout"])),
        "live_summary": live, "replay_summary": replay_again, "byte_equal": live == replay_again,
        "verdict_expectation": "UNDERPOWERED"
    }
    (ROOT / manifest["transcript"]).write_text(json.dumps(transcript, indent=2) + "\n", encoding="utf-8")
    (ROOT / manifest["power_worksheet"]).write_text(json.dumps(power_worksheet(), indent=2) + "\n", encoding="utf-8")
    return transcript
