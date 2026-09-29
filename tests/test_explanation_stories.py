"""Canonical story, binding, dependency and retained numerical witnesses."""

import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tb3_medical import explanation_stories as stories
from tb3_medical import storage, task_briefs, task_catalog
from tb3_medical.errors import MedicalError

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path("groups/tubular-anatomy/presentation/stories/route-unfold-teaching-v1.story.md")


class ExplanationStoriesTests(unittest.TestCase):
    def test_source_slice_pack_requires_reference_disclosure_and_retained_terms(self):
        source = Path("groups/anatomy-audit/presentation/stories/mixed-tissue-audit.story.md")
        plan = stories.compile_story(ROOT, source)
        self.assertEqual(plan["reference_policy"], "reader-reference-reveal")
        with tempfile.TemporaryDirectory(dir=ROOT / ".local") as temp:
            path = Path(temp) / "hidden-reference.story.md"
            path.write_text(
                (ROOT / source)
                .read_text()
                .replace(
                    "reference_policy: reader-reference-reveal",
                    "reference_policy: no-reference-assets",
                )
            )
            with self.assertRaisesRegex(ValueError, "reference policy mismatch"):
                stories.compile_story(ROOT, path)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            source_dir = "presentation/task-explorer/mixed-tissue"
            shutil.copytree(ROOT / source_dir, root / source_dir)
            index_path = root / "presentation/assets/teaching-prefabs.json"
            index_path.parent.mkdir(parents=True)
            shutil.copyfile(ROOT / "presentation/assets/teaching-prefabs.json", index_path)
            manifest_path = root / source_dir / "manifest.json"
            original = json.loads(manifest_path.read_text())
            stories.resolve_assets(root, "retained-mixed-tissue-v1")
            for mutation in ("license", "reference", "hash"):
                changed = copy.deepcopy(original)
                if mutation == "license":
                    changed["license"] = "CC0-1.0"
                elif mutation == "reference":
                    next(a for a in changed["assets"] if a["file"] == "fixture.json")["role"] = (
                        "illustration"
                    )
                else:
                    changed["assets"][0]["sha256"] = "0" * 64
                manifest_path.write_text(json.dumps(changed))
                with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                    stories.resolve_assets(root, "retained-mixed-tissue-v1")

    def test_symbolic_input_pack_rejects_reference_and_provenance_leakage(self):
        pack_id = "retained-automed-full-feta-seg-v1"
        story = Path("presentation/external-tasks/stories/automedbench-full-feta-seg-task.story.md")
        plan = stories.compile_story(ROOT, story)
        self.assertEqual(plan["source_class"], "symbolic-protocol")
        self.assertEqual(plan["reference_policy"], "no-reference-assets")
        with tempfile.TemporaryDirectory(dir=ROOT / ".local") as temp:
            path = Path(temp) / "symbolic.story.md"
            raw = (ROOT / story).read_text()
            for before, after in (
                ("source_class: symbolic-protocol", "source_class: source-derived-teaching"),
                (
                    "reference_policy: no-reference-assets",
                    "reference_policy: reader-reference-reveal",
                ),
            ):
                path.write_text(raw.replace(before, after))
                with self.subTest(after=after), self.assertRaises(ValueError):
                    stories.compile_story(ROOT, path)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            source_dir = "presentation/task-explorer/automedbench-full-feta-seg-task"
            shutil.copytree(ROOT / source_dir, root / source_dir)
            index_path = root / "presentation/assets/teaching-prefabs.json"
            index_path.parent.mkdir(parents=True)
            shutil.copyfile(ROOT / "presentation/assets/teaching-prefabs.json", index_path)
            manifest_path = root / source_dir / "manifest.json"
            original = json.loads(manifest_path.read_text())
            for source_name in original["sources"]:
                source_copy = root / source_name
                source_copy.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / source_name, source_copy)
            stories.resolve_assets(root, pack_id)
            original_index = json.loads(index_path.read_text())
            escaped_index = copy.deepcopy(original_index)
            escaped_index["packs"][pack_id]["manifest"] = "../../etc/passwd"
            index_path.write_text(json.dumps(escaped_index))
            with self.assertRaises(MedicalError):
                stories.resolve_assets(root, pack_id)
            index_path.write_text(json.dumps(original_index))
            from unittest.mock import patch

            with patch.dict(
                stories.SOURCE_REFERENCE_PACKS,
                {
                    pack_id: (
                        "source-records",
                        "reference.json",
                        {asset["file"] for asset in original["assets"]},
                    )
                },
            ):
                with self.assertRaisesRegex(ValueError, "cannot contain reference assets"):
                    stories.resolve_assets(root, pack_id)
            for mutation in (
                "asset-provenance",
                "asset-role",
                "reference-policy",
                "self-source-pin",
                "source-pin",
            ):
                changed = copy.deepcopy(original)
                if mutation == "asset-provenance":
                    changed["assets"][0]["provenance"] = "source-derived-teaching"
                elif mutation == "asset-role":
                    changed["assets"][0]["role"] = "reader-reference-reveal"
                elif mutation == "reference-policy":
                    changed["reference_policy"] = "reader-reference-reveal"
                elif mutation == "self-source-pin":
                    asset = changed["assets"][0]
                    changed["sources"] = {f"{source_dir}/{asset['file']}": asset["sha256"]}
                else:
                    key = next(iter(changed["sources"]))
                    changed["sources"][key] = "0" * 64
                manifest_path.write_text(json.dumps(changed))
                with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                    stories.resolve_assets(root, pack_id)

    def test_schema_dispatch_uses_only_parsed_frontmatter(self):
        route = (ROOT / SOURCE).read_text()
        expansion = (ROOT / "presentation/external-tasks/stories/ct-forward.story.md").read_text()
        with tempfile.TemporaryDirectory(dir=ROOT / ".local") as temp:
            source = Path(temp) / "example.story.md"
            for raw, expected in (
                (route + "\n```yaml\nschema: 2\n```\n", 1),
                (route.replace("\n", "\r\n"), 1),
                (expansion.replace("schema: 2", "schema:   2  # supported version"), 2),
            ):
                with self.subTest(schema=expected):
                    source.write_bytes(raw.encode())
                    plan = stories.compile_story(ROOT, source)
                    self.assertEqual(plan["schema"], expected)
            for schema in ("true", "3", "'2'", "2.0"):
                source.write_text(expansion.replace("schema: 2", "schema: " + schema))
                with self.subTest(schema=schema), self.assertRaises(ValueError):
                    stories.compile_story(ROOT, source)

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
        self.assertIn(
            ("ours", "route-unfold-teaching-v1"),
            [
                (e["id"], e["illustration"]["story_id"])
                for e in catalog["entries"]
                if e.get("illustration", {}).get("story_id")
            ],
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
            for name in stories.COMPILER_SOURCES:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, target)
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
            with self.assertRaisesRegex(ValueError, "workspace-relative"):
                storage.inside(root, "../outside")

    def test_workspace_paths_reject_aliases_and_links_without_losing_valid_sources(self):
        from unittest.mock import patch

        raw = (ROOT / "presentation/external-tasks/stories/ct-forward.story.md").read_text()
        with tempfile.TemporaryDirectory(dir=ROOT / ".local") as temp:
            folder = Path(temp)
            source = folder / "example.story.md"
            original = stories.parse_document(raw)
            valid = folder / "nested/source.md"
            valid.parent.mkdir()
            valid.write_text("Source")
            link = folder / "link.md"
            link.symlink_to(valid)
            with patch.object(stories, "resolve_assets", side_effect=lambda *args: ("a" * 64, {})):
                for locator in (
                    str(valid),
                    "../outside",
                    str(link.relative_to(ROOT)),
                    str(folder.relative_to(ROOT) / "nested/../nested/source.md"),
                    str(folder.relative_to(ROOT) / "missing.md"),
                ):
                    source.write_text(raw.replace(original.header["source_locators"][0], locator))
                    with self.subTest(locator=locator), self.assertRaises(ValueError):
                        stories.compile_story(ROOT, source)
                source.write_text(
                    raw.replace(
                        original.header["source_locators"][0], valid.relative_to(ROOT).as_posix()
                    )
                )
                plan = stories.compile_story(ROOT, source)
                self.assertEqual(
                    plan["dependencies"][valid.relative_to(ROOT).as_posix()], storage.sha(valid)
                )
                valid.write_text("Revised source brief")
                changed = stories.compile_story(ROOT, source)
                self.assertEqual(plan["source_sha256"], changed["source_sha256"])
                self.assertNotEqual(plan["dependencies"], changed["dependencies"])
                alias = folder / "alias.story.md"
                alias.symlink_to(source)
                with self.assertRaisesRegex(ValueError, "symlink"):
                    stories.compile_story(ROOT, alias)

    def test_compiler_source_and_selected_story_freshness_are_separate_from_renderer(self):
        from unittest.mock import patch

        from frontend_fixture import install_frontend

        from tb3_medical import frontend

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            install_frontend(root)
            for name in stories.COMPILER_SOURCES:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                if not target.exists():
                    target.write_bytes((ROOT / name).read_bytes())
            source = root / "story.md"
            raw = (ROOT / SOURCE).read_text()
            source.write_text(raw)
            with patch.object(stories, "resolve_assets", side_effect=lambda *args: ("a" * 64, {})):
                plan = stories.compile_story(root, source)
                (root / "sibling.story.md").write_text("Unrelated")
                self.assertEqual(stories.compile_story(root, source), plan)
                frontend.assets(root, "explorer")
                compiler = root / "src/tb3_medical/explanation_stories.py"
                compiler.write_text(compiler.read_text() + "\n# changed compiler\n")
                updated = stories.compile_story(root, source)
                self.assertNotEqual(plan["dependencies"], updated["dependencies"])
                frontend.assets(root, "explorer")
                with self.assertRaisesRegex(ValueError, "Compiled story dependency changed"):
                    stories.write_export(root, plan, root / "stale")
                source.write_text(raw + "\nNew source text\n")
                changed = stories.compile_story(root, source)
                self.assertNotEqual(changed["source_sha256"], plan["source_sha256"])
                frontend.assets(root, "explorer")

            def drift(*args):
                source.write_text(raw + "\nEdited during compilation\n")
                return "a" * 64, {}

            with patch.object(stories, "resolve_assets", side_effect=drift):
                with self.assertRaisesRegex(ValueError, "Compiled story dependency changed"):
                    stories.compile_story(root, source)
