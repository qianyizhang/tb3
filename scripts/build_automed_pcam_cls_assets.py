"""Build symbolic PCam-classification contract assets in a fresh explicit directory."""

import argparse
import hashlib
import json
from pathlib import Path

ENTRY = "automedbench-full-patchcamelyon-cls-task"
RECEIPT = f"presentation/external-tasks/sources/{ENTRY}-resolution.json"
PACK = "retained-automed-pcam-cls-v1"


def encode(data):
    return (json.dumps(data, sort_keys=True, indent=2) + "\n").encode()


def build(root, out, figure, source_root=None):
    if out.exists():
        raise ValueError("Refuse overwrite; output must be fresh")
    raw = (root / RECEIPT).read_bytes()
    r = json.loads(raw)
    if r.get("entry_id") != ENTRY:
        raise ValueError("Wrong entry receipt")
    if source_root is not None:
        for pin in r["source_pins"]:
            data = (source_root / pin["path"]).read_bytes()
            if len(data) != pin["bytes"] or hashlib.sha256(data).hexdigest() != pin["sha256"]:
                raise ValueError(f"Stale source pin: {pin['path']}")
    classes = r["task_contract"]["classes"]
    assert classes == ["negative", "positive"]
    assert hashlib.sha256(figure.read_bytes()).hexdigest() == r["source_example"]["sha256"]
    assets = {
        "figure.jpg": figure.read_bytes(),
        "source.json": encode(
            {
                "notice": r["top_warning"],
                "role": "symbolic-required-Full-tile-geometry",
                "native_patch": None,
                "full_case_id": None,
                "private_label": None,
                "tile_px": [96, 96],
                "center_px": [32, 32],
                "center_bounds_half_open": [32, 64, 32, 64],
                "units": "px",
                "physical_spacing": None,
            }
        ),
        "helper.json": encode(
            {
                "role": "official-upstream-label-marked-figure-not-Full-reference",
                "classes": classes,
                "source_mapping": {"0": "negative", "1": "positive"},
                "class_descriptions": {
                    "negative": "No tumor pixel in central32x32",
                    "positive": "At least one tumor pixel in central32x32",
                },
                "figure": "figure.jpg",
                "figure_shape_px": [1600, 400],
                "figure_row_ids": None,
                "figure_partition": None,
                "training_label": None,
                "checkpoint": None,
                "checkpoint_id2label": None,
                "tiers": {
                    "lite": "ResNet18_Weights.IMAGENET1K_V1, replace two-class head; train official train only",
                    "standard": "ResNet50 / DenseNet121 / ConvNeXtTiny; select on public validation",
                },
                "index_boundary": "Map0 to negative and1 to positive; verify checkpoint ordering and center-preserving crop/resize",
                "training_labels": "Collage green boxes indicate source positives; no exact training or Fullcase annotation retained",
                "splits": {"train": 262144, "validation": 32768, "test": 32768},
                "split_boundary": "Upstream splits are WSI-disjoint with 50/50 labels; balance of the Full 100-case subset is unverified.",
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
                "tiers": "Provisional generic accuracy thresholds: >= .85 good; >= .50 baseline. Rating also requires format validity.",
                "CSV_precedence": "CSV nonempty label preferred per ID; JSON fallback; duplicate CSV ID last row wins",
                "clinical_boundary": "clinical_score is a source field name for dataset agreement; no clinical benefit established",
            }
        ),
        "NOTICE.md": (
            "# Symbolic required-input workflow\n\n"
            + r["actual_data_gap"]
            + "\n\nOfficial acquisition: "
            + r["acquisition_route"]
            + "\n\nOfficial annotated README collage is reader-reveal teaching imagery only, with unknown row IDs and partition. No native Fulltile, private label, prediction or score is synthesized.\n"
        ).encode(),
        "DATA-LICENSE.txt": b"LicenseRef-PCam-CC0-data-MIT-figure. PCam pinned README declares data CC0 and remaining repository MIT. Official README figure is retained unchanged as teaching imagery with source labels, not a matched dataset case. Bas S. Veeling, Jasper Linmans, Jim Winkens, Taco Cohen, Max Welling, Rotation Equivariant CNNs for Digital Pathology (2018); PCam https://github.com/basveeling/pcam at521af5fc74c20cc6df83974f20abb1d394797612; Camelyon16-derived imagery acknowledged. No model weights or private targets redistributed.\n",
    }
    manifest = {
        "id": PACK,
        "frame": "PCam-symbolic-geometry-plus-README-figure",
        "units": "px",
        "license": "LicenseRef-PCam-CC0-data-MIT-figure",
        "label_license": None,
        "reference_policy": "no-reference-assets",
        "illustration_basis": "mixed",
        "sources": {RECEIPT: hashlib.sha256(raw).hexdigest()},
        "checks": {
            "native_image": False,
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
    p.add_argument("--figure", type=Path, required=True)
    p.add_argument("--source-root", type=Path)
    a = p.parse_args()
    build(
        a.root.resolve(),
        a.output.resolve(),
        a.figure.resolve(),
        a.source_root.resolve() if a.source_root else None,
    )


if __name__ == "__main__":
    main()
