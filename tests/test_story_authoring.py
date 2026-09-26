"""Drafting respects nested ownership, existing bindings and authoring boundaries."""

import json
import re
import tempfile
import unittest
from pathlib import Path

from tb3_medical import explanation_stories as stories
from tb3_medical import story_authoring as author
from tb3_medical.errors import MedicalError


class StoryAuthoringTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.owner = self.root / "groups/example/presentation"
        self.owner.mkdir(parents=True)
        self.brief = self.owner / "brief.md"
        self.brief.write_text("# Transfer a point\n\nActual condition.\n")
        self.entry = {"id": "example", "brief": self.brief.relative_to(self.root).as_posix()}
        self.leaf = self.owner / "catalog.json"
        self.leaf.write_text(json.dumps({"entries": [self.entry, {"id": "sibling"}]}))
        catalog = self.root / "presentation/task-explorer/catalog.json"
        catalog.parent.mkdir(parents=True)
        catalog.write_text(json.dumps({"collections": [str(self.leaf.relative_to(self.root))]}))

    def test_preview_and_draft_never_change_catalogue_or_activate_story(self):
        before = self.leaf.read_bytes()
        preview = author.new(
            self.root, "example", "new-story", recipe="correspondence-v1", preview=True
        )
        self.assertFalse((self.owner / "stories").exists())
        result = author.new(self.root, "example", "new-story", recipe="correspondence-v1")
        path = self.root / result["destination"]
        self.assertEqual(path.parent, self.owner / "stories/drafts")
        self.assertEqual(path.read_text(), preview["content"])
        self.assertEqual(self.leaf.read_bytes(), before)
        self.assertFalse(result["bound"])
        self.assertEqual(stories.resolve_stories(self.root, [self.entry]), {})
        with self.assertRaisesRegex(ValueError, "Unfinished story draft"):
            stories.compile_story(self.root, path)
        with self.assertRaisesRegex(MedicalError, "already exists"):
            author.new(self.root, "example", "new-story", recipe="correspondence-v1")
        self.assertEqual(path.read_text(), preview["content"])

    def test_every_recipe_draft_uses_the_compilers_actual_channel_contract(self):
        for recipe in author.recipes():
            for acquisition in recipe.acquisitions or (None,):
                with self.subTest(recipe=recipe.id, acquisition=acquisition):
                    result = author.new(
                        self.root,
                        "example",
                        "draft",
                        recipe=recipe.id,
                        acquisition=acquisition,
                        preview=True,
                    )
                    raw = re.sub(r"\[\[AUTHOR:.*?\]\]", "Authored explanation", result["content"])
                    parsed = stories.parse_expansion(raw)
                    self.assertEqual(
                        parsed.source_locators, (str(self.brief.relative_to(self.root)),)
                    )
                    self.assertEqual(parsed.title, "Transfer a point")
                    self.assertEqual(sum(beat.frames for beat in parsed.beats), 360)
        with self.assertRaisesRegex(MedicalError, "acquisition"):
            author.new(self.root, "example", "draft", recipe="inverse-v1", preview=True)

    def test_unknown_ambiguous_and_escaping_ids_do_not_write(self):
        for key in ("../outside", "bad/name"):
            with self.assertRaises(MedicalError):
                author.new(self.root, "example", key, recipe="correspondence-v1")
        with self.assertRaisesRegex(MedicalError, "found 0"):
            author.new(self.root, "missing", "draft", recipe="correspondence-v1")
        self.leaf.write_text(json.dumps({"entries": [self.entry, self.entry]}))
        with self.assertRaisesRegex(MedicalError, "found 2"):
            author.new(self.root, "example", "draft", recipe="correspondence-v1")
        self.assertFalse((self.owner / "stories").exists())
