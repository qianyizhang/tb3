"""Protect symbolic VQA output, reference boundaries and source pinning."""

import copy
import hashlib
import json
import shutil
import tempfile
import unittest
import zlib
from pathlib import Path

from tb3_medical import explanation_stories as stories

ROOT = Path(__file__).resolve().parents[1]
STORY = Path("presentation/external-tasks/stories/automedbench-full-medxpertqa-mm-task.story.md")
SOURCE = Path("presentation/task-explorer/automedbench-full-medxpertqa-mm-task")
PACK = "retained-automed-medxpert-mm-source-v1"


class AutomedMedxpertStoryTests(unittest.TestCase):
    def test_compilation_preserves_empty_participant_and_separate_native_reference(self):
        plan = stories.compile_story(ROOT, STORY)
        self.assertEqual(plan["source_class"], "source-derived-teaching")
        self.assertEqual(plan["reference_policy"], "reader-reference-reveal")
        self.assertEqual(
            [b["channels"]["progress"][0] for b in plan["beats"] if b["scene"] == "operation"],
            [0, 0.5, 1],
        )
        self.assertIn("Official MedXpertQA", plan["beats"][0]["caption"])
        output = json.loads((ROOT / SOURCE / "output.json").read_text())
        fixture = json.loads((ROOT / SOURCE / "fixture.json").read_text())
        self.assertIsNone(fixture["actual_prediction"])
        self.assertIsNone(fixture["actual_reference"])
        for key in [
            "predicted_label",
            "predicted_answer",
            "raw_model_output",
            "model_name",
            "runtime_s",
            "private_reference",
            "score",
        ]:
            self.assertIsNone(output[key])
        source = json.loads((ROOT / SOURCE / "source.json").read_text())
        reference = json.loads((ROOT / SOURCE / "reference.json").read_text())
        self.assertNotIn("label", source["source_question"])
        self.assertNotIn("public_reference", source)
        self.assertEqual(source["source_question"]["id"], "MM-2000")
        self.assertEqual(reference["label"], "D")
        self.assertEqual(reference["option_text"], source["source_question"]["options"]["D"])
        manifest = json.loads((ROOT / SOURCE / "manifest.json").read_text())
        self.assertEqual(
            next(a for a in manifest["assets"] if a["file"] == "reference.json")["role"],
            "reader-reference-reveal",
        )

    def test_full_inventory_native_binding_tiers_and_calibration_boundaries(self):
        from tb3_medical import task_briefs

        doc = task_briefs.load(ROOT)
        self.assertEqual(len(doc["entries"]), 205)
        row = next(v for v in doc["entries"] if v["id"] == "automedbench-full-medxpertqa-mm-task")
        self.assertEqual(
            [v["name"] for v in row["variants"]],
            ["Full · Lite", "Full · Standard", "Related source listing"],
        )
        source = json.loads((ROOT / SOURCE / "source.json").read_text())
        c = source["task_contract"]
        self.assertFalse(c["full_case_membership_verified"])
        self.assertIn("not a recovered Full", c["qid_mapping"])
        self.assertIn("conversion/membership unstaged", c["image_binding"])
        self.assertEqual(c["calibration"]["source_request_exact"], 15)
        self.assertEqual(c["calibration"]["smoke_bounds"], [1, 10])
        self.assertFalse(c["calibration"]["private_tuning_allowed"])
        self.assertIsNone(c["calibration"]["actual_calibration"])
        native = (ROOT / SOURCE / "source-preview.jpeg").read_bytes()
        self.assertEqual(len(native), 96627)
        self.assertEqual(zlib.crc32(native) & 0xFFFFFFFF, 0x3AB54169)
        self.assertEqual(hashlib.sha256(native).hexdigest(), source["native_example"]["sha256"])
        self.assertEqual(source["native_example"]["geometry"]["width"], 945)
        self.assertEqual(source["native_example"]["geometry"]["height"], 999)
        self.assertNotIn("preview_data_uri", source)
        self.assertIn("gold answer_label exact", c["normalization"])
        self.assertIn("missing/malformed/placeholder", c["denominator"])
        self.assertIn("wrong nonempty option text", c["format_gap"])
        self.assertIn("empty N", c["schema_threshold"])
        self.assertIn("do not contribute to MCQ", c["scorer_backend"])

    def test_ready_transition_requires_mixed_basis_and_real_structured_attempts(self):
        from tb3_medical.explainer_queue import _ready_transition

        receipt = "presentation/external-tasks/sources/automedbench-full-medxpertqa-mm-task-resolution.json"
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
            "actual_data_gap": "Full selected IDs/private gold absent",
            "acquisition_route": "https://huggingface.co/datasets/TsinghuaC3I/MedXpertQA",
            "warning_text": "Public dev source only",
            "source_resolution_receipt": receipt,
            "source_review": {
                "receipt": receipt,
                "receipt_sha256": hashlib.sha256((ROOT / receipt).read_bytes()).hexdigest(),
            },
        }
        _ready_transition(ROOT, row, "automedbench-full-medxpertqa-mm-task")
        wrong = copy.deepcopy(row)
        wrong["illustration_basis"] = "source-derived-teaching"
        with self.assertRaisesRegex(ValueError, "Invalid illustration basis"):
            _ready_transition(ROOT, wrong, "automedbench-full-medxpertqa-mm-task")
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
                _ready_transition(local, wrong, "automedbench-full-medxpertqa-mm-task")

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
                    "presentation/external-tasks/sources/automedbench-full-medxpertqa-mm-task-resolution.json"
                ),
                Path("presentation/external-tasks/briefs/automedbench-full-medxpertqa-mm-task.md"),
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
                / "presentation/external-tasks/sources/automedbench-full-medxpertqa-mm-task-resolution.json"
            )
            receipt.write_text(receipt.read_text() + "\n")
            with self.assertRaisesRegex(ValueError, "Stale symbolic source pin"):
                stories.resolve_assets(root, PACK)


if __name__ == "__main__":
    unittest.main()
