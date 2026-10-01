"""Protect denoise parameter, helper provenance and artifact/reference boundaries."""

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
STORY = Path("presentation/external-tasks/stories/bcer-short-denoise.story.md")
SOURCE = Path("presentation/task-explorer/bcer-short-denoise")
PACK = "retained-bcer-denoise-source-v1"


class BcerDenoiseStoryTests(unittest.TestCase):
    def test_symbolic_compilation_preserves_empty_patient_and_result_fields(self):
        plan = stories.compile_story(ROOT, STORY)
        self.assertEqual(plan["source_class"], "source-derived-teaching")
        self.assertEqual(plan["reference_policy"], "reader-reference-reveal")
        self.assertEqual(
            [b["channels"]["progress"][0] for b in plan["beats"] if b["scene"] == "operation"],
            [0, 0.5, 1],
        )
        self.assertIn("zenodo.org/records/6624726", plan["beats"][0]["caption"])
        output = json.loads((ROOT / SOURCE / "output.json").read_text())
        fixture = json.loads((ROOT / SOURCE / "fixture.json").read_text())
        self.assertIsNone(fixture["actual_output"])
        self.assertIsNone(fixture["clean_reference"])
        for key in ["denoised_nifti", "actual_image", "elapsed_seconds", "quality_score"]:
            self.assertIsNone(output[key])
        self.assertIsNone(fixture["clean_reference"])
        reference = json.loads((ROOT / SOURCE / "reference.json").read_text())
        self.assertIsNone(reference["clean_image"])
        self.assertEqual(fixture["normalized"], [0, 0.25, 0.5, 1])
        self.assertEqual(fixture["raw_sigma"], [1.2, 3.2, 6.0])

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
                Path("presentation/external-tasks/sources/bcer-short-denoise-resolution.json"),
                Path("presentation/external-tasks/briefs/bcer-short-denoise.md"),
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
                root / "presentation/external-tasks/sources/bcer-short-denoise-resolution.json"
            )
            receipt.write_text(receipt.read_text() + "\n")
            with self.assertRaisesRegex(ValueError, "Stale symbolic source pin"):
                stories.resolve_assets(root, PACK)

    def test_original_condition_cells_and_historical_acquisition_preserved(self):
        receipt = json.loads(
            (
                ROOT / "presentation/external-tasks/sources/bcer-short-denoise-resolution.json"
            ).read_text()
        )
        text = (ROOT / "presentation/external-tasks/briefs/bcer-short-denoise.md").read_text()
        section = "## Conditions" + text.split("## Conditions", 1)[1].split("\n## ", 1)[0]
        self.assertEqual(
            hashlib.sha256(section.encode()).hexdigest(),
            receipt["original_conditions"]["section_sha256"],
        )
        projection = _brief_projection(
            ROOT, ROOT / "presentation/external-tasks/briefs/bcer-short-denoise.md"
        )
        self.assertEqual(projection["variants"], receipt["original_conditions"]["rows"])
        self.assertEqual(
            receipt["historical_acquisition_attempts"],
            [
                {
                    "date": "2026-09-30",
                    "route": "OfficialPI-CAI record API",
                    "outcome": "HTTP2008844B;retainedcompatiblevolumealreadyavailable,noBCERshortcaseoutputfromrecord",
                }
            ],
        )
        for attempt in receipt["attempts"]:
            self.assertTrue(
                all(attempt.get(key) for key in ["action", "source", "outcome", "attempted_at"])
            )
        self.assertFalse(receipt["tool_run"])
        self.assertFalse(receipt["model_run"])

    def test_estimated_sigma_native_helper_and_validator_are_not_quality_evidence(self):
        source = json.loads((ROOT / SOURCE / "source.json").read_text())
        native = source["representative_input"]
        self.assertEqual(native["shape_xyz"], [640, 640, 21])
        self.assertNotIn("preview_data_uri", source)
        self.assertFalse(source["display_derivative"]["tool_output"])
        self.assertEqual(source["display_derivative"]["to"], [320, 320])
        self.assertIn("neither matching BM3D", native["role"])
        contract = source["task_contract"]
        self.assertIn("estimated", contract["noise_boundary"])
        self.assertIn("not injected", contract["noise_boundary"])
        self.assertIn("1e-3", contract["evaluator_boundary"])
        self.assertIn("Not quality", contract["evaluator_boundary"])
        reference = json.loads((ROOT / SOURCE / "reference.json").read_text())
        self.assertIsNone(reference["clean_image"])
        self.assertIsNone(reference["quality_metric"])


if __name__ == "__main__":
    unittest.main()
