"""Retention and path guarantees at the shared storage boundary."""

import tempfile
import unittest
from pathlib import Path

from tb3_medical import core, storage


class StorageTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)

    def test_exclusive_publish_and_explicit_replacement_preserve_format(self):
        for suffix in (".json", ".toml", ".md"):
            with self.subTest(suffix=suffix):
                path = self.root / ("record" + suffix)
                original = {"title": "First", **({"body": "Body"} if suffix == ".md" else {})}
                storage.write_new(path, original)
                before = path.read_bytes()
                with self.assertRaises(FileExistsError):
                    storage.write_new(path, {**original, "title": "Lost update"})
                self.assertEqual(path.read_bytes(), before)
                updated = {**original, "title": "Replacement"}
                storage.atomic_write(path, updated)
                self.assertEqual(storage.read_object(path), updated)
                self.assertFalse(list(self.root.glob(".*.tmp")))

    def test_serialization_failure_does_not_replace_evidence_or_leave_tempfile(self):
        path = self.root / "record.json"
        storage.write_new(path, {"value": 1})
        with self.assertRaises(ValueError):
            storage.atomic_write(path, {"value": float("nan")})
        self.assertEqual(storage.read_object(path), {"value": 1})
        self.assertFalse(list(self.root.glob(".*.tmp")))

    def test_workspace_paths_reject_traversal_absolute_paths_and_symlinks(self):
        (self.root / "real").mkdir()
        (self.root / "alias").symlink_to(self.root / "real", target_is_directory=True)
        for value in ("../outside", str(self.root / "real"), "alias/input.json"):
            with self.subTest(value=value), self.assertRaises(core.MedicalError):
                storage.inside(self.root, value)

    def test_nonobject_record_reports_a_domain_error(self):
        path = self.root / "groups/g/group.json"
        path.parent.mkdir(parents=True)
        path.write_text("[]")
        self.assertEqual(storage.read(path), [])
        with self.assertRaisesRegex(core.MedicalError, "Expected a document object"):
            core.load(self.root)
