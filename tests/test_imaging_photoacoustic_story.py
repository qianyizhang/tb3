"""Protect MRI output, reference boundaries and source pinning."""

import copy
import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tb3_medical import explanation_stories as stories

ROOT = Path(__file__).resolve().parents[1]
STORY = Path("presentation/external-tasks/stories/imaging101-photoacoustic-tomography.story.md")
SOURCE = Path("presentation/task-explorer/imaging101-photoacoustic-tomography")
PACK = "retained-imaging101-photoacoustic-tomography-source-v1"


class ImagingPhotoacousticStoryTests(unittest.TestCase):
    def test_compilation_preserves_empty_measurement_and_result_fields(self):
        plan = stories.compile_story(ROOT, STORY)
        self.assertEqual(plan["source_class"], "source-derived-teaching")
        self.assertEqual(plan["reference_policy"], "reader-reference-reveal")
        self.assertEqual(
            [b["channels"]["progress"][0] for b in plan["beats"] if b["scene"] == "operation"],
            [0, 0.5, 1],
        )
        self.assertIn("Official Imaging101", plan["beats"][0]["caption"])
        output = json.loads((ROOT / SOURCE / "output.json").read_text())
        fixture = json.loads((ROOT / SOURCE / "fixture.json").read_text())
        self.assertIsNone(fixture["actual_output"])
        self.assertIsNone(fixture["clean_reference"])
        for key in ["reconstruction_npy", "actual_image", "quality_score"]:
            self.assertIsNone(output[key])
        self.assertIsNone(fixture["clean_reference"])
        reference = json.loads((ROOT / SOURCE / "reference.json").read_text())
        self.assertIsNone(reference["clean_image"])
        self.assertEqual(fixture["branches"], [0, 1, 2])
        source = json.loads((ROOT / SOURCE / "source.json").read_text())
        self.assertEqual(source["source_condition"]["positive_truth_pixels"], 101)
        self.assertEqual(
            source["source_condition"]["available_truth_keys"],
            ["ground_truth_image", "image_x", "image_y"],
        )

    def test_native_units_geometry_and_crop_denominators_are_explicit(self):
        source = json.loads((ROOT / SOURCE / "source.json").read_text())
        condition = source["source_condition"]
        self.assertEqual(condition["measurement_cells"], 1301 * 31 * 31)
        self.assertEqual(condition["crop_pixels"], 33 * 33)
        self.assertEqual(condition["full_pixels"], 41 * 41)
        self.assertIsNone(condition["fluence"])
        self.assertIsNone(condition["pressure_calibration"])
        self.assertFalse(condition["noise_added"])
        self.assertEqual(len(source["native_profiles"]["values"][0]), 1301)
        self.assertFalse(source["native_profiles"]["projection_or_reconstruction_executed"])

    def test_ready_transition_requires_canonical_basis_and_structured_attempts(self):
        from tb3_medical.explainer_queue import _ready_transition

        receipt = "presentation/external-tasks/sources/imaging101-photoacoustic-tomography-resolution.json"
        row = {
            "dependency_resolution_history": [
                {
                    "state": "needs-resolution",
                    "category": "contract-audit",
                    "attempt_status": "retained-audit-verified",
                    "next_action": "main visual review",
                }
            ],
            "illustration_basis": "mixed",
            "actual_data_gap": "No participant outcome/calibration",
            "acquisition_route": "https://huggingface.co/datasets/starpacker52/imaging-101",
            "warning_text": "Synthetic source, no participant outcome",
            "source_resolution_receipt": receipt,
            "source_review": {
                "receipt": receipt,
                "receipt_sha256": hashlib.sha256((ROOT / receipt).read_bytes()).hexdigest(),
            },
        }
        _ready_transition(ROOT, row, "imaging101-photoacoustic-tomography")
        wrong = copy.deepcopy(row)
        wrong["illustration_basis"] = "source-derived-teaching"
        with self.assertRaisesRegex(ValueError, "Invalid illustration basis"):
            _ready_transition(ROOT, wrong, "imaging101-photoacoustic-tomography")
        with tempfile.TemporaryDirectory() as tmp:
            local = Path(tmp)
            rp = local / receipt
            rp.parent.mkdir(parents=True)
            doc = json.loads((ROOT / receipt).read_text())
            doc["attempts"] = []
            rp.write_text(json.dumps(doc))
            wrong = copy.deepcopy(row)
            wrong["source_review"]["receipt_sha256"] = hashlib.sha256(rp.read_bytes()).hexdigest()
            with self.assertRaisesRegex(ValueError, "needs attempts"):
                _ready_transition(local, wrong, "imaging101-photoacoustic-tomography")

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
                    "presentation/external-tasks/sources/imaging101-photoacoustic-tomography-resolution.json"
                ),
                Path("presentation/external-tasks/briefs/imaging101-photoacoustic-tomography.md"),
            ]:
                (root / rel).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / rel, root / rel)
            stories.resolve_assets(root, PACK)
            mp = root / SOURCE / "manifest.json"
            original = json.loads(mp.read_text())
            changed = copy.deepcopy(original)
            next(a for a in changed["assets"] if a["file"] == "signals.png")["role"] = (
                "illustration"
            )
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
                / "presentation/external-tasks/sources/imaging101-photoacoustic-tomography-resolution.json"
            )
            receipt.write_text(receipt.read_text() + "\n")
            with self.assertRaisesRegex(ValueError, "Stale symbolic source pin"):
                stories.resolve_assets(root, PACK)


if __name__ == "__main__":
    unittest.main()
