"""Authored modality navigation remains distinct from case inputs and scientific evidence."""

import copy
import tempfile
import unittest
from pathlib import Path

from tb3_medical import task_catalog
from tb3_medical.errors import MedicalError


class TaskModalityTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.taxonomy = {
            "modalities": {
                "ct": "CT",
                "mri": "MRI",
                "ultrasound": "Ultrasound",
                "unspecified": "Not specified",
                "imaging-unspecified": "Imaging modality not specified",
            }
        }

    def classify(self, entry, **settings):
        data = {
            "taxonomy": copy.deepcopy(self.taxonomy),
            "task_families": {},
            "entries": [entry],
            **settings,
        }
        task_catalog.classify(self.root, data)
        return data

    def test_scaffold_default_does_not_guess_from_task_identifiers(self):
        row = {"id": "an-mri-ct-ultrasound-sounding-identifier"}
        data = self.classify(row, taxonomy={})
        self.assertEqual(row["modalities"], ["unspecified"])
        self.assertEqual(data["taxonomy"]["modalities"], {"unspecified": "Not specified"})
        task_catalog.classify(self.root, data)
        self.assertEqual(row["modalities"], ["unspecified"])

    def test_maintained_catalogue_requires_explicit_modalities(self):
        with self.assertRaisesRegex(MedicalError, "missing explicit modalities"):
            self.classify({"id": "task"}, require_modalities=True)

    def test_known_multiple_modalities_survive_projection(self):
        row = {"id": "registration", "modalities": ["mri", "ultrasound"]}
        self.classify(row, require_modalities=True)
        self.assertEqual(row["modalities"], ["mri", "ultrasound"])

    def test_invalid_or_ambiguous_modality_arrays_are_rejected(self):
        for value in (
            [],
            "ct",
            ["ct", "ct"],
            ["made-up"],
            [42],
            [{"id": "ct"}],
            ["ct", "unspecified"],
            ["mri", "imaging-unspecified"],
        ):
            with self.subTest(value=value):
                with self.assertRaisesRegex(MedicalError, "invalid modalities"):
                    self.classify({"id": "task", "modalities": value})

    def test_bad_taxonomy_labels_fail_before_rendering(self):
        for modalities in ({}, {"ct": "CT"}, {"unspecified": ""}, {"unspecified": 3}):
            with self.subTest(modalities=modalities):
                with self.assertRaisesRegex(MedicalError, "valid modality labels"):
                    self.classify({"id": "task"}, taxonomy={"modalities": modalities})
