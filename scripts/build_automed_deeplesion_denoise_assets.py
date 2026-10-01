"""Import-safe symbolic DeepLesion noise/contract builder; no FFT/reconstruction/evaluator."""

import argparse
import hashlib
import json
from pathlib import Path

ENTRY = "automedbench-full-deeplesion-denoising-task"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()
    rp = a.root / f"presentation/external-tasks/sources/{ENTRY}-resolution.json"
    bp = a.root / f"presentation/external-tasks/briefs/{ENTRY}.md"
    r = json.loads(rp.read_text())
    assert sha(bp) == r["brief_sha256"]
    if a.output.exists():
        raise FileExistsError(a.output)
    a.output.mkdir(parents=True)

    def put(n, v):
        (a.output / n).write_text(json.dumps(v, sort_keys=True, separators=(",", ":")) + "\n")

    source = {
        k: r[k]
        for k in [
            "entry_id",
            "actual_data_gap",
            "acquisition_route",
            "source_roles",
            "task_contract",
            "source_condition",
        ]
    }
    source["notice"] = {
        "label": "Matching noisy CT / target missing",
        "text": r["warning_text"],
        "url": r["acquisition_route"],
        "link_label": "Official DeepLesion acquisition",
    }
    source["symbolic_display"] = {
        "native_image": None,
        "low_cells": 4,
        "high_cells": 4,
        "native_pixel_parity": "not applicable: no native image; authored symbolic cells only",
        "no_denoising_or_model": True,
    }
    put("source.json", source)
    put("fixture.json", r["fixture"])
    put("reference.json", r["public_reference"])
    put(
        "operation.json",
        {
            "steps": [
                "normalized sigma and unknown clean/noise boundary",
                "Full Lite / Standard help and format checker",
                "same geometry with unknown clean/output values",
            ],
            "native_reconstruction": None,
            "fitting_or_evaluator_executed": False,
        },
    )
    put(
        "output.json",
        {
            "enhanced_npy": None,
            "actual_image": None,
            "quality_score": None,
            "task_outcome": None,
        },
    )
    (a.output / "SOURCE-LICENSE.txt").write_text(
        "Release-owned Full harness source pinned by archive/member SHA; no original clinical data or model license is conveyed. DeepLesion upstream source data reuse terms unresolved, no data supplied.\n"
    )
    (a.output / "DATA-LICENSE.txt").write_text(
        "LicenseRef-AutoMedBench-DeepLesion-symbolic-teaching: authored illustrative pixel values and geometry only; no patient image, private target, model or metric. Controlled DeepLesion dataset rights remain separate.\n"
    )
    (a.output / "NOTICE.md").write_text(
        r["warning_text"]
        + " "
        + r["acquisition_route"]
        + "\nTeal authored noisy cells; outlined clean/output cells unknown, same geometry. Not CT, Gaussian random realization, denoised result, private reference or clinical outcome.\n"
    )
    assets = [
        {
            "file": q.name,
            "bytes": q.stat().st_size,
            "sha256": sha(q),
            "role": "input-preview"
            if q.suffix == ".png"
            else "reader-reference-reveal"
            if q.name == "reference.json"
            else "illustration",
            "provenance": "symbolic-protocol"
            if q.name == "fixture.json"
            else "source-derived-teaching",
        }
        for q in sorted(a.output.iterdir())
    ]
    put(
        "manifest.json",
        {
            "schema": 1,
            "id": "retained-automedbench-full-deeplesion-denoising-task-source-v1",
            "frame": "DeepLesion-normalized-noise-symbolic-grid-only",
            "units": "illustrative normalized intensity and sigma; no HU or physical voxel scale",
            "license": "LicenseRef-AutoMedBench-DeepLesion-symbolic-teaching",
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
