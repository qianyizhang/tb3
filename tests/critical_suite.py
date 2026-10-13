"""Fast hosted regressions for shared contracts and evidence integrity.

The full catalogue/story and rendering suites remain local gates (make check and
make presentation-check). Keep this list explicit so CI scope changes are reviewable.
"""

import unittest

MODULES = [
    "test_storage",
    "test_tb3_hygiene",
    "test_doc_links",
    "test_skill_checks",
    "test_medical",
    "test_methods",
    "test_workflow_refinements",
    "test_harbor_import",
    "test_hub",
    "test_task_package",
    "test_artifact_retention",
    "test_evidence",
    "test_datasets",
    "test_dataset_previews",
    "test_landmark_scoring",
    "test_litemedsam_skill",
    "test_frontend",
    "test_presentation_contracts",
    "test_explainer_framework",
    "test_native_trace",
    "test_landmark_trace",
    "test_mri_trace",
    "test_coronary_trace",
]

if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromNames(MODULES)
    )
    raise SystemExit(not result.wasSuccessful())
