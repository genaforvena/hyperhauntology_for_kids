import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cryptohaunt.preflight import assess


ROOT = Path(__file__).resolve().parents[1]


class TestPreflight(unittest.TestCase):
    def test_closed_manifest_is_reported_blocked_without_being_ready(self):
        manifest = json.loads((ROOT / "protocol/design-manifest.json").read_text())

        result = assess(ROOT, manifest)

        self.assertEqual(result["status"], "BLOCKED_EXTERNAL")
        self.assertFalse(result["ready"])
        self.assertFalse(result["authorization_open"])
        self.assertTrue(result["provider_exclusive_required"])
        self.assertTrue(result["static_checks_pass"])

    def test_open_manifest_fails_closed(self):
        manifest = json.loads((ROOT / "protocol/design-manifest.json").read_text())
        manifest["safety_boundary"]["live_model_campaign_authorized"] = True

        result = assess(ROOT, manifest)

        self.assertEqual(result["status"], "REFUSED_UNSAFE_MANIFEST")
        self.assertFalse(result["ready"])
        self.assertFalse(result["static_checks_pass"])


if __name__ == "__main__":
    unittest.main()
