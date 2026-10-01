"""Native ultrasound units, source helper, output and guarded pending preparation."""

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
ENTRY = "imaging101-ultrasound-sos-tomography"
STORY = Path(f"presentation/external-tasks/stories/{ENTRY}.story.md")
SOURCE = Path(f"presentation/task-explorer/{ENTRY}")
RECEIPT = Path(f"presentation/external-tasks/sources/{ENTRY}-resolution.json")
PACK = "retained-imaging-ultrasound-sos-v1"


class UltrasoundStoryTests(unittest.TestCase):
    def test_native_units_domains_and_empty_outputs(self):
        p = stories.compile_story(ROOT, STORY)
        self.assertEqual(p["reference_policy"], "no-reference-assets")
        self.assertIn("Time units unresolved", p["beats"][0]["caption"])
        self.assertIn("starpacker52/imaging-101", p["beats"][0]["caption"])
        m = json.loads((ROOT / SOURCE / "measurement.json").read_text())
        h = json.loads((ROOT / SOURCE / "helper.json").read_text())
        o = json.loads((ROOT / SOURCE / "output.json").read_text())
        self.assertEqual(m["shape"], [1, 128, 60])
        self.assertEqual(m["angles"], list(range(0, 180, 3)))
        self.assertEqual(len(m["native_detector_trace"]), 60)
        self.assertNotIn("source_center_speed", m)
        self.assertFalse(h["initially_visible"])
        self.assertTrue(h["solver_visible_truth"])
        self.assertIsNone(h["private_reference"])
        for k in ["prediction", "map", "reference", "score"]:
            self.assertIsNone(o[k])
        self.assertIn("16384", o["metric"])
        self.assertIn("10404", o["task_metric"])
        self.assertIn("0.0", o["task_metric"])
        self.assertIn("infinity", o["task_metric"])
        self.assertIn("sos_phantom", o["reference_selection"])
        _brief_projection(ROOT, ROOT / f"presentation/external-tasks/briefs/{ENTRY}.md")
        panels = (
            ROOT / "presentation/frontend/task-visuals/imaging-ultrasound-sos-panels.tsx"
        ).read_text()
        self.assertNotIn("useId", panels)
        self.assertIn("useLayoutEffect", panels)
        self.assertIn("show && stable", panels)
        self.assertEqual(p["durationFrames"], 1176)
        self.assertEqual(p["beats"][5]["scene"], "helper")
        self.assertIn("key={state.beatId}", panels)
        self.assertIn('aria-controls="sos-native-source-truth"', panels)

    def test_reference_and_implicit_cut_rejected(self):
        d = stories.parse_document((ROOT / STORY).read_text())
        data = {**d.header, "beats": list(d.beats)}
        changed = copy.deepcopy(data)
        changed["beats"][0]["channels"]["reference"] = [0, 1]
        with self.assertRaisesRegex(ValueError, "no private reference"):
            stories.ADAPTER.validate_python(changed)
        changed = copy.deepcopy(data)
        del changed["beats"][1]["cut"]
        with self.assertRaisesRegex(ValueError, "explicit cut|discontinuity"):
            stories.ADAPTER.validate_python(changed)

    def test_provenance_and_stale_source_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            shutil.copytree(ROOT / SOURCE, root / SOURCE)
            for rel in [Path("presentation/assets/teaching-prefabs.json"), RECEIPT]:
                (root / rel).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / rel, root / rel)
            stories.resolve_assets(root, PACK)
            path = root / SOURCE / "manifest.json"
            d = json.loads(path.read_text())
            next(x for x in d["assets"] if x["file"] == "measurement.json")["role"] = (
                "reader-reference-reveal"
            )
            path.write_text(json.dumps(d))
            with self.assertRaisesRegex(ValueError, "incorrectly classified"):
                stories.resolve_assets(root, PACK)
            shutil.copyfile(ROOT / SOURCE / "manifest.json", path)
            (root / RECEIPT).write_text((root / RECEIPT).read_text() + "\n")
            with self.assertRaisesRegex(ValueError, "Stale symbolic source pin"):
                stories.resolve_assets(root, PACK)

    def test_pure_native_index_sign_and_reset(self):
        module = (
            ROOT / "presentation/frontend/task-visuals/imaging-ultrasound-sos-controls.ts"
        ).as_uri()
        code = f"import assert from 'node:assert/strict';const m=await import({json.dumps(module)});assert.equal(m.canonicalMethod('tv'),'tv');assert.equal(m.canonicalMethod('reconstruction'),null);assert.equal(m.nativeAngle(59),59);for(const x of[-1,60,0.5])assert.equal(m.nativeAngle(x),null);assert.ok(m.signedSlowness(1450)>0);assert.equal(m.signedSlowness(1500),0);assert.ok(m.signedSlowness(2500)<0);assert.equal(m.signedSlowness(0),null);assert.equal(m.resetOnBackward(20,19),true);assert.equal(m.resetOnBackward(19,20),false);"
        subprocess.run(["node", "--input-type=module", "-e", code], check=True, capture_output=True)

    def test_ready_transition_and_actual_pending_prepare(self):
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
            warning_text=receipt["display_warning"],
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
                Path("scripts/build_imaging_ultrasound_sos_assets.py"),
                *map(Path, stories.COMPILER_SOURCES),
            ]:
                (root / rel).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / rel, root / rel)
            shutil.copytree(ROOT / SOURCE, root / SOURCE)
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
