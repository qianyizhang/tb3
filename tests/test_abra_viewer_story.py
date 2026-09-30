"""Protect mixed source/state provenance and the viewer's non-reference contract."""

import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tb3_medical import explanation_stories as stories

ROOT = Path(__file__).resolve().parents[1]
STORY = Path("presentation/external-tasks/stories/abra-viewer-control.story.md")
PACK = "retained-abra-viewer-control-workflow-v1"
SOURCE_DIR = Path("presentation/task-explorer/abra-viewer-control")
RECEIPT = Path("presentation/external-tasks/sources/abra-viewer-control-resolution.json")


class AbraViewerStoryTests(unittest.TestCase):
    def test_story_compiles_without_an_observed_viewer_or_reference(self):
        plan = stories.compile_story(ROOT, STORY)
        self.assertEqual(plan["recipe"], "abra-viewer-control-v1")
        self.assertEqual(plan["reference_policy"], "no-reference-assets")
        self.assertTrue(all(b["channels"]["reference"] == [0.0, 0.0] for b in plan["beats"]))
        source = json.loads((ROOT / SOURCE_DIR / "source.json").read_text())
        output = json.loads((ROOT / SOURCE_DIR / "output.json").read_text())
        self.assertIsNone(source["preview"]["viewer_slice_index"])
        self.assertFalse(source["viewer_index_mapping_verified"])
        self.assertIsNone(source["observed_viewport"])
        self.assertIsNone(output["observed_state"])
        self.assertIsNone(output["score"])
        self.assertIn("cancerimagingarchive.net/collection/lidc-idri/", plan["beats"][0]["caption"])

    def test_nonzero_reference_and_missing_scene_cut_are_rejected(self):
        document = stories.parse_document((ROOT / STORY).read_text())
        data = {**document.header, "beats": list(document.beats)}
        changed = copy.deepcopy(data)
        changed["beats"][0]["channels"]["reference"] = [0.0, 1.0]
        with self.assertRaisesRegex(ValueError, "no reference assets"):
            stories.ADAPTER.validate_python(changed)
        changed = copy.deepcopy(data)
        del changed["beats"][1]["cut"]
        with self.assertRaisesRegex(ValueError, "explicit cut"):
            stories.ADAPTER.validate_python(changed)

    def test_mixed_pack_rejects_relabelled_preview_and_stale_source_pin(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            shutil.copytree(ROOT / SOURCE_DIR, root / SOURCE_DIR)
            for relative in [Path("presentation/assets/teaching-prefabs.json"), RECEIPT]:
                (root / relative).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / relative, root / relative)
            stories.resolve_assets(root, PACK)
            manifest_path = root / SOURCE_DIR / "manifest.json"
            original = json.loads(manifest_path.read_text())
            for role, provenance in [
                ("reader-reference-reveal", "source-derived"),
                ("input-preview", "source-derived-teaching"),
            ]:
                changed = copy.deepcopy(original)
                preview = next(a for a in changed["assets"] if a["file"] == "source_preview.png")
                preview.update(role=role, provenance=provenance)
                manifest_path.write_text(json.dumps(changed))
                with (
                    self.subTest(role=role, provenance=provenance),
                    self.assertRaisesRegex(ValueError, "incorrectly classified"),
                ):
                    stories.resolve_assets(root, PACK)
            manifest_path.write_text(json.dumps(original))
            with (root / RECEIPT).open("a") as stream:
                stream.write("\n")
            with self.assertRaisesRegex(ValueError, "Stale symbolic source pin"):
                stories.resolve_assets(root, PACK)


if __name__ == "__main__":
    unittest.main()
