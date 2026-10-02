"""Protect MRCT synthesis output, reference boundaries and source pinning."""

import copy
import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tb3_medical import explanation_stories as stories

ROOT = Path(__file__).resolve().parents[1]
STORY = Path(
    "presentation/external-tasks/stories/automedbench-full-synthrad2025-mrct-task.story.md"
)
SOURCE = Path("presentation/task-explorer/automedbench-full-synthrad2025-mrct-task")
PACK = "retained-automedbench-full-synthrad2025-mrct-task-source-v1"


class AutomedSynthradMrctStoryTests(unittest.TestCase):
    def test_compilation_preserves_empty_input_synthesis_and_reference(self):
        plan = stories.compile_story(ROOT, STORY)
        self.assertEqual(
            [b["channels"]["progress"][0] for b in plan["beats"] if b["scene"] == "operation"],
            [0, 1 / 3, 2 / 3, 1],
        )
        self.assertIn("zenodo.org/records/15373853", plan["beats"][0]["caption"])
        fixture = json.loads((ROOT / SOURCE / "fixture.json").read_text())
        output = json.loads((ROOT / SOURCE / "output.json").read_text())
        reference = json.loads((ROOT / SOURCE / "reference.json").read_text())
        for k in ["actual_output", "clean_reference", "native_image"]:
            self.assertIsNone(fixture[k])
        for k in ["sct_volume", "actual_image", "quality_score"]:
            self.assertIsNone(output[k])
        self.assertIsNone(reference["clean_image"])
        self.assertIsNone(reference["actual_metric"])
        self.assertFalse(fixture["computed_synthesis"])
        self.assertEqual(fixture["branches"], [0, 1, 2, 3])
        helper = reference["upstream_MR_helper"]
        self.assertFalse(helper["actual_Full_pair"])
        self.assertFalse(helper["CT_or_mask_acquired"])
        self.assertEqual(helper["display"]["shape"], [101, 101])
        self.assertEqual(
            helper["member_sha256"],
            "79ebf8c0caa3d7f26a4501550bc2eb1975f153e67500f1cada504bce43c99a71",
        )

    def test_full_inventory_domain_geometry_backend_and_denominator_boundaries(self):
        from tb3_medical import task_briefs

        doc = task_briefs.load(ROOT)
        self.assertEqual(len(doc["entries"]), 205)
        row = next(
            v for v in doc["entries"] if v["id"] == "automedbench-full-synthrad2025-mrct-task"
        )
        self.assertEqual(
            [v["name"] for v in row["variants"]],
            ["Full · Lite", "Full · Standard", "Related source listing"],
        )
        s = json.loads((ROOT / SOURCE / "source.json").read_text())
        c = s["source_condition"]
        contract = s["task_contract"]
        self.assertEqual(c["task_type"], "synthesis")
        self.assertEqual(c["CT_unit"], "HU")
        for k in [
            "super_resolution_factor",
            "native_shape",
            "affine",
            "spacing",
            "orientation",
            "registration",
            "actual_supplied_ids",
            "partition_mapping",
        ]:
            self.assertIsNone(c[k])
        self.assertFalse(c["private_target_available"])
        self.assertFalse(c["model_weights_available"])
        self.assertIn("not a generic SR/LDCT", contract["metric_binding"])
        self.assertIn("4095", contract["metrics"])
        self.assertIn("empty mask", contract["metrics"])
        self.assertIn("finite-only PSNR", contract["denominators"])
        self.assertIn("no enforced20", contract["denominators"])
        self.assertIn("not an A/B gate", contract["rating"])
        self.assertIn("conflict", contract["generic_prompt_conflict"])
        self.assertIsNone(s["symbolic_display"]["native_image"])
        self.assertTrue(s["symbolic_display"]["no_resizing_or_model"])

    def test_ready_transition_requires_canonical_basis_and_structured_attempts(self):
        from tb3_medical.explainer_queue import _ready_transition

        receipt = "presentation/external-tasks/sources/automedbench-full-synthrad2025-mrct-task-resolution.json"
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
            "acquisition_route": "https://zenodo.org/records/15373853",
            "warning_text": "Matching Full MRCT pair absent",
            "source_resolution_receipt": receipt,
            "source_review": {
                "receipt": receipt,
                "receipt_sha256": hashlib.sha256((ROOT / receipt).read_bytes()).hexdigest(),
            },
        }
        _ready_transition(ROOT, row, "automedbench-full-synthrad2025-mrct-task")
        wrong = copy.deepcopy(row)
        wrong["illustration_basis"] = "source-derived-teaching"
        with self.assertRaisesRegex(ValueError, "Invalid illustration basis"):
            _ready_transition(ROOT, wrong, "automedbench-full-synthrad2025-mrct-task")
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
                _ready_transition(local, wrong, "automedbench-full-synthrad2025-mrct-task")

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
                    "presentation/external-tasks/sources/automedbench-full-synthrad2025-mrct-task-resolution.json"
                ),
                Path(
                    "presentation/external-tasks/briefs/automedbench-full-synthrad2025-mrct-task.md"
                ),
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
                / "presentation/external-tasks/sources/automedbench-full-synthrad2025-mrct-task-resolution.json"
            )
            receipt.write_text(receipt.read_text() + "\n")
            with self.assertRaisesRegex(ValueError, "Stale symbolic source pin"):
                stories.resolve_assets(root, PACK)


if __name__ == "__main__":
    unittest.main()
