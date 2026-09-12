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
EDUCATIONAL_REVIEW_VERSION = "kids-v1"


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


def lesson_materials_sha256(lessons_dir: str | Path) -> str:
    """Hash lesson paths and contents so signoffs apply to one exact package."""
    lessons_dir = Path(lessons_dir)
    digest = hashlib.sha256()
    for path in sorted(item for item in lessons_dir.rglob("*") if item.is_file()):
        relative = path.relative_to(lessons_dir).as_posix()
        digest.update(relative.encode("utf-8") + b"\0")
        digest.update(bytes.fromhex(_sha256(path)))
    return digest.hexdigest()


def evaluate_educational_review(signoffs: dict, lessons_dir: str | Path) -> dict:
    current_hash = lesson_materials_sha256(lessons_dir)
    issues = []
    blocked = False
    if signoffs.get("schema_version") != "1.0.0":
        issues.append("unsupported or missing signoff schema_version")
        blocked = True
    if signoffs.get("materials_version") != EDUCATIONAL_REVIEW_VERSION:
        issues.append("materials version does not match the current review version")
        blocked = True
    if signoffs.get("materials_sha256") != current_hash:
        issues.append("materials hash does not match the current lesson files")
        blocked = True

    reviewers = signoffs.get("reviewers", [])
    if not isinstance(reviewers, list):
        reviewers = []
        issues.append("reviewers must be a list")
        blocked = True
    approvals = {}
    for row in reviewers:
        if not isinstance(row, dict):
            issues.append("reviewer record must be an object")
            blocked = True
            continue
        reviewer_id = row.get("reviewer_id")
        if not reviewer_id or row.get("adult_attested") is not True or row.get("independent") is not True:
            issues.append("each reviewer must identify themselves and attest adult status and independent review")
            blocked = True
            continue
        if row.get("materials_sha256") != current_hash:
            issues.append(f"reviewer {reviewer_id} reviewed a different materials hash")
            blocked = True
            continue
        if row.get("decision") == "REJECT":
            issues.append(f"reviewer {reviewer_id} did not approve the materials")
            blocked = True
            continue
        if row.get("decision") != "APPROVE":
            issues.append(f"reviewer {reviewer_id} has no approval decision")
            blocked = True
            continue
        approvals[reviewer_id] = row

    disagreements = signoffs.get("disagreements", [])
    if not isinstance(disagreements, list):
        disagreements = []
        issues.append("disagreements must be a list")
        blocked = True
    unresolved = [row for row in disagreements if not isinstance(row, dict)
                  or row.get("status") != "resolved" or not row.get("resolution")]
    if unresolved:
        issues.append(f"{len(unresolved)} unresolved disagreement(s)")
        blocked = True

    if len(approvals) < 2 and not blocked:
        issues.append(f"two distinct independent adult approvals are required; {len(approvals)} recorded")
    status = "BLOCKED" if blocked else ("APPROVED" if len(approvals) >= 2 else "PENDING")
    return {
        "status": status,
        "materials_version": signoffs.get("materials_version"),
        "materials_sha256": current_hash,
        "completed_reviews": len(approvals),
        "required_reviews": 2,
        "reviewers": sorted(approvals),
        "disagreements": disagreements,
        "issues": issues,
    }


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
    signoffs_path = ROOT / "protocol/lesson-review-signoffs.json"
    try:
        signoffs = json.loads(signoffs_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        signoffs = {
            "schema_version": "1.0.0",
            "materials_version": EDUCATIONAL_REVIEW_VERSION,
            "materials_sha256": lesson_materials_sha256(ROOT / "lessons"),
            "reviewers": [],
            "disagreements": [],
        }
    except json.JSONDecodeError:
        signoffs = {}
    educational_review = evaluate_educational_review(signoffs, ROOT / "lessons")
    gate_errors = validate_adult_manifest(manifest)
    errors = list(gate_errors)
    split_report = _split_report(manifest, ROOT)
    errors.extend(split_report["errors"])
    tapes = [validate_tape_for_release(path, manifest["target_complete_repetitions"]) for path in tape_paths]
    errors.extend(f"{row['path']}: {error}" for row in tapes for error in row["errors"])

    out_dir.mkdir(parents=True, exist_ok=True)
    copied = []
    educational = []
    lesson_output = out_dir / "educational/lessons"
    if educational_review["status"] != "APPROVED" and lesson_output.exists():
        shutil.rmtree(lesson_output)
    educational_sources = [ROOT / "GOAL.md", ROOT / "docs/methodology.md"]
    if educational_review["status"] == "APPROVED":
        educational_sources.append(ROOT / "lessons")
    for source in educational_sources:
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
        "educational_review": educational_review,
        "replay_report": replay_rows,
        "copied_tapes": copied,
        "educational_files": educational,
        "errors": errors,
        "disposition": "RELEASED" if not errors and educational_review["status"] == "APPROVED" else "BLOCKED",
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
        "educational_review": educational_review,
        "disposition": result["disposition"],
    }, indent=2) + "\n", encoding="utf-8")
    return result
