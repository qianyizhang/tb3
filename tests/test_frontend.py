"""The publication boundary rejects stale source and modified compiled assets."""

import tempfile
import unittest
from pathlib import Path

from frontend_fixture import install_frontend

from tb3_medical import frontend
from tb3_medical.errors import MedicalError


class FrontendTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_missing_build_has_actionable_error(self):
        with self.assertRaisesRegex(MedicalError, "npm run frontend:build"):
            frontend.assets(self.root, "explorer")

    def test_source_change_and_new_module_invalidate_build(self):
        install_frontend(self.root)
        self.assertIn("Vite", frontend.assets(self.root, "explorer")[0])
        (self.root / "package-lock.json").write_text('{"changed": true}')
        with self.assertRaisesRegex(MedicalError, "stale"):
            frontend.assets(self.root, "explorer")
        install_frontend(self.root)
        module = self.root / "presentation/frontend/new.ts"
        module.parent.mkdir(parents=True)
        module.write_text("export const added = true;")
        with self.assertRaisesRegex(MedicalError, "stale"):
            frontend.assets(self.root, "explorer")

    def test_story_and_fixture_changes_invalidate_build(self):
        install_frontend(self.root)
        story = self.root / "groups/test/presentation/stories/test.story.md"
        story.parent.mkdir(parents=True)
        story.write_text("canonical story")
        with self.assertRaisesRegex(MedicalError, "stale"):
            frontend.assets(self.root, "explorer")
        install_frontend(self.root)
        fixture = self.root / "presentation/assets/teaching-fixtures/test/route.json"
        fixture.parent.mkdir(parents=True)
        fixture.write_text('{"source": "changed"}')
        with self.assertRaisesRegex(MedicalError, "stale"):
            frontend.assets(self.root, "explorer")

    def test_modified_output_is_rejected(self):
        install_frontend(self.root)
        (self.root / frontend.BUILD_DIR / "overview.js").write_text("altered")
        with self.assertRaisesRegex(MedicalError, "stale"):
            frontend.assets(self.root, "overview")

    def test_nested_asset_and_inventory_policy_changes_invalidate_build(self):
        for name in (
            "presentation/task-explorer/anatomy/nested/mesh.json",
            "src/tb3_medical/frontend.py",
        ):
            with self.subTest(input=name):
                install_frontend(self.root)
                source = self.root / name
                source.parent.mkdir(parents=True, exist_ok=True)
                source.write_text("changed")
                with self.assertRaisesRegex(MedicalError, "stale"):
                    frontend.assets(self.root, "explorer")

    def test_external_story_discovery_matches_supported_authoring_paths(self):
        install_frontend(self.root)
        for name in ("README.md", "nested/draft.story.md"):
            note = self.root / "presentation/external-tasks/stories" / name
            note.parent.mkdir(parents=True, exist_ok=True)
            note.write_text("Not a compiled story")
        frontend.assets(self.root, "explorer")
        story = self.root / "presentation/external-tasks/stories/accepted.story.md"
        story.write_text("A supported story path")
        with self.assertRaisesRegex(MedicalError, "stale"):
            frontend.assets(self.root, "explorer")


if __name__ == "__main__":
    unittest.main()
