import json
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cryptohaunt.runner import ConfigError
from cryptohaunt.tape import completed_repetitions, expected_graded_count, read_tape


class TestTapeCompletion(unittest.TestCase):
    def test_only_status_with_all_three_arms_is_complete(self):
        path = Path(self.id().replace(".", "_") + ".jsonl")
        try:
            path.write_text(
                '{"kind":"header","reps":2}\n'
                '{"kind":"status","rep":1,"status":"derailed"}\n'
                '{"kind":"graded","rep":1,"arm":"switch","probe":"p"}\n'
                '{"kind":"graded","rep":1,"arm":"control","probe":"p"}\n'
                '{"kind":"graded","rep":1,"arm":"noise","probe":"p"}\n'
            )
            tape = read_tape(path)
            self.assertEqual(expected_graded_count(["p"], ["switch", "control", "noise"]), 3)
            self.assertEqual(
                completed_repetitions(tape, ["p"], ["switch", "control", "noise"]),
                {1},
            )
        finally:
            path.unlink(missing_ok=True)

    def test_partial_repetition_is_not_complete(self):
        path = Path(self.id().replace(".", "_") + ".jsonl")
        try:
            path.write_text(
                '{"kind":"header","reps":1}\n'
                '{"kind":"status","rep":1,"status":"derailed"}\n'
                '{"kind":"graded","rep":1,"arm":"switch","probe":"p"}\n'
            )
            self.assertEqual(
                completed_repetitions(read_tape(path), ["p"], ["switch", "control", "noise"]),
                set(),
            )
        finally:
            path.unlink(missing_ok=True)


class TestResumeValidation(unittest.TestCase):
    def test_resume_rejects_different_rule(self):
        from cryptohaunt.tape import validate_resume_header

        header = {
            "model": "m",
            "provider": "ollama",
            "rule": "zy",
            "seed_word": "x",
            "turns": 10,
            "reps": 2,
            "probes": ["p"],
        }
        args = SimpleNamespace(
            model="m", provider="ollama", rule="o2cyrillic", seed_word="x", turns=10, reps=2
        )
        with self.assertRaisesRegex(ConfigError, "rule"):
            validate_resume_header(header, args, ["p"])

    def test_complete_resume_does_not_call_provider(self):
        from cryptohaunt.runner import run
        from cryptohaunt.probes import DEFAULT_PROBES

        path = Path(self.id().replace(".", "_") + ".jsonl")
        header = {
            "kind": "header",
            "version": "0.1.0",
            "model": "m",
            "provider": "ollama",
            "rule": "zy",
            "seed_word": "mozerov",
            "turns": 2,
            "reps": 1,
            "temperature": 0.7,
            "sampling_seed": 7,
            "probes": [probe.key for probe in DEFAULT_PROBES],
        }
        finding = {"detector": "rule_leak", "value": 0.0, "reason": "clean", "evidence": []}
        try:
            rows = [header, {"kind": "status", "rep": 1, "status": "derailed"}]
            rows.extend(
                {"kind": "graded", "rep": 1, "arm": arm, "probe": probe.key, "family": probe.family, "finding": finding}
                for arm in ("switch", "control", "noise")
                for probe in DEFAULT_PROBES
            )
            path.write_text("".join(json.dumps(row) + "\n" for row in rows))
            args = SimpleNamespace(
                model="m", provider="ollama", rule="zy", seed_word="mozerov", turns=2,
                reps=1, temperature=0.7, seed=7, timeout=1.0, probes=None,
                out=None, resume=str(path), max_mde=0.30, verbose=False,
            )
            with patch("cryptohaunt.runner.derail", side_effect=AssertionError("provider called")):
                output = run(args)
            self.assertIn("UNDERPOWERED", output)
        finally:
            path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
