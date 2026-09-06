# Resumable Powered Runs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make long three-arm experiments safely resumable from their append-only JSONL tape without changing the scientific grading rules or counting a partial repetition twice.

**Architecture:** A run header records the immutable design, and each repetition becomes complete only after its status and all expected graded probe records are present. `run --resume PATH` validates the header, skips complete repetitions, appends only missing repetitions, and renders the combined evidence; replay uses the same completion rules offline.

**Tech Stack:** Python 3.10+, stdlib `json`, `unittest`, JSONL tapes, argparse.

## Global Constraints

- Keep treatment, clean control, and noise control mandatory; no verdict may be emitted with a missing arm.
- Preserve `None` as ungradable and preserve coverage in every rendered arm.
- Never treat `NOT-ESTABLISHED`, `MUTE`, `TRUNCATED`, or provider failure as a finding.
- Do not add dependencies or network calls to tests.
- Do not re-measure retired H1; this change only protects collection and replay of H2/H4 campaigns.
- Update `README.md` with the user-facing resume command and commit every completed increment.

---

### Task 1: Define tape completion and validation helpers

**Files:**
- Create: `cryptohaunt/tape.py`
- Test: `tests/test_tape.py`

**Interfaces:**
- Produces `expected_graded_count(probe_keys, arm_names) -> int`, `read_tape(path) -> TapeData`, `completed_repetitions(tape, probe_keys, arm_names) -> set[int]`, and `validate_resume_header(header, args, probe_keys) -> None`.

- [x] **Step 1: Write the failing tests**

```python
from cryptohaunt.tape import completed_repetitions, expected_graded_count, read_tape

def test_only_status_with_all_three_arms_is_complete(tmp_path):
    path = tmp_path / "run.jsonl"
    path.write_text(
        '{"kind":"header","reps":2}\n'
        '{"kind":"status","rep":1,"status":"derailed"}\n'
        '{"kind":"graded","rep":1,"arm":"switch","probe":"p"}\n'
        '{"kind":"graded","rep":1,"arm":"control","probe":"p"}\n'
        '{"kind":"graded","rep":1,"arm":"noise","probe":"p"}\n'
    )
    tape = read_tape(path)
    assert expected_graded_count(["p"], ["switch", "control", "noise"]) == 3
    assert completed_repetitions(tape, ["p"], ["switch", "control", "noise"]) == {1}

def test_partial_repetition_is_not_complete(tmp_path):
    path = tmp_path / "partial.jsonl"
    path.write_text(
        '{"kind":"header","reps":1}\n'
        '{"kind":"status","rep":1,"status":"derailed"}\n'
        '{"kind":"graded","rep":1,"arm":"switch","probe":"p"}\n'
    )
    assert completed_repetitions(read_tape(path), ["p"], ["switch", "control", "noise"]) == set()
```

- [x] **Step 2: Run the focused tests and verify they fail**

Run: `python3 -m pytest tests/test_tape.py -q`
Expected: FAIL because `cryptohaunt.tape` does not exist.

- [x] **Step 3: Implement the minimal tape parser and completion calculation**

```python
from dataclasses import dataclass
import json

@dataclass
class TapeData:
    header: dict
    rows: list[dict]

def read_tape(path):
    rows = [json.loads(line) for line in open(path, encoding="utf-8") if line.strip()]
    headers = [row for row in rows if row.get("kind") == "header"]
    if len(headers) != 1:
        raise ValueError(f"{path} must contain exactly one header")
    return TapeData(headers[0], rows)

def expected_graded_count(probe_keys, arm_names):
    return len(probe_keys) * len(arm_names)

def completed_repetitions(tape, probe_keys, arm_names):
    statuses = {row["rep"] for row in tape.rows if row.get("kind") == "status"}
    expected = {(arm, probe) for arm in arm_names for probe in probe_keys}
    graded = {}
    for row in tape.rows:
        if row.get("kind") == "graded":
            graded.setdefault(row["rep"], set()).add((row["arm"], row["probe"]))
    return {rep for rep in statuses if graded.get(rep, set()) >= expected}
```

- [x] **Step 4: Run focused tests and then the baseline suite**

Run: `python3 -m pytest tests/test_tape.py -q && python3 -m unittest discover -q`
Expected: focused tests pass; all tests pass.

- [x] **Step 5: Commit**

```bash
git add cryptohaunt/tape.py tests/test_tape.py
git commit -m "test: define complete experiment repetitions"
```

### Task 2: Add safe resume execution

**Files:**
- Modify: `cryptohaunt/runner.py`
- Modify: `cryptohaunt/cli.py`
- Modify: `tests/test_tape.py`

**Interfaces:**
- `run(args)` accepts `args.resume`; resumed runs append to the existing tape and return a summary over all valid rows.
- Resume rejects mismatched model/provider/rule/seed-word/turns/reps/probe set instead of silently combining experiments.

- [x] **Step 1: Add failing tests for header mismatch and complete-run no-op**

```python
from types import SimpleNamespace
from cryptohaunt.runner import ConfigError
from cryptohaunt.tape import validate_resume_header

def test_resume_rejects_different_rule():
    header = {"model":"m", "provider":"ollama", "rule":"zy", "seed_word":"x", "turns":10, "reps":2, "probes":["p"]}
    args = SimpleNamespace(model="m", provider="ollama", rule="o2cyrillic", seed_word="x", turns=10, reps=2)
    with pytest.raises(ConfigError, match="rule"):
        validate_resume_header(header, args, ["p"])
```

- [x] **Step 2: Run the focused test and verify it fails**

Run: `python3 -m pytest tests/test_tape.py::test_resume_rejects_different_rule -q`
Expected: FAIL because resume validation is not implemented.

- [x] **Step 3: Implement validation and append/skip behavior**

Add `--resume PATH` to the `run` parser. When present, require `--out` to be absent, read the tape, validate immutable header fields, reconstruct prior arm rows/statuses, skip completed reps, and open the file with append mode. Use `next_rep = max(existing reps, default=0) + 1` and run until `args.reps`; never overwrite an existing line. If all requested repetitions are already complete, do no provider calls and render the existing result.

- [x] **Step 4: Run focused and full tests**

Run: `python3 -m pytest tests/test_tape.py -q && python3 -m unittest discover -q`
Expected: PASS with no network calls.

- [x] **Step 5: Commit**

```bash
git add cryptohaunt/runner.py cryptohaunt/cli.py tests/test_tape.py
git commit -m "feat: resume interrupted experiment tapes"
```

### Task 3: Document and verify the long-run workflow

**Files:**
- Modify: `README.md`
- Modify: `GOAL.md`
- Test: `tests/test_tape.py`

**Interfaces:**
- Documents an interrupted run followed by `cryptohaunt run --resume runs/<tape>.jsonl --reps N`.
- Documents that complete repetitions, not lines or calls, determine resume progress.

- [x] **Step 1: Add a documentation regression test**

```python
def test_resume_workflow_is_documented():
    readme = Path("README.md").read_text()
    assert "--resume" in readme
    assert "complete repetition" in readme.lower()
```

- [x] **Step 2: Run it red, update docs, and run it green**

Run: `python3 -m pytest tests/test_tape.py::test_resume_workflow_is_documented -q`
Expected before docs change: FAIL; after docs change: PASS.

- [x] **Step 3: Run all project checks**

Run: `python3 -m unittest discover -v` and `python3 -m cryptohaunt selftest`.
Expected: 43 tests pass, both commands exit 0, and no network is used.

- [ ] **Step 4: Verify offline replay and repository sync**

Run: `git fetch --prune origin && git status --short --branch && python3 -m cryptohaunt replay runs/example-verified.jsonl` after placing a checked-in example tape at that exact path.
Expected: branch is not behind `origin/main`; replay produces a verdict without network access; no unrelated files are modified.

- [ ] **Step 5: Commit**

```bash
git add README.md GOAL.md tests/test_tape.py
git commit -m "docs: publish the resumable powered-run workflow"
```

## Self-review checklist

- The three-arm requirement remains enforced by existing `verdict_for` and is not bypassed by resume.
- Partial rows cannot become a completed repetition because all arm/probe pairs are required.
- Existing tape rows remain append-only and replayable.
- Header mismatches fail before provider calls.
- H1 remains retired; the feature only protects collection for controlled H2/H4 work.

### Task 4: Validate the methodology with extensive local campaigns

**Files:**
- Create: `runs/example-verified.jsonl`
- Modify: `README.md`

**Interfaces:**
- Uses the same three-arm design and replay path for every local model.
- Reports coverage, verdict, MDE, and model/provider configuration; it never promotes an underpowered or blind run to a finding.

- [x] **Step 1: Run a smoke campaign and preserve a checked-in replay fixture**

Run: `python3 -m cryptohaunt run --model tiny-fleet-v1:latest --provider ollama --rule zy --turns 8 --reps 1 --temperature 0.7 --seed 7 --out runs/example-verified.jsonl -v`.
Expected: a JSONL tape with header, status, and all three arms; any `BLIND`, `MUTE`, `TRUNCATED`, or `INCONCLUSIVE` result is retained honestly.

- [x] **Step 2: Replay the fixture offline**

Run: `python3 -m cryptohaunt replay runs/example-verified.jsonl`.
Expected: a verdict summary is produced without contacting Ollama.

- [x] **Step 3: Run powered exploratory campaigns**

Run the same design at `--reps 30` sequentially for each available model, starting with `tiny-fleet-v1:latest` and `tiny-fleet-v2:latest`; larger local models may be deferred if provider loading starves the queue. Report each family separately, with coverage and MDE. Do not pool models or families unless a later analysis plan specifies that estimand.

- [x] **Step 4: Interrupt and resume one campaign**

Stop one powered run after at least one repetition, then run the identical command with `--resume` and the same `--reps 30` target.
Expected: complete repetitions are skipped, a partial repetition is rerun, tape line count only increases, and replay agrees with the live summary.

- [ ] **Step 5: Commit the fixture and methodology record**

```bash
git add runs/example-verified.jsonl README.md
git commit -m "exp: validate controlled methodology on local models"
```
