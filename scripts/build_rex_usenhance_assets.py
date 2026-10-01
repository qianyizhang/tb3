"""Build only symbolic USEnhance protocol; never import/run preparer or grader."""

import argparse
import hashlib
import json
from pathlib import Path

import yaml

ENTRY = "rexmle-usenhance"
PACK = "symbolic-rex-usenhance-v1"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source-root", type=Path, required=True)
    ap.add_argument("--receipt", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()
    root = a.source_root.resolve()
    r = json.loads(a.receipt.read_text())
    if r["entry_id"] != ENTRY or a.output.exists():
        raise ValueError("Wrong receipt or nonfresh output")
    for pin in r["source_pins"]:
        raw = (root / pin["path"]).read_bytes()
        if len(raw) != pin["bytes"] or hashlib.sha256(raw).hexdigest() != pin["sha256"]:
            raise ValueError("Stale source pin: " + pin["path"])
    cfg = yaml.safe_load(
        (
            root / next(x["path"] for x in r["source_pins"] if x["path"].endswith("/config.yaml"))
        ).read_text()
    )
    if (
        cfg["id"] != "usenhance"
        or cfg["dataset"]["answers"] != "usenhance/prepared/private/test_labels.csv"
    ):
        raise ValueError("Changed private staging")
    out = a.output.resolve()
    out.mkdir(parents=True)

    def put(name, value):
        (out / name).write_text(json.dumps(value, sort_keys=True, indent=2) + "\n")

    put(
        "source.json",
        {
            "notice": r["top_warning"],
            "basis": "symbolic",
            "pixels": None,
            "patient": None,
            "native_geometry": None,
            "pair_id": None,
            "split_ids": None,
            "input": "Required public/test/low_quality PNGs; exact native pair and prepared split absent.",
            "pairing": "Within each organ, same low/high PNG filename; image_id=organ_name+'_'+filename stem. Organ traversal unsorted, low PNGs sorted; no native patient/frame join or registration proof.",
            "partition": "Image-ID train_test_split test_size=0.2,random_state=42; expected 1200/300 only if 1500 valid pairs. Seed does not establish patient isolation or independence from input ordering.",
            "units": "Grader PIL convert L or OpenCV grayscale, then float32 display values. Native dimensions, acoustic intensity, pixel spacing and orientation unverified; no calibrated physical units.",
            "declared_counts": {"patients": 109, "pairs": 1500},
            "observed_counts": None,
        },
    )
    put(
        "helper.json",
        {
            "initially_visible": False,
            "training_high_pixels": None,
            "private_reference": None,
            "public_train": "public/train/low_quality plus matching public/train/high_quality are training helpers, not a held-out answer.",
            "public_test": "public/test/low_quality only",
            "private_test": "private/test/high_quality plus test_labels.csv; no image or reference text included.",
            "rule": "Expected pair mapping is only a source filename rule. No public training pair is acquired or split-qualified, so reveal shows roles only, never pixels.",
            "model": "No fixed checkpoint/model or inference runtime required by these source task files. ML/numerical dependencies and adaptation/training remain unexecuted task work. Public copied grade.py lacks adjacent metric_config.json/leaderboard.csv and still needs rexmle.grade_helpers; standalone recovery unverified.",
            "reset": "Teaching role reveal resets before paint on backwards replay and chapter exit.",
        },
    )
    put(
        "operation.json",
        {
            "executed": False,
            "steps": [
                "Audit organ/filename pair and prepared split membership",
                "Develop method only from public training pairs",
                "Infer each required public-test low without private highs",
                "Write every image ID/path and enhanced PNG",
            ],
            "limitations": "No source prepare, split, training, inference, image enhancement or grader executed; no current model recommendation or availability claim.",
        },
    )
    put(
        "output.json",
        {
            "path": "submission.csv",
            "columns": ["image_id", "enhanced_image_path"],
            "prediction": None,
            "images": None,
            "score": None,
            "reference": None,
            "shape": None,
            "format": "CSV image_id and enhanced_image_path, e.g. enhanced/<image_id>.png. The source loader supports images but required artifact is PNG plus CSV; no actual case ID or pixel dimension illustrated.",
            "geometry": "Grader loads enhanced and private high in grayscale float32; if shapes differ, prediction is INTER_LINEAR resized to high shape. Match does not prove low/high registration or clinical anatomy preservation.",
            "coverage": "Inner merge on image_id then merged-row count equals answer-row count; no explicit uniqueness or set-equivalence guard. Duplicates can offset missing IDs. Mean metric denominator is merged image rows, not patients.",
            "rules": {
                "lncc": "Each image independently min-max normalized; 11 x 11 cv2.filter2D local windows. Valid only where both variance > 1e-10. Uniform normalized images become zeros; allclose branch can return 1 for different original constant levels. Mechanics only, not a measured score.",
                "ssim_psnr": "SSIM and PSNR use joint max-minus-min range, not fixed 255. PSNR in dB, infinite for exact equality; SSIM may be negative. No universal 0..1 restriction or clinical meaning.",
                "rank": "Pinned historical original-challenge leaderboard exists; ReX held-out training split differs original challenge test. Rank comparability is not established. Append submission mean LNCC/SSIM/PSNR, higher-better ranks method=min, then mean ranks lower-better. Percentile=1-(mean_position-1)/number competitor rows, not patient denominator.",
                "fallback": "If leaderboard absent/read fails: overall=-(mean LNCC+mean SSIM+mean PSNR/30). No division by 3, no (PSNR-20)/30 or LNCC shift; differs description normalized composite.",
            },
            "boundary": "ReX task-specific image grader, not generic imaging101 scorer; no hidden Full reference, actual metric, ranking or clinical accuracy. Native pairs/terms/split/patient correspondence remain unresolved.",
        },
    )
    (out / "NOTICE.md").write_text(
        r["actual_data_gap"]
        + "\n"
        + r["acquisition_route"]
        + "\nNo native ultrasound/anatomy, reference pixels, enhanced image or score.\n"
    )
    (out / "DATA-LICENSE.txt").write_text(
        "LicenseRef-TB3-symbolic-teaching: authored noncommercial symbolic sockets and source-derived protocol records. No native ultrasound or private data redistributed. Original USEnhance data terms unverified; this pack does not grant image rights. ReX-MLE adapter b3d8f7c3ff1df5af46d8f3e5312760af3ad18a53 pinned for attribution; no executable grader/preparer copied into pack.\n"
    )
    names = [
        "DATA-LICENSE.txt",
        "NOTICE.md",
        "helper.json",
        "operation.json",
        "output.json",
        "source.json",
    ]
    assets = [
        {
            "file": name,
            "bytes": (out / name).stat().st_size,
            "sha256": hashlib.sha256((out / name).read_bytes()).hexdigest(),
            "provenance": "symbolic-protocol",
            "role": "illustration",
        }
        for name in names
    ]
    put(
        "manifest.json",
        {
            "id": PACK,
            "frame": "symbolic-case-workflow",
            "units": "unitless",
            "license": "LicenseRef-TB3-symbolic-teaching",
            "label_license": None,
            "reference_policy": "no-reference-assets",
            "illustration_basis": "symbolic",
            "sources": {
                "presentation/external-tasks/sources/" + ENTRY + "-resolution.json": hashlib.sha256(
                    a.receipt.read_bytes()
                ).hexdigest()
            },
            "assets": assets,
            "checks": {
                "patient_pixels": False,
                "model_run": False,
                "scorer_run": False,
                "private_reference": False,
            },
        },
    )


if __name__ == "__main__":
    main()
