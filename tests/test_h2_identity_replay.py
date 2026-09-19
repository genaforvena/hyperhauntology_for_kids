import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cryptohaunt.runner import replay


ROOT = Path(__file__).resolve().parents[1]


class TestH2IdentityReplayContract(unittest.TestCase):
    def test_powered_three_arm_fixture_is_not_blind(self):
        report = replay(str(ROOT / "fixtures/h2-identity-replay.jsonl"))
        self.assertIn("identity", report)
        self.assertIn("CARRIED", report)

    def test_below_coverage_fixture_is_blind(self):
        report = replay(str(ROOT / "fixtures/h2-identity-replay-blind.jsonl"))
        self.assertIn("identity", report)
        self.assertIn("BLIND", report)

    def test_fixtures_are_provider_free(self):
        for name in ("h2-identity-replay.jsonl", "h2-identity-replay-blind.jsonl"):
            header = json.loads((ROOT / "fixtures" / name).read_text().splitlines()[0])
            self.assertEqual(header["provider_calls"], 0)


if __name__ == "__main__":
    unittest.main()
