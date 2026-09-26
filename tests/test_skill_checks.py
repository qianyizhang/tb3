"""Skill packaging failures remain visible even when declared versions match."""

import shutil
import tempfile
import unittest
from pathlib import Path

from tb3_medical.skill_checks import check, check_skill


class SkillChecksTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.skill = self.root / "skills/example"
        (self.skill / "references").mkdir(parents=True)
        (self.skill / "SKILL.md").write_text(
            '---\nname: example\ndescription: Example\nmetadata:\n  version: "1.0.0"\n'
            "---\n\n[Details](references/feedback-ledger.md#active-lessons)\n"
        )
        (self.skill / "references/feedback-ledger.md").write_text("## Active lessons\n\nNone.\n")

    def test_same_version_does_not_hide_missing_changed_or_extra_resources(self):
        installed = self.root / "installed"
        mirror = installed / "example"
        shutil.copytree(self.skill, mirror)
        self.assertFalse(check(self.root, installed_root=installed)[0].issues)
        (mirror / "SKILL.md").write_text((mirror / "SKILL.md").read_text() + "Changed.\n")
        (mirror / "references/feedback-ledger.md").unlink()
        (mirror / "obsolete.md").write_text("Old instructions")
        before = (mirror / "SKILL.md").read_bytes()
        result = check_skill(self.skill, installed)
        self.assertEqual(len(result.issues), 3)
        self.assertEqual(result.version, "1.0.0")
        self.assertEqual(before, (mirror / "SKILL.md").read_bytes())

    def test_repo_link_is_invalid_even_when_it_exists_next_to_source(self):
        (self.root / "docs").mkdir()
        (self.root / "docs/guide.md").write_text("# Guide")
        with (self.skill / "SKILL.md").open("a") as file:
            file.write("[Workspace contract](../../docs/guide.md)\n")
        self.assertTrue(any("escapes" in issue for issue in check_skill(self.skill).issues))

    def test_missing_anchor_unclosed_fence_and_unknown_selection_fail(self):
        (self.skill / "references/feedback-ledger.md").write_text("## Renamed\n\n```\n")
        issues = check_skill(self.skill).issues
        self.assertTrue(any("missing anchor" in issue for issue in issues))
        self.assertTrue(any("unclosed" in issue for issue in issues))
        with self.assertRaises(ValueError):
            check(self.root, names=["absent"])
