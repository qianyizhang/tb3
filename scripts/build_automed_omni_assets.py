"""Package public README question/options, missing-image mechanics and separate annotation."""

import argparse
import hashlib
import json
from pathlib import Path

ENTRY = "automedbench-full-vqa-omnimedvqa-task"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, required=True)

    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()
    out = a.output
    if out.exists():
        raise FileExistsError(out)
    rp = a.root / f"presentation/external-tasks/sources/{ENTRY}-resolution.json"
    bp = a.root / f"presentation/external-tasks/briefs/{ENTRY}.md"
    r = json.loads(rp.read_text())
    assert sha(bp) == r["brief_sha256"]
    out.mkdir(parents=True)

    def put(n, o):
        (out / n).write_text(json.dumps(o, sort_keys=True, separators=(",", ":")) + "\n")

    s = {
        k: r[k]
        for k in [
            "entry_id",
            "actual_data_gap",
            "acquisition_route",
            "source_roles",
            "task_contract",
            "source_question",
            "source_geometry",
        ]
    }
    s["notice"] = {
        "label": "Source QA; matching image/private answer absent",
        "text": r["warning_text"],
        "url": r["acquisition_route"],
        "link_label": "OmniMedVQA dataset route",
    }
    put("source.json", s)
    put("reference.json", r["public_reference"])
    put(
        "operation.json",
        {
            "steps": [
                "Bind image/question/options",
                "A-D parser controls",
                "Schema/scorer boundary",
            ],
            "actual_decode": None,
            "task_specific_smoke_bounds": [1, 10],
            "config_smoke_bounds": [1, 10],
        },
    )
    put(
        "output.json",
        {
            "question_id": None,
            "predicted_label": None,
            "predicted_answer": None,
            "raw_model_output": None,
            "model_name": None,
            "runtime_s": None,
            "private_reference": None,
            "score": None,
        },
    )
    put("fixture.json", r["fixture"])
    (out / "NOTICE.md").write_text(
        r["warning_text"]
        + "\n"
        + r["actual_data_gap"]
        + "\nreference.json is public source README annotation for later reader reveal only, never private Full gold.\n"
    )
    (out / "DATA-LICENSE.txt").write_text(
        "OmniMedVQA, Yutao Hu, Tianbin Li, Quanfeng Lu, Wenqi Shao, Junjun He, Yu Qiao, Ping Luo (2024), arXiv2402.09181. foreverbeliever/OmniMedVQA pinned1ba51c28fc0773bdf7efb8396e5bcfd4227e22da; official source card public QA example retained. No global image license, original image terms/rights remain source-owned. No medical image acquired or reproduced; missing socket and parser examples original symbolic teaching only, noncommercial local explanation; no publication, model output, clinical finding or Full reference.\n"
    )
    assets = [
        {
            "file": x.name,
            "bytes": x.stat().st_size,
            "sha256": sha(x),
            "role": "reader-reference-reveal"
            if x.name == "reference.json"
            else "input-preview"
            if x.name == "source-preview.jpeg"
            else "illustration",
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
            "id": "retained-automed-omni-source-v1",
            "frame": "symbolic-unit-grid",
            "units": "unitless",
            "license": "LicenseRef-OmniMedVQA-per-source-symbolic-teaching",
            "label_license": None,
            "source_class": "source-derived-teaching",
            "runtime_geometry": "source-records",
            "reference_policy": "reader-reference-reveal",
            "sources": {str(rp.relative_to(a.root)): sha(rp), str(bp.relative_to(a.root)): sha(bp)},
            "assets": assets,
        },
    )


if __name__ == "__main__":
    main()
