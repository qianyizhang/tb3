"""Portable navigation and maintained prose checks without local medical payloads."""

from pathlib import Path
import shutil
import tempfile
import unittest

from tb3_medical import core as c, presentation as p, task_briefs


class PresentationRefinementTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "workbench.toml").write_text("version=1\n")
        repo = Path(__file__).resolve().parents[1]
        for name in ("index.html", "app.js", "style.css"):
            target = self.root / "presentation" / name
            target.parent.mkdir(exist_ok=True)
            shutil.copyfile(repo / "presentation" / name, target)
        for name in ("first", "second"):
            c.write_new(
                self.root / "groups" / name / "group.json",
                {"schema_version": 2, "kind": "group", "id": name, "title": name},
            )
            folder = self.root / "groups" / name / "presentation"
            folder.mkdir()
            (folder / "story.md").write_text("# A chapter\n\n## Results\n")

    def test_chapter_links_use_rendered_pages_and_heading_fragments(self):
        source = self.root / "groups/first/presentation/story.md"
        source.write_text("# First\n\n[Next](../../second/presentation/story.md#results)\n")
        c.write_new(
            self.root / "groups/first/findings/f.json",
            {
                "schema_version": 2,
                "kind": "finding",
                "id": "f",
                "group_id": "first",
                "claim": "Example",
                "experiment_ids": [],
                "links": [{"label": "Chapter", "path": "groups/first/presentation/story.md"}],
            },
        )
        output = self.root / "output"
        p.present(self.root, output)
        self.assertIn('href="second.html#results"', (output / "stories/first.html").read_text())
        self.assertIn('id="results"', (output / "stories/second.html").read_text())
        rows = {r["id"]: r for r in c.read(output / "records.json")["records"]}
        self.assertEqual(rows["f"]["portable_links"][0]["url"], "stories/first.html")
        self.assertFalse((output / "groups/first/presentation/story.md").exists())
        rendered = p.markdown("# Results\n\n# Results\n\n# Results", lambda value: value)
        for identifier in ("results", "results-1", "results-2"):
            self.assertIn(f'id="{identifier}"', rendered)

    def test_protocol_wrappers_are_checked_but_runtime_locators_remain_optional(self):
        source = self.root / "groups/first/experiments/e/protocol.md"
        source.parent.mkdir(parents=True)
        source.write_text("[Historical protocol](../../../../../outside.md)\n")
        with self.assertRaisesRegex(c.MedicalError, "escapes repository"):
            p.check(self.root)
        source.write_text("[Missing](../../../../missing.md)\n")
        with self.assertRaisesRegex(c.MedicalError, "Missing portable prose link"):
            p.check(self.root)
        source.write_text("[Local scan](../../../../runs/scan.nii.gz)\n")
        self.assertEqual(p.check(self.root)["protocols_checked"], 1)

    def test_integrated_explorer_has_context_and_standalone_remains_independent(self):
        repo = Path(__file__).resolve().parents[1]
        shutil.copytree(
            repo / "presentation/task-explorer", self.root / "presentation/task-explorer"
        )
        task_briefs.new(self.root, "example", "Example", "Research", "Imaging", "briefs/example.md")
        output = self.root / "output"
        result = p.present(self.root, output)
        self.assertEqual(result["task_explorer"]["briefs"], 1)
        self.assertTrue((output / "task-explorer/index.html").is_file())
        self.assertEqual(
            c.read(output / "records.json")["task_explorer_url"], "task-explorer/index.html"
        )


if __name__ == "__main__":
    unittest.main()
