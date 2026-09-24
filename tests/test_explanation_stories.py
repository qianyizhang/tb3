"""Canonical story, binding, dependency and retained numerical witnesses."""

import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tb3_medical import explanation_stories as stories
from tb3_medical import task_briefs, task_catalog
from tb3_medical.errors import MedicalError

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path("groups/tubular-anatomy/presentation/stories/route-unfold-teaching-v1.story.md")


class ExplanationStoriesTests(unittest.TestCase):
    def test_parser_rejects_invalid_authoring(self):
        raw = (ROOT / SOURCE).read_text()
        cases = [
            raw.replace("fps: 24", "fps: 24\nfps: 24"),
            raw.replace("id: trace", "id: orient"),
            raw.replace("fps: 24", "fps: true"),
            raw.replace("fps: 24", "fps: 24\nunknown: 1"),
            raw.replace("duration: 5", "duration: .nan", 1),
            raw.replace("duration: 5", "duration: 5.01", 1),
            raw.replace("duration: 5", "duration: true", 1),
            raw.replace("context: [1, 1]", "context: [true, 1]", 1),
            raw.replace("asset_pack: tb3-route-kit-v1", "asset_pack: ../other"),
            raw.replace("no-reference-assets", "include-reference"),
            raw.replace("schema: 1", "schema: true"),
            raw + "\n```beat\nid: unfinished\n",
        ]
        for invalid in cases:
            with self.subTest(invalid=invalid[:150]), self.assertRaises(ValueError):
                stories.parse_story(invalid)

    def test_asset_index_requires_complete_unambiguous_pack(self):
        original = json.loads((ROOT / "presentation/assets/teaching-prefabs.json").read_text())
        for mutation in ("missing", "duplicate", "geometry", "unknown"):
            index = copy.deepcopy(original)
            pack = index["packs"]["tb3-route-kit-v1"]
            if mutation == "missing":
                pack["retained_files"].remove("route.json")
            elif mutation == "duplicate":
                pack["retained_files"].append("route.json")
            elif mutation == "geometry":
                pack["runtime_geometry"] = "tree.glb"
            else:
                pack["unknown"] = True
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                stories.PrefabIndex.model_validate(index)

    def test_binding_survives_collection_and_brief_projection(self):
        catalog = task_catalog.collection(ROOT, task_catalog.DEFAULT_CATALOG)
        self.assertEqual(
            [
                (e["id"], e["illustration"]["story_id"])
                for e in catalog["entries"]
                if e.get("illustration", {}).get("story_id")
            ],
            [("ours", "route-unfold-teaching-v1")],
        )
        data = task_briefs.load(ROOT)
        ours = next(e for e in data["entries"] if e["id"] == "ours")
        self.assertEqual(ours["illustration"]["story_id"], "route-unfold-teaching-v1")
        self.assertIn("<img ", ours["visuals"]["input"])
        self.assertIn("<img ", ours["visuals"]["helpers"])
        self.assertIn("Post-run", ours["visuals"]["answer"])
        self.assertEqual(
            data["explanation_stories"]["route-unfold-teaching-v1"]["durationFrames"], 792
        )
        with self.assertRaises(MedicalError):
            stories.resolve_stories(ROOT, [{"illustration": {"story_id": "missing-story"}}])
        self.assertEqual(
            stories.resolve_stories(ROOT, [{"illustration": {"kind": "route_unfold"}}]), {}
        )

    def test_copy_timing_and_dependencies_are_canonical(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            shutil.copytree(
                ROOT / "presentation/assets/teaching-fixtures",
                root / "presentation/assets/teaching-fixtures",
            )
            shutil.copyfile(
                ROOT / "presentation/assets/teaching-prefabs.json",
                root / "presentation/assets/teaching-prefabs.json",
            )
            source = root / SOURCE
            source.parent.mkdir(parents=True)
            source.write_bytes((ROOT / SOURCE).read_bytes())
            first = stories.compile_story(root, source)
            before = first["dependencies"]
            source.write_text(
                source.read_text()
                .replace(
                    "One branching volume. Two supplied endpoints.", "Temporary changed caption."
                )
                .replace("duration: 5", "duration: 6", 1)
            )
            second = stories.compile_story(root, source)
            self.assertNotEqual(before, second["dependencies"])
            self.assertEqual(second["durationFrames"], 816)
            stale_output = root / "stale-export"
            with self.assertRaisesRegex(ValueError, "Compiled story dependency changed"):
                stories.write_export(root, first, stale_output)
            self.assertFalse(stale_output.exists())
            out = root / "out"
            stories.write_projections(second, out)
            for name in ("plan.json", "captions.srt", "captions.vtt", "transcript.md"):
                self.assertIn("Temporary changed caption.", (out / name).read_text())
            manifest = root / "presentation/assets/teaching-fixtures/route-unfold-v1/manifest.json"
            original = json.loads(manifest.read_text())
            bad = copy.deepcopy(original)
            next(a for a in bad["assets"] if a["file"] == "route.json")["role"] = "reference"
            manifest.write_text(json.dumps(bad))
            with self.assertRaisesRegex(ValueError, "prohibits reference"):
                stories.compile_story(root, source)
            manifest.write_text(json.dumps(original))
            (manifest.parent / "route.json").write_text("{}")
            with self.assertRaisesRegex(ValueError, "Stale asset"):
                stories.compile_story(root, source)
            (manifest.parent / "route.json").unlink()
            with self.assertRaises(FileNotFoundError):
                stories.compile_story(root, source)
            with self.assertRaisesRegex(ValueError, "escaped"):
                stories.inside(root, "../outside")
