"""Build symbolic brain-classification contract assets in a fresh explicit directory."""

import argparse
import hashlib
import json
from pathlib import Path

ENTRY = "automedbench-full-braintumor-cls-task"
RECEIPT = f"presentation/external-tasks/sources/{ENTRY}-resolution.json"
PACK = "symbolic-automed-brain-cls-v1"


def encode(data):
    return (json.dumps(data, sort_keys=True, indent=2) + "\n").encode()


def build(root, out, source_root=None):
    if out.exists():
        raise ValueError("Refuse overwrite; output must be fresh")
    raw = (root / RECEIPT).read_bytes()
    r = json.loads(raw)
    if r["entry_id"] != ENTRY:
        raise ValueError("Wrong entry receipt")
    if source_root is not None:
        for pin in r["source_pins"]:
            pinned = (source_root / pin["path"]).read_bytes()
            if hashlib.sha256(pinned).hexdigest() != pin["sha256"] or len(pinned) != pin["bytes"]:
                raise ValueError("Stale source pin: " + pin["path"])
    classes = r["task_contract"]["classes"]
    assert classes == ["glioma", "meningioma", "notumor", "pituitary"]
    assets = {
        "source.json": encode(
            {
                "notice": r["top_warning"],
                "role": "symbolic-required-input-socket",
                "filename": "image.jpg",
                "native_image": None,
                "full_case_id": None,
                "private_label": None,
                "training_label": None,
                "geometry": None,
            }
        ),
        "helper.json": encode(
            {
                "role": "public-task-guidance-not-case-label",
                "classes": classes,
                "checkpoint": None,
                "checkpoint_id2label": None,
                "tiers": {
                    "lite": "Named ViT/ResNet guidance; provision and verify checkpoint and dependencies",
                    "standard": "Candidate methods; research and choose a compatible pipeline",
                },
                "index_boundary": "Configured class order is not a checkpoint logit index map",
                "training_labels": "Only genuine upstream training examples may supply source-folder labels; none retained",
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
                "tiers": "accuracy >= .85 good; >= .50 baseline; rating also requires format validity",
                "CSV_precedence": "CSV nonempty label preferred per ID; JSON fallback; duplicate CSV ID last row wins",
                "clinical_boundary": "clinical_score is a source field name for dataset agreement; no clinical benefit established",
            }
        ),
        "NOTICE.md": (
            "# Symbolic required-input workflow\n\n"
            + r["actual_data_gap"]
            + "\n\nOfficial acquisition: "
            + r["acquisition_route"]
            + "\n\nNo MRI image, case label, checkpoint output, score or clinical finding is synthesized.\n"
        ).encode(),
        "DATA-LICENSE.txt": b"Symbolic teaching assets only; LicenseRef-TB3-symbolic-teaching. No dataset image or model weights redistributed. Pinned Full task envelope declares CC BY 4.0 dataset policy; verify official terms and source attribution when obtaining pixels.\n",
    }
    manifest = {
        "id": PACK,
        "frame": "symbolic-case-workflow",
        "units": "unitless",
        "license": "LicenseRef-TB3-symbolic-teaching",
        "label_license": None,
        "reference_policy": "no-reference-assets",
        "illustration_basis": "symbolic",
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
                "provenance": "symbolic-protocol",
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
    p.add_argument(
        "--source-root", type=Path, help="Optional retained-source root for independent pin checks"
    )
    a = p.parse_args()
    build(a.root.resolve(), a.output.resolve(), a.source_root.resolve() if a.source_root else None)


if __name__ == "__main__":
    main()
