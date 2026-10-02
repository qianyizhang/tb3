"""Family boundary, selected asset closure and served publication regressions."""

import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tb3_medical import explanation_stories, storage
from tb3_medical.explainers.compiler import compile_views
from tb3_medical.explainers.families import restoration

ROOT = Path(__file__).resolve().parents[1]
STORIES = [
    "automedbench-full-mri-sr-task",
    "automedbench-full-ctorg-ctsr-task",
    "automedbench-full-msd-pancreas-ctsr-task",
    "automedbench-full-totalsegmentator-ctsr-task",
]


class ExplainerFrameworkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plans = {
            key: explanation_stories.compile_story(
                ROOT, Path(f"presentation/external-tasks/stories/{key}.story.md")
            )
            for key in STORIES
        }

    def test_family_keeps_exact_scientific_copy_and_selected_assets(self):
        before = copy.deepcopy(self.plans)
        views = compile_views(ROOT, self.plans)
        self.assertEqual(self.plans, before, "View compilation cannot change canonical timing")
        for key, view in views.items():
            with self.subTest(story=key):
                assets = view["bundle"]["assets"]
                self.assertEqual(len(assets), 6)
                self.assertEqual(
                    {a["role"] for a in assets},
                    {
                        "input-contract",
                        "helper-contract",
                        "operation-contract",
                        "output-contract",
                        "license",
                    },
                )
                for asset in assets:
                    self.assertIn(f"/{key}/", asset["path"])
                    self.assertEqual(storage.sha(ROOT / asset["path"]), asset["sha256"])
                for record in ("source", "helper", "operation", "output"):
                    raw = storage.read(ROOT / f"presentation/task-explorer/{key}/{record}.json")
                    for field, value in view[record].items():
                        self.assertEqual(value, raw[field])
                self.assertIn("Private", view["output"]["boundary"])
                self.assertEqual(view["bundle"]["reference_policy"], "no-reference-assets")
        self.assertIn("720", views[STORIES[0]]["geometry"]["output"])
        self.assertIn("normalized", views[STORIES[0]]["geometry"]["declared"])
        for key in STORIES[1:]:
            self.assertIn("HU", views[key]["geometry"]["declared"])
            self.assertIn("Same", views[key]["geometry"]["mapping"])

    def test_family_rejects_wrong_binding_and_observed_reference(self):
        plan = copy.deepcopy(self.plans[STORIES[0]])
        plan["reference_policy"] = "reader-reference-reveal"
        with self.assertRaisesRegex(ValueError, "binding differ"):
            restoration.compile_view(ROOT, plan)
        original = storage.read

        def read(path):
            result = original(path)
            if str(path).endswith(STORIES[0] + "/source.json"):
                result["private_reference"] = "unexpected-reference.npy"
            return result

        with (
            patch.object(storage, "read", side_effect=read),
            self.assertRaisesRegex(ValueError, "Unexpected observed evidence"),
        ):
            restoration.compile_view(ROOT, self.plans[STORIES[0]])

    def test_family_validates_definition_and_keeps_legacy_unbound(self):
        self.assertEqual(compile_views(ROOT, {}), {})
        route = explanation_stories.compile_story(
            ROOT,
            Path("groups/tubular-anatomy/presentation/stories/route-unfold-teaching-v1.story.md"),
        )
        self.assertIsNone(restoration.compile_view(ROOT, route))
        definition = storage.read(ROOT / restoration.DEFINITIONS)
        definition["unknown"] = "not an authoring field"
        with self.assertRaises(ValueError):
            restoration.Definitions.model_validate(definition)

    def test_served_externalization_preserves_source_bytes(self):
        from tb3_medical import frontend
        from tb3_medical.explainers.packaging import prepare_served

        pixel = "data:image/png;base64,aGVsbG8="
        data = {
            "explanation_stories": {},
            "explainer_views": {},
            "image": pixel,
            "same_image": f'<img src="{pixel}">',
            "local_sources": {"raw": {"content": pixel}},
            "source_snapshot": pixel,
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            build = root / frontend.BUILD_DIR
            build.mkdir(parents=True)
            (build / "manifest.json").write_text(json.dumps({"servedOutputs": [], "outputs": {}}))
            with patch.object(frontend, "assets", return_value=("", "")):
                result, script = prepare_served(root, root / "site/index.html", data)
            self.assertEqual(result["local_sources"], data["local_sources"])
            self.assertEqual(result["source_snapshot"], pixel)
            self.assertIn(result["image"], result["same_image"])
            self.assertEqual(len(list((root / "site/assets").iterdir())), 1)
            self.assertEqual((root / "site" / result["image"]).read_bytes(), b"hello")
            self.assertIn('type="module"', script)
