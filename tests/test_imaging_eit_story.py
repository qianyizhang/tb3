"""EIT native ordering, source visibility, unsubmitted outputs and recipe guards."""

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
ENTRY = "imaging101-eit-conductivity-reconstruction"
STORY = Path(f"presentation/external-tasks/stories/{ENTRY}.story.md")
SOURCE_DIR = Path(f"presentation/task-explorer/{ENTRY}")
RECEIPT = Path(f"presentation/external-tasks/sources/{ENTRY}-resolution.json")
PACK = "retained-imaging-eit-v1"


class EitStoryTests(unittest.TestCase):
    def test_native_order_domains_and_visibility(self):
        p = stories.compile_story(ROOT, STORY)
        self.assertEqual(p["reference_policy"], "no-reference-assets")
        self.assertIn("starpacker52/imaging-101", p["beats"][0]["caption"])
        m = json.loads((ROOT / SOURCE_DIR / "measurement.json").read_text())
        h = json.loads((ROOT / SOURCE_DIR / "helper.json").read_text())
        o = json.loads((ROOT / SOURCE_DIR / "output.json").read_text())
        op = json.loads((ROOT / SOURCE_DIR / "operation.json").read_text())
        self.assertEqual(len(m["node"]), 376)
        self.assertEqual(len(m["element"]), 686)
        self.assertEqual(len(m["v0"]), 208)
        self.assertEqual(m["ref_node"], 16)
        self.assertEqual(m["ex_mat"][0], [0, 1])
        self.assertEqual(m["meas_mat"][0], [3, 2, 0])
        self.assertNotIn("perm_anomaly", m)
        self.assertFalse(h["initially_visible"])
        self.assertTrue(h["solver_visible_truth"])
        self.assertIsNone(h["private_reference"])
        self.assertIn("sign(v0.real)", op["methods"]["BP"]["normalize"])
        self.assertIn("abs(v0)", op["methods"]["JAC"]["normalize"])
        for k in ["prediction", "map", "score", "reference"]:
            self.assertIsNone(o[k])
        self.assertIn("uncentered", o["metric"])
        self.assertIn("flux", o["task_metric"])
        self.assertIn("no top-level", o["threshold"])
        selection = o["reference_selection"]
        self.assertIn("six float64 arrays shaped (1,686)", selection)
        self.assertIn("only ndim > 2", selection)
        self.assertIn("output (686,) matches none", selection)
        self.assertIn("Output (376,) can match saved BP reconstruction", selection)
        self.assertIn("incomplete retained tree only", selection)
        self.assertIn("full official tree lists ground_truth_bp.npy", selection)
        self.assertIn("No-filesystem scorer instead requires ground_truth.npy", selection)

        # Independent shape mechanics: a 2D singleton remains 2D; >2D squeezes.
        def prepare_shape(shape):
            return tuple(x for x in shape if x != 1) if len(shape) > 2 else shape

        self.assertEqual(prepare_shape((1, 686)), (1, 686))
        self.assertEqual(prepare_shape((1, 1, 686)), (686,))
        self.assertNotEqual(prepare_shape((1, 686)), (686,))
        _brief_projection(ROOT, ROOT / f"presentation/external-tasks/briefs/{ENTRY}.md")
        panel = (ROOT / "presentation/frontend/task-visuals/imaging-eit-panels.tsx").read_text()
        self.assertNotIn("useId", panel)
        self.assertIn("resetOnBackward", panel)
        self.assertIn("key={state.beatId}", panel)
        self.assertIn('aria-controls="eit-source-truth"', panel)

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
        module = (ROOT / "presentation/frontend/task-visuals/imaging-eit-controls.ts").as_uri()
        code = f"""import assert from 'node:assert/strict'; const m=await import({json.dumps(module)});
assert.equal(m.canonicalMethod('BP'),'BP');assert.equal(m.canonicalMethod('0'),null);assert.equal(m.canonicalMethod('bp'),null);
assert.equal(m.measurementRow(207,208),207);assert.equal(m.measurementRow(208,208),null);assert.equal(m.measurementRow(-1,208),null);assert.equal(m.measurementRow(1.5,208),null);
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
        self.assertEqual(len(receipt["historical_acquisition_attempts"]), 9)
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
