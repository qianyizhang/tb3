"""Build symbolic CRC-classification contract assets in a fresh explicit directory."""

import argparse
import hashlib
import io
import json
from pathlib import Path

ENTRY = "automedbench-full-crc-histology-cls-task"
RECEIPT = f"presentation/external-tasks/sources/{ENTRY}-resolution.json"
PACK = "retained-automed-crc-cls-v1"


def encode(data):
    return (json.dumps(data, sort_keys=True, indent=2) + "\n").encode()


def build(root, out, native, source_root=None):
    from PIL import Image

    if out.exists():
        raise ValueError("Refuse overwrite; output must be fresh")
    raw = (root / RECEIPT).read_bytes()
    r = json.loads(raw)
    if r["entry_id"] != ENTRY:
        raise ValueError("Wrong entry receipt")
    if source_root is not None:
        for pin in r["source_pins"]:
            pinned = (source_root / pin["path"]).read_bytes()
            if len(pinned) != pin["bytes"] or hashlib.sha256(pinned).hexdigest() != pin["sha256"]:
                raise ValueError("Stale source pin: " + pin["path"])
    classes = r["task_contract"]["classes"]
    assert classes == ["adi", "back", "deb", "lym", "muc", "mus", "norm", "str", "tum"]
    expected = next(
        p["sha256"] for p in r["source_pins"] if p["role"] == "official-upstream-training-tile"
    )
    assert hashlib.sha256(native.read_bytes()).hexdigest() == expected
    image = Image.open(native)
    assert image.mode == "RGB" and image.size == (224, 224)
    image_bytes = io.BytesIO()
    image.save(image_bytes, format="PNG", optimize=False)
    assets = {
        "image.png": image_bytes.getvalue(),
        "source.json": encode(
            {
                "notice": r["top_warning"],
                "role": "official-public-training-example",
                "image_size_px": [224, 224],
                "source_resolution_mpp": 0.5,
                "scale_basis": "Official dataset description, not independently calibrated WSI geometry",
                "color_normalization": "Upstream NCT-CRC-HE-100K Macenko normalization; preview adds none",
                "full_case_id": None,
                "private_label": None,
                "source_coordinates": None,
                "display": "Decoded RGB pixels preserved; no resizing or stain transform",
            }
        ),
        "helper.json": encode(
            {
                "role": "public-upstream-training-folder-not-Full-reference",
                "classes": classes,
                "class_descriptions": r["class_descriptions"],
                "source_member": "NCT-CRC-HE-100K/ADI/ADI-AAAMHQMK.tif",
                "training_label": "adi",
                "training_partition": "NCT-CRC-HE-100K",
                "evaluation_source": "CRC-VAL-HE-7K",
                "checkpoint": None,
                "checkpoint_id2label": None,
                "tiers": {
                    "lite": "ResNet50_Weights.IMAGENET1K_V2, replace nine-class head and fine-tune authorized train only",
                    "standard": "ResNet50 / ConvNeXtTiny / ViTB16; select with balanced accuracy on train-derived validation",
                },
                "index_boundary": "Record and verify checkpoint class order; config tokens do not prove arbitrary checkpoint index mapping",
                "training_labels": "Source ADI folder is public training annotation only; no Full held-out truth retained",
            }
        ),
        "operation.json": encode(
            {
                "role": "symbolic-method-contract",
                "steps": [
                    "Inspect permitted inputs and source partition",
                    "Verify checkpoint id2label and preprocessing",
                    "Infer one canonical class per exact Full ID",
                    "Submit CSV or per-case JSON",
                ],
                "executed": False,
                "model_prediction": None,
            }
        ),
        "output.json": encode(
            {
                "role": "required-schema-not-observed-output",
                "formats": {
                    "csv": "agents_outputs/predictions.csv: patient_id,label",
                    "json": "agents_outputs/{case_id}/prediction.json: label",
                },
                "values": {"patient_id": None, "label": None},
                "prediction": None,
                "private_reference": None,
                "score": None,
                "format_boundary": "Missing cases can pass format if at least one valid prediction is present; wholly empty output fails",
                "accuracy": "correct / all supplied Full case IDs; missing predictions count wrong",
                "balanced_accuracy": "mean recall over configured classes with positive true-class support; absent-class recall null",
                "units": "0..1 fractions, rounded to four decimals",
                "overall": "0.5 workflow + 0.5 configured accuracy",
                "workflow": "S1-S3 None count as zero in full default denominator; S4 .15 and S5 .10 give maximum .25 when those alone complete",
                "tiers": "provisional generic accuracy thresholds .85/.50; not achieved CRC outcomes",
                "CSV_precedence": "CSV nonempty label preferred per ID; JSON fallback; duplicate CSV ID last row wins",
                "clinical_boundary": "clinical_score is dataset agreement, not clinical validation",
                "metric_discrepancy": "Executable config/aggregate headline accuracy; data-policy prose and Standard selection request balanced accuracy. Preserve unresolved discrepancy.",
            }
        ),
        "NOTICE.md": (
            "# Symbolic required-input workflow\n\n"
            + r["actual_data_gap"]
            + "\n\nOfficial acquisition: "
            + r["acquisition_route"]
            + "\n\nOfficial training RGB patch only; public annotation behind helper reveal. No Full test label, checkpoint output, score or clinical finding synthesized.\n"
        ).encode(),
        "DATA-LICENSE.txt": b"CC-BY-4.0. Official training patch and source metadata: Jakob Nikolas Kather, Niels Halama, Alexander Marx, 100,000 histological images of human colorectal cancer and healthy tissue (2018), DOI 10.5281/zenodo.1214456, https://zenodo.org/records/1214456 . RGB TIFF-to-PNG lossless decoding derivative; no resizing or stain processing. Source folder annotation is upstream training helper, not independently adjudicated diagnosis. Full release-owned harness provenance pinned separately.\n",
    }
    manifest = {
        "id": PACK,
        "frame": "upstream-training-tile-grid",
        "units": "0.5 um/pixel and px",
        "license": "CC-BY-4.0",
        "label_license": None,
        "reference_policy": "no-reference-assets",
        "illustration_basis": "mixed",
        "sources": {RECEIPT: hashlib.sha256(raw).hexdigest()},
        "checks": {
            "native_image": True,
            "private_reference": False,
            "model_run": False,
            "evaluator_run": False,
        },
        "assets": [
            {
                "file": name,
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
                "provenance": "source-derived-teaching",
                "role": "illustration",
            }
            for name, data in sorted(assets.items())
        ],
    }
    assets["manifest.json"] = encode(manifest)
    out.mkdir(parents=True)
    for name, data in assets.items():
        (out / name).write_bytes(data)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--native", type=Path, required=True)
    p.add_argument("--source-root", type=Path)
    a = p.parse_args()
    build(
        a.root.resolve(),
        a.output.resolve(),
        a.native.resolve(),
        a.source_root.resolve() if a.source_root else None,
    )


if __name__ == "__main__":
    main()
