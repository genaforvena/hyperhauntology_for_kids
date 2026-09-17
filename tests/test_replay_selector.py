import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cryptohaunt.runner import replay


def _tape(path: Path) -> None:
    header = {
        "kind": "header", "model": "tiny", "provider": "offline",
        "rule": "abcase", "seed_word": "Abacus", "turns": 4,
        "reps": 1, "temperature": 0.7, "sampling_seed": 19,
        "max_mde": 0.3, "probes": ["neutral.dough", "identity.human"],
    }
    rows = [header, {"kind": "status", "rep": 1, "status": "derailed"}]
    for arm in ("switch", "control", "noise"):
        for probe, family in (("neutral.dough", "neutral"), ("identity.human", "identity")):
            rows.append({
                "kind": "graded", "rep": 1, "arm": arm, "probe": probe,
                "family": family,
                "finding": {"detector": "x", "value": 0.0, "reason": "fixture", "evidence": []},
            })
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


class TestReplaySelector(unittest.TestCase):
    def test_family_selector_isolates_identity(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "tape.jsonl"
            _tape(path)
            selected = replay(str(path), family="identity")
            self.assertIn("identity", selected)
            self.assertNotIn("neutral", selected)

    def test_probe_selector_isolates_identity_probe(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "tape.jsonl"
            _tape(path)
            selected = replay(str(path), probe="identity.human")
            self.assertIn("identity", selected)
            self.assertNotIn("neutral", selected)

    def test_default_replay_keeps_all_families(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "tape.jsonl"
            _tape(path)
            selected = replay(str(path))
            self.assertIn("neutral", selected)
            self.assertIn("identity", selected)


if __name__ == "__main__":
    unittest.main()
