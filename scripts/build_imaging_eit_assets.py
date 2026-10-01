"""Read pinned NPZ bytes without NumPy or executing an EIT solver/scorer."""

import argparse
import ast
import hashlib
import json
import math
import struct
import zipfile
from pathlib import Path

ENTRY = "imaging101-eit-conductivity-reconstruction"
PACK = "retained-imaging-eit-v1"
FRAME = "EIT-native-boundary-voltage-plus-symbolic-inverse"


def npy(raw):
    if raw[:6] != b"\x93NUMPY" or raw[6] not in (1, 2):
        raise ValueError("Unsupported numeric NPY")
    offset = 10 if raw[6] == 1 else 12
    length = int.from_bytes(raw[8:offset], "little")
    h = ast.literal_eval(raw[offset : offset + length].decode())
    if h["fortran_order"]:
        raise ValueError("Fortran order unsupported")
    formats = {"<f8": "d", "<i8": "q", "<i4": "i", "|b1": "?"}
    fmt = formats[h["descr"]]
    shape = h["shape"]
    count = math.prod(shape)
    values = list(struct.unpack("<" + str(count) + fmt, raw[offset + length :]))

    def nest(vals, dims):
        if not dims:
            return vals[0]
        if len(dims) == 1:
            return vals
        stride = math.prod(dims[1:])
        return [nest(vals[i * stride : (i + 1) * stride], dims[1:]) for i in range(dims[0])]

    return nest(values, shape), list(shape)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source-root", type=Path, required=True)
    ap.add_argument("--receipt", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()
    r = json.loads(a.receipt.read_text())
    if r["entry_id"] != ENTRY or a.output.exists():
        raise ValueError("Wrong entry or nonfresh output")
    brief = a.receipt.resolve().parents[1] / "briefs" / f"{ENTRY}.md"
    assert hashlib.sha256(brief.read_bytes()).hexdigest() == r["brief_sha256"]
    pins = r["source_pins"]
    for p in pins:
        raw = (a.source_root / p["path"]).read_bytes()
        if len(raw) != p["bytes"] or hashlib.sha256(raw).hexdigest() != p["sha256"]:
            raise ValueError("Stale source pin: " + p["path"])

    def read(suffix):
        matches = [p for p in pins if p["path"].endswith(suffix)]
        if len(matches) != 1:
            raise ValueError("Ambiguous source: " + suffix)
        return a.source_root / matches[0]["path"]

    with zipfile.ZipFile(read("/assets/eit_conductivity_reconstruction/data/raw_data.npz")) as z:
        arrays = {k[:-4]: npy(z.read(k)) for k in z.namelist()}
    fresh = read("/source-evidence/raw_data.npz").read_bytes()
    if fresh != read("/assets/eit_conductivity_reconstruction/data/raw_data.npz").read_bytes():
        raise ValueError("Fresh archive differs")
    bp = {k[3:]: v for k, (v, _shape) in arrays.items() if k.startswith("bp_")}
    if arrays["bp_node"][1] != [376, 3] or arrays["bp_element"][1] != [686, 3]:
        raise ValueError("Changed native geometry")
    if bp["ref_node"] != 16 or len(bp["v0"]) != 208 or len(arrays["jac_dyn_v0"][0]) != 192:
        raise ValueError("Changed reference/protocol")
    if bp["meas_mat"][0] != [3, 2, 0] or bp["ex_mat"][0] != [0, 1]:
        raise ValueError("Changed ordered sign convention")
    out = a.output.resolve()
    out.mkdir(parents=True)

    def put(name, data):
        (out / name).write_text(json.dumps(data, sort_keys=True, separators=(",", ":")) + "\n")

    put(
        "measurement.json",
        {
            k: bp[k]
            for k in ["node", "element", "el_pos", "ref_node", "v0", "v1", "ex_mat", "meas_mat"]
        },
    )
    put(
        "source.json",
        {
            "notice": r["top_warning"],
            "basis": "mixed",
            "private_reference": None,
            "patient": None,
            "source_saved_output_is_agent_result": False,
            "native_shape": {k: shape for k, (_v, shape) in arrays.items()},
            "geometry": "Native synthetic circular FEM geometry; README labels m, V, S/m, not calibrated patient acquisition. Actual raw arrays omit batch axis.",
            "contact": "Point electrode nodes with +/-1 RHS; no finite contact impedance/electrode area, frequency or measured current calibration in source operator.",
            "voltage": "For meas_mat=[N,M,exc], V=potential(exc,N)-potential(exc,M); ref_node 16 fixes additive gauge, distinct from baseline v0.",
            "protocol": "BP/GREIT adjacent drive 208 samples; JAC opposite drive 192. Source index order retained; SVG axes are x-right, y-up.",
        },
    )
    put(
        "helper.json",
        {
            "initially_visible": False,
            "solver_visible_truth": True,
            "private_reference": None,
            "public_truth_role": "Synthetic source anomaly truth already solver-visible; educational reveal only, not prediction or private evaluator.",
            "public_truth": {
                "bp": "8/686 elements have conductivity 10, other 678 have 1; background 1 (README S/m)",
                "greit": "12 elements0.1,16 elements10,658 elements1; four source anomalies",
                "jac_dynamic": "8 elements1000,678 elements1; large contrast does not validate small-perturbation approximation",
            },
            "tiers": {
                "L1": "README + data + requirements; source anomaly conductivity included",
                "L2": "L1 + plan/approach.md",
                "L3": "L1 + complete plan including software design",
            },
            "reset": "Hide on backward replay and chapter exit",
        },
    )
    put(
        "operation.json",
        {
            "executed": False,
            "steps": [
                "Pair ordered v0/v1 at matching measurement index",
                "Preserve N-minus-M voltage convention and reference node",
                "Choose inverse normalization and regularization",
                "Declare node/element/grid domain and scale",
            ],
            "methods": {
                "BP": {
                    "domain": "376 mesh nodes",
                    "normalize": "(v1-v0)/sign(v0.real)",
                    "inverse": "-B.T @ dv, then main multiplies 192; weight none",
                    "path": "output/reconstruction_bp.npy",
                },
                "JAC": {
                    "domain": "686 mesh elements",
                    "normalize": "(v1-v0)/abs(v0)",
                    "inverse": "-H @ dv; Kotre p 0.5, lambda 0.01, normalized Jacobian",
                    "path": "output/reconstruction_jac_dynamic.npy",
                },
                "GREIT": {
                    "domain": "32x32 grid with outside-domain zeros",
                    "normalize": "(v1-v0)/abs(v0)",
                    "inverse": "Regularized Jacobian with sigmoid grid interpolation; p 0.5, lambda 0.01",
                    "path": "output/reconstruction_greit.npz (xg,yg,ds)",
                },
            },
            "linearization": "deltaV approximately J deltaSigma is a local approximation, not a demonstrated guarantee for large source conductivity contrasts.",
        },
    )
    put(
        "output.json",
        {
            "path": "output/reconstruction.npy",
            "prediction": None,
            "map": None,
            "score": None,
            "reference": None,
            "generic": "One real numeric array; shape/key-ranked reference discovery, squeeze dimensions>2, complex magnitude. Absolute versus delta scale is not enforced by shape.",
            "metric": "MSE=mean squared error over all array entries; NRMSE=sqrt(MSE)/(max(gt)-min(gt)); zero range gives infinity. NCC is uncentered cosine with1e-30 denominator epsilon. No flux normalization despite module header.",
            "task_metric": "Source visualization first flux-normalizes by sum(abs(gt))/sum(abs(recon)); NRMSE is L2 error/||gt||, and NCC centers both arrays; BP compares node-interpolated delta truth, JAC element delta, GREIT metrics skipped. Source BP 192 scaling is not generic reference normalization.",
            "reference_summary": "Six float64 truth arrays are (1,686); ndim 2 stays. (1,686) selects absolute bp_perm_anomaly. In full staging, (376,) selects ground_truth_bp delta; (686,) first takes BP376 then shape mismatch. NPY loads do not target-filter. In incomplete staging, saved BP376 may replace missing truth. No-filesystem route requires absent ground_truth.npy. Pin actual files, route and scale before scoring.",
            "reference_selection": "Native ground_truth.npz has six float64 arrays shaped (1,686). Generic preparation squeezes only ndim > 2, preserving this leading singleton. Output (1,686) lexically selects bp_perm_anomaly absolute conductivity; output (686,) matches none of the six arrays. For the incomplete retained tree only, discovery could fall through to saved reconstruction_bp.npy (376,) then shape mismatch; Output (376,) can match saved BP reconstruction, not conductivity truth. The full official tree lists ground_truth_bp.npy, ground_truth_greit.npy and ground_truth_jac_dynamic.npy before saved reconstructions. Newly acquired official NPY bytes match revision-pinned LFS SHA/size: float64/C-order BP delta (376,), GREIT element delta (686,) and JAC element delta (686,). NPY loading returns its array unconditionally: after the NPZ nonmatch, complete-tree discovery takes ground_truth_bp.npy first even for (686,), then shape-mismatch rather than search later shape-compatible files. Output (376,) instead resolves BP delta truth when these full-tree files are staged. No-filesystem scorer instead requires ground_truth.npy under reference_outputs or data; the pinned tree lists neither. Actual reference behavior depends on staged files and filesystem route, not a guaranteed truth or privacy contract.",
            "threshold": "Pinned metrics.json has nested bp/jac_dynamic saved source results; no top-level ncc_boundary or nrmse_boundary, so generic passed=None. No saved numeric result displayed.",
            "limits": r["reopening_condition"],
        },
    )
    (out / "NOTICE.md").write_text(
        r["actual_data_gap"]
        + "\n"
        + r["acquisition_route"]
        + "\nSource truth is already solver-visible; teaching reveal does not establish isolation. No solver/scorer/model was run.\n"
    )
    (out / "DATA-LICENSE.txt").write_text(
        "AI4ImagingLab imaging-101-release pinned dc2f668939b21e8312e22529615def610f8611df declares MIT. Synthetic asset mirror starpacker52/imaging-101 revision a9de559b54849a25988a8a0d8a5e869063a5a7a3; retained native LFS identities verified. Derived geometry/voltage JSON preserves exact source float values and order. Physics source header credits pyEIT, Copyright Benyuan Liu, new BSD; this pack copies no implementation. Local noncommercial task interpretation.\n\n"
        + read("/source-evidence/LICENSE").read_text()
    )
    names = [
        "DATA-LICENSE.txt",
        "NOTICE.md",
        "measurement.json",
        "source.json",
        "helper.json",
        "operation.json",
        "output.json",
    ]
    put(
        "manifest.json",
        {
            "id": PACK,
            "frame": FRAME,
            "units": "m, V; normalized change",
            "license": "MIT",
            "label_license": None,
            "reference_policy": "no-reference-assets",
            "illustration_basis": "mixed",
            "sources": {
                f"presentation/external-tasks/sources/{ENTRY}-resolution.json": hashlib.sha256(
                    a.receipt.read_bytes()
                ).hexdigest(),
                f"presentation/external-tasks/briefs/{ENTRY}.md": hashlib.sha256(
                    brief.read_bytes()
                ).hexdigest(),
            },
            "assets": [
                {
                    "file": n,
                    "bytes": (out / n).stat().st_size,
                    "sha256": hashlib.sha256((out / n).read_bytes()).hexdigest(),
                    "provenance": "source-derived-teaching",
                    "role": "illustration",
                }
                for n in names
            ],
            "checks": {
                "solver_run": False,
                "scorer_run": False,
                "model_run": False,
                "native_synthetic_input": True,
                "private_reference": False,
                "source_truth_reader_reveal": True,
            },
        },
    )


if __name__ == "__main__":
    main()
