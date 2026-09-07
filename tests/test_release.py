import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cryptohaunt.release import validate_adult_manifest, validate_tape_for_release


class TestAdultRelease(unittest.TestCase):
    def test_adult_manifest_requires_no_child_subjects_and_three_arms(self):
        manifest = {
            "status": "adult-only-study",
            "adult_only": True,
            "human_subjects": False,
            "arms": ["treatment", "clean", "context_matched_noise"],
            "target_complete_repetitions": 30,
            "power_target": 0.80,
            "max_mde": 0.30,
            "split_manifest": "protocol/split-manifest.json",
        }
        self.assertEqual(validate_adult_manifest(manifest), [])

    def test_release_tape_rejects_duplicate_header_and_reports_hash(self):
        path = Path(self.id().replace(".", "_") + ".jsonl")
        try:
            path.write_text(
                '{"kind":"header","reps":0,"probes":[]}\n'
                '{"kind":"header","reps":0,"probes":[]}\n'
            )
            result = validate_tape_for_release(path, target_reps=0)
            self.assertIn("exactly one header", " ".join(result["errors"]))
            self.assertEqual(len(result["sha256"]), 64)
        finally:
            path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
