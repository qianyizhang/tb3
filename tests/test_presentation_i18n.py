"""A Chinese view must never silently imply an English record was translated."""

import json
import tempfile
import unittest
from pathlib import Path

from tb3_medical import presentation_i18n
from tb3_medical.errors import MedicalError


class PresentationLanguageTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        (self.root / "presentation").mkdir()
        (self.root / "groups/example/presentation").mkdir(parents=True)
        (self.root / "groups/example/group.json").write_text('{"id":"example"}')
        self.briefs = [{"id": "task-a", "variants": [{"name": "Input"}]}]
        self.datasets = {
            "records": [{"id": "dataset-a", "sample_sets": [{"note": "One source"}]}],
            "previews": {},
        }
        self.manifest = {
            "schema_version": 1,
            "source_language": "en",
            "target_language": "zh-CN",
            "source_fallback": {
                "briefs": ["task-a"],
                "datasets": ["dataset-a"],
                "stories": ["example"],
            },
        }
        self.save()

    def save(self):
        (self.root / presentation_i18n.MANIFEST).write_text(json.dumps(self.manifest))

    def test_declared_source_fallback_is_reported_and_missing_one_fails(self):
        result = presentation_i18n.check(self.root, self.briefs, self.datasets)
        self.assertEqual(result["briefs"], {"translated": 0, "source_fallback": 1})
        self.manifest["source_fallback"]["briefs"] = []
        self.save()
        with self.assertRaisesRegex(MedicalError, "undeclared fallback"):
            presentation_i18n.check(self.root, self.briefs, self.datasets)

    def test_companion_requires_manifest_update_and_complete_sample_copy(self):
        self.datasets["records"][0]["locales"] = {"zh-CN": {"title": "数据集"}}
        with self.assertRaisesRegex(MedicalError, "stale fallback"):
            presentation_i18n.check(self.root, self.briefs, self.datasets)
        self.manifest["source_fallback"]["datasets"] = []
        self.save()
        with self.assertRaisesRegex(MedicalError, "incomplete zh-CN fields"):
            presentation_i18n.check(self.root, self.briefs, self.datasets)

    def test_translated_story_cannot_remain_marked_as_source_fallback(self):
        (self.root / "groups/example/presentation/story.zh-CN.md").write_text("# 中文\n")
        with self.assertRaisesRegex(MedicalError, "stale fallback"):
            presentation_i18n.check(self.root, self.briefs, self.datasets)


if __name__ == "__main__":
    unittest.main()
