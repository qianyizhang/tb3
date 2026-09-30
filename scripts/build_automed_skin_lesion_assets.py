#!/usr/bin/env python3
"""Package original public HAM10000 source example plus explicitly authored file contracts."""

import argparse
import base64
import hashlib
import json
from pathlib import Path

ENTRY = "automedbench-full-skin-lesion-cls-task"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, required=True)
    ap.add_argument("--sample", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--source-root", type=Path)
    a = ap.parse_args()
    out = a.output
    if out.exists():
        raise FileExistsError(out)
    rp = a.root / f"presentation/external-tasks/sources/{ENTRY}-resolution.json"
    bp = a.root / f"presentation/external-tasks/briefs/{ENTRY}.md"
    r = json.loads(rp.read_text())
    if r.get("entry_id") != ENTRY:
        raise ValueError("Wrong entry source receipt")
    if a.source_root:
        for pin in (
            r["source_files"]
            + r["retained_source_pins"]
            + r["checkpoint_source_pins"]
            + r["transport_receipts"]
        ):
            path = Path(pin["path"])
            if path.is_absolute():
                path = Path(*path.parts[path.parts.index(".local") :])
            p = a.source_root / path
            if p.stat().st_size != pin["bytes"] or sha(p) != pin["sha256"]:
                raise ValueError(f"Stale source pin: {path}")
    assert sha(bp) == r["brief_sha256"]
    assert sha(a.sample) == r["native_example"]["file"]["sha256"]
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
            "source_mapping",
            "processor_config",
        ]
    }
    source["notice"] = {
        "label": "Source example; Full test absent",
        "text": r["warning_text"],
        "url": r["acquisition_route"],
        "link_label": "Official ISIC archive",
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
                "RGB → pinned processor settings",
                "seven checkpoint indices → canonical strings",
                "one label per staged ID",
            ],
            "mapping": r["source_mapping"],
            "processor": r["processor_config"],
            "actual_case_ids": None,
            "actual_logits": None,
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
            "CSV": "patient_id,label\ntoy-case,melanocytic_nevi",
            "JSON": {"label": "melanocytic_nevi"},
            "toy_row_is_not_displayed_native_case": True,
            "actual_prediction": None,
            "actual_reference": None,
            "metric": "headline macro recall over represented GT classes; missing predictions wrong",
            "missing_gt_caveat": "reference validity not established; missing GT never correct but remains in denominator",
        },
    )
    (out / "NOTICE.md").write_text(
        r["warning_text"]
        + "\n"
        + r["actual_data_gap"]
        + "\nNative public source metadata label is helper only, not diagnosis/model output/private test GT. No native prediction or score.\n"
    )
    (out / "DATA-LICENSE.txt").write_text(
        "Source-delivered ISIC_0024306 JPEG: MILK study team (per-image attribution), HAM10000 ISIC collection212. CC BY-NC 4.0: https://creativecommons.org/licenses/by-nc/4.0/ . Cite Tschandl, P., Rosendahl, C. and Kittler, H. (2018), The HAM10000 dataset, a large collection of multi-source dermatoscopic images of common pigmented skin lesions, Scientific Data 5,180161, doi:10.1038/sdata.2018.161. Official source: https://api.isic-archive.com/collections/212/ . Received JPEG bytes unchanged, no crop/resampling/annotation; API byte-size discrepancy retained. Local noncommercial task interpretation; no publication or blanket Full dataset terms clearance.\n"
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
            "id": "retained-automed-full-skin-lesion-source-v1",
            "frame": "symbolic-unit-grid",
            "units": "unitless",
            "license": "CC-BY-NC-4.0",
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
