"""Keep constructed report fields separate from MRI findings and actual outputs."""

import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tb3_medical import explanation_stories as stories

ROOT = Path(__file__).resolve().parents[1]
STORY = Path("presentation/external-tasks/stories/abra-birads.story.md")
PACK = "retained-abra-birads-contract-v1"
SOURCE_DIR = Path("presentation/task-explorer/abra-birads")
RECEIPT = Path("presentation/external-tasks/sources/abra-birads-resolution.json")


class AbraBiradsStoryTests(unittest.TestCase):
    def test_mixed_contract_compiles_without_patient_targets_or_pixels(self):
        plan = stories.compile_story(ROOT, STORY)
        self.assertEqual(plan["reference_policy"], "no-reference-assets")
        source = json.loads((ROOT / SOURCE_DIR / "source.json").read_text())
        output = json.loads((ROOT / SOURCE_DIR / "output.json").read_text())
        derivation = json.loads((ROOT / SOURCE_DIR / "derivation.json").read_text())
        self.assertIsNone(source["pixels"])
        self.assertIsNone(source["generated_task"])
        self.assertTrue(all(v is None for v in output["values"].values()))
        for key in ["submitted_report", "oracle_response", "score", "private_reference"]:
            self.assertIsNone(output[key])
        self.assertIsNone(derivation["private_reference"])
        self.assertEqual(derivation["role"], "general-source-code-policy-not-patient-reference")
        self.assertEqual(output["optional_quadrant"], "findings[0].location_quadrant")
        self.assertIn(
            "cancerimagingarchive.net/collection/duke-breast-cancer-mri/",
            plan["beats"][0]["caption"],
        )

    def test_reveal_outside_its_chapter_and_missing_cut_are_rejected(self):
        document = stories.parse_document((ROOT / STORY).read_text())
        data = {**document.header, "beats": list(document.beats)}
        changed = copy.deepcopy(data)
        changed["beats"][0]["channels"]["reference"] = [0.0, 1.0]
        with self.assertRaisesRegex(ValueError, "inside reference chapter"):
            stories.ADAPTER.validate_python(changed)
        changed = copy.deepcopy(data)
        del changed["beats"][1]["cut"]
        with self.assertRaisesRegex(ValueError, "explicit cut"):
            stories.ADAPTER.validate_python(changed)

    def test_pack_rejects_private_reference_relabelling_and_stale_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            shutil.copytree(ROOT / SOURCE_DIR, root / SOURCE_DIR)
            for relative in [Path("presentation/assets/teaching-prefabs.json"), RECEIPT]:
                (root / relative).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / relative, root / relative)
            stories.resolve_assets(root, PACK)
            path = root / SOURCE_DIR / "manifest.json"
            original = json.loads(path.read_text())
            changed = copy.deepcopy(original)
            next(a for a in changed["assets"] if a["file"] == "derivation.json")["role"] = (
                "reader-reference-reveal"
            )
            path.write_text(json.dumps(changed))
            with self.assertRaisesRegex(ValueError, "incorrectly classified"):
                stories.resolve_assets(root, PACK)
            path.write_text(json.dumps(original))
            with (root / RECEIPT).open("a") as stream:
                stream.write("\n")
            with self.assertRaisesRegex(ValueError, "Stale symbolic source pin"):
                stories.resolve_assets(root, PACK)


if __name__ == "__main__":
    unittest.main()
