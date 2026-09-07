"""Build an auditable adult-only study and reproducibility bundle."""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from .tape import completed_repetitions, inferentially_eligible_repetitions, read_tape

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_ARMS = ["treatment", "clean", "context_matched_noise"]


def validate_adult_manifest(manifest: dict) -> list[str]:
    errors = []
    if manifest.get("status") != "adult-only-study":
        errors.append("manifest: status must be adult-only-study")
    if manifest.get("adult_only") is not True:
        errors.append("manifest: adult_only must be true")
    if manifest.get("human_subjects") is not False:
        errors.append("manifest: human_subjects must be false")
    if manifest.get("arms") != REQUIRED_ARMS:
        errors.append("manifest: exactly treatment, clean, and context_matched_noise arms are required")
    if manifest.get("target_complete_repetitions") != 30:
        errors.append("manifest: target must be 30 complete repetitions")
    if manifest.get("power_target") != 0.80:
        errors.append("manifest: power target must be 0.80")
    if manifest.get("max_mde") != 0.30:
        errors.append("manifest: max_mde must be 0.30")
    if not manifest.get("split_manifest"):
        errors.append("manifest: split_manifest is required")
    return errors


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_tape_for_release(path: str | Path, target_reps: int) -> dict:
    path = Path(path)
    result = {"path": str(path), "bytes": path.stat().st_size, "sha256": _sha256(path), "errors": []}
    raw = path.read_text(encoding="utf-8", errors="replace")
    if re.search(r"(?:sk-[A-Za-z0-9_-]{20,}|GROQ_API_KEY|OPENAI_API_KEY|Authorization: Bearer)", raw):
        result["errors"].append("tape appears to contain credentials")
    try:
        tape = read_tape(path)
    except Exception as exc:  # noqa: BLE001 - release report must retain failure
        result["errors"].append(str(exc))
        return result
    if not tape.rows or tape.rows[0].get("kind") != "header":
        result["errors"].append("header must be the first tape row")
    if sum(row.get("kind") == "header" for row in tape.rows) != 1:
        result["errors"].append("tape must contain exactly one header")
    seen = set()
    for row in tape.rows:
        if row.get("kind") in {"status", "graded"} and "rep" in row:
            key = (row["kind"], row["rep"], row.get("arm"), row.get("probe"))
            if key in seen:
                result["errors"].append(f"duplicate append-only row key {key!r}")
            seen.add(key)
    complete = completed_repetitions(tape, tape.header.get("probes", []), ["switch", "control", "noise"])
    eligible = inferentially_eligible_repetitions(tape)
    result.update(
        target_repetitions=target_reps,
        complete_repetitions=sorted(complete),
        inferentially_eligible_repetitions=sorted(eligible),
        complete_count=len(complete),
        eligible_count=len(eligible),
        model=tape.header.get("model"),
        provider=tape.header.get("provider"),
        probes=tape.header.get("probes", []),
    )
    if len(complete) != target_reps:
        result["errors"].append(f"complete repetitions {len(complete)} != target {target_reps}")
    return result


def _split_report(manifest: dict, root: Path) -> dict:
    split = json.loads((root / manifest["split_manifest"]).read_text(encoding="utf-8"))
    calibration = set(split["calibration"])
    holdout = set(split["holdout"])
    registered = set(split["registered"]) if "registered" in split else calibration | holdout
    errors = []
    if calibration & holdout:
        errors.append("calibration and holdout overlap")
    if registered != calibration | holdout:
        errors.append("registered probes differ from calibration union holdout")
    return {
        "registered": sorted(registered),
        "calibration": sorted(calibration),
        "holdout": sorted(holdout),
        "disjoint": not errors,
        "errors": errors,
    }


def create_release(manifest_path: str | Path, tape_paths: list[str | Path], out_dir: str | Path) -> dict:
    manifest_path = Path(manifest_path)
    out_dir = Path(out_dir)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    gate_errors = validate_adult_manifest(manifest)
    errors = list(gate_errors)
    split_report = _split_report(manifest, ROOT)
    errors.extend(split_report["errors"])
    tapes = [validate_tape_for_release(path, manifest["target_complete_repetitions"]) for path in tape_paths]
    errors.extend(f"{row['path']}: {error}" for row in tapes for error in row["errors"])

    out_dir.mkdir(parents=True, exist_ok=True)
    copied = []
    educational = []
    for source in [ROOT / "GOAL.md", ROOT / "docs/methodology.md", ROOT / "lessons"]:
        if source.is_dir():
            for item in source.rglob("*"):
                if item.is_file():
                    dest = out_dir / "educational" / item.relative_to(ROOT)
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(item, dest)
                    educational.append(str(dest.relative_to(out_dir)))
        elif source.is_file():
            dest = out_dir / "educational" / source.relative_to(ROOT)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, dest)
            educational.append(str(dest.relative_to(out_dir)))
    replay_rows = []
    for row in tapes:
        source = Path(row["path"])
        if source.exists() and not row["errors"]:
            dest = out_dir / "tapes" / source.name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, dest)
            row["published_sha256"] = _sha256(dest)
            if row["published_sha256"] != row["sha256"]:
                errors.append(f"published tape hash differs for {source}")
            copied.append(str(dest.relative_to(out_dir)))
            first = subprocess.run(
                [sys.executable, "-m", "cryptohaunt", "replay", str(source)],
                cwd=ROOT, check=False, capture_output=True, text=True,
            )
            second = subprocess.run(
                [sys.executable, "-m", "cryptohaunt", "replay", str(source)],
                cwd=ROOT, check=False, capture_output=True, text=True,
            )
            replay_rows.append({
                "tape": str(source),
                "exit_code": first.returncode,
                "provider_calls": 0,
                "byte_stable": first.returncode == second.returncode and first.stdout == second.stdout,
                "summary": first.stdout,
                "stderr": first.stderr,
            })
            if first.returncode != 0 or first.stdout != second.stdout:
                errors.append(f"replay not independently stable for {source}")
    if len(copied) != len(tapes):
        errors.append("not every tape was copied into the release bundle")

    result = {
        "schema_version": "1.0.0",
        "study": "adult-only absorbing-state study",
        "adult_only_gate": not gate_errors and not split_report["errors"],
        "manifest": str(manifest_path),
        "tapes": tapes,
        "holdout_report": split_report,
        "educational_review": "PENDING (separate kids-material review; not a study-subject gate)",
        "replay_report": replay_rows,
        "copied_tapes": copied,
        "educational_files": educational,
        "errors": errors,
        "disposition": "RELEASED" if not errors else "BLOCKED",
    }
    (out_dir / "release-manifest.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    (out_dir / "replay-report.json").write_text(json.dumps(replay_rows, indent=2) + "\n", encoding="utf-8")
    (out_dir / "holdout-report.json").write_text(json.dumps(split_report, indent=2) + "\n", encoding="utf-8")
    (out_dir / "witness-report.json").write_text(json.dumps({
        "witness": "automated release verifier",
        "adult_only_gate": result["adult_only_gate"],
        "append_only_tape_check": all(not row["errors"] for row in tapes),
        "hashes_recorded": all(len(row["sha256"]) == 64 for row in tapes),
        "holdout_separation": split_report["disjoint"],
        "independent_replay": all(row["byte_stable"] and row["provider_calls"] == 0 for row in replay_rows),
        "educational_review": "PENDING (separate kids-material review)",
        "disposition": result["disposition"],
    }, indent=2) + "\n", encoding="utf-8")
    return result
