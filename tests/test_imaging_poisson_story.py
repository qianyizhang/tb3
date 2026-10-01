"""Protect Poisson output, reference boundaries and source pinning."""

import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tb3_medical import explanation_stories as stories

ROOT = Path(__file__).resolve().parents[1]
STORY = Path("presentation/external-tasks/stories/imaging101-ct-poisson-lowdose.story.md")
SOURCE = Path("presentation/task-explorer/imaging101-ct-poisson-lowdose")
PACK = "retained-imaging101-poisson-source-v1"


class ImagingPoissonStoryTests(unittest.TestCase):
    def test_compilation_preserves_empty_measurement_and_result_fields(self):
        plan = stories.compile_story(ROOT, STORY)
        self.assertEqual(plan["source_class"], "source-derived-teaching")
        self.assertEqual(plan["reference_policy"], "reader-reference-reveal")
        self.assertEqual(
            [b["channels"]["progress"][0] for b in plan["beats"] if b["scene"] == "operation"],
            [0, 0.5, 1],
        )
        self.assertIn("Official Imaging101", plan["beats"][0]["caption"])
        output = json.loads((ROOT / SOURCE / "output.json").read_text())
        fixture = json.loads((ROOT / SOURCE / "fixture.json").read_text())
        self.assertIsNone(fixture["actual_output"])
        self.assertIsNone(fixture["clean_reference"])
        for key in ["reconstruction_npy", "actual_image", "quality_score"]:
            self.assertIsNone(output[key])
        self.assertIsNone(fixture["clean_reference"])
        reference = json.loads((ROOT / SOURCE / "reference.json").read_text())
        self.assertIsNone(reference["clean_image"])
        self.assertEqual(fixture["I0"], 300)
        self.assertEqual(fixture["floored_counts"], [300, 100, 1])
        self.assertAlmostEqual(fixture["postlog"][2], 5.703782474656201)
        self.assertEqual(reference["expected_count_subset"]["units"], "expected photons/bin")

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
                    "presentation/external-tasks/sources/imaging101-ct-poisson-lowdose-resolution.json"
                ),
                Path("presentation/external-tasks/briefs/imaging101-ct-poisson-lowdose.md"),
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
                / "presentation/external-tasks/sources/imaging101-ct-poisson-lowdose-resolution.json"
            )
            receipt.write_text(receipt.read_text() + "\n")
            with self.assertRaisesRegex(ValueError, "Stale symbolic source pin"):
                stories.resolve_assets(root, PACK)

    def test_toy_floor_log_and_source_version_are_not_reconstruction(self):
        import importlib.util
        import math

        module_path = ROOT / "scripts/build_imaging_poisson_assets.py"
        spec = importlib.util.spec_from_file_location("safe_poisson_builder", module_path)
        builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(builder)
        self.assertEqual(builder.illustrative_postlog(0, 300), builder.illustrative_postlog(1, 300))
        self.assertAlmostEqual(builder.illustrative_postlog(100, 300), math.log(3))
        self.assertLess(builder.illustrative_postlog(301, 300), 0)
        for incident in [0, -1, float("nan"), float("inf")]:
            with self.assertRaisesRegex(ValueError, "positive incident"):
                builder.illustrative_postlog(100, incident)
        receipt = json.loads(
            (
                ROOT
                / "presentation/external-tasks/sources/imaging101-ct-poisson-lowdose-resolution.json"
            ).read_text()
        )
        self.assertEqual(sum(x["manifest_match"] for x in receipt["source_inputs"]), 4)
        self.assertTrue(
            all(
                x["action"] == "retained-validation" and x["attempted_at"] and x["source"]
                for x in receipt["attempts"]
            )
        )
        self.assertEqual(receipt["historical_attempts"][0]["date"], "2026-10-01")
        self.assertIn("L2-relative", receipt["task_contract"]["backend_difference"])
        rules = receipt["task_contract"]["constant_reference_rules"]
        self.assertEqual(rules["task_local_helper"], 0.0)
        self.assertEqual(rules["filesystem_generic"], "infinity")
        reference = json.loads((ROOT / SOURCE / "reference.json").read_text())
        self.assertEqual(reference["constant_reference_rules"], rules)
        # These are source guard receipts; no task/evaluator function is imported or run.
        local_pin = next(
            p for p in receipt["source_files"] if p["path"].endswith("/src/visualization.py")
        )
        generic_pin = next(
            p for p in receipt["source_files"] if p["path"].endswith("/reference_scoring.py")
        )
        self.assertNotEqual(local_pin["sha256"], generic_pin["sha256"])
        import ast

        evidence = receipt["constant_range_source_evidence"]
        local_tree = ast.parse(evidence["task_local_helper"]["verified_source_excerpt"])
        guard = next(
            n
            for n in ast.walk(local_tree)
            if isinstance(n, ast.If) and isinstance(n.test, ast.Compare)
        )
        self.assertEqual(guard.test.comparators[0].value, 0)
        self.assertEqual(guard.body[0].value.value, 0.0)
        generic_tree = ast.parse(evidence["filesystem_generic"]["verified_source_excerpt"])
        assignment = next(
            n
            for n in ast.walk(generic_tree)
            if isinstance(n, ast.Assign)
            and isinstance(n.targets[0], ast.Name)
            and n.targets[0].id == "nrmse"
        )
        self.assertIsInstance(assignment.value, ast.IfExp)
        self.assertEqual(assignment.value.orelse.func.id, "float")
        self.assertEqual(assignment.value.orelse.args[0].value, "inf")

    def test_reader_fixture_is_conditional_and_shared_reset_is_preserved(self):
        panel = (
            ROOT / "presentation/frontend/task-visuals/imaging101-ct-poisson-lowdose-panels.tsx"
        ).read_text()
        self.assertIn("referenceVisible(state, revealed) ?", panel)
        self.assertIn("useLayoutEffect", panel)
        self.assertIn("state.frame < previous.current", panel)
        self.assertIn("setRevealed(false)", panel)
        self.assertNotIn("<details", panel)
        visual = (ROOT / "presentation/frontend/task-visuals/TaskVisual.tsx").read_text()
        self.assertGreaterEqual(visual.count("key={player.resetRevision}"), 3)
        reference = json.loads((ROOT / SOURCE / "reference.json").read_text())
        self.assertIn("ground truth", reference["expected_count_subset"]["prohibited_roles"])
        self.assertEqual(reference["expected_count_subset"]["view_indices"], [120, 136])
        self.assertEqual(reference["expected_count_subset"]["channel_indices"], [175, 191])


if __name__ == "__main__":
    unittest.main()
