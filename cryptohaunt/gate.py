"""Dependency-free offline lesson lint and fixture replay gate."""
from __future__ import annotations
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN = re.compile(r"password|credential|secret|api[_ -]?key|personal data|self[- ]?harm|sexual|violent|ignore the adult|jailbreak|bypass", re.I)
AGES = {"8-10", "11-13", "14-17"}

def load_yaml_json(path: Path) -> dict:
    # The shipped .yaml files are JSON-compatible YAML, keeping the package offline/dependency-free.
    return json.loads(path.read_text(encoding="utf-8"))

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

def run_gate() -> int:
    manifest = json.loads((ROOT / "protocol/design-manifest.json").read_text(encoding="utf-8"))
    errors = []
    for rel in manifest["lesson_files"]: errors.extend(lint_lesson(ROOT / rel))
    errors.extend(replay_fixture(ROOT / manifest["offline_gate"]["fixture"]))
    mutation_errors = lint_lesson(ROOT / manifest["offline_gate"]["mutation_fixture"])
    mutation_passed = bool(mutation_errors)
    report = {"gate": "PASS" if not errors and mutation_passed else "FAIL", "lesson_errors": errors, "mutation_expected_fail": mutation_passed, "provider_calls": 0}
    out = ROOT / "reports/offline-gate.json"; out.parent.mkdir(exist_ok=True); out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["gate"] == "PASS" else 1
