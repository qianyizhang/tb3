"""Dynamic MRI acquisition, source visibility, unsubmitted outputs and recipe guards."""

import base64
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
ENTRY = "imaging101-mri-dynamic-dce"
STORY = Path(f"presentation/external-tasks/stories/{ENTRY}.story.md")
SOURCE_DIR = Path(f"presentation/task-explorer/{ENTRY}")
RECEIPT = Path(f"presentation/external-tasks/sources/{ENTRY}-resolution.json")
PACK = "retained-imaging-dynamic-mri-v1"


class DynamicMriStoryTests(unittest.TestCase):
    def test_native_order_domains_and_visibility(self):
        p = stories.compile_story(ROOT, STORY)
        self.assertEqual(p["reference_policy"], "no-reference-assets")
        self.assertIn("starpacker52/imaging-101", p["beats"][0]["caption"])
        m = json.loads((ROOT / SOURCE_DIR / "measurement.json").read_text())
        h = json.loads((ROOT / SOURCE_DIR / "helper.json").read_text())
        o = json.loads((ROOT / SOURCE_DIR / "output.json").read_text())
        op = json.loads((ROOT / SOURCE_DIR / "operation.json").read_text())
        self.assertEqual(m["shape"], [1, 20, 128, 128])
        self.assertEqual(m["sample_counts"], [2457] * 20)
        self.assertEqual(m["mask_encoding"], "base64-lsb0-frame-row-column")
        bits = base64.b64decode(m["mask_bits_base64"], validate=True)
        self.assertEqual(len(bits), 40960)
        self.assertEqual(
            [sum(x.bit_count() for x in bits[t * 2048 : (t + 1) * 2048]) for t in range(20)],
            [2457] * 20,
        )
        self.assertEqual(m["time_seconds"][0], 0)
        self.assertEqual(m["time_seconds"][-1], 60)
        self.assertFalse(h["initially_visible"])
        self.assertTrue(h["solver_visible_truth"])
        self.assertIsNone(h["private_reference"])
        self.assertEqual(len(h["source_pixel_series"]), 20)
        self.assertIn("PGD", op["methods"]["temporal_tv"])
        self.assertIn("complex temporal differences", op["methods"]["prox"])
        for key in ["prediction", "map", "score", "reference"]:
            self.assertIsNone(o[key])
        self.assertIn("327680", o["metric"])
        self.assertIn("20 frames", o["task_metric"])
        self.assertIn("no metrics.json", o["threshold"])
        self.assertIn(
            "No-filesystem scoring instead requires generic ground_truth.npy", o["scorer_route"]
        )
        self.assertIn("absent from the pinned DCE listing", o["scorer_route"])
        _brief_projection(ROOT, ROOT / f"presentation/external-tasks/briefs/{ENTRY}.md")
        panel = (
            ROOT / "presentation/frontend/task-visuals/imaging-dynamic-mri-panels.tsx"
        ).read_text()
        self.assertNotIn("useId", panel)
        self.assertIn("resetOnBackward", panel)
        self.assertIn("key={state.beatId}", panel)
        self.assertIn('aria-controls="dynamic-mri-source-series"', panel)

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
            for rel in [
                Path("presentation/assets/teaching-prefabs.json"),
                RECEIPT,
                Path(f"presentation/external-tasks/briefs/{ENTRY}.md"),
            ]:
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

    def test_pure_method_index_and_reset_controls(self):
        module = (
            ROOT / "presentation/frontend/task-visuals/imaging-dynamic-mri-controls.ts"
        ).as_uri()
        code = f"""import assert from 'node:assert/strict'; const m=await import({json.dumps(module)});
assert.equal(m.canonicalMethod('temporal_tv'),'temporal_tv');assert.equal(m.canonicalMethod('ADMM'),null);assert.equal(m.canonicalMethod('0'),null);
assert.equal(m.nativeFrame(19),19);assert.equal(m.nativeFrame(20),null);assert.equal(m.nativeFrame(-1),null);assert.equal(m.nativeFrame(0.5),null);
assert.equal(m.resetOnBackward(20,19),true);assert.equal(m.resetOnBackward(19,20),false);
"""
        subprocess.run(["node", "--input-type=module", "-e", code], check=True, capture_output=True)

    def test_original_condition_rows_and_historical_acquisition_preserved(self):
        path = ROOT / f"presentation/external-tasks/briefs/{ENTRY}.md"
        receipt = json.loads((ROOT / RECEIPT).read_text())
        section = (
            "## Conditions" + path.read_text().split("## Conditions", 1)[1].split("\n## ", 1)[0]
        )
        self.assertEqual(
            hashlib.sha256(section.encode()).hexdigest(),
            receipt["original_conditions"]["section_sha256"],
        )
        self.assertEqual(
            _brief_projection(ROOT, path)["variants"], receipt["original_conditions"]["rows"]
        )
        self.assertEqual(len(receipt["original_conditions"]["rows"]), 3)
        self.assertEqual(len(receipt["historical_acquisition_attempts"]), 5)
        self.assertEqual(
            sum("attempted_at" in item for item in receipt["historical_acquisition_attempts"]), 2
        )
        for attempt in receipt["attempts"]:
            self.assertTrue(
                all(attempt.get(key) for key in ["action", "source", "outcome", "attempted_at"])
            )
        for field in ["solver_run", "evaluator_run", "model_run", "preparer_run", "acceptance_run"]:
            self.assertFalse(receipt[field])


if __name__ == "__main__":
    unittest.main()
