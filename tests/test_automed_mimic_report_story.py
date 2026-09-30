"""Keep text-proxy scoring separate from patient findings and model outcomes."""

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
ENTRY = "automedbench-full-mimic-cxr-report-task"
STORY = Path(f"presentation/external-tasks/stories/{ENTRY}.story.md")
SOURCE_DIR = Path(f"presentation/task-explorer/{ENTRY}")
RECEIPT = Path(f"presentation/external-tasks/sources/{ENTRY}-resolution.json")
PACK = "symbolic-automed-mimic-report-v1"


class MimicReportTests(unittest.TestCase):
    def test_study_contract_and_unset_text_proxy_outputs(self):
        plan = stories.compile_story(ROOT, STORY)
        self.assertEqual(plan["reference_policy"], "no-reference-assets")
        self.assertIn("physionet.org/content/mimic-cxr/2.1.0/", plan["beats"][0]["caption"])
        source = json.loads((ROOT / SOURCE_DIR / "source.json").read_text())
        helper = json.loads((ROOT / SOURCE_DIR / "helper.json").read_text())
        output = json.loads((ROOT / SOURCE_DIR / "output.json").read_text())
        self.assertEqual(source["unit"], "study")
        self.assertEqual(source["grouping_rule"], "first_three_underscore_fields")
        self.assertEqual(source["target"], "findings_only")
        self.assertIsNone(source["view_count"])
        self.assertIn("no fixed checkpoint", helper["tiers"]["lite"])
        self.assertIn("at least 3", helper["tiers"]["standard"])
        self.assertIsNone(source["pixels"])
        self.assertIsNone(source["patient_join"])
        self.assertEqual(len(helper["classes"]), 12)
        self.assertIn("clear_lungs", helper["classes"])
        self.assertIn("post_surgical_changes", helper["classes"])
        self.assertEqual(output["path"], "agent_outputs/<case_id>/report.txt")
        for key in ["text", "score", "rating", "private_reference"]:
            self.assertIsNone(output[key])
        self.assertIn("Every discovered case", output["completeness"])
        self.assertIn("Both positive sets empty", output["empty_positive"])
        _brief_projection(ROOT, ROOT / f"presentation/external-tasks/briefs/{ENTRY}.md")

    def test_reference_and_missing_cut_are_rejected(self):
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

    def test_public_rule_relabelling_and_receipt_drift_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            shutil.copytree(ROOT / SOURCE_DIR, root / SOURCE_DIR)
            for rel in [Path("presentation/assets/teaching-prefabs.json"), RECEIPT]:
                (root / rel).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / rel, root / rel)
            stories.resolve_assets(root, PACK)
            manifest = root / SOURCE_DIR / "manifest.json"
            original = json.loads(manifest.read_text())
            changed = copy.deepcopy(original)
            next(a for a in changed["assets"] if a["file"] == "helper.json")["role"] = (
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

    def test_canonical_tier_metric_and_reset_controls(self):
        subprocess.run(
            ["node", str(ROOT / "tests/automed_mimic_report_contract.cjs")],
            cwd=ROOT,
            check=True,
            capture_output=True,
        )
        text = (
            ROOT / "presentation/frontend/task-visuals/automed-mimic-report-panels.tsx"
        ).read_text()
        self.assertIn("useLayoutEffect", text)
        self.assertIn("key={state.beatId}", text)
        self.assertNotIn("useId", text)
        for reset in ["setTier('lite')", "setDetail(false)", "setMetric('macro')"]:
            self.assertIn(reset, text)

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
            warning_text=receipt["top_warning"]["text"],
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
        _ready_transition(ROOT, row, ENTRY)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel in [
                STORY,
                RECEIPT,
                Path(f"presentation/external-tasks/briefs/{ENTRY}.md"),
                Path("presentation/external-tasks/catalog.json"),
                Path("presentation/assets/teaching-prefabs.json"),
                Path("scripts/build_automed_mimic_report_assets.py"),
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
