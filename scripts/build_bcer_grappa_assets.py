"""Package symbolic GRAPPA rules, never raw patient k-space or reconstruction."""

import argparse
import hashlib
import json
from pathlib import Path

ENTRY = "bcer-short-recon-grappa"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, required=True)
    ap.add_argument("--source-license", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()
    rp = a.root / f"presentation/external-tasks/sources/{ENTRY}-resolution.json"
    bp = a.root / f"presentation/external-tasks/briefs/{ENTRY}.md"
    r = json.loads(rp.read_text())
    assert sha(bp) == r["brief_sha256"]
    pin = next(x for x in r["source_files"] if x["path"].endswith("/LICENSE"))
    assert sha(a.source_license) == pin["sha256"]
    if a.output.exists():
        raise FileExistsError(a.output)
    a.output.mkdir(parents=True)

    def put(n, v):
        (a.output / n).write_text(json.dumps(v, sort_keys=True, separators=(",", ":")) + "\n")

    s = {
        k: r[k]
        for k in [
            "entry_id",
            "actual_data_gap",
            "acquisition_route",
            "source_roles",
            "task_contract",
        ]
    }
    s["notice"] = {
        "label": "Symbolic k-space; matching H5 absent",
        "text": r["warning_text"],
        "url": r["acquisition_route"],
        "link_label": "Official CMRxRecon acquisition",
    }
    put("source.json", s)
    put("fixture.json", r["fixture"])
    put("reference.json", r["public_reference"])
    put(
        "operation.json",
        {
            "stages": ["frame axes/coils", "ACS/mask/mode rules", "IFFT/RSS/typed artifact"],
            "ACS_default": 24,
            "kernel_default": [5, 5],
            "actual_tool_run": False,
        },
    )
    put(
        "output.json",
        {
            "reconstructed_nifti": None,
            "actual_image": None,
            "mode": None,
            "frame_counts": None,
            "elapsed_seconds": None,
            "quality_score": None,
        },
    )
    (a.output / "BCER-LICENSE.txt").write_bytes(a.source_license.read_bytes())
    (a.output / "DATA-LICENSE.txt").write_text(
        "Original symbolic frequency-mask diagrams and mode rules for local task explanation; MIT. No CMRxRecon patient data, measurements or reconstruction included; no source image license or public redistribution permission asserted. BCER code attribution/license retained separately.\n"
    )
    (a.output / "NOTICE.md").write_text(
        "Albertlongzi/BCER source code, pinned d10816712793a9e27f2e70640f9afc06f08a0c5c, MIT full license retained. Original symbolic diagrams label frequency indices, sampled/ACS/missing lines and distinct modes; no measured k-space, pristine target, model/tool trial or clinical image. "
        + r["warning_text"]
        + " "
        + r["acquisition_route"]
        + "\n"
    )
    assets = [
        {
            "file": x.name,
            "bytes": x.stat().st_size,
            "sha256": sha(x),
            "role": "reader-reference-reveal" if x.name == "reference.json" else "illustration",
            "provenance": "symbolic-protocol"
            if x.name == "fixture.json"
            else "source-derived-teaching",
        }
        for x in sorted(a.output.iterdir())
    ]
    put(
        "manifest.json",
        {
            "schema": 1,
            "id": "retained-bcer-grappa-source-v1",
            "frame": "symbolic-unit-grid",
            "units": "unitless",
            "license": "MIT",
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
