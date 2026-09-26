"""Discriminated scripts retain v1 and fail closed at new source/recipe boundaries."""

import copy
import unittest
from pathlib import Path

from tb3_medical import explanation_stories as stories
from tb3_medical import task_briefs

ROOT = Path(__file__).resolve().parents[1]


class ExpansionTests(unittest.TestCase):
    def test_all_expansion_sources_and_projection(self):
        for path in ROOT.glob("groups/*/presentation/stories/*.story.md"):
            plan = stories.compile_story(ROOT, path)
            self.assertEqual(plan["beats"][-1]["endFrame"], plan["durationFrames"])
            self.assertEqual(plan["reference_policy"], "no-reference-assets")
            if plan["schema"] == 2:
                for locator in plan["source_locators"]:
                    self.assertIn(locator, plan["dependencies"])
                self.assertNotIn("BR030", plan["scope"])

    def test_recipe_channels_and_continuity_fail_closed(self):
        path = ROOT / "groups/registration/presentation/stories/rigid-correspondence.story.md"
        raw = path.read_text()
        for bad in [
            raw.replace("schema: 2", "schema: 2\nunknown: true"),
            raw.replace("locale: en", "locale: en\nlocale: en"),
            raw.replace("frames: 120", "frames: true", 1),
            raw.replace("transform:", "route:", 1),
            raw.replace("recipe: correspondence-v1", "recipe: missing"),
            raw.replace("no-reference-assets", "include-reference"),
        ]:
            with self.assertRaises(ValueError):
                stories.parse_expansion(bad)
        model = stories.parse_expansion(raw)
        data = copy.deepcopy(model.model_dump())
        data["beats"][1]["channels"]["transform"] = (0.5, 1.0)
        with self.assertRaises(ValueError):
            type(model).model_validate(data)

    def test_nested_planar_binding_survives_projection(self):
        data = task_briefs.load(ROOT)
        for entry_id, story_id in [
            ("wsi-hiesd-patches", "wsi-patches"),
            ("wsi-hiesd-map", "wsi-coverage"),
        ]:
            entry = next(e for e in data["entries"] if e["id"] == entry_id)
            self.assertEqual(entry["illustration"]["story_id"], story_id)
            self.assertEqual(data["explanation_stories"][story_id]["recipe"], "multiscale-v1")
            self.assertTrue(entry["reference"])
