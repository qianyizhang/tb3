"""Symbolic taxonomy cannot become a case label or measured classifier result."""

import copy
import importlib.util
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from tb3_medical import explanation_stories as stories
from tb3_medical.task_briefs import _brief_projection

ROOT = Path(__file__).resolve().parents[1]
ENTRY = "automedbench-full-braintumor-cls-task"
STORY = Path(f"presentation/external-tasks/stories/{ENTRY}.story.md")
SOURCE = Path(f"presentation/task-explorer/{ENTRY}")
RECEIPT = Path(f"presentation/external-tasks/sources/{ENTRY}-resolution.json")
PACK = "symbolic-automed-brain-cls-v1"


class AutomedBrainClsTests(unittest.TestCase):
    def test_symbolic_contract_has_no_case_label_or_checkpoint(self):
        _brief_projection(ROOT, ROOT / f"presentation/external-tasks/briefs/{ENTRY}.md")
        plan = stories.compile_story(ROOT, STORY)
        self.assertEqual(plan["reference_policy"], "no-reference-assets")
        self.assertIn("kaggle.com/datasets/", plan["beats"][0]["caption"])
        s = json.loads((ROOT / SOURCE / "source.json").read_text())
        h = json.loads((ROOT / SOURCE / "helper.json").read_text())
        o = json.loads((ROOT / SOURCE / "output.json").read_text())
        self.assertEqual(h["classes"], ["glioma", "meningioma", "notumor", "pituitary"])
        self.assertIsNone(h["checkpoint_id2label"])
        for key in ("native_image", "full_case_id", "training_label", "private_label"):
            self.assertIsNone(s[key])
        for key in ("prediction", "private_reference", "score"):
            self.assertIsNone(o[key])
        self.assertTrue(all(v is None for v in o["values"].values()))
        self.assertIn("all supplied", o["accuracy"])
        self.assertIn("positive true-class support", o["balanced_accuracy"])

    def test_named_class_controls_and_import_safe_builder(self):
        code = r"""
import assert from 'node:assert/strict';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const controls=await import(pathToFileURL(path.resolve('presentation/frontend/task-visuals/automed-brain-cls-controls.ts')).href);
const classes=['glioma','meningioma','notumor','pituitary'];
for(const token of classes) assert.equal(controls.canonicalNamedClass(token.toUpperCase(),classes),token);
assert.equal(controls.canonicalNamedClass('0',classes),null);
assert.equal(controls.canonicalNamedClass('tumor',classes),null);
assert.equal(controls.canonicalNamedClass('',classes),null);
assert.deepEqual(Array.from(controls.submissionFields('csv')),['patient_id','label']);
assert.deepEqual(Array.from(controls.submissionFields('json')),['label']);
assert.equal(controls.shouldResetControls(500,200),true);
assert.equal(controls.shouldResetControls(200,500),false);
assert.equal(controls.shouldResetControls(200,200),false);
"""
        subprocess.run(["node", "--input-type=module", "-e", code], cwd=ROOT, check=True)
        builder = ROOT / "scripts/build_automed_brain_cls_assets.py"
        spec = importlib.util.spec_from_file_location("brain_cls_builder", builder)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertTrue(callable(module.build))
        self.assertTrue(callable(module.main))
        panels = (
            ROOT / "presentation/frontend/task-visuals/automed-brain-cls-panels.tsx"
        ).read_text()
        for selector in [
            "data-brain-cls-class-selection",
            "data-brain-cls-formatter",
            "data-brain-cls-grader",
        ]:
            self.assertIn(selector, panels)
        self.assertNotIn("useId", panels)

    def test_reference_and_missing_scene_cut_rejected(self):
        d = stories.parse_document((ROOT / STORY).read_text())
        data = {**d.header, "beats": list(d.beats)}
        change = copy.deepcopy(data)
        change["beats"][1]["channels"]["reference"] = [0, 1]
        with self.assertRaisesRegex(ValueError, "no private reference"):
            stories.ADAPTER.validate_python(change)
        change = copy.deepcopy(data)
        del change["beats"][1]["cut"]
        with self.assertRaisesRegex(ValueError, "discontinuity|explicit cut"):
            stories.ADAPTER.validate_python(change)

    def test_pack_rejects_reference_reclassification_and_stale_source(self):
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
