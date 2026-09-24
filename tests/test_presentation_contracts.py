"""Python export contracts and generated browser types share one authority."""

import copy
import unittest
from pathlib import Path

from tb3_medical import core, task_briefs
from tb3_medical import presentation_contracts as contracts
from tb3_medical.errors import MedicalError


class PresentationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parents[1]
        cls.explorer = task_briefs.load(cls.root)

    def test_current_projection_and_generated_types_match(self):
        contracts.validate_payload(self.explorer, "explorer")
        contracts.validate_payload(
            {
                "schema_version": 1,
                "records": list(core.projection(self.root).values()),
                "vocabulary": core.VOCABULARY,
                "local_media": False,
            },
            "overview",
        )
        self.assertEqual((self.root / contracts.GENERATED).read_text(), contracts.typescript())

    def test_bad_version_and_nested_condition_fail_with_field_path(self):
        data = copy.deepcopy(self.explorer)
        data["schema_version"] = True
        with self.assertRaisesRegex(MedicalError, r"explorer.schema_version"):
            contracts.validate_payload(data, "explorer")
        data["schema_version"] = 1
        data["entries"][0]["variants"][0]["remaining"] = None
        with self.assertRaisesRegex(MedicalError, r"entries\[0\].variants\[0\].remaining"):
            contracts.validate_payload(data, "explorer")

    def test_missing_visual_role_is_rejected_but_source_extensions_survive(self):
        data = copy.deepcopy(self.explorer)
        data["entries"][0]["retained_source_note"] = {"revision": "unchanged"}
        self.assertIs(contracts.validate_payload(data, "explorer"), data)
        del data["entries"][0]["visuals"]["answer"]
        with self.assertRaisesRegex(MedicalError, r"visuals.answer"):
            contracts.validate_payload(data, "explorer")

    def test_illustration_controls_reject_untyped_extensions(self):
        data = copy.deepcopy(self.explorer)
        entry = next(entry for entry in data["entries"] if entry.get("illustration"))
        for key, invalid in (("initial_candidate", "false"), ("mask_mode", []), ("input_form", 3)):
            with self.subTest(field=key):
                illustration = entry["illustration"]
                original = copy.deepcopy(illustration)
                illustration[key] = invalid
                with self.assertRaisesRegex(MedicalError, rf"illustration.{key}"):
                    contracts.validate_payload(data, "explorer")
                entry["illustration"] = original


if __name__ == "__main__":
    unittest.main()
