"""Preserve source training roles, empty outputs and canonical private boundaries."""

import copy
import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from tb3_medical import explanation_stories as stories
from tb3_medical.explainer_queue import _ready_transition, prepare
from tb3_medical.task_briefs import _brief_projection

ROOT = Path(__file__).resolve().parents[1]
ENTRY = "automedbench-full-vqa-rad-task"
STORY = Path(f"presentation/external-tasks/stories/{ENTRY}.story.md")
SOURCE_DIR = Path(f"presentation/task-explorer/{ENTRY}")
RECEIPT = Path(f"presentation/external-tasks/sources/{ENTRY}-resolution.json")
PACK = "retained-automed-vqa-rad-v1"


class VqaRadStoryTests(unittest.TestCase):
    def test_native_pair_open_mode_and_unsubmitted_outputs(self):
        plan = stories.compile_story(ROOT, STORY)
        self.assertEqual(plan["reference_policy"], "no-reference-assets")
        self.assertIn("osf.io/89kps/", plan["beats"][0]["caption"])
        source = json.loads((ROOT / SOURCE_DIR / "source.json").read_text())
        helper = json.loads((ROOT / SOURCE_DIR / "helper.json").read_text())
        operation = json.loads((ROOT / SOURCE_DIR / "operation.json").read_text())
        output = json.loads((ROOT / SOURCE_DIR / "output.json").read_text())
        self.assertEqual(source["source_partition"], "train")
        self.assertEqual(source["question"], "are regions of the brain infarcted?")
        self.assertIsNone(source["options"])
        self.assertIsNone(source["full_membership"])
        self.assertEqual(operation["configured_mode"], "open_ended")
        self.assertFalse(helper["initially_visible"])
        self.assertEqual(helper["public_answer"], "yes")
        self.assertIn("not Full gold", helper["public_answer_role"])
        self.assertTrue(all(v is None for v in output["values"].values()))
        self.assertIsNone(output["score"])
        self.assertIn("all discovered question_ids", output["accuracy"])
        self.assertIn("replaces primary accuracy", output["judge"])
        self.assertEqual(
            hashlib.sha256((ROOT / SOURCE_DIR / "image.jpg").read_bytes()).hexdigest(),
            "379dff334415856e4ee966f9abfcba8d50f2a2a3534d4965bbd6c462baeaada2",
        )
        _brief_projection(ROOT, ROOT / f"presentation/external-tasks/briefs/{ENTRY}.md")
        panel = (ROOT / "presentation/frontend/task-visuals/automed-vqa-rad-panels.tsx").read_text()
        self.assertIn("useState(false)", panel)
        self.assertIn("state.frame < previous.current", panel)
        self.assertNotIn("useId", panel)

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
            manifest = root / SOURCE_DIR / "manifest.json"
            original = json.loads(manifest.read_text())
            changed = copy.deepcopy(original)
            next(x for x in changed["assets"] if x["file"] == "image.jpg")["role"] = (
                "reader-reference-reveal"
            )
            manifest.write_text(json.dumps(changed))
            with self.assertRaisesRegex(ValueError, "incorrectly classified"):
                stories.resolve_assets(root, PACK)
            manifest.write_text(json.dumps(original))
            with (root / RECEIPT).open("a") as stream:
                stream.write("\n")
            with self.assertRaisesRegex(ValueError, "Stale symbolic source pin"):
                stories.resolve_assets(root, PACK)

    def test_canonical_controls_and_public_annotation_reset(self):
        subprocess.run(
            ["node", str(ROOT / "tests/automed_vqa_rad_contract.cjs")],
            cwd=ROOT,
            check=True,
            capture_output=True,
        )
        panel = (ROOT / "presentation/frontend/task-visuals/automed-vqa-rad-panels.tsx").read_text()
        for token in [
            "useLayoutEffect",
            "setTier('lite')",
            "setCalibration(false)",
            "setDetail(false)",
            "setMetric('accuracy')",
            "data-vqa-rad-step",
            "publicAnnotationVisible(state, revealed)",
        ]:
            self.assertIn(token, panel)
        self.assertNotIn("useId", panel)
        self.assertNotIn("<details", panel)
        self.assertTrue(
            all(
                b["channels"]["reference"] == [0.0, 0.0]
                for b in stories.compile_story(ROOT, STORY)["beats"]
            )
        )

    def test_pending_mixed_prepare_and_structured_source_receipt(self):
        original = (ROOT / "presentation/EXPLAINER-LEDGER.json").read_bytes()
        data = json.loads(original)
        row = next(r for r in data["entries"] if r["entry_id"] == ENTRY)
        resolution = row.pop("dependency_resolution", None)
        if resolution is not None:
            row.setdefault("dependency_resolution_history", []).append(resolution)
        receipt = json.loads((ROOT / RECEIPT).read_text())
        row.update(
            reviewed_disposition="pending-operation-review",
            story_id=ENTRY,
            blocking_dependency=None,
            illustration_basis="mixed",
            source_class="source-derived-teaching",
            actual_data_gap=receipt["actual_data_gap"],
            acquisition_route=receipt["acquisition_route"],
            warning_text=receipt["warning_text"],
            source_resolution_receipt=RECEIPT.as_posix(),
            source_review={
                "receipt": RECEIPT.as_posix(),
                "receipt_sha256": hashlib.sha256((ROOT / RECEIPT).read_bytes()).hexdigest(),
            },
        )
        _ready_transition(ROOT, row, ENTRY)
        self.assertTrue(receipt["attempts"])
        for attempt in receipt["attempts"]:
            self.assertTrue(
                all(attempt.get(k) for k in ["action", "source", "outcome", "attempted_at"])
            )
        self.assertEqual(receipt["task_contract"]["standard_s1_candidate_count"], 6)
        self.assertEqual(receipt["task_contract"]["model_info_candidate_count"], 5)
        self.assertEqual(receipt["task_contract"]["actual_calibration_verifier_min"], 10)
        try:
            (ROOT / "presentation/EXPLAINER-LEDGER.json").write_text(json.dumps(data))
            with tempfile.TemporaryDirectory(dir=ROOT / ".local") as out:
                prepare(ROOT, ENTRY, Path(out) / "packet")
        finally:
            (ROOT / "presentation/EXPLAINER-LEDGER.json").write_bytes(original)


if __name__ == "__main__":
    unittest.main()
