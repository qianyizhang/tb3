"""Official training helper must not become a prediction or private reference."""

import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tb3_medical import explanation_stories as stories
from tb3_medical.task_briefs import _brief_projection

ROOT = Path(__file__).resolve().parents[1]
STORY = Path("presentation/external-tasks/stories/rexmle-ldct-iqa.story.md")
SOURCE = Path("presentation/task-explorer/rexmle-ldct-iqa")
RECEIPT = Path("presentation/external-tasks/sources/rexmle-ldct-iqa-resolution.json")
PACK = "retained-rexmle-ldct-iqa-interpretation-v1"


class RexLdctIqaTests(unittest.TestCase):
    def test_training_helper_and_empty_output_compile(self):
        _brief_projection(ROOT, ROOT / "presentation/external-tasks/briefs/rexmle-ldct-iqa.md")
        plan = stories.compile_story(ROOT, STORY)
        self.assertEqual(plan["reference_policy"], "no-reference-assets")
        self.assertIn("zenodo.org/records/7833096", plan["beats"][0]["caption"])
        h = json.loads((ROOT / SOURCE / "helper.json").read_text())
        o = json.loads((ROOT / SOURCE / "output.json").read_text())
        s = json.loads((ROOT / SOURCE / "source.json").read_text())
        self.assertEqual(h["image_id"], "0559.tif")
        self.assertEqual(h["training_reader_score"], 3.8)
        self.assertIsNone(h["scale_endpoints"])
        self.assertIsNone(s["HU_calibration"])
        for key in ("private_reference", "prediction", "score", "overall"):
            self.assertIsNone(o[key])
        self.assertTrue(all(v is None for v in o["values"].values()))
        self.assertEqual(o["score_rule"], "abs(PLCC) + abs(SROCC) + abs(KROCC)")

    def test_reference_and_missing_scene_cut_rejected(self):
        d = stories.parse_document((ROOT / STORY).read_text())
        data = {**d.header, "beats": list(d.beats)}
        changed = copy.deepcopy(data)
        changed["beats"][1]["channels"]["reference"] = [0, 1]
        with self.assertRaisesRegex(ValueError, "no private reference"):
            stories.ADAPTER.validate_python(changed)
        changed = copy.deepcopy(data)
        del changed["beats"][1]["cut"]
        with self.assertRaisesRegex(ValueError, "discontinuity|explicit cut"):
            stories.ADAPTER.validate_python(changed)

    def test_role_and_source_receipt_hash_guard(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            shutil.copytree(ROOT / SOURCE, root / SOURCE)
            for rel in (RECEIPT, Path("presentation/assets/teaching-prefabs.json")):
                (root / rel).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / rel, root / rel)
            stories.resolve_assets(root, PACK)
            p = root / SOURCE / "manifest.json"
            original = json.loads(p.read_text())
            change = copy.deepcopy(original)
            next(a for a in change["assets"] if a["file"] == "helper.json")["role"] = (
                "reader-reference-reveal"
            )
            p.write_text(json.dumps(change))
            with self.assertRaisesRegex(ValueError, "incorrectly classified"):
                stories.resolve_assets(root, PACK)
            p.write_text(json.dumps(original))
            (root / RECEIPT).write_text((root / RECEIPT).read_text() + "\n")
            with self.assertRaisesRegex(ValueError, "Stale symbolic source pin"):
                stories.resolve_assets(root, PACK)


if __name__ == "__main__":
    unittest.main()
