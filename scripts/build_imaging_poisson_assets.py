"""Build count/log teaching and a reader-only source fixture subset; no task execution."""

import argparse
import ast
import hashlib
import json
import math
import struct
import zipfile
from pathlib import Path

ENTRY = "imaging101-ct-poisson-lowdose"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def subset(path):
    with zipfile.ZipFile(path) as z:
        raw = z.read("output_transmission.npy")
    assert raw[:6] == b"\x93NUMPY" and raw[6:8] == b"\x01\x00"
    n = struct.unpack("<H", raw[8:10])[0]
    h = ast.literal_eval(raw[10 : 10 + n].decode())
    assert h == {"descr": "<f8", "fortran_order": False, "shape": (256, 367)}
    data = raw[10 + n :]
    assert len(data) == 256 * 367 * 8
    return [
        [struct.unpack_from("<d", data, 8 * (v * 367 + c))[0] for c in range(175, 191)]
        for v in range(120, 136)
    ]


def illustrative_postlog(count, incident):
    """Authored toy formula only; validation is not a source runtime claim."""
    if not math.isfinite(count) or count < 0 or not math.isfinite(incident) or incident <= 0:
        raise ValueError("Finite nonnegative count and positive incident count required")
    return -math.log(max(count, 1) / incident)


def verify_pins(root, receipt):
    for pin in (
        receipt["source_files"]
        + receipt["source_inputs"]
        + receipt["source_transport"]
        + receipt["retained_evidence"]
    ):
        path = Path(pin["path"])
        if not path.is_absolute():
            path = root / path
        raw = path.read_bytes()
        if len(raw) != pin["bytes"] or sha(path) != pin["sha256"]:
            raise ValueError(f"Stale source pin: {pin['path']}")
        if (
            "git_blob" in pin
            and hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
            != pin["git_blob"]
        ):
            raise ValueError(f"Stale Git blob: {pin['path']}")


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--root", type=Path, required=True)
    a.add_argument("--source-root", type=Path, required=True)
    a.add_argument("--source-license", type=Path, required=True)
    a.add_argument("--physics-fixture", type=Path, required=True)
    a.add_argument("--output", type=Path, required=True)
    a = a.parse_args()
    rp = a.root / f"presentation/external-tasks/sources/{ENTRY}-resolution.json"
    bp = a.root / f"presentation/external-tasks/briefs/{ENTRY}.md"
    r = json.loads(rp.read_text())
    assert sha(bp) == r["brief_sha256"]
    verify_pins(a.source_root, r)
    for evidence in r["constant_range_source_evidence"].values():
        assert evidence["verified_source_excerpt"] in (a.source_root / evidence["path"]).read_text()
    f = r["fixture"]
    assert f["postlog"] == [illustrative_postlog(x, f["I0"]) for x in f["illustrative_counts"]]
    assert sha(a.source_license) == next(
        x["sha256"] for x in r["source_files"] if x["path"].endswith("/LICENSE")
    )
    pin = next(x for x in r["source_inputs"] if x["path"].endswith("physics_model_fixtures.npz"))
    assert pin["manifest_match"] and sha(a.physics_fixture) == pin["sha256"]
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
        "label": "300-photon noisy input unmatched",
        "text": r["warning_text"],
        "url": r["acquisition_route"],
        "link_label": "Official Imaging101 acquisition",
    }
    put("source.json", s)
    put("fixture.json", r["fixture"])
    reference = dict(r["public_reference"])
    reference["expected_count_subset"] = {
        "source_sha256": pin["sha256"],
        "member": "output_transmission.npy",
        "native_shape": [256, 367],
        "view_indices": [120, 136],
        "channel_indices": [175, 191],
        "frame": "parallel-beam view/detector indices",
        "units": "expected photons/bin",
        "I0": 300,
        "values": subset(a.physics_fixture),
        "derivation": "Native contiguous 16 views x16 channels, no resize/normalization; display0..300 expected photons",
        "prohibited_roles": [
            "measured noisy realization",
            "reconstruction",
            "ground truth",
            "participant output",
        ],
    }
    put("reference.json", reference)
    put(
        "operation.json",
        {
            "stages": ["Poisson expected counts", "floor/log and weights", "weighted TV contract"],
            "actual_task_execution": False,
            "units_conflict": "cm^-1 vs mm^-1",
        },
    )
    put(
        "output.json",
        {
            "reconstruction_npy": None,
            "actual_image": None,
            "quality_score": None,
            "task_outcome": None,
        },
    )
    (a.output / "SOURCE-LICENSE.txt").write_bytes(a.source_license.read_bytes())
    (a.output / "DATA-LICENSE.txt").write_text(
        "AI4ImagingLab Imaging101 pinned source/physics fixtures MIT; original symbolic rays/count examples MIT. No patient image, noisy300 acquisition, reconstruction or GT image included. Full source license retained.\n"
    )
    (a.output / "NOTICE.md").write_text(
        "AI4ImagingLab imaging-101-release dc2f668939b21e8312e22529615def610f8611df, MIT. HF revision a9de559b54849a25988a8a0d8a5e869063a5a7a3. "
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
            "id": "retained-imaging101-poisson-source-v1",
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
