"""Protect symbolic VQA output, reference boundaries and source pinning."""

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
STORY = Path("presentation/external-tasks/stories/automedbench-full-vqa-kvasir-task.story.md")
ENTRY = "automedbench-full-vqa-kvasir-task"
RECEIPT = Path(f"presentation/external-tasks/sources/{ENTRY}-resolution.json")
SOURCE_DIR = Path(f"presentation/task-explorer/{ENTRY}")
SOURCE = Path("presentation/task-explorer/automedbench-full-vqa-kvasir-task")
PACK = "retained-automed-kvasir-source-v1"


class AutomedKvasirStoryTests(unittest.TestCase):
    def test_symbolic_compilation_preserves_empty_patient_and_result_fields(self):
        plan = stories.compile_story(ROOT, STORY)
        self.assertEqual(plan["source_class"], "source-derived-teaching")
        self.assertEqual(plan["reference_policy"], "reader-reference-reveal")
        self.assertEqual(
            [b["channels"]["progress"][0] for b in plan["beats"] if b["scene"] == "operation"],
            [0, 0.5, 1],
        )
        self.assertIn("HF SimulaMet-HOST/Kvasir-VQA", plan["beats"][0]["caption"])
        output = json.loads((ROOT / SOURCE / "output.json").read_text())
        fixture = json.loads((ROOT / SOURCE / "fixture.json").read_text())
        self.assertIsNone(fixture["actual_prediction"])
        self.assertIsNone(fixture["actual_reference"])
        for key in [
            "predicted_label",
            "predicted_answer",
            "raw_model_output",
            "model_name",
            "runtime_s",
            "private_reference",
            "score",
        ]:
            self.assertIsNone(output[key])
        source = json.loads((ROOT / SOURCE / "source.json").read_text())
        reference = json.loads((ROOT / SOURCE / "reference.json").read_text())
        self.assertNotIn("label", source["source_question"])
        self.assertNotIn("public_reference", source)
        self.assertEqual(source["source_question"]["source_row_index"], 0)
        self.assertEqual(reference["answer"], "ulcerative colitis")
        self.assertNotIn("answer", source["source_question"])
        self.assertNotIn("source", source["source_question"])
        self.assertEqual(reference["category"], "Ulcerative Colitis")
        manifest = json.loads((ROOT / SOURCE / "manifest.json").read_text())
        self.assertEqual(
            next(a for a in manifest["assets"] if a["file"] == "reference.json")["role"],
            "reader-reference-reveal",
        )

    def test_reference_outside_reference_scene_and_implicit_cut_are_rejected(self):
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

    def test_symbolic_assets_cannot_be_relabelled_or_unpinned(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            shutil.copytree(ROOT / SOURCE, root / SOURCE)
            for rel in [
                Path("presentation/assets/teaching-prefabs.json"),
                Path(
                    "presentation/external-tasks/sources/automedbench-full-vqa-kvasir-task-resolution.json"
                ),
                Path("presentation/external-tasks/briefs/automedbench-full-vqa-kvasir-task.md"),
            ]:
                (root / rel).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / rel, root / rel)
            stories.resolve_assets(root, PACK)
            mp = root / SOURCE / "manifest.json"
            original = json.loads(mp.read_text())
            changed = copy.deepcopy(original)
            next(a for a in changed["assets"] if a["file"] == "reference.json")["role"] = (
                "illustration"
            )
            mp.write_text(json.dumps(changed))
            with self.assertRaisesRegex(ValueError, "incorrectly classified"):
                stories.resolve_assets(root, PACK)
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
                / "presentation/external-tasks/sources/automedbench-full-vqa-kvasir-task-resolution.json"
            )
            receipt.write_text(receipt.read_text() + "\n")
            with self.assertRaisesRegex(ValueError, "Stale symbolic source pin"):
                stories.resolve_assets(root, PACK)

    def test_canonical_controls_reader_request_and_native_parity(self):
        subprocess.run(
            ["node", str(ROOT / "tests/automed_kvasir_contract.cjs")],
            cwd=ROOT,
            check=True,
            capture_output=True,
        )
        text = (
            ROOT / "presentation/frontend/task-visuals/automedbench-full-vqa-kvasir-task-panels.tsx"
        ).read_text()
        for token in [
            "useLayoutEffect",
            "setRevealed(false)",
            "setTier('lite')",
            "setCalibration(false)",
            "setFormat(false)",
            'aria-controls="kvasir-public-reference"',
            "data-kvasir-step",
        ]:
            self.assertIn(token, text)
        self.assertNotIn("useId", text)
        self.assertEqual(
            hashlib.sha256((ROOT / SOURCE_DIR / "source-preview.jpeg").read_bytes()).hexdigest(),
            "1500eb8e766c4eb761518b1c5829316416bcd348d06885e146cbd4d2c8ec0de8",
        )
        _brief_projection(ROOT, ROOT / f"presentation/external-tasks/briefs/{ENTRY}.md")
        r = json.loads((ROOT / RECEIPT).read_text())
        self.assertEqual(r["license_context"]["license"], "CC-BY-NC-4.0")
        self.assertEqual(r["task_contract"]["task_specific_smoke_bounds"], [1, 10])
        self.assertEqual(r["task_contract"]["generic_validation_min"], 10)
        self.assertEqual(r["task_contract"]["standard_candidate_count"], 6)
        dispatch = (ROOT / "presentation/frontend/task-visuals/operation-view.tsx").read_text()
        self.assertIn("<AutomedKvasirScene key={state.beatId}", dispatch)

    def test_pending_mixed_prepare_and_structured_attempts(self):
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
        row.update(
            reviewed_disposition="pending-operation-review",
            story_id=ENTRY,
            blocking_dependency=None,
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
                Path("scripts/build_automed_kvasir_assets.py"),
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


if __name__ == "__main__":
    unittest.main()
