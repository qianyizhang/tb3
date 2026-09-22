"""Small synthetic check: uncertain candidates remain primary, subset drops only masks."""

import importlib.util
import json
from pathlib import Path
import sys
import tempfile

import nibabel as nib
import numpy as np

METHOD = Path(__file__).parent
SCORER = METHOD.parent / "longitudinal-ct-image-only/score.py"


def main():
    spec = importlib.util.spec_from_file_location("score", SCORER)
    scorer = importlib.util.module_from_spec(spec)
    sys.modules["score"] = scorer
    spec.loader.exec_module(scorer)
    import evaluate

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        answer, reference = root / "answer", root / "reference"
        answer.mkdir()
        reference.mkdir()
        affine = np.diag([2.0, 2.0, 2.0, 1.0])
        data = np.zeros((20, 20, 20), dtype=np.uint16)
        data[2:5, 2:5, 2:5] = 1
        data[12:15, 12:15, 12:15] = 2
        truth = {
            "schema_version": 1,
            "groups": [
                {"baseline_ids": [i], "followup_ids": [i], "event": "persistent"} for i in [1, 2]
            ],
        }
        candidates = {"schema_version": 1, "visits": {}}
        for visit in ["baseline", "followup"]:
            path = f"{visit}_instances.nii.gz"
            nib.save(nib.Nifti1Image(data, affine), reference / path)
            nib.save(nib.Nifti1Image(data, affine), answer / path)
            candidates["visits"][visit] = [
                {"id": 1, "p_tumor": 0.49, "reason": "Plausible but benign favored."},
                {"id": 2, "p_tumor": 0.5, "reason": "Threshold boundary fixture."},
            ]
        for folder in [answer, reference]:
            (folder / "events.json").write_text(json.dumps(truth))
        (answer / "report.md").write_text("Synthetic contract fixture, not patient evidence.")
        sidecar = answer / "candidates.json"
        sidecar.write_text(json.dumps(candidates))
        result = evaluate.evaluate(answer, reference)
        assert result["valid"]
        assert result["detection_micro"]["tp"] == 4
        assert result["segmentation_gt_macro_dice"] == 1
        assert result["association"]["events_end_to_end"]["tp"] == 2
        subset = result["probable_tumor_subset"]
        assert subset["detection_micro"]["tp"] == 2
        assert subset["detection_micro"]["fn"] == 2
        assert subset["segmentation_gt_macro_dice"] == 0.5
        sidecar.unlink()
        missing = evaluate.evaluate(answer, reference)
        assert not missing["valid"] and missing["original_contract_valid"]
        assert missing["detection_micro"]["tp"] == 4
        assert missing["probable_tumor_subset"] is None
    print(
        json.dumps(
            {
                "synthetic_only": True,
                "low_probability_retained_in_primary": True,
                "subset_threshold_inclusive": True,
                "primary_events_unchanged": True,
                "missing_sidecar_fails_contract_but_retains_original_metrics": True,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
