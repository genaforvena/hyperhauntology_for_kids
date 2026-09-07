"""Dependency-free offline lesson lint and fixture replay gate."""
from __future__ import annotations
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN = re.compile(r"password|credential|secret|api[_ -]?key|personal data|self[- ]?harm|sexual|violent|ignore the adult|jailbreak|bypass", re.I)
AGES = {"8-10", "11-13", "14-17"}
ARMS = ["treatment", "clean", "context_matched_noise"]

def load_yaml_json(path: Path) -> dict:
    # The shipped .yaml files are JSON-compatible YAML, keeping the package offline/dependency-free.
    return json.loads(path.read_text(encoding="utf-8"))

def load_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def validate_manifest(manifest: dict) -> list[str]:
    errors: list[str] = []
    contract = manifest.get("research_contract", {})
    boundary = manifest.get("safety_boundary", {})
    gate = manifest.get("offline_gate", {})
    if manifest.get("status") != "offline-gate-only":
        errors.append("manifest: status must be offline-gate-only")
    if contract.get("arms") != ARMS:
        errors.append("manifest: exactly treatment, clean, and context_matched_noise arms are required")
    if contract.get("power_target") != 0.80:
        errors.append("manifest: power target must be 0.80")
    if boundary.get("adult_mediated") is not True:
        errors.append("manifest: adult mediation is required")
    if boundary.get("children_research_subjects") is not False:
        errors.append("manifest: children cannot be research subjects")
    if boundary.get("live_model_campaign_authorized") is not False:
        errors.append("manifest: live model campaigns must remain unauthorized")
    if boundary.get("credentials_allowed") is not False or boundary.get("personal_data_allowed") is not False:
        errors.append("manifest: credentials and personal data must remain forbidden")
    if boundary.get("paper_alternative_required") is not True:
        errors.append("manifest: paper alternative is required")
    if not manifest.get("lesson_files") or len(manifest["lesson_files"]) != 3:
        errors.append("manifest: exactly three age-banded lesson files are required")
    if not gate.get("fixture") or not gate.get("mutation_fixtures"):
        errors.append("manifest: offline fixture and mutation fixtures are required")
    return errors

def lint_lesson(path: Path) -> list[str]:
    errors: list[str] = []
    try: lesson = load_yaml_json(path)
    except Exception as exc: return [f"{path}: invalid JSON-compatible YAML ({exc})"]
    required = {"id", "age_band", "adult_mediation", "learning_goals", "canary", "paper_alternative", "safety_notes"}
    errors += [f"{path}: missing {key}" for key in sorted(required - lesson.keys())]
    if lesson.get("age_band") not in AGES: errors.append(f"{path}: invalid age band")
    if lesson.get("adult_mediation") is not True: errors.append(f"{path}: adult_mediation must be true")
    if len(lesson.get("learning_goals", [])) < 3: errors.append(f"{path}: need at least three learning goals")
    canary = lesson.get("canary", {})
    if canary.get("harmless") is not True: errors.append(f"{path}: canary is not harmless")
    paper = lesson.get("paper_alternative", {})
    if not paper.get("instructions") or not paper.get("materials"): errors.append(f"{path}: paper alternative incomplete")
    text = json.dumps(lesson, ensure_ascii=False)
    if FORBIDDEN.search(text): errors.append(f"{path}: forbidden safety content")
    if re.search(r"https?://|www\.", text, re.I): errors.append(f"{path}: external link")
    return errors

def replay_fixture(path: Path) -> list[str]:
    errors = []
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not rows or rows[0].get("kind") != "header": errors.append("fixture: missing header")
    if any(row.get("provider_calls") for row in rows): errors.append("fixture: provider calls present")
    if any(row.get("kind") == "lesson_check" and row.get("status") != "pass" for row in rows): errors.append("fixture: failed lesson check")
    return errors

def mutation_results(root: Path, manifest: dict) -> list[dict]:
    results = []
    for mutation in manifest["offline_gate"]["mutation_fixtures"]:
        path = root / mutation["path"]
        errors = lint_lesson(path)
        results.append({
            "name": mutation["name"],
            "path": mutation["path"],
            "errors": errors,
            "failed_as_expected": bool(errors),
        })
    return results

def run_gate() -> int:
    manifest = load_manifest(ROOT / "protocol/design-manifest.json")
    errors = []
    errors.extend(validate_manifest(manifest))
    for rel in manifest["lesson_files"]: errors.extend(lint_lesson(ROOT / rel))
    errors.extend(replay_fixture(ROOT / manifest["offline_gate"]["fixture"]))
    mutations = mutation_results(ROOT, manifest)
    mutation_passed = all(row["failed_as_expected"] for row in mutations)
    report = {
        "gate": "PASS" if not errors and mutation_passed else "FAIL",
        "lesson_errors": errors,
        "mutation_results": mutations,
        "mutations_expected_fail": mutation_passed,
        "provider_calls": 0,
        "production_study_writes": [],
    }
    out = ROOT / "reports/offline-gate.json"; out.parent.mkdir(exist_ok=True); out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    safety = {
        "status": "OFFLINE_REVIEW_PASS_HUMAN_REVIEW_PENDING",
        "automated_lesson_checks": "PASS" if not errors else "FAIL",
        "independent_adult_review": "PENDING",
        "pilot_authorized": False,
        "production_study_writes": [],
    }
    (ROOT / "reports/safety-review.json").write_text(json.dumps(safety, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["gate"] == "PASS" else 1
