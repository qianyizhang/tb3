"""Protect symbolic VQA output, reference boundaries and source pinning."""

import copy
import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tb3_medical import explanation_stories as stories
from tb3_medical.task_briefs import _brief_projection

ROOT = Path(__file__).resolve().parents[1]
STORY = Path("presentation/external-tasks/stories/automedbench-full-vqa-omnimedvqa-task.story.md")
SOURCE = Path("presentation/task-explorer/automedbench-full-vqa-omnimedvqa-task")
PACK = "retained-automed-omni-source-v1"


class AutomedOmniStoryTests(unittest.TestCase):
    def test_symbolic_compilation_preserves_empty_patient_and_result_fields(self):
        plan = stories.compile_story(ROOT, STORY)
        self.assertEqual(plan["source_class"], "source-derived-teaching")
        self.assertEqual(plan["reference_policy"], "reader-reference-reveal")
        self.assertEqual(
            [b["channels"]["progress"][0] for b in plan["beats"] if b["scene"] == "operation"],
            [0, 0.5, 1],
        )
        self.assertIn("Official OmniMedVQA", plan["beats"][0]["caption"])
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
        self.assertEqual(source["source_question"]["question_id"], "Covid CT_0082")
        self.assertEqual(reference["answer"], "Chest region.")
        self.assertNotIn("answer", source["source_question"])
        self.assertNotIn("gt_answer", source["source_question"])
        manifest = json.loads((ROOT / SOURCE / "manifest.json").read_text())
        self.assertEqual(
            next(a for a in manifest["assets"] if a["file"] == "reference.json")["role"],
            "reader-reference-reveal",
        )

    def test_entire_original_conditions_and_structured_retained_attempt(self):
        receipt = json.loads(
            (
                ROOT
                / "presentation/external-tasks/sources/automedbench-full-vqa-omnimedvqa-task-resolution.json"
            ).read_text()
        )
        path = Path("presentation/external-tasks/briefs/automedbench-full-vqa-omnimedvqa-task.md")
        brief = _brief_projection(ROOT, path)
        self.assertEqual(brief["variants"], receipt["original_conditions"]["rows"])
        raw = (ROOT / path).read_text()
        section = "## Conditions\n" + raw.split("## Conditions\n", 1)[1].split("\n## ", 1)[0]
        self.assertEqual(
            hashlib.sha256(section.encode()).hexdigest(),
            receipt["original_conditions"]["section_sha256"],
        )
        self.assertEqual(len(receipt["historical_acquisition_attempts"]), 2)
        for attempt in receipt["attempts"]:
            for key in ["action", "source", "outcome", "attempted_at"]:
                self.assertTrue(attempt[key])

    def test_task_specific_options_tiers_and_missing_native_boundary(self):
        receipt = json.loads(
            (
                ROOT
                / "presentation/external-tasks/sources/automedbench-full-vqa-omnimedvqa-task-resolution.json"
            ).read_text()
        )
        contract = receipt["task_contract"]
        self.assertEqual(contract["answer_mode"], "multiple_choice")
        self.assertEqual(contract["valid_labels"], list("ABCD"))
        self.assertEqual(contract["tiers"]["lite_and_standard_smoke"], [1, 10])
        self.assertEqual(len(contract["tiers"]["standard_exact_candidates"]), 6)
        self.assertTrue(contract["tiers"]["not_lite15_public_gold_calibration"])
        self.assertFalse(contract["dataset_included"])
        self.assertFalse(contract["full_case_membership_verified"])
        self.assertIn("all evaluator-supplied", contract["denominator"])
        self.assertFalse(
            any(p.suffix.lower() in {".png", ".jpg", ".jpeg"} for p in (ROOT / SOURCE).iterdir())
        )
        fixture = json.loads((ROOT / SOURCE / "fixture.json").read_text())
        self.assertEqual(fixture["parsed_examples"], ["A", None, None])
        self.assertIsNone(fixture["actual_prediction"])
        self.assertIsNone(fixture["actual_reference"])
        panel = (
            ROOT
            / "presentation/frontend/task-visuals/automedbench-full-vqa-omnimedvqa-task-panels.tsx"
        ).read_text()
        self.assertIn("referenceVisible(state, show)", panel)
        self.assertIn("useLayoutEffect", panel)
        self.assertNotIn("useId", panel)

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
                    "presentation/external-tasks/sources/automedbench-full-vqa-omnimedvqa-task-resolution.json"
                ),
                Path("presentation/external-tasks/briefs/automedbench-full-vqa-omnimedvqa-task.md"),
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
                / "presentation/external-tasks/sources/automedbench-full-vqa-omnimedvqa-task-resolution.json"
            )
            receipt.write_text(receipt.read_text() + "\n")
            with self.assertRaisesRegex(ValueError, "Stale symbolic source pin"):
                stories.resolve_assets(root, PACK)


if __name__ == "__main__":
    unittest.main()
