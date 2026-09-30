"""Protect symbolic PathCap100 output, reference boundaries and source pinning."""

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
STORY = Path(
    "presentation/external-tasks/stories/automedbench-full-pathology-caption-100-task.story.md"
)
SOURCE = Path("presentation/task-explorer/automedbench-full-pathology-caption-100-task")
ENTRY = "automedbench-full-pathology-caption-100-task"
SOURCE_DIR = SOURCE
RECEIPT = Path(f"presentation/external-tasks/sources/{ENTRY}-resolution.json")
PACK = "retained-automed-pathology-caption-100-workflow-v1"


class AutomedPathology100StoryTests(unittest.TestCase):
    def test_symbolic_compilation_preserves_empty_patient_and_result_fields(self):
        plan = stories.compile_story(ROOT, STORY)
        self.assertEqual(plan["source_class"], "symbolic-protocol")
        self.assertEqual(plan["reference_policy"], "no-reference-assets")
        self.assertEqual(
            [b["channels"]["progress"][0] for b in plan["beats"] if b["scene"] == "operation"],
            [0, 0.5, 1],
        )
        self.assertIn("huggingface.co/datasets/jamessyx/PathCap", plan["beats"][0]["caption"])
        output = json.loads((ROOT / SOURCE / "output.json").read_text())
        fixture = json.loads((ROOT / SOURCE / "fixture.json").read_text())
        for key in [
            "participant_prediction",
            "checkpoint",
            "score",
            "private_reference",
            "actual_case_ids",
        ]:
            self.assertIsNone(output[key])
        self.assertIsNone(fixture["actual_prediction"])
        self.assertIsNone(fixture["actual_reference"])
        self.assertTrue(fixture["toy_row_is_not_displayed_native_case"])

    def test_study_is_symbolic_and_scorer_discrepancy_is_preserved(self):
        source = json.loads((ROOT / SOURCE / "source.json").read_text())
        study = json.loads((ROOT / SOURCE / "study.json").read_text())
        self.assertEqual(source["native_examples"], {"images": 0, "reports": 0, "actual_cases": 0})
        self.assertEqual(len(study["image_sockets"]), 1)
        self.assertEqual(study["reports_required"], 1)
        self.assertIsNone(study["actual_images"])
        self.assertIn("CXR-regex", source["runtime_discrepancy"])
        self.assertIn("Private evaluator", source["source_roles"]["reference"])
        self.assertEqual(source["selection"]["expected_case_count"], 100)
        self.assertEqual(source["selection"]["relationship_to_500"], "unknown")
        self.assertFalse(source["selection"]["expected_count_enforced_by_evaluator"])

    def test_reference_outside_reference_scene_and_implicit_cut_are_rejected(self):
        doc = stories.parse_document((ROOT / STORY).read_text())
        data = {**doc.header, "beats": list(doc.beats)}
        changed = copy.deepcopy(data)
        changed["beats"][0]["channels"]["reference"] = [0, 1]
        with self.assertRaisesRegex(ValueError, "no private reference"):
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
                Path(
                    "presentation/external-tasks/sources/automedbench-full-pathology-caption-100-task-resolution.json"
                ),
                Path(
                    "presentation/external-tasks/briefs/automedbench-full-pathology-caption-100-task.md"
                ),
            ]:
                (root / rel).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / rel, root / rel)
            stories.resolve_assets(root, PACK)
            mp = root / SOURCE / "manifest.json"
            original = json.loads(mp.read_text())
            changed = copy.deepcopy(original)
            next(a for a in changed["assets"] if a["file"] == "fixture.json")["provenance"] = (
                "source-derived-teaching"
            )
            mp.write_text(json.dumps(changed))
            with self.assertRaisesRegex(ValueError, "incorrectly classified"):
                stories.resolve_assets(root, PACK)
            mp.write_text(json.dumps(original))
            receipt = (
                root
                / "presentation/external-tasks/sources/automedbench-full-pathology-caption-100-task-resolution.json"
            )
            receipt.write_text(receipt.read_text() + "\n")
            with self.assertRaisesRegex(ValueError, "Stale symbolic source pin"):
                stories.resolve_assets(root, PACK)

    def test_ready_transition_uses_symbolic_basis_and_complete_attempts(self):
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
            illustration_basis="symbolic",
            actual_data_gap=receipt["actual_data_gap"],
            acquisition_route=receipt["acquisition_route"],
            warning_text=receipt["warning_text"],
            source_resolution_receipt=RECEIPT.as_posix(),
            source_review={
                "receipt": RECEIPT.as_posix(),
                "receipt_sha256": hashlib.sha256(raw).hexdigest(),
            },
            source_class="symbolic-protocol",
        )
        row.update(
            reviewed_disposition="pending-operation-review",
            story_id=ENTRY,
            blocking_dependency=None,
        )
        _brief_projection(ROOT, ROOT / f"presentation/external-tasks/briefs/{ENTRY}.md")
        subprocess.run(
            ["node", str(ROOT / "tests/automed_pathology100_contract.cjs")],
            check=True,
            capture_output=True,
        )
        _ready_transition(ROOT, row, ENTRY)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel in [
                STORY,
                RECEIPT,
                Path(f"presentation/external-tasks/briefs/{ENTRY}.md"),
                Path("presentation/external-tasks/catalog.json"),
                Path("presentation/assets/teaching-prefabs.json"),
                Path("scripts/build_automed_pathology100_assets.py"),
                *map(Path, stories.COMPILER_SOURCES),
            ]:
                (root / rel).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / rel, root / rel)
            shutil.copytree(ROOT / SOURCE_DIR, root / SOURCE_DIR)
            for rel, key in [
                ("presentation/EXPLAINER-SCOPE.json", "entry_id"),
                ("presentation/EXPLAINER-LEDGER.json", "entry_id"),
            ]:
                data = json.loads((ROOT / rel).read_text())
                data["entries"] = [r for r in data["entries"] if r[key] == ENTRY]
                if rel.endswith("EXPLAINER-LEDGER.json"):
                    data["entries"] = [row]
                (root / rel).write_text(json.dumps(data))
            packet = prepare(root, ENTRY, ".local/ready-packet")
            self.assertEqual(packet["story_id"], ENTRY)
            self.assertEqual(packet["ledger"]["status"], "pending-operation-review")

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
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            other = Path(
                "presentation/external-tasks/stories/automedbench-full-skin-lesion-cls-task.story.md"
            )
            text = (ROOT / other).read_text()
            doc = stories.parse_document(text)
            for rel in [
                *map(Path, stories.COMPILER_SOURCES),
                *map(Path, doc.header["source_locators"]),
            ]:
                (root / rel).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / rel, root / rel)
            (root / other).parent.mkdir(parents=True, exist_ok=True)
            (root / other).write_text(
                text.replace(
                    "source_class: source-derived-teaching", "source_class: symbolic-protocol"
                )
            )
            with self.assertRaisesRegex(ValueError, "Recipe provenance mismatch"):
                stories.compile_story(root, other)
        row["illustration_basis"] = "symbolic-protocol"
        with self.assertRaisesRegex(ValueError, "Invalid illustration basis"):
            _ready_transition(ROOT, row, ENTRY)


if __name__ == "__main__":
    unittest.main()
