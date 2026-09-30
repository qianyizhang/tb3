"""Protect classification output, reference boundaries and source pinning."""

import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tb3_medical import explanation_stories as stories

ROOT = Path(__file__).resolve().parents[1]
STORY = Path(
    "presentation/external-tasks/stories/automedbench-full-chest-xray-pneumonia-cls-task.story.md"
)
SOURCE = Path("presentation/task-explorer/automedbench-full-chest-xray-pneumonia-cls-task")
PACK = "retained-automed-full-pneumonia-source-v1"


class AutomedPneumoniaStoryTests(unittest.TestCase):
    def test_symbolic_compilation_preserves_empty_patient_and_result_fields(self):
        plan = stories.compile_story(ROOT, STORY)
        self.assertEqual(plan["source_class"], "source-derived-teaching")
        self.assertEqual(plan["reference_policy"], "no-reference-assets")
        self.assertEqual(
            [b["channels"]["progress"][0] for b in plan["beats"] if b["scene"] == "operation"],
            [0, 0.5, 1],
        )
        self.assertIn("Official Mendeley acquisition", plan["beats"][0]["caption"])
        output = json.loads((ROOT / SOURCE / "output.json").read_text())
        fixture = json.loads((ROOT / SOURCE / "fixture.json").read_text())
        for key in [
            "participant_prediction",
            "checkpoint",
            "score",
            "private_reference",
            "actual_case_ids",
        ]:
            self.assertIsNone(output[key])
        self.assertIsNone(fixture["actual_prediction"])
        self.assertIsNone(fixture["actual_reference"])
        self.assertTrue(fixture["toy_row_is_not_displayed_native_case"])

    def test_native_example_is_public_training_helper_not_test_reference(self):
        source = json.loads((ROOT / SOURCE / "source.json").read_text())
        self.assertEqual(source["native_example"]["partition"], "train")
        self.assertEqual(source["native_example"]["source_folder_label"], "NORMAL")
        self.assertEqual(source["native_example"]["canonical_helper_label"], "normal")
        self.assertFalse(source["native_example"]["full_archive_SHA256_verified"])
        self.assertEqual(source["native_example"]["width"], 2090)
        self.assertEqual(source["native_example"]["height"], 1858)
        self.assertIn("Private evaluator", source["source_roles"]["reference"])

    def test_reference_outside_reference_scene_and_implicit_cut_are_rejected(self):
        doc = stories.parse_document((ROOT / STORY).read_text())
        data = {**doc.header, "beats": list(doc.beats)}
        changed = copy.deepcopy(data)
        changed["beats"][0]["channels"]["reference"] = [0, 1]
        with self.assertRaisesRegex(ValueError, "limited to the reference scene"):
            stories.ADAPTER.validate_python(changed)
        changed = copy.deepcopy(data)
        del changed["beats"][1]["cut"]
        with self.assertRaisesRegex(ValueError, "explicit cut"):
            stories.ADAPTER.validate_python(changed)

    def test_symbolic_assets_cannot_be_relabelled_or_unpinned(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            shutil.copytree(ROOT / SOURCE, root / SOURCE)
            for rel in [
                Path("presentation/assets/teaching-prefabs.json"),
                Path(
                    "presentation/external-tasks/sources/automedbench-full-chest-xray-pneumonia-cls-task-resolution.json"
                ),
                Path(
                    "presentation/external-tasks/briefs/automedbench-full-chest-xray-pneumonia-cls-task.md"
                ),
            ]:
                (root / rel).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / rel, root / rel)
            stories.resolve_assets(root, PACK)
            mp = root / SOURCE / "manifest.json"
            original = json.loads(mp.read_text())
            changed = copy.deepcopy(original)
            next(a for a in changed["assets"] if a["file"] == "fixture.json")["provenance"] = (
                "source-derived-teaching"
            )
            mp.write_text(json.dumps(changed))
            with self.assertRaisesRegex(ValueError, "incorrectly classified"):
                stories.resolve_assets(root, PACK)
            mp.write_text(json.dumps(original))
            receipt = (
                root
                / "presentation/external-tasks/sources/automedbench-full-chest-xray-pneumonia-cls-task-resolution.json"
            )
            receipt.write_text(receipt.read_text() + "\n")
            with self.assertRaisesRegex(ValueError, "Stale symbolic source pin"):
                stories.resolve_assets(root, PACK)


if __name__ == "__main__":
    unittest.main()
