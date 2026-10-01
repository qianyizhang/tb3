"""Preserve source training roles, empty outputs and canonical private boundaries."""

import copy
import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tb3_medical import explanation_stories as stories
from tb3_medical.task_briefs import _brief_projection

ROOT = Path(__file__).resolve().parents[1]
ENTRY = "automedbench-full-slake-task"
STORY = Path(f"presentation/external-tasks/stories/{ENTRY}.story.md")
SOURCE_DIR = Path(f"presentation/task-explorer/{ENTRY}")
RECEIPT = Path(f"presentation/external-tasks/sources/{ENTRY}-resolution.json")
PACK = "retained-automed-slake-v1"


class SlakeStoryTests(unittest.TestCase):
    def test_native_pair_open_mode_and_unsubmitted_outputs(self):
        plan = stories.compile_story(ROOT, STORY)
        self.assertEqual(plan["reference_policy"], "reader-reference-reveal")
        self.assertIn("Official SLAKE", plan["beats"][0]["caption"])
        source = json.loads((ROOT / SOURCE_DIR / "source.json").read_text())
        helper = json.loads((ROOT / SOURCE_DIR / "helper.json").read_text())
        operation = json.loads((ROOT / SOURCE_DIR / "operation.json").read_text())
        output = json.loads((ROOT / SOURCE_DIR / "output.json").read_text())
        self.assertEqual(source["source_partition"], "train")
        self.assertEqual(source["question"], "What modality is used to take this image?")
        self.assertIsNone(source["options"])
        self.assertIsNone(source["full_membership"])
        self.assertEqual(operation["configured_mode"], "open_ended")
        self.assertFalse(helper["initially_visible"])
        self.assertEqual(
            json.loads((ROOT / SOURCE_DIR / "reference.json").read_text())["public_answer"], "MRI"
        )
        self.assertIn(
            "not Full gold",
            json.loads((ROOT / SOURCE_DIR / "reference.json").read_text())["public_answer_role"],
        )
        self.assertTrue(all(v is None for v in output["values"].values()))
        self.assertIsNone(output["score"])
        self.assertIn("all evaluator-supplied question IDs", output["accuracy"])
        self.assertIn("replaces primary accuracy", output["judge"])
        self.assertEqual(
            hashlib.sha256((ROOT / SOURCE_DIR / "image.jpg").read_bytes()).hexdigest(),
            "4e591a1ace76cbf3e539069b73e848f9fde485879a24b95f212bbe0ac1d84609",
        )
        _brief_projection(ROOT, ROOT / f"presentation/external-tasks/briefs/{ENTRY}.md")
        panel = (ROOT / "presentation/frontend/task-visuals/automed-slake-panels.tsx").read_text()
        self.assertIn("useState(false)", panel)
        self.assertIn("resetOnBackward(previous.current, state.frame)", panel)
        self.assertNotIn("useId", panel)

    def test_all_original_conditions_and_four_canonical_steps(self):
        brief = _brief_projection(ROOT, ROOT / f"presentation/external-tasks/briefs/{ENTRY}.md")
        self.assertEqual(
            [v["name"] for v in brief["variants"]],
            ["Full · Lite", "Full · Standard", "Related source listing"],
        )
        receipt = json.loads((ROOT / RECEIPT).read_text())
        self.assertEqual(brief["variants"], receipt["original_conditions"]["rows"])
        raw = (ROOT / f"presentation/external-tasks/briefs/{ENTRY}.md").read_text()
        section = "## Conditions\n" + raw.split("## Conditions\n", 1)[1].split("\n## ", 1)[0]
        self.assertEqual(
            hashlib.sha256(section.encode()).hexdigest(),
            receipt["original_conditions"]["section_sha256"],
        )
        plan = stories.compile_story(ROOT, STORY)
        operations = [b for b in plan["beats"] if b["scene"] == "operation"]
        self.assertEqual(len(operations), 4)
        self.assertEqual([b["channels"]["progress"][0] for b in operations], [0, 1 / 3, 2 / 3, 1])
        self.assertTrue(
            all(
                b["channels"]["reference"] == ([1, 1] if b["scene"] == "helper" else [0, 0])
                for b in plan["beats"]
            )
        )
        self.assertEqual(plan["durationFrames"], 1440)

    def test_source_specific_format_metric_and_attempt_boundaries(self):
        r = json.loads((ROOT / RECEIPT).read_text())
        self.assertEqual(r["task_contract"]["answer_mode"], "open_ended")
        self.assertEqual(r["task_contract"]["valid_labels"], [])
        self.assertEqual(r["illustration_basis"], "mixed")
        self.assertEqual(len(r["historical_acquisition_attempts"]), 7)
        for a in r["attempts"]:
            for k in ["action", "source", "outcome", "attempted_at"]:
                self.assertTrue(a[k])
        out = json.loads((ROOT / SOURCE_DIR / "output.json").read_text())
        self.assertIn("strict normalized yes/no", out["accuracy"])
        self.assertIn("all evaluator-supplied question IDs", out["accuracy"])
        self.assertIn("Only parsed records judged", out["judge"])
        self.assertIn("max(expected,1)", out["format_gate"])
        self.assertIn("Both-empty", out["checker_difference"])
        self.assertEqual(r["task_contract"]["calibration"]["lite_s3_exact_public_samples"], 15)
        self.assertEqual(
            r["task_contract"]["calibration"]["standard_s3_smoke_schema_questions"], [1, 10]
        )
        self.assertEqual(r["task_contract"]["calibration"]["generic_verifier_min_records"], 10)
        self.assertEqual(r["task_contract"]["source_inconsistencies"]["standard_s1_candidates"], 6)
        self.assertEqual(
            r["task_contract"]["source_inconsistencies"]["model_info_standard_candidates"], 5
        )
        self.assertFalse(r["evaluator_run"])
        self.assertFalse(r["model_run"])

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


if __name__ == "__main__":
    unittest.main()
