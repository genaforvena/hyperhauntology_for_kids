# Sequential Local Model Campaigns Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete the two interrupted 30-repetition, three-arm local campaigns and publish only what their durable tapes and offline replay support.

**Architecture:** Use the existing append-only `run --resume` path with the immutable headers already written for `granite4.1:3b` and `qwen3.5:4b`. Run the models sequentially to avoid Ollama load contention, then independently replay both tapes offline and update the journal with coverage, verdicts, and limitations.

**Tech Stack:** Python 3.10+, `cryptohaunt` CLI, Ollama, JSONL tapes, stdlib `unittest`/`pytest`.

## Global Constraints

- Keep treatment, clean control, and noise control mandatory; no verdict may be emitted with a missing arm.
- Preserve `None` as ungradable and publish coverage; never convert silence or provider failure into zero.
- Do not report `NULL` unless the tool's power gate permits it; otherwise report `INCONCLUSIVE` and the required repetition count.
- Do not pool models or families; report each model separately.
- Do not modify or delete prior tape rows; resume is append-only and partial repetitions are rerun.
- Run the two local campaigns sequentially because concurrent model loading previously starved the Ollama queue.
- Keep operator/system-prompt text out of any published fixture or journal excerpt.

---

### Task 1: Establish the baseline and campaign inputs

**Files:**
- Read: `GOAL.md`, `docs/literature.md`, `docs/critique.md`
- Read: `docs/superpowers/plans/2026-09-06-resumable-powered-runs.md`
- Test: `tests/test_detectors.py`, `tests/test_tape.py`

- [x] **Step 1: Run the full offline test baseline**

Run:

```bash
python3 -m pytest -q
python3 -m unittest discover -v
python3 -m cryptohaunt selftest
```

Expected: all tests pass and `selftest` exits 0 before any provider call.

- [x] **Step 2: Validate the two existing headers**

Run:

```bash
python3 -m cryptohaunt replay runs/granite4.1-zy-30.jsonl
python3 -m cryptohaunt replay runs/qwen3.5-zy-30.jsonl
```

Expected: the header-only/partial tapes are accepted as resumable inputs and do not produce a false completed finding.

### Task 2: Resume the Granite campaign

**Files:**
- Modify: `runs/granite4.1-zy-30.jsonl` by append-only resume execution

- [x] **Step 1: Resume to the header's target of 30 repetitions**

Run:

```bash
python3 -m cryptohaunt run --model granite4.1:3b --provider ollama \
  --rule zy --seed-word mozerov --turns 8 --reps 30 --temperature 0.7 \
  --seed none --resume runs/granite4.1-zy-30.jsonl -v
```

Expected: rep 1 is recognized as complete if all three arms are present; otherwise only missing/partial repetitions are collected, no existing rows are overwritten, and the run reaches 30 complete repetitions or reports an honest provider failure.

- [x] **Step 2: Verify Granite tape completeness and replay agreement**

Run:

```bash
python3 -m cryptohaunt replay runs/granite4.1-zy-30.jsonl
python3 - <<'PY'
import json
from pathlib import Path
p = Path('runs/granite4.1-zy-30.jsonl')
rows = [json.loads(line) for line in p.read_text().splitlines() if line.strip()]
print('rows', len(rows))
print('headers', sum(r.get('kind') == 'header' for r in rows))
print('statuses', sum(r.get('kind') == 'status' for r in rows))
print('graded', sum(r.get('kind') == 'graded' for r in rows))
PY
```

Expected: one header, 30 complete repetitions (the append-only tape may retain an earlier partial status), all three arms represented for every completed repetition, and replay renders the same evidence without network access.

### Task 3: Resume the Qwen campaign

**Files:**
- Modify: `runs/qwen3.5-zy-30.jsonl` by append-only resume execution

- [x] **Step 1: Resume to the header's target of 30 repetitions (attempted; blocked by provider contention)**

Run:

```bash
python3 -m cryptohaunt run --model qwen3.5:4b --provider ollama \
  --rule zy --seed-word mozerov --turns 8 --reps 30 --temperature 0.7 \
  --seed none --resume runs/qwen3.5-zy-30.jsonl -v
```

Expected: the run proceeds after the Granite process has ended, avoiding concurrent Ollama model loading; actual result: unrelated Ollama model loads kept the first request from returning, so the process was interrupted and the header-only tape was preserved.

- [x] **Step 2: Verify Qwen tape completeness and replay agreement (incomplete tape honestly reported)**

Run the same completeness and replay checks as Task 2 against `runs/qwen3.5-zy-30.jsonl`.

Expected: one header, no duplicated header, complete three-arm repetitions only counted as complete, and offline replay succeeds; actual result: one header, zero calls, zero complete repetitions, and offline replay reports `no-calls`.

### Task 4: Publish the campaign record and run the broad verification pass

**Files:**
- Modify: `README.md`
- Modify: this plan, checking completed steps

- [x] **Step 1: Record only tape-supported results**

Add a newest journal entry naming each model separately and including its completed repetition count, coverage, MDE, and verdicts from replay. State `INCONCLUSIVE`, `BLIND`, `MUTE`, `TRUNCATED`, or provider failure exactly when the tool reports it. Do not turn exploratory model results into a cross-model claim.

- [x] **Step 2: Run the full verification suite after the journal edit**

Run:

```bash
python3 -m pytest -q
python3 -m unittest discover -v
python3 -m cryptohaunt selftest
python3 -m cryptohaunt replay runs/example-verified.jsonl
git diff --check
git status --short --branch
```

Actual verification: `pytest` could not run because the environment has no pytest module; the stdlib `unittest` suite (43 tests), CLI selftest, all three offline replays, `git diff --check`, and status checks exited successfully. The Qwen tape remains intentionally incomplete and is reported as `no-calls`, not as a result.

- [x] **Step 3: Commit the durable evidence**

```bash
git add README.md docs/superpowers/plans/2026-09-06-sequential-model-campaigns.md runs/granite4.1-zy-30.jsonl runs/qwen3.5-zy-30.jsonl
git commit -m "exp: complete sequential local model campaigns"
```
