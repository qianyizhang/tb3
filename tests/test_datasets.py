"""Dataset provenance, coverage and availability are separate contracts."""

import json
import tempfile
import unittest
from pathlib import Path

from tb3_medical import datasets, storage
from tb3_medical.errors import MedicalError


class DatasetTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        (self.root / "datasets").mkdir()
        self.receipt = self.root / "receipt.json"
        self.receipt.write_text(
            json.dumps({"files": [{"path": "runs/scan.nii", "sha256": "0" * 64}]})
        )
        self.ref = {
            "path": "receipt.json",
            "sha256": storage.sha(self.receipt),
            "pointer": "/files",
        }
        self.row = {
            "id": "dataset-example",
            "title": "Example",
            **dict.fromkeys(datasets.FIELDS, "Recorded source"),
            "sample_sets": [
                {
                    "sample_ids": ["case-1"],
                    "role": "used",
                    "note": "One selected case",
                    "receipt": self.ref,
                }
            ],
            "experiment_ids": [],
            "brief_ids": [],
            "file_sets": [{"receipt": self.ref, "path_field": "path"}],
        }
        self.save()

    def save(self):
        (self.root / "datasets/example.json").write_text(json.dumps(self.row))

    def test_missing_payload_does_not_block_portable_metadata_but_is_an_audit_gap(self):
        data = datasets.load(self.root, require_coverage=True)
        report = datasets.audit(self.root, data)
        self.assertEqual(report["local_file_counts"], {"missing": 1})
        self.assertFalse((self.root / "runs").exists())

    def test_receipt_drift_and_invalid_pointer_fail_before_build(self):
        self.receipt.write_text('{"files": []}')
        with self.assertRaisesRegex(MedicalError, "receipt changed"):
            datasets.load(self.root)
        self.ref["sha256"] = storage.sha(self.receipt)
        self.ref["pointer"] = "/missing"
        self.save()
        with self.assertRaisesRegex(MedicalError, "receipt pointer"):
            datasets.load(self.root)

    def test_new_experiment_requires_dataset_mapping(self):
        path = self.root / "groups/group/experiments/new/experiment.toml"
        path.parent.mkdir(parents=True)
        path.write_text('id = "new-experiment"\ntitle = "New experiment"\n')
        with self.assertRaisesRegex(MedicalError, "missing dataset documentation"):
            datasets.load(self.root, require_coverage=True)
        self.row["experiment_ids"] = ["new-experiment"]
        self.save()
        self.assertEqual(
            datasets.load(self.root, require_coverage=True)["coverage"]["experiments"], 1
        )

    def test_unknown_brief_and_escaping_file_are_rejected(self):
        self.row["brief_ids"] = ["missing"]
        self.save()
        with self.assertRaisesRegex(MedicalError, "unknown task brief"):
            datasets.load(self.root, require_coverage=True)
        self.row["brief_ids"] = []
        self.row["file_sets"][0]["local_root"] = "../outside"
        self.save()
        with self.assertRaisesRegex(MedicalError, "workspace-relative"):
            datasets.load(self.root)

    def test_external_acquired_files_have_exactly_one_owner(self):
        path = self.root / "presentation/external-tasks/samples.json"
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps({"downloads": [{"path": "runs/input.nii", "sha256": "a" * 64}]}))
        with self.assertRaisesRegex(MedicalError, "exactly one dataset owner"):
            datasets.load(self.root, require_coverage=True)
        spec = {
            "receipt": {
                "path": "presentation/external-tasks/samples.json",
                "sha256": storage.sha(path),
                "pointer": "/downloads",
            },
            "path_field": "path",
        }
        self.row["file_sets"] = [spec]
        self.save()
        datasets.load(self.root, require_coverage=True)
        self.row["file_sets"].append(spec)
        self.save()
        with self.assertRaisesRegex(MedicalError, "exactly one dataset owner"):
            datasets.load(self.root, require_coverage=True)

    def test_local_mismatch_is_not_silently_rebaselined(self):
        path = self.root / "runs/scan.nii"
        path.parent.mkdir()
        path.write_bytes(b"changed bytes")
        before = self.receipt.read_bytes()
        report = datasets.audit(self.root, datasets.load(self.root))
        self.assertEqual(report["local_file_counts"], {"mismatch": 1})
        self.assertEqual(self.receipt.read_bytes(), before)

    def test_recovered_metadata_does_not_hide_unverified_image(self):
        self.row["unverified_payloads"] = [
            {
                "sample_id": "atlas",
                "original_runtime_path": "/container/cache/atlas.nii",
                "note": "Archive is a pointer; the image was not retained",
                "receipt": self.ref,
            }
        ]
        self.save()
        report = datasets.audit(self.root, datasets.load(self.root))
        self.assertEqual(report["unverified_payloads"][0]["sample_id"], "atlas")
        self.assertEqual(report["unverified_payloads"][0]["dataset_id"], "dataset-example")

    def test_repeated_views_cannot_be_duplicated_sample_identities(self):
        self.row["sample_sets"][0]["sample_ids"] = ["case-1", "case-1"]
        self.save()
        with self.assertRaisesRegex(MedicalError, "incomplete sample selection"):
            datasets.load(self.root)


if __name__ == "__main__":
    unittest.main()
