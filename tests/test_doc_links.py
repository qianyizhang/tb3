"""Tests for the maintained-document link boundary."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tb3_medical.doc_links import audit


class DocumentLinkTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.write(
            "configs/doc-links.json",
            json.dumps(
                {
                    "schema_version": 1,
                    "required_files": ["docs/README.md"],
                    "include_globs": ["groups/**/*.md"],
                    "exclude_globs": ["groups/*/history/**"],
                    "optional_local_roots": [".local", "runs"],
                    "external_schemes": ["https", "mailto", "codex"],
                }
            ),
        )
        self.write(
            "docs/README.md",
            "# Docs\n\n[Guide](guide.md#prepare--replay) [web](https://example.com) "
            "[mail](mailto:a@example.com) [panel](codex://threads/1)\n\n"
            "[optional](../.local/report.png)\n",
        )
        self.write("docs/guide.md", "# Prepare & replay\n")

    def write(self, name: str, content: str) -> None:
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def reasons(self) -> list[str]:
        return [issue.reason for issue in audit(self.root).issues]

    def test_valid_relative_external_anchor_and_optional_links_pass(self) -> None:
        result = audit(self.root)
        self.assertEqual(result.issues, ())
        self.assertEqual(result.optional_local_links, 1)

    def test_missing_target_fails(self) -> None:
        self.write("docs/README.md", "[missing](missing.md)\n")
        self.assertIn("target does not exist", self.reasons())

    def test_escape_and_machine_absolute_paths_fail(self) -> None:
        self.write("docs/README.md", "[escape](../../outside.md) [local](/Users/a/file.md)\n")
        reasons = self.reasons()
        self.assertIn("path escapes repository", reasons)
        self.assertIn("machine-absolute path is not portable", reasons)

    def test_missing_anchor_fails(self) -> None:
        self.write("docs/README.md", "[bad](guide.md#missing)\n")
        self.assertIn("heading anchor does not exist", self.reasons())

    def test_missing_same_file_anchor_and_reference_target_fail(self) -> None:
        self.write(
            "docs/README.md",
            "# Docs\n\n[bad anchor](#missing) [bad path][cross-wire]\n\n"
            "[cross-wire]: ../wrong/location.md\n",
        )
        reasons = self.reasons()
        self.assertIn("heading anchor does not exist", reasons)
        self.assertIn("target does not exist", reasons)

    def test_fenced_examples_and_excluded_history_are_ignored(self) -> None:
        self.write("docs/README.md", "```md\n[example](missing.md)\n```\n")
        self.write("groups/demo/history/old.md", "[old](missing.md)\n")
        self.assertEqual(audit(self.root).issues, ())

    def test_current_group_document_is_checked(self) -> None:
        self.write("groups/demo/findings/current.md", "[missing](nope.md)\n")
        self.assertIn("target does not exist", self.reasons())


if __name__ == "__main__":
    unittest.main()
