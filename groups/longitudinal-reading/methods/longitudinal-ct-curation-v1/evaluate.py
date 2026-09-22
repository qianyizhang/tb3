"""Private candidate-contract wrapper around the unchanged scientific scorer."""

import argparse
import json
import math
from pathlib import Path
import tempfile

import nibabel as nib
import numpy as np

import score


def validate_candidates(path, ids):
    obj = json.loads(Path(path).read_text())
    if not isinstance(obj, dict) or obj.get("schema_version") != 1:
        raise ValueError("candidates schema_version must be 1")
    visits = obj.get("visits")
    if not isinstance(visits, dict) or set(visits) != set(score.VISITS):
        raise ValueError("candidates visits must contain baseline and followup")
    for visit in score.VISITS:
        rows = visits[visit]
        if not isinstance(rows, list):
            raise ValueError(f"{visit} candidates must be an array")
        seen = set()
        for row in rows:
            if not isinstance(row, dict):
                raise ValueError("each candidate must be an object")
            ident = row.get("id")
            if type(ident) is not int or ident <= 0 or ident in seen:
                raise ValueError("candidate IDs must be unique positive integers")
            seen.add(ident)
            probability = row.get("p_tumor")
            if (
                type(probability) not in (int, float)
                or not math.isfinite(probability)
                or not 0 <= probability <= 1
            ):
                raise ValueError("p_tumor must be a finite number in [0,1]")
            if not isinstance(row.get("reason"), str) or not row["reason"].strip():
                raise ValueError("each candidate requires a nonempty reason")
        if seen != set(ids[visit]):
            raise ValueError(f"{visit} candidate IDs must exactly match mask IDs")
    return visits


def evaluate(answer, reference):
    result = score.score(answer, reference)
    result["original_contract_valid"] = result["valid"]
    try:
        if not all(v["valid"] for v in result["visits"].values()):
            raise ValueError("valid masks are required to check the candidate contract")
        candidates = validate_candidates(
            answer / "candidates.json", {v: result["visits"][v]["ids"] for v in score.VISITS}
        )
        result["candidate_contract"] = {"valid": True, "visits": candidates}
        subset = {}
        with tempfile.TemporaryDirectory(prefix="probable-candidates-") as directory:
            for visit in score.VISITS:
                image = nib.load(answer / f"{visit}_instances.nii.gz")
                data = np.asarray(image.dataobj).copy()
                kept = [row["id"] for row in candidates[visit] if row["p_tumor"] >= 0.5]
                data[~np.isin(data, kept)] = 0
                path = Path(directory) / f"{visit}_instances.nii.gz"
                nib.save(nib.Nifti1Image(data, image.affine, image.header), path)
                subset[visit] = score.visit_score(path, reference / path.name)
        result["probable_tumor_subset"] = {
            "threshold": 0.5,
            "visits": subset,
            "detection_micro": score.prf(
                *(sum(r["detection"][k] for r in subset.values()) for k in ("tp", "fp", "fn"))
            ),
            "segmentation_gt_macro_dice": score.avg(
                [x["best_one_to_one_dice"] for r in subset.values() for x in r["per_gt"]]
            ),
            "association": "not filtered or reinterpreted; see all-candidate primary endpoints",
        }
    except Exception as exc:
        result["candidate_contract"] = {"valid": False, "reason": str(exc)}
        result["probable_tumor_subset"] = None
    result["valid"] = result["original_contract_valid"] and result["candidate_contract"]["valid"]
    return result


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--answer", type=Path, default=Path("/app/answer"))
    parser.add_argument("--reference", type=Path, default=Path("/tests/reference"))
    parser.add_argument("--output", type=Path, default=Path("/logs/verifier"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    result = evaluate(args.answer, args.reference)
    (args.output / "metrics.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    (args.output / "reward.txt").write_text(str(int(result["valid"])) + "\n")
    print(
        json.dumps({"contract_valid": result["valid"], "reward_meaning": result["reward_meaning"]})
    )


if __name__ == "__main__":
    main()
