"""GRAPPA full-data roles, source visibility, unsubmitted outputs and recipe guards."""

import copy
import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from tb3_medical import explanation_stories as stories
from tb3_medical.task_briefs import _brief_projection

ROOT = Path(__file__).resolve().parents[1]
ENTRY = "imaging101-mri-grappa"
STORY = Path(f"presentation/external-tasks/stories/{ENTRY}.story.md")
SOURCE_DIR = Path(f"presentation/task-explorer/{ENTRY}")
RECEIPT = Path(f"presentation/external-tasks/sources/{ENTRY}-resolution.json")
PACK = "retained-imaging-grappa-v1"


class GrappaStoryTests(unittest.TestCase):
    def test_native_order_domains_and_visibility(self):
        p = stories.compile_story(ROOT, STORY)
        self.assertEqual(p["reference_policy"], "no-reference-assets")
        self.assertIn("starpacker52/imaging-101", p["beats"][0]["caption"])
        m = json.loads((ROOT / SOURCE_DIR / "measurement.json").read_text())
        h = json.loads((ROOT / SOURCE_DIR / "helper.json").read_text())
        o = json.loads((ROOT / SOURCE_DIR / "output.json").read_text())
        op = json.loads((ROOT / SOURCE_DIR / "operation.json").read_text())
        self.assertEqual(m["shape"], [1, 128, 128, 8])
        self.assertEqual(m["retained_line_count"], 74)
        self.assertEqual(m["acs_rows"], [54, 73])
        self.assertEqual(len(m["native_center_kspace"]), 8)
        self.assertNotIn("native_full_target_pairs", m)
        self.assertFalse(h["initially_visible"])
        self.assertTrue(h["solver_visible_full_data"])
        self.assertIsNone(h["private_reference"])
        self.assertEqual(h["source_target_row_col"], [51, 64])
        self.assertEqual(len(h["native_full_target_pairs"]), 8)
        self.assertIn("n_sources", op["methods"]["calibration"])
        self.assertIn("exact zeros=0", op["methods"]["interpolation"])
        for key in ["prediction", "map", "score", "reference"]:
            self.assertIsNone(o[key])
        self.assertIn("16384", o["metric"])
        self.assertIn("skimage", o["task_metric"])
        self.assertIn("RSS", o["reference_selection"])
        self.assertIn("no top-level", o["threshold"])
        _brief_projection(ROOT, ROOT / f"presentation/external-tasks/briefs/{ENTRY}.md")
        panel = (ROOT / "presentation/frontend/task-visuals/imaging-grappa-panels.tsx").read_text()
        self.assertNotIn("useId", panel)
        self.assertIn("resetOnBackward", panel)
        self.assertIn("key={state.beatId}", panel)
        self.assertIn('aria-controls="grappa-native-full-target"', panel)

    def test_reference_and_canonical_cut_rejection(self):
        d = stories.parse_document((ROOT / STORY).read_text())
        data = {**d.header, "beats": list(d.beats)}
        changed = copy.deepcopy(data)
        changed["beats"][0]["channels"]["reference"] = [0.0, 1.0]
        with self.assertRaisesRegex(ValueError, "no private reference"):
            stories.ADAPTER.validate_python(changed)
        changed = copy.deepcopy(data)
        del changed["beats"][1]["cut"]
        with self.assertRaisesRegex(ValueError, "explicit cut|discontinuity"):
            stories.ADAPTER.validate_python(changed)

    def test_native_role_and_source_pin_guards(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            shutil.copytree(ROOT / SOURCE_DIR, root / SOURCE_DIR)
            for rel in [Path("presentation/assets/teaching-prefabs.json"), RECEIPT]:
                (root / rel).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / rel, root / rel)
            stories.resolve_assets(root, PACK)
            path = root / SOURCE_DIR / "manifest.json"
            original = json.loads(path.read_text())
            changed = copy.deepcopy(original)
            next(x for x in changed["assets"] if x["file"] == "measurement.json")["role"] = (
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
            self.assertTrue(
                all(
                    hashlib.sha256((ROOT / SOURCE_DIR / x["file"]).read_bytes()).hexdigest()
                    == x["sha256"]
                    for x in original["assets"]
                )
            )

    def test_canonical_seek_and_backend_constant_range_rules(self):
        module = (ROOT / "presentation/frontend/task-visuals/imaging-grappa-controls.ts").as_uri()
        code = f"""import assert from 'node:assert/strict';const m=await import({json.dumps(module)});
const plan={{beats:[{{scene:'input',frames:288}},{{scene:'helper',frames:288}},{{scene:'operation',frames:288}}]}};
// Independent closed-form inverse smoothstep yields indices 0,111,176,287.
assert.deepEqual([0,1,2,3].map(s=>m.operationFrame(plan,s)),[576,687,752,863]);
assert.equal(m.sourceTargetVisible('operation',true),false);
assert.equal(m.sourceTargetVisible('helper',false),false);
assert.equal(m.sourceTargetVisible('helper',true),true);
"""
        subprocess.run(["node", "--input-type=module", "-e", code], check=True, capture_output=True)
        o = json.loads((ROOT / SOURCE_DIR / "output.json").read_text())
        self.assertIn("zero range", o["metric"])
        self.assertIn("infinity", o["task_metric"])
        self.assertIn("flux-normalizes", o["task_metric"])

    def test_pure_method_index_and_reset_controls(self):
        module = (ROOT / "presentation/frontend/task-visuals/imaging-grappa-controls.ts").as_uri()
        code = f"""import assert from 'node:assert/strict';const m=await import({json.dumps(module)});
assert.equal(m.canonicalMethod('calibration'),'calibration');assert.equal(m.canonicalMethod('reconstruction'),null);assert.equal(m.canonicalMethod('0'),null);
assert.equal(m.nativeCoil(7),7);assert.equal(m.nativeCoil(8),null);assert.equal(m.nativeCoil(-1),null);assert.equal(m.nativeCoil(0.5),null);
assert.equal(m.resetOnBackward(20,19),true);assert.equal(m.resetOnBackward(19,20),false);
"""
        subprocess.run(["node", "--input-type=module", "-e", code], check=True, capture_output=True)


if __name__ == "__main__":
    unittest.main()
