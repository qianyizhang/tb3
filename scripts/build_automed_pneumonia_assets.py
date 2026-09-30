#!/usr/bin/env python3
"""Package original public training example plus explicitly authored file contracts."""

import argparse
import base64
import hashlib
import json
from pathlib import Path

ENTRY = "automedbench-full-chest-xray-pneumonia-cls-task"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, required=True)
    ap.add_argument("--sample", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()
    out = a.output
    if out.exists():
        raise FileExistsError(out)
    rp = a.root / f"presentation/external-tasks/sources/{ENTRY}-resolution.json"
    bp = a.root / f"presentation/external-tasks/briefs/{ENTRY}.md"
    r = json.loads(rp.read_text())
    assert sha(bp) == r["brief_sha256"]
    assert sha(a.sample) == r["native_example"]["sha256"]
    out.mkdir(parents=True)

    def put(name, obj):
        (out / name).write_text(json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n")

    source = {
        k: r[k]
        for k in [
            "entry_id",
            "actual_data_gap",
            "acquisition_route",
            "source_roles",
            "task_contract",
            "native_example",
            "prompt_conflict",
        ]
    }
    source["notice"] = {
        "label": "Training example; Full test absent",
        "text": r["warning_text"],
        "url": r["acquisition_route"],
        "link_label": "Official Mendeley data",
    }
    source["preview_data_uri"] = (
        "data:image/jpeg;base64," + base64.b64encode(a.sample.read_bytes()).decode()
    )
    put("source.json", source)
    (out / "source-preview.jpeg").write_bytes(a.sample.read_bytes())
    put(
        "operation.json",
        {
            "steps": [
                "training-derived preprocessing/validation only",
                "record [normal,pneumonia] checkpoint class order",
                "all staged case IDs → one canonical label per case",
            ],
            "source_mapping": {"NORMAL": "normal", "PNEUMONIA": "pneumonia"},
            "native_role": "public training helper; never evaluation reference",
            "test_id_count_target": 100,
            "actual_frozen_ids": None,
        },
    )
    put(
        "output.json",
        {
            "participant_prediction": None,
            "checkpoint": None,
            "score": None,
            "private_reference": None,
            "actual_case_ids": None,
            "CSV": "agents_outputs/predictions.csv: patient_id,label",
            "JSON": "agents_outputs/<case_id>/prediction.json: label",
        },
    )
    put(
        "fixture.json",
        {
            "role": "authored nonpatient syntax/denominator controls only",
            "CSV": "patient_id,label\ntoy-case,normal",
            "JSON": {"label": "normal"},
            "toy_row_is_not_displayed_native_case": True,
            "actual_prediction": None,
            "actual_reference": None,
            "metric": "n_correct / len(patient_ids); missing predictions wrong",
            "missing_gt_caveat": "reference validity not established; missing GT never correct but remains in denominator",
        },
    )
    (out / "NOTICE.md").write_text(
        r["warning_text"]
        + "\n"
        + r["actual_data_gap"]
        + "\nNative public training-folder label is helper only, not diagnosis/model output/private test GT. No native prediction or score.\n"
    )
    (out / "DATA-LICENSE.txt").write_text(
        "Native training JPEG: Kermany, Daniel; Zhang, Kang; Goldbaum, Michael (2018), Labeled Optical Coherence Tomography (OCT) and Chest X-Ray Images for Classification, Mendeley Data, V2, doi:10.17632/rscbjbr9sj.2. CC BY 4.0: https://creativecommons.org/licenses/by/4.0/ . Official dataset: https://data.mendeley.com/datasets/rscbjbr9sj/2 . Source native JPEG bytes unchanged; no crop/resampling/annotation. Task harness retained locally from pinned Full release; no upstream runtime code copied into pack.\n"
    )
    assets = [
        {
            "file": x.name,
            "bytes": x.stat().st_size,
            "sha256": sha(x),
            "role": "input-preview" if x.name == "source-preview.jpeg" else "illustration",
            "provenance": "symbolic-protocol"
            if x.name == "fixture.json"
            else "source-derived-teaching",
        }
        for x in sorted(out.iterdir())
    ]
    put(
        "manifest.json",
        {
            "schema": 1,
            "id": "retained-automed-full-pneumonia-source-v1",
            "frame": "symbolic-unit-grid",
            "units": "unitless",
            "license": "CC-BY-4.0",
            "label_license": None,
            "source_class": "source-derived-teaching",
            "runtime_geometry": "source-records",
            "reference_policy": "no-reference-assets",
            "sources": {
                f"presentation/external-tasks/sources/{ENTRY}-resolution.json": sha(rp),
                f"presentation/external-tasks/briefs/{ENTRY}.md": sha(bp),
            },
            "assets": assets,
        },
    )


if __name__ == "__main__":
    main()
