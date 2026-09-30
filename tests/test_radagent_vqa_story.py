"""Protect symbolic VQA output, reference boundaries and source pinning."""

import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tb3_medical import explanation_stories as stories

ROOT = Path(__file__).resolve().parents[1]
STORY = Path("presentation/external-tasks/stories/radagent-vqa.story.md")
SOURCE = Path("presentation/task-explorer/radagent-vqa")
PACK = "retained-radagent-vqa-contract-v2"


class RadagentVqaStoryTests(unittest.TestCase):
    def test_symbolic_compilation_preserves_empty_patient_and_result_fields(self):
        plan = stories.compile_story(ROOT, STORY)
        self.assertEqual(plan["source_class"], "symbolic-protocol")
        self.assertEqual(plan["reference_policy"], "no-reference-assets")
        self.assertEqual(
            [b["channels"]["progress"][0] for b in plan["beats"] if b["scene"] == "operation"],
            [0, 0.5, 1],
        )
        self.assertIn("huggingface.co/datasets/ibrahimhamamci/CT-RATE", plan["beats"][0]["caption"])
        output = json.loads((ROOT / SOURCE / "output.json").read_text())
        fixture = json.loads((ROOT / SOURCE / "formatting-fixture.json").read_text())
        for key in ["participant_answer", "participant_trace", "actual_score", "private_reference"]:
            self.assertIsNone(output[key])
        for key in [
            "actual_question",
            "actual_options",
            "actual_reference",
            "actual_prediction",
            "actual_score",
        ]:
            self.assertIsNone(fixture[key])

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
                Path("presentation/external-tasks/sources/radagent-vqa-resolution.json"),
                Path("presentation/external-tasks/briefs/radagent-vqa.md"),
            ]:
                (root / rel).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / rel, root / rel)
            stories.resolve_assets(root, PACK)
            mp = root / SOURCE / "manifest.json"
            original = json.loads(mp.read_text())
            changed = copy.deepcopy(original)
            next(a for a in changed["assets"] if a["file"] == "formatting-fixture.json")[
                "provenance"
            ] = "source-derived-teaching"
            mp.write_text(json.dumps(changed))
            with self.assertRaisesRegex(ValueError, "incorrectly classified"):
                stories.resolve_assets(root, PACK)
            mp.write_text(json.dumps(original))
            receipt = root / "presentation/external-tasks/sources/radagent-vqa-resolution.json"
            receipt.write_text(receipt.read_text() + "\n")
            with self.assertRaisesRegex(ValueError, "Stale symbolic source pin"):
                stories.resolve_assets(root, PACK)


if __name__ == "__main__":
    unittest.main()
