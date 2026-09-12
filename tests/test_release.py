import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import cryptohaunt.release as release
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

    def test_release_blocks_unreviewed_lessons_before_copying_them(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temp_dir:
            out_dir = Path(temp_dir) / "release"
            stale_lesson = out_dir / "educational/lessons/ages-8-10.yaml"
            stale_lesson.parent.mkdir(parents=True)
            stale_lesson.write_text("stale published lesson")
            result = release.create_release(
                root / "protocol/adult-study-manifest.json",
                [root / "runs/adult-study-gemma4-e2b-zy-30.jsonl"],
                out_dir,
            )

            self.assertEqual(result["disposition"], "BLOCKED")
            self.assertEqual(result["educational_review"]["status"], "PENDING")
            self.assertEqual(result["educational_review"]["completed_reviews"], 0)
            self.assertFalse(any(path.startswith("educational/lessons/") for path in result["educational_files"]))
            self.assertFalse((out_dir / "educational/lessons").exists())
            self.assertTrue(result["adult_only_gate"])

    def test_educational_review_requires_two_distinct_adult_independent_approvals(self):
        digest = release.lesson_materials_sha256(release.ROOT / "lessons")
        signoffs = {
            "schema_version": "1.0.0",
            "materials_version": "kids-v1",
            "materials_sha256": digest,
            "reviewers": [
                {"reviewer_id": "adult-1", "adult_attested": True, "independent": True,
                 "decision": "APPROVE", "materials_sha256": digest},
                {"reviewer_id": "adult-2", "adult_attested": True, "independent": True,
                 "decision": "APPROVE", "materials_sha256": digest},
            ],
            "disagreements": [],
        }
        result = release.evaluate_educational_review(signoffs, release.ROOT / "lessons")
        self.assertEqual(result["status"], "APPROVED")
        self.assertEqual(result["completed_reviews"], 2)

        signoffs["reviewers"][1]["reviewer_id"] = "adult-1"
        result = release.evaluate_educational_review(signoffs, release.ROOT / "lessons")
        self.assertEqual(result["status"], "PENDING")
        self.assertEqual(result["completed_reviews"], 1)

    def test_educational_review_blocks_stale_material_and_unresolved_disagreement(self):
        digest = release.lesson_materials_sha256(release.ROOT / "lessons")
        signoffs = {
            "schema_version": "1.0.0",
            "materials_version": "kids-v1",
            "materials_sha256": "stale",
            "reviewers": [],
            "disagreements": [{"id": "d1", "status": "open", "resolution": ""}],
        }
        result = release.evaluate_educational_review(signoffs, release.ROOT / "lessons")
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("materials hash", " ".join(result["issues"]))
        self.assertIn("unresolved disagreement", " ".join(result["issues"]))


if __name__ == "__main__":
    unittest.main()
