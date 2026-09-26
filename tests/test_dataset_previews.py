"""A frozen preview is distinct from native-data availability and clinical truth."""

import json
import tempfile
import unittest
from pathlib import Path

from tb3_medical import dataset_previews as previews
from tb3_medical import storage
from tb3_medical.errors import MedicalError


class DatasetPreviewTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        (self.root / "datasets/previews").mkdir(parents=True)
        self.image = self.root / "snapshot.png"
        self.image.write_bytes(b"frozen image bytes")
        self.row = {
            "dataset_id": "dataset-test",
            "sample_id": "case-a",
            "status": "input-only",
            "summary": "Acquired example",
            "reference_note": "No paired reference acquired",
            "sources": [{"path": "runs/native.nii.gz", "sha256": "a" * 64}],
            "panels": [
                {
                    "role": "input",
                    "path": "snapshot.png",
                    "sha256": storage.sha(self.image),
                    "caption": "Full source plane; frozen for reader inspection",
                }
            ],
        }
        self.save()

    def save(self):
        (self.root / previews.CATALOG).write_text(json.dumps({"entries": [self.row]}))

    def load(self):
        return previews.load(self.root, {"dataset-test"}, required=True)["dataset-test"]

    def test_snapshots_work_without_native_volumes_and_do_not_fetch_them(self):
        row = self.load()
        self.assertTrue(row["panels"][0]["image_url"].startswith("data:image/png;base64,"))
        self.assertFalse((self.root / "runs").exists())

    def test_changed_snapshot_fails_and_missing_snapshot_stays_explicit(self):
        self.image.write_bytes(b"different pixels")
        with self.assertRaisesRegex(MedicalError, "snapshot changed"):
            self.load()
        self.image.unlink()
        panel = self.load()["panels"][0]
        self.assertFalse(panel["available"])
        self.assertNotIn("image_url", panel)

    def test_every_source_needs_a_preview_or_documented_unavailability(self):
        with self.assertRaisesRegex(MedicalError, "Every dataset"):
            previews.load(self.root, {"dataset-test", "dataset-missing"}, required=True)
        self.row["status"] = "paired"
        self.save()
        with self.assertRaisesRegex(MedicalError, "contradicts"):
            self.load()

    def test_unavailable_and_reference_only_cannot_be_counted_as_paired(self):
        self.row["status"] = "reference-only"
        self.row["panels"][0]["role"] = "reference"
        self.save()
        self.assertEqual(self.load()["status"], "reference-only")
        self.row["status"] = "unavailable"
        self.row["panels"] = [{"role": "metadata", "caption": "Access screen", "text": "401"}]
        self.save()
        self.assertEqual(self.load()["panels"][0]["text"], "401")

    def test_escaping_source_path_is_rejected(self):
        self.row["sources"][0]["path"] = "../outside.nii.gz"
        self.save()
        with self.assertRaisesRegex(MedicalError, "workspace-relative"):
            self.load()
