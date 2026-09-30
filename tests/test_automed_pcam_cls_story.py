"""Symbolic taxonomy cannot become a case label or measured classifier result."""

import copy
import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from tb3_medical import explanation_stories as stories
from tb3_medical.explainer_queue import _ready_transition
from tb3_medical.task_briefs import _brief_projection

ROOT = Path(__file__).resolve().parents[1]
ENTRY = "automedbench-full-patchcamelyon-cls-task"
STORY = Path(f"presentation/external-tasks/stories/{ENTRY}.story.md")
SOURCE = Path(f"presentation/task-explorer/{ENTRY}")
RECEIPT = Path(f"presentation/external-tasks/sources/{ENTRY}-resolution.json")
PACK = "retained-automed-pcam-cls-v1"


class AutomedPcamClsTests(unittest.TestCase):
    def test_symbolic_contract_has_no_case_label_or_checkpoint(self):
        plan = stories.compile_story(ROOT, STORY)
        self.assertEqual(plan["reference_policy"], "no-reference-assets")
        self.assertIn("github.com/basveeling/pcam", plan["beats"][0]["caption"])
        s = json.loads((ROOT / SOURCE / "source.json").read_text())
        h = json.loads((ROOT / SOURCE / "helper.json").read_text())
        o = json.loads((ROOT / SOURCE / "output.json").read_text())
        self.assertEqual(h["classes"], ["negative", "positive"])
        self.assertIsNone(h["checkpoint_id2label"])
        self.assertIsNone(h["figure_row_ids"])
        self.assertIsNone(h["figure_partition"])
        self.assertIsNone(h["training_label"])
        self.assertEqual(s["tile_px"], [96, 96])
        self.assertEqual(s["center_bounds_half_open"], [32, 64, 32, 64])
        self.assertEqual(h["source_mapping"], {"0": "negative", "1": "positive"})
        for key in ("native_patch", "full_case_id", "private_label"):
            self.assertIsNone(s[key])
        for key in ("prediction", "private_reference", "score"):
            self.assertIsNone(o[key])
        self.assertTrue(all(v is None for v in o["values"].values()))
        _brief_projection(ROOT, ROOT / f"presentation/external-tasks/briefs/{ENTRY}.md")
        panel = (
            ROOT / "presentation/frontend/task-visuals/automed-pcam-cls-panels.tsx"
        ).read_text()
        self.assertIn("useLayoutEffect", panel)
        self.assertIn("shouldResetControls(previous.current, state.frame)", panel)
        self.assertIn("key={state.beatId}", panel)
        self.assertNotIn("useId", panel)
        self.assertIn("all supplied", o["accuracy"])
        self.assertIn("positive true-class support", o["balanced_accuracy"])

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

    def test_named_token_format_and_reset_controls(self):
        uri = (ROOT / "presentation/frontend/task-visuals/automed-pcam-cls-controls.ts").as_uri()
        code = f"""import assert from 'node:assert/strict'; const m=await import({json.dumps(uri)});
const classes=['negative','positive'];
assert.equal(m.upstreamBinaryClass(0),'negative');assert.equal(m.upstreamBinaryClass(1),'positive');assert.equal(m.upstreamBinaryClass(2),null);
for(const c of classes) assert.equal(m.canonicalNamedClass(c.toUpperCase(),classes),c);
assert.equal(m.canonicalNamedClass('0',classes),null);assert.equal(m.canonicalNamedClass('cancer',classes),null);
assert.deepEqual(m.submissionFields('csv'),['patient_id','label']);assert.deepEqual(m.submissionFields('json'),['label']);
assert.equal(m.shouldResetControls(12,11),true);assert.equal(m.shouldResetControls(11,12),false);
"""
        subprocess.run(["node", "--input-type=module", "-e", code], check=True, capture_output=True)

    def test_ready_transition_uses_mixed_basis_and_complete_attempts(self):
        row = copy.deepcopy(
            next(
                r
                for r in json.loads((ROOT / "presentation/EXPLAINER-LEDGER.json").read_text())[
                    "entries"
                ]
                if r["entry_id"] == ENTRY
            )
        )
        resolution = row.pop("dependency_resolution", None)
        if resolution is not None:
            row.setdefault("dependency_resolution_history", []).append(resolution)
        raw = (ROOT / RECEIPT).read_bytes()
        receipt = json.loads(raw)
        row.update(
            illustration_basis="mixed",
            actual_data_gap=receipt["actual_data_gap"],
            acquisition_route=receipt["acquisition_route"],
            warning_text=receipt["top_warning"]["text"],
            source_resolution_receipt=RECEIPT.as_posix(),
            source_review={
                "receipt": RECEIPT.as_posix(),
                "receipt_sha256": hashlib.sha256(raw).hexdigest(),
            },
            source_class="source-derived-teaching",
        )
        _ready_transition(ROOT, row, ENTRY)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bad = copy.deepcopy(receipt)
            del bad["attempts"][0]["attempted_at"]
            path = root / RECEIPT
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps(bad))
            altered = copy.deepcopy(row)
            altered["source_review"]["receipt_sha256"] = hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
            with self.assertRaisesRegex(ValueError, "attempted_at"):
                _ready_transition(root, altered, ENTRY)
        row["illustration_basis"] = "source-derived-teaching"
        with self.assertRaisesRegex(ValueError, "Invalid illustration basis"):
            _ready_transition(ROOT, row, ENTRY)


if __name__ == "__main__":
    unittest.main()
