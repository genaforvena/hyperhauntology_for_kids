import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cryptohaunt.offline_pilot import ROOT, run, validate_splits


class TestOfflinePilot(unittest.TestCase):
    def test_registry_split_is_exact_and_disjoint(self):
        split = validate_splits()
        self.assertEqual(set(split["calibration"]) & set(split["holdout"]), set())
        self.assertEqual(set(split["registered"]), set(split["calibration"]) | set(split["holdout"]))

    def test_pilot_is_provider_free_replay_deterministic_and_blocked(self):
        transcript = run()
        self.assertEqual(transcript["provider_calls"], 0)
        self.assertEqual(transcript["production_study_writes"], [])
        self.assertTrue(transcript["holdout_separation"])
        self.assertTrue(transcript["byte_equal"])
        self.assertIn("UNDERPOWERED", transcript["live_summary"])

    def test_pilot_manifests_point_to_artifacts(self):
        manifest = json.loads((ROOT / "protocol/pilot-manifest.json").read_text())
        self.assertEqual(manifest["arms"], ["switch", "control", "noise"])
        self.assertEqual(manifest["provider_calls"], 0)


if __name__ == "__main__":
    unittest.main()
