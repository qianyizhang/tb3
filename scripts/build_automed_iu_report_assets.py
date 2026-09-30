"""Deterministic source-pinned symbolic IU study contract pack; no patient report."""

import argparse
import hashlib
import json
from pathlib import Path

ENTRY = "automedbench-full-iu-xray-report-task"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, required=True)
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
        raise ValueError("Wrong source receipt")
    if a.source_root:
        for pin in r["source_files"] + r["retained_source_pins"]:
            p = a.source_root / pin["path"]
            if p.stat().st_size != pin["bytes"] or sha(p) != pin["sha256"]:
                raise ValueError(f"Stale source pin: {p}")
    assert sha(bp) == r["brief_sha256"]
    out.mkdir(parents=True)

    def put(n, o):
        (out / n).write_text(json.dumps(o, sort_keys=True, separators=(",", ":")) + "\n")

    source = {
        k: r[k]
        for k in [
            "entry_id",
            "actual_data_gap",
            "acquisition_route",
            "source_roles",
            "task_contract",
            "runtime_discrepancy",
            "native_examples",
        ]
    }
    source["notice"] = {
        "label": "Symbolic IU study; matching data absent",
        "text": r["warning_text"],
        "url": r["acquisition_route"],
        "link_label": "Official Open-i acquisition",
    }
    put("source.json", source)
    put(
        "study.json",
        {
            "role": "authored illustrative study/image sockets, no patient data",
            "study_id": "toy-study",
            "image_sockets": ["toy-image-A", "toy-image-B"],
            "reports_required": 1,
            "actual_case_ids": None,
            "actual_images": None,
        },
    )
    put(
        "operation.json",
        {
            "unit": "study",
            "views_per_case": "one_or_more",
            "min_chars": 40,
            "max_chars": 8000,
            "min_alpha_chars": 20,
            "printable": "Python string.printable",
            "runtime_discrepancy": r["runtime_discrepancy"],
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
            "path": "agent_outputs/<case_id>/report.txt",
        },
    )
    put(
        "fixture.json",
        {
            "role": "authored nonclinical syntax only",
            "text": "This illustrative text demonstrates a plain file format only. It describes no patient or medical finding.",
            "actual_prediction": None,
            "actual_reference": None,
            "toy_row_is_not_displayed_native_case": True,
        },
    )
    (out / "NOTICE.md").write_text(
        r["warning_text"]
        + "\n"
        + r["actual_data_gap"]
        + "\nNo public or private source report is bundled.\n"
    )
    (out / "DATA-LICENSE.txt").write_text(
        "Authored symbolic teaching sockets/text only; no IU image/report redistribution. Source contract from pinned Full package. Exact IU dataset terms are unverified: retained headers and current FAQ timeout do not establish licence content or redistribution permission. No dataset licence clearance or publication implied.\n"
    )
    assets = [
        {
            "file": x.name,
            "bytes": x.stat().st_size,
            "sha256": sha(x),
            "role": "illustration",
            "provenance": "symbolic-protocol"
            if x.name in {"study.json", "fixture.json"}
            else "source-derived-teaching",
        }
        for x in sorted(out.iterdir())
    ]
    put(
        "manifest.json",
        {
            "schema": 1,
            "id": "retained-automed-full-iu-report-workflow-v1",
            "frame": "symbolic-unit-grid",
            "units": "unitless",
            "license": "LicenseRef-IU-symbolic-teaching",
            "label_license": None,
            "source_class": "source-derived-teaching",
            "runtime_geometry": "source-records",
            "reference_policy": "no-reference-assets",
            "sources": {str(rp.relative_to(a.root)): sha(rp), str(bp.relative_to(a.root)): sha(bp)},
            "assets": assets,
        },
    )


if __name__ == "__main__":
    main()
