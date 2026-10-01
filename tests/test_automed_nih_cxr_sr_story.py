"""Protect chest X-ray output, reference boundaries and source pinning."""

import copy
import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tb3_medical import explanation_stories as stories

ROOT = Path(__file__).resolve().parents[1]
STORY = Path("presentation/external-tasks/stories/automedbench-full-nih-cxr-sr-task.story.md")
SOURCE = Path("presentation/task-explorer/automedbench-full-nih-cxr-sr-task")
PACK = "retained-automedbench-full-nih-cxr-sr-task-source-v1"


class AutomedNihCxrSrStoryTests(unittest.TestCase):
    def test_compilation_preserves_empty_measurement_and_result_fields(self):
        plan = stories.compile_story(ROOT, STORY)
        self.assertEqual(plan["source_class"], "source-derived-teaching")
        self.assertEqual(plan["reference_policy"], "reader-reference-reveal")
        self.assertEqual(
            [b["channels"]["progress"][0] for b in plan["beats"] if b["scene"] == "operation"],
            [0, 0.5, 1],
        )
        self.assertIn("Official NIH", plan["beats"][0]["caption"])
        output = json.loads((ROOT / SOURCE / "output.json").read_text())
        fixture = json.loads((ROOT / SOURCE / "fixture.json").read_text())
        self.assertIsNone(fixture["actual_output"])
        self.assertIsNone(fixture["clean_reference"])
        for key in ["enhanced_npy", "actual_image", "quality_score"]:
            self.assertIsNone(output[key])
        self.assertIsNone(fixture["clean_reference"])
        reference = json.loads((ROOT / SOURCE / "reference.json").read_text())
        self.assertIsNone(reference["clean_image"])
        self.assertEqual(fixture["branches"], [0, 1, 2])
        source = json.loads((ROOT / SOURCE / "source.json").read_text())
        self.assertEqual(source["source_condition"]["input_pixels"], 16384)
        self.assertFalse(source["source_condition"]["private_target_available"])

    def test_full_brief_inventory_degradation_private_and_effective_boundaries(self):
        from tb3_medical import task_briefs

        document = task_briefs.load(ROOT)
        self.assertEqual(len(document["entries"]), 205)
        row = next(r for r in document["entries"] if r["id"] == "automedbench-full-nih-cxr-sr-task")
        self.assertEqual(
            [v["name"] for v in row["variants"]],
            ["Full · Lite", "Full · Standard", "Related source listing"],
        )
        source = json.loads((ROOT / SOURCE / "source.json").read_text())
        c = source["source_condition"]
        self.assertEqual(c["output_pixels"], 4 * c["input_pixels"])
        self.assertIsNone(c["bicubic_library"])
        self.assertIsNone(c["coordinate_alignment"])
        self.assertIsNone(c["physical_pixel_spacing"])
        self.assertIsNone(c["n_cases"])
        self.assertFalse(c["private_target_available"])
        self.assertIsNone(source["symbolic_display"]["native_image"])
        self.assertTrue(source["symbolic_display"]["no_resizing_or_model"])
        effective = source["task_contract"]["effective"]
        self.assertIn("absent v2 TASK_NORM", effective)
        self.assertIn("runner consumes TASK environment (default empty)", effective)
        self.assertIn("v3 A/B/C gates rawPSNR+SSIM only", effective)
        self.assertIn("LPIPS notgated", effective)
        self.assertIn("Missing assets/runtime and bands", effective)

    def test_ready_transition_requires_canonical_basis_and_structured_attempts(self):
        from tb3_medical.explainer_queue import _ready_transition

        receipt = (
            "presentation/external-tasks/sources/automedbench-full-nih-cxr-sr-task-resolution.json"
        )
        row = {
            "dependency_resolution_history": [
                {
                    "state": "needs-resolution",
                    "category": "contract-audit",
                    "attempt_status": "retained-audit-verified",
                    "next_action": "main visual review",
                }
            ],
            "illustration_basis": "symbolic",
            "actual_data_gap": "No participant outcome/calibration",
            "acquisition_route": "https://nihcc.app.box.com/v/ChestXray-NIHCC",
            "warning_text": "Matching Full NIH CXR pair absent",
            "source_resolution_receipt": receipt,
            "source_review": {
                "receipt": receipt,
                "receipt_sha256": hashlib.sha256((ROOT / receipt).read_bytes()).hexdigest(),
            },
        }
        _ready_transition(ROOT, row, "automedbench-full-nih-cxr-sr-task")
        wrong = copy.deepcopy(row)
        wrong["illustration_basis"] = "source-derived-teaching"
        with self.assertRaisesRegex(ValueError, "Invalid illustration basis"):
            _ready_transition(ROOT, wrong, "automedbench-full-nih-cxr-sr-task")
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
                _ready_transition(local, wrong, "automedbench-full-nih-cxr-sr-task")

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
                    "presentation/external-tasks/sources/automedbench-full-nih-cxr-sr-task-resolution.json"
                ),
                Path("presentation/external-tasks/briefs/automedbench-full-nih-cxr-sr-task.md"),
            ]:
                (root / rel).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / rel, root / rel)
            stories.resolve_assets(root, PACK)
            mp = root / SOURCE / "manifest.json"
            original = json.loads(mp.read_text())
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
                / "presentation/external-tasks/sources/automedbench-full-nih-cxr-sr-task-resolution.json"
            )
            receipt.write_text(receipt.read_text() + "\n")
            with self.assertRaisesRegex(ValueError, "Stale symbolic source pin"):
                stories.resolve_assets(root, PACK)


if __name__ == "__main__":
    unittest.main()
