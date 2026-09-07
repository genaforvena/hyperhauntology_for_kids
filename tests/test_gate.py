import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cryptohaunt.gate import lint_lesson, load_manifest, mutation_results, validate_manifest


ROOT = Path(__file__).resolve().parents[1]


class TestLessonGate(unittest.TestCase):
    def test_frozen_manifest_has_three_arms_and_offline_only_boundary(self):
        manifest = load_manifest(ROOT / "protocol/design-manifest.json")
        self.assertEqual(validate_manifest(manifest), [])
        self.assertEqual(manifest["research_contract"]["arms"], ["treatment", "clean", "context_matched_noise"])
        self.assertFalse(manifest["safety_boundary"]["live_model_campaign_authorized"])

    def test_all_age_bands_lint_clean(self):
        manifest = load_manifest(ROOT / "protocol/design-manifest.json")
        for rel in manifest["lesson_files"]:
            with self.subTest(lesson=rel):
                self.assertEqual(lint_lesson(ROOT / rel), [])

    def test_unsafe_and_content_mutations_fail_with_named_reasons(self):
        manifest = load_manifest(ROOT / "protocol/design-manifest.json")
        results = mutation_results(ROOT, manifest)
        self.assertEqual({row["name"] for row in results}, {"unsafe_content", "missing_paper_path"})
        self.assertTrue(all(row["failed_as_expected"] for row in results))
        self.assertTrue(any("forbidden safety content" in e for e in results[0]["errors"]))
        self.assertTrue(any("paper alternative incomplete" in e for e in results[1]["errors"]))

    def test_gate_fixture_cannot_smuggle_provider_calls(self):
        rows = [json.loads(line) for line in (ROOT / "fixtures/offline-replay.jsonl").read_text().splitlines()]
        self.assertTrue(all(row.get("provider_calls", 0) == 0 for row in rows))


if __name__ == "__main__":
    unittest.main()
