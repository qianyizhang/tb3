"""Offline authoring/build checks; no native images or external tasks required."""

import base64
import hashlib
import io
import json
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from tb3_medical import cli
from tb3_medical import core as c
from tb3_medical import task_briefs as briefs


class TaskBriefTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        source = Path(__file__).resolve().parents[1] / "presentation/task-explorer"
        shutil.copytree(source, self.root / "presentation/task-explorer")
        self.catalog = "collection/catalog.json"

    def test_native_cli_build_and_check_use_explicit_workspace(self):
        (self.root / "workbench.toml").write_text('name = "fixture"\n')
        self.scaffold()
        for action in ("check", "build"):
            output = io.StringIO()
            with redirect_stdout(output):
                code = cli.main(
                    [
                        "--root",
                        str(self.root),
                        "brief",
                        action,
                        "--catalog",
                        self.catalog,
                    ]
                )
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(output.getvalue())["briefs"], 1)
        self.assertTrue((self.root / "runs/task-explorer/index.html").is_file())

    def scaffold(self, key="example"):
        return briefs.new(
            self.root,
            key,
            "Inspect a scan",
            "A project",
            "Imaging",
            "group/" + key + ".md",
            self.catalog,
        )

    def test_scaffold_is_proposed_and_preserves_other_briefs(self):
        self.scaffold()
        first = (self.root / "group/example.md").read_bytes()
        self.scaffold("second")
        data = briefs.load(self.root, self.catalog)
        self.assertEqual(len(data["entries"]), 2)
        self.assertTrue(all(e["proposed"] for e in data["entries"]))
        self.assertEqual((self.root / "group/example.md").read_bytes(), first)
        self.assertFalse(list(self.root.rglob("experiment.json")))
        with self.assertRaises(c.MedicalError):
            self.scaffold()

    def test_markdown_edits_flow_to_standalone_build(self):
        self.scaffold()
        p = self.root / "group/example.md"
        p.write_text(
            p.read_text().replace("Describe the remaining work", "Locate the missing boundary.")
        )
        # A raw HTML-looking string remains text and cannot close the data script.
        p.write_text(
            p.read_text().replace(
                "State the action the agent must accomplish in one sentence.",
                "Inspect </script><script>alert(1)</script> safely.",
            )
        )
        svg = self.root / "group/input.svg"
        svg.write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
        p.write_text(
            p.read_text().replace(
                "Add a representative input image or state the missing visual. Markdown images use paths relative to this brief.",
                "![Input](input.svg)",
            )
        )
        out = self.root / "output/index.html"
        briefs.build(self.root, out, self.catalog)
        result = out.read_text()
        self.assertIn("data:image/svg+xml;base64,", result)
        self.assertNotIn("</script><script>alert(1)", result)
        self.assertNotIn("__DATA__", result)
        self.assertNotIn("__APP__", result)
        self.assertIn("Locate the missing boundary.", result)

    def test_missing_media_is_explicit_but_bad_source_link_fails(self):
        self.scaffold()
        p = self.root / "group/example.md"
        p.write_text(
            p.read_text().replace(
                "Add a representative input image or state the missing visual. Markdown images use paths relative to this brief.",
                "![Input](absent.png)",
            )
        )
        self.assertEqual(
            briefs.check(self.root, self.catalog)["missing_media"], ["group/absent.png"]
        )
        p.write_text(
            p.read_text().replace(
                "Link the task prompt, relevant scorer, data/figure attribution and supporting evidence.",
                "[Task](missing-task.md)",
            )
        )
        with self.assertRaises(c.MedicalError):
            briefs.load(self.root, self.catalog)

    def test_build_does_not_overwrite_authored_file(self):
        self.scaffold()
        target = self.root / "user.html"
        target.write_text("Keep my page")
        with self.assertRaises(c.MedicalError):
            briefs.build(self.root, target, self.catalog)
        self.assertEqual(target.read_text(), "Keep my page")
        path = self.root / self.catalog
        data = json.loads(path.read_text())
        data["entries"].append(data["entries"][0])
        path.write_text(json.dumps(data))
        with self.assertRaises(c.MedicalError):
            briefs.check(self.root, self.catalog)

    def test_required_overview_survives_missing_optional_media(self):
        self.scaffold()
        path = self.root / self.catalog
        data = json.loads(path.read_text())
        data["require_overview_visuals"] = True
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(c.MedicalError, "missing overview visual"):
            briefs.check(self.root, self.catalog)
        brief = self.root / "group/example.md"
        brief.write_text(
            brief.read_text().replace("### Input\n", "### Input\n\n![Input](optional.png)\n")
        )
        with self.assertRaisesRegex(c.MedicalError, "missing overview visual"):
            briefs.check(self.root, self.catalog)
        data["entries"][0]["illustration"] = {
            "kind": "segment",
            "input": "Scan",
            "output": "Mask",
            "caption": "Conceptual, not a source example.",
        }
        path.write_text(json.dumps(data))
        checked = briefs.check(self.root, self.catalog)
        self.assertEqual(checked["illustrated_overviews"], 1)
        self.assertEqual(checked["missing_media"], ["group/optional.png"])
        data["entries"][0]["illustration"]["caption"] = " "
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(c.MedicalError, "incomplete overview illustration"):
            briefs.check(self.root, self.catalog)

    def test_sources_are_exact_bounded_deduplicated_and_not_recursive(self):
        self.scaffold()
        self.scaffold("second")
        exact = b"# Protocol\r\n\r\nSee [private input](../runs/private.txt).\r\n"
        (self.root / "group/protocol.md").write_bytes(exact)
        (self.root / "group/large.txt").write_bytes(b"x" * (briefs.SOURCE_MAX_BYTES + 1))
        (self.root / "group/binary.json").write_bytes(b"\xff")
        (self.root / "group/script.py").write_text("PRIVATE_SCRIPT")
        (self.root / "runs").mkdir()
        (self.root / "runs/private.txt").write_text("PRIVATE_RUNTIME")
        for key in ("example", "second"):
            p = self.root / f"group/{key}.md"
            p.write_text(
                p.read_text().replace(
                    "Link the task prompt, relevant scorer, data/figure attribution and supporting evidence.",
                    "[Protocol](protocol.md)\n[Large](large.txt)\n[Binary](binary.json)\n"
                    "[Script](script.py)\n[Runtime](../runs/private.txt)",
                )
            )
        data = briefs.load(self.root, self.catalog)
        sources = data["local_sources"]
        self.assertEqual(len(sources), 5)
        source = sources["group/protocol.md"]
        self.assertEqual(base64.b64decode(source["base64"]), exact)
        self.assertEqual(source["content"], exact.decode())
        self.assertEqual(source["sha256"], hashlib.sha256(exact).hexdigest())
        for path in ("group/large.txt", "group/binary.json", "group/script.py", "runs/private.txt"):
            self.assertIn("unavailable", sources[path])
        target = self.root / "output/index.html"
        briefs.build(self.root, target, self.catalog)
        self.assertNotIn("PRIVATE_RUNTIME", target.read_text())
        self.assertNotIn("PRIVATE_SCRIPT", target.read_text())
        self.assertNotIn('"presentation_context":', target.read_text())
        context = {"home_url": "../index.html", "home_label": "Evidence", "story_urls": {}}
        result = briefs.build(self.root, target, self.catalog, presentation_context=context)
        self.assertTrue(result["integrated"])
        self.assertIn('"home_url": "../index.html"', target.read_text())

    def test_source_bundle_combined_limit_and_link_escape(self):
        entries = [{"sources": []}]
        for i in range(5):
            path = self.root / f"source-{i}.txt"
            path.write_bytes(bytes([65 + i]) * briefs.SOURCE_MAX_BYTES)
            entries[0]["sources"].append(["Source", path.name])
        with self.assertRaisesRegex(c.MedicalError, "256 KiB combined limit"):
            briefs.source_bundle(self.root, entries)
        entries[0]["sources"].pop()
        sources = briefs.source_bundle(self.root, entries)
        self.assertEqual(
            sum(s.get("bytes", 0) for s in sources.values()), briefs.SOURCE_TOTAL_BYTES
        )
        with self.assertRaisesRegex(c.MedicalError, "escapes repository"):
            briefs.local_path(self.root, self.root / "brief.md", "../outside.md")

    def test_catalogue_coverage_condition_and_repository_are_checked(self):
        self.scaffold()
        catalog_path = self.root / self.catalog
        data = json.loads(catalog_path.read_text())
        data.update(inventory="collection/inventory.json", require_brief_coverage=True)
        catalog_path.write_text(json.dumps(data))
        inventory_path = self.root / data["inventory"]
        item = {"id": "case-27"}
        inventory = {"repositories": [{"id": "example", "items": [item]}]}

        def save():
            inventory_path.write_text(json.dumps(inventory))

        save()
        with self.assertRaisesRegex(c.MedicalError, "lacks a task brief"):
            briefs.check(self.root, self.catalog)
        item.update(brief_id="example", condition_index=0)
        save()
        self.assertEqual(briefs.check(self.root, self.catalog)["linked_entries"], 1)
        for invalid in (-1, 99, "0", True):
            item["condition_index"] = invalid
            save()
            with self.assertRaisesRegex(c.MedicalError, "Invalid inventory condition"):
                briefs.check(self.root, self.catalog)
        item["condition_index"] = 0
        inventory["repositories"][0]["id"] = "another-project"
        save()
        with self.assertRaisesRegex(c.MedicalError, "another repository"):
            briefs.check(self.root, self.catalog)
