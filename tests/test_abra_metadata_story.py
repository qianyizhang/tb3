"""Protect metadata/reference roles, symbolic provenance and source pins."""

import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tb3_medical import explanation_stories as stories

ROOT = Path(__file__).resolve().parents[1]
STORY = Path("presentation/external-tasks/stories/abra-metadata-qa.story.md")
SOURCE = Path("presentation/task-explorer/abra-metadata-qa")
PACK = "retained-abra-metadata-qa-contract-v2"


class AbraMetadataStoryTests(unittest.TestCase):
    def test_compilation_preserves_five_query_beats_and_no_private_assets(self):
        plan = stories.compile_story(ROOT, STORY)
        operation = [b for b in plan["beats"] if b["scene"] == "operation"]
        self.assertEqual([b["channels"]["progress"][0] for b in operation], [0, 0.25, 0.5, 0.75, 1])
        self.assertEqual(plan["reference_policy"], "no-reference-assets")
        self.assertIn("Task/live response absent", plan["beats"][0]["caption"])
        self.assertIn("github.com/Luab/ABRA", plan["beats"][0]["caption"])
        output = json.loads((ROOT / SOURCE / "output.json").read_text())
        for key in ["participant_answer", "participant_trace", "score", "private_reference"]:
            self.assertIsNone(output[key])

    def test_reveal_outside_reference_and_missing_cut_are_rejected(self):
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

    def test_fixture_cannot_be_relabelled_as_source_or_private_reference(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            shutil.copytree(ROOT / SOURCE, root / SOURCE)
            for rel in [
                Path("presentation/assets/teaching-prefabs.json"),
                Path("presentation/external-tasks/sources/abra-metadata-qa-resolution.json"),
                Path("presentation/external-tasks/briefs/abra-metadata-qa.md"),
            ]:
                (root / rel).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / rel, root / rel)
            stories.resolve_assets(root, PACK)
            mp = root / SOURCE / "manifest.json"
            original = json.loads(mp.read_text())
            for role, provenance in [
                ("illustration", "source-derived-teaching"),
                ("reader-reference-reveal", "symbolic-protocol"),
            ]:
                changed = copy.deepcopy(original)
                a = next(a for a in changed["assets"] if a["file"] == "formatting-fixture.json")
                a.update(role=role, provenance=provenance)
                mp.write_text(json.dumps(changed))
                with self.assertRaisesRegex(ValueError, "incorrectly classified"):
                    stories.resolve_assets(root, PACK)
            mp.write_text(json.dumps(original))
            receipt = root / "presentation/external-tasks/sources/abra-metadata-qa-resolution.json"
            receipt.write_text(receipt.read_text() + "\n")
            with self.assertRaisesRegex(ValueError, "Stale symbolic source pin"):
                stories.resolve_assets(root, PACK)


if __name__ == "__main__":
    unittest.main()
