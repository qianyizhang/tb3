"""Protect GRAPPA mode, sampling, reference and source-pinning boundaries."""

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
STORY = Path("presentation/external-tasks/stories/bcer-short-recon-grappa.story.md")
SOURCE = Path("presentation/task-explorer/bcer-short-recon-grappa")
PACK = "retained-bcer-grappa-source-v1"


class BcerGrappaStoryTests(unittest.TestCase):
    def test_symbolic_compilation_preserves_empty_patient_and_result_fields(self):
        plan = stories.compile_story(ROOT, STORY)
        self.assertEqual(plan["source_class"], "source-derived-teaching")
        self.assertEqual(plan["reference_policy"], "reader-reference-reveal")
        self.assertEqual(
            [b["channels"]["progress"][0] for b in plan["beats"] if b["scene"] == "operation"],
            [0, 0.5, 1],
        )
        self.assertIn("CMRxRecon2025", plan["beats"][0]["caption"])
        output = json.loads((ROOT / SOURCE / "output.json").read_text())
        fixture = json.loads((ROOT / SOURCE / "fixture.json").read_text())
        self.assertIsNone(fixture["actual_output"])
        self.assertIsNone(fixture["clean_reference"])
        for key in ["reconstructed_nifti", "actual_image", "elapsed_seconds", "quality_score"]:
            self.assertIsNone(output[key])
        self.assertIsNone(fixture["clean_reference"])
        reference = json.loads((ROOT / SOURCE / "reference.json").read_text())
        self.assertIsNone(reference["clean_image"])
        self.assertEqual(fixture["sampled_lines"], [28, 32, 28])
        self.assertEqual(fixture["ACS_bounds"], [4, 28])
        self.assertEqual(sum(fixture["masks"][0]), 28)

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
                Path("presentation/external-tasks/sources/bcer-short-recon-grappa-resolution.json"),
                Path("presentation/external-tasks/briefs/bcer-short-recon-grappa.md"),
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
                root / "presentation/external-tasks/sources/bcer-short-recon-grappa-resolution.json"
            )
            receipt.write_text(receipt.read_text() + "\n")
            with self.assertRaisesRegex(ValueError, "Stale symbolic source pin"):
                stories.resolve_assets(root, PACK)

    def test_mask_denominator_is_symbolic_not_net_acceleration_or_image_pixels(self):
        fixture = json.loads((ROOT / SOURCE / "fixture.json").read_text())
        expected = [ky % 2 == 0 or 4 <= ky < 28 for ky in range(32)]
        self.assertEqual(fixture["masks"][0], expected)
        self.assertEqual(sum(expected), 28)
        self.assertEqual(fixture["sampled_fraction"], [28 / 32, 1, 28 / 32])
        self.assertNotEqual(32 / sum(expected), 2)
        self.assertEqual((fixture["kx"], fixture["ky"], fixture["coils"]), (8, 32, 2))
        self.assertIsNone(fixture["actual_output"])
        self.assertIsNone(fixture["clean_reference"])

    def test_entire_condition_cells_and_historical_attempts_preserved(self):
        path = ROOT / "presentation/external-tasks/briefs/bcer-short-recon-grappa.md"
        receipt = json.loads(
            (
                ROOT / "presentation/external-tasks/sources/bcer-short-recon-grappa-resolution.json"
            ).read_text()
        )
        text = path.read_text()
        section = "## Conditions" + text.split("## Conditions", 1)[1].split("\n## ", 1)[0]
        self.assertEqual(
            hashlib.sha256(section.encode()).hexdigest(),
            receipt["original_conditions"]["section_sha256"],
        )
        self.assertEqual(
            _brief_projection(ROOT, path)["variants"], receipt["original_conditions"]["rows"]
        )
        self.assertEqual(len(receipt["historical_acquisition_attempts"]), 2)
        for old in receipt["historical_acquisition_attempts"]:
            self.assertIn("date", old)
            self.assertNotIn("attempted_at", old)
        for attempt in receipt["attempts"]:
            self.assertTrue(
                all(attempt.get(key) for key in ["action", "source", "outcome", "attempted_at"])
            )
        self.assertFalse(receipt["tool_run"])
        self.assertFalse(receipt["model_run"])
        self.assertIn("Docstring says smallest", receipt["task_contract"]["coil_axis_discrepancy"])


if __name__ == "__main__":
    unittest.main()
