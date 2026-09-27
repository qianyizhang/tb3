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
            self.assertEqual(
                plan["reference_policy"],
                "reader-reference-reveal"
                if plan["recipe"]
                in {
                    "mixed-tissue-v1",
                    "prototype-identity-v1",
                    "mask-screen-v1",
                    "anatomy-curation-v1",
                    "respiratory-v1",
                    "registration-analysis-v1",
                    "resect-correspondence-v1",
                    "resect-pilot-v1",
                    "vessel-source-v1",
                    "airway-repair-v1",
                    "topbrain-screen-v1",
                    "hubmap-inventory-v1",
                    "tiger-context-v1",
                }
                else "no-reference-assets",
            )
            if plan["schema"] == 2:
                for locator in plan["source_locators"]:
                    self.assertIn(locator, plan["dependencies"])
                self.assertNotIn("BR030", plan["scope"])

    def test_recipe_channels_and_continuity_fail_closed(self):
        path = ROOT / "groups/registration/presentation/stories/rigid-correspondence.story.md"
        raw = path.read_text().replace("frames:", "show_deformed_target: false\nframes:")
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

    def test_source_screen_scene_changes_require_explicit_cuts(self):
        for group, name in [
            ("anatomy-audit", "mask-reasoning-study"),
            ("anatomy-audit", "anatomy-curation"),
            ("registration", "respiratory-correspondence"),
            ("registration", "registration-failure-analysis"),
            ("registration", "resect-point-correspondence"),
            ("registration", "resect-point-pilot"),
            ("tubular-anatomy", "vessel-source-screen"),
            ("tubular-anatomy", "airway-repair"),
            ("tubular-anatomy", "topbrain-screen"),
            ("lesion-localization", "hubmap-inventory"),
            ("lesion-localization", "tiger-context"),
        ]:
            path = ROOT / f"groups/{group}/presentation/stories/{name}.story.md"
            model = stories.parse_expansion(path.read_text())
            data = copy.deepcopy(model.model_dump(by_alias=True))
            index = next(
                i
                for i, beat in enumerate(data["beats"])
                if i and beat["scene"] != data["beats"][i - 1]["scene"]
            )
            data["beats"][index]["cut"] = "continuous"
            # Hold numeric channels continuous so only the scene boundary is invalid.
            for beat in data["beats"]:
                beat["channels"] = dict.fromkeys(beat["channels"], (0.0, 0.0))
            with self.assertRaisesRegex(ValueError, "Changing source scenes"):
                type(model).model_validate(data)

    def test_curation_pack_rejects_wrong_source_terms(self):
        import json
        from unittest.mock import patch

        path = ROOT / "presentation/task-explorer/anatomy-curation/manifest.json"
        for key in ("license", "label_license"):
            manifest = json.loads(path.read_text())
            manifest[key] = "CC-BY-4.0"
            with patch.object(stories.json, "loads", return_value=manifest):
                with self.assertRaisesRegex(ValueError, "exact provenance, terms"):
                    stories.resolve_assets(ROOT, "retained-anatomy-curation-v1")

    def test_respiratory_pack_rejects_mislabeled_frame_and_terms(self):
        import json
        from unittest.mock import patch

        for name in [
            "respiratory",
            "registration-analysis",
            "resect",
            "resect-pilot",
            "vessel-source",
            "airway-repair",
            "topbrain-screen",
            "hubmap-inventory",
            "tiger-context",
        ]:
            path = ROOT / f"presentation/task-explorer/{name}/manifest.json"
            for key, value in [
                ("frame", "LPS"),
                ("label_license", "Apache-2.0"),
                ("units", "mm" if name in {"hubmap-inventory", "tiger-context"} else "px"),
            ]:
                manifest = json.loads(path.read_text())
                manifest[key] = value
                with patch.object(stories.json, "loads", return_value=manifest):
                    with self.assertRaisesRegex(ValueError, "exact provenance, terms"):
                        stories.resolve_assets(ROOT, f"retained-{name}-v1")

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

    def test_legacy_compatibility_is_source_pinned_and_new_semantics_are_explicit(self):
        import json
        import tempfile

        import yaml

        baseline = json.loads((ROOT / "tests/fixtures/story-baseline.json").read_text())
        for witness in baseline["stories"]:
            path = ROOT / witness["source"]
            plan = stories.compile_story(ROOT, path)
            self.assertEqual(plan["source_sha256"], witness["source_sha256"])
            if witness["source"] not in stories.LEGACY_SEMANTICS:
                continue
            with self.subTest(story=plan["id"]):
                raw = path.read_text()
                with self.assertRaises(ValueError):
                    stories.parse_expansion(raw)
                document = stories.parse_document(raw)
                header = dict(document.header)
                beats = [dict(beat) for beat in document.beats]
                if plan["recipe"] == "correspondence-v1":
                    for beat, compiled in zip(beats, plan["beats"], strict=True):
                        beat["show_deformed_target"] = compiled["show_deformed_target"]
                else:
                    header["operation"] = plan["operation"]
                explicit = stories.parse_expansion(stories.StoryDocument(header, tuple(beats)))
                header["id"] = "renamed-story"
                for i, beat in enumerate(beats):
                    beat["id"] = f"renamed-{i}"
                renamed = stories.parse_expansion(stories.StoryDocument(header, tuple(beats)))
                self.assertEqual(
                    [beat.channels for beat in explicit.beats],
                    [beat.channels for beat in renamed.beats],
                )
                with tempfile.TemporaryDirectory(dir=ROOT / ".local") as temp:
                    draft = Path(temp) / path.name
                    draft.write_text(raw)
                    with self.assertRaises(ValueError):
                        stories.compile_story(ROOT, draft)
                    # Copying a familiar ID never activates compatibility, even at a new path.
                    text = "---\n" + yaml.safe_dump(header) + "---\n"
                    text += "\n".join("```beat\n" + yaml.safe_dump(b) + "```" for b in beats)
                    draft.write_text(text)
                    self.assertEqual(stories.compile_story(ROOT, draft)["id"], "renamed-story")
                bad = dict(header, operation="unsupported")
                with self.assertRaises(ValueError):
                    stories.parse_expansion(stories.StoryDocument(bad, tuple(beats)))

    def test_malformed_document_and_fenced_examples(self):
        raw = (ROOT / "presentation/external-tasks/stories/ct-forward.story.md").read_text()
        original = stories.parse_expansion(raw)
        self.assertEqual(stories.parse_expansion(raw.replace("\n", "\r\n")), original)
        example = "\n````markdown\n```beat\nnot: a real beat\n```\n````\n"
        self.assertEqual(stories.parse_expansion(raw + example), original)
        for bad in (
            "---\n[]\n---\n",
            "---\nnull\n---\n",
            raw + "\n```beat\n[]\n```\n",
            raw + "\n```beat\nnull\n```\n",
            raw.replace("  observations:\n", "  observations: [0, 0]\n  observations:\n", 1),
            raw + "\n```beat \nid: unfinished\n```\n",
            raw + "\n```beat\nid: unclosed\n",
        ):
            with self.subTest(raw=bad[-120:]), self.assertRaises(ValueError):
                stories.parse_expansion(bad)
