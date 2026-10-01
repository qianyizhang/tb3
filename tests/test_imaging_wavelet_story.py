"""Protect MRI output, reference boundaries and source pinning."""

import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tb3_medical import explanation_stories as stories

ROOT = Path(__file__).resolve().parents[1]
STORY = Path("presentation/external-tasks/stories/imaging101-mri-l1-wavelet.story.md")
SOURCE = Path("presentation/task-explorer/imaging101-mri-l1-wavelet")
PACK = "retained-imaging101-wavelet-source-v1"


class ImagingWaveletStoryTests(unittest.TestCase):
    def test_compilation_preserves_empty_measurement_and_result_fields(self):
        plan = stories.compile_story(ROOT, STORY)
        self.assertEqual(plan["source_class"], "source-derived-teaching")
        self.assertEqual(plan["reference_policy"], "reader-reference-reveal")
        self.assertEqual(
            [b["channels"]["progress"][0] for b in plan["beats"] if b["scene"] == "operation"],
            [0, 0.5, 1],
        )
        self.assertIn("Official Imaging101 MRI", plan["beats"][0]["caption"])
        output = json.loads((ROOT / SOURCE / "output.json").read_text())
        fixture = json.loads((ROOT / SOURCE / "fixture.json").read_text())
        self.assertIsNone(fixture["actual_output"])
        self.assertIsNone(fixture["clean_reference"])
        for key in ["reconstruction_npy", "actual_image", "quality_score"]:
            self.assertIsNone(output[key])
        self.assertIsNone(fixture["clean_reference"])
        reference = json.loads((ROOT / SOURCE / "reference.json").read_text())
        self.assertIsNone(reference["clean_image"])
        self.assertEqual(fixture["toy_shrunk"], [2.4, 3.2])
        source = json.loads((ROOT / SOURCE / "source.json").read_text())
        self.assertEqual(sum(source["native_mask"]), 80)
        self.assertEqual(source["source_condition"]["available_truth_keys"], ["mvue"])
        self.assertEqual(source["source_condition"]["loader_key"], "phantom")

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

    def test_released_mask_geometry_is_not_readme_or_clean_reference(self):
        source = json.loads((ROOT / SOURCE / "source.json").read_text())
        self.assertEqual(len(source["native_mask"]), 320)
        self.assertEqual(sum(source["native_mask"]), 80)
        self.assertEqual(source["source_condition"]["available_truth_keys"], ["mvue"])
        self.assertEqual(source["source_condition"]["loader_key"], "phantom")
        self.assertIsNone(json.loads((ROOT / SOURCE / "reference.json").read_text())["clean_image"])

    def test_late_reader_policy_never_creates_a_participant_output(self):
        plan = stories.compile_story(ROOT, STORY)
        self.assertEqual(plan["reference_policy"], "reader-reference-reveal")
        self.assertTrue(
            all(
                b["channels"]["reference"] == [0.0, 0.0]
                for b in plan["beats"]
                if b["scene"] != "reference"
            )
        )
        output = json.loads((ROOT / SOURCE / "output.json").read_text())
        self.assertTrue(all(value is None for value in output.values()))

    def test_symbolic_assets_cannot_be_relabelled_or_unpinned(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            shutil.copytree(ROOT / SOURCE, root / SOURCE)
            for rel in [
                Path("presentation/assets/teaching-prefabs.json"),
                Path(
                    "presentation/external-tasks/sources/imaging101-mri-l1-wavelet-resolution.json"
                ),
                Path("presentation/external-tasks/briefs/imaging101-mri-l1-wavelet.md"),
            ]:
                (root / rel).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / rel, root / rel)
            stories.resolve_assets(root, PACK)
            mp = root / SOURCE / "manifest.json"
            original = json.loads(mp.read_text())
            changed = copy.deepcopy(original)
            next(a for a in changed["assets"] if a["file"] == "coil-0.png")["role"] = "illustration"
            mp.write_text(json.dumps(changed))
            with self.assertRaisesRegex(ValueError, "incorrectly classified"):
                stories.resolve_assets(root, PACK)
            changed = copy.deepcopy(original)
            next(a for a in changed["assets"] if a["file"] == "reference.json")["role"] = (
                "illustration"
            )
            mp.write_text(json.dumps(changed))
            with self.assertRaisesRegex(ValueError, "incorrectly classified"):
                stories.resolve_assets(root, PACK)
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
                / "presentation/external-tasks/sources/imaging101-mri-l1-wavelet-resolution.json"
            )
            receipt.write_text(receipt.read_text() + "\n")
            with self.assertRaisesRegex(ValueError, "Stale symbolic source pin"):
                stories.resolve_assets(root, PACK)


if __name__ == "__main__":
    unittest.main()
