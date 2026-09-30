"""Build exact Full Spleen and TSG teaching packs from source records only."""
from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import io
import json
import struct
from pathlib import Path

import numpy as np
from PIL import Image

SRC = Path(".local/explainers/core-20260929/automed-seg-d-source")
KEYS = ("spleen", "tsg-multiorgan")


def root():
    for p in Path(__file__).resolve().parents:
        if (p / "presentation/EXPLAINER-SCOPE.json").exists():
            return p
    raise RuntimeError("tb3 root not found")


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def dump(p, d):
    p.write_text(json.dumps(d, sort_keys=True, separators=(",", ":")) + "\n")


def uri(arr, mode):
    stream = io.BytesIO()
    Image.fromarray(arr, mode=mode).save(stream, format="PNG", optimize=False)
    return "data:image/png;base64," + base64.b64encode(stream.getvalue()).decode("ascii")


def volume(path):
    with gzip.open(path, "rb") as stream:
        data = stream.read()
    e = "<" if struct.unpack_from("<i", data)[0] == 348 else ">"
    assert struct.unpack_from(e + "i", data)[0] == 348
    dim = struct.unpack_from(e + "8h", data, 40)
    shape = tuple(dim[1:dim[0] + 1])
    datatype = struct.unpack_from(e + "h", data, 70)[0]
    dtype = {2: "u1", 16: "f4"}[datatype]
    offset = int(struct.unpack_from(e + "f", data, 108)[0])
    arr = np.frombuffer(data, dtype=np.dtype(e + dtype), count=int(np.prod(shape)), offset=offset).reshape(shape, order="F")
    return arr


def make(r, key, out, receipt):
    if key not in KEYS:
        raise ValueError(key)
    if out.exists():
        raise FileExistsError(f"Refusing to overwrite {out}")
    receipt = receipt.resolve()
    d = json.loads(receipt.read_text())
    assert d["entry_id"] == f"automedbench-full-{key}-seg-task" and all(a["attempted_at"] for a in d["attempts"])
    pins = d["source_files"]
    for item in pins.values():
        p = r / item["path"]
        assert sha(p) == item["sha256"], p
    assert len(d["class_map"]) == (1 if key == "spleen" else 117)
    assert {int(value) for value in d["class_map"]} == ({1} if key == "spleen" else set(range(1, 118)))
    pkg = r / pins["task_package"]["path"]
    task = json.loads((r / pins["task_json"]["path"]).read_text())
    assert task["dataset"]["included"] is False and task["output_contract"]["paths"] == ["{case_id}/dseg.nii.gz"]
    sources = {item["path"]: item["sha256"] for item in pins.values()}
    sources[str(receipt.relative_to(r))] = sha(receipt)
    builder = Path(__file__).resolve()
    sources[str(builder.relative_to(r))] = sha(builder)
    views = []
    reference = None
    if key == "spleen":
        ct = volume(r / pins["ct"]["path"])
        label = volume(r / pins["training_label"]["path"])
        assert ct.shape == label.shape == (512, 512, 51)
        assert set(np.unique(label).tolist()) == {0, 1}
        ref_views = []
        for k in (20, 26, 32):
            plane = ct[:, :, k]
            grey = np.rint(np.clip((plane.astype(np.float32) + 160) / 400, 0, 1) * 255).astype(np.uint8)
            view = np.flipud(grey.T)
            mask = np.flipud((label[:, :, k] == 1).T)
            rgba = np.zeros((*mask.shape, 4), np.uint8)
            rgba[mask] = (238, 141, 189, 165)
            views.append({"index": k, "width": 512, "height": 512, "png": uri(view, "L")})
            ref_views.append({"index": k, "overlay_png": uri(rgba, "RGBA"), "source_label_voxels": int(mask.sum())})
        reference = {"role": "public-MSD-training-label-reader-helper-not-Full-private-GT",
                     "source_case": "spleen_19", "views": ref_views,
                     "label": {"1": "spleen"}, "full_private_reference": None, "prediction": None}
        source_case = "spleen_19"
        geometry = pins["ct"]["geometry"]
        display = "axial; flipud(native_i_j_slice.T)"
        selection = "Post hoc teaching planes k=20,26,32 selected with the released training label; not solver-provided locations."
    else:
        prior = json.loads((r / pins["prior_inputs"]["path"]).read_text())
        assert prior["native"]["sha256"] == pins["ct"]["sha256"] and prior["source_case"] == "s1366"
        views = [{"index": v["y"], "width": v["width"], "height": v["height"], "png": v["png"]} for v in prior["views"]]
        source_case = "s1366"
        geometry = pins["ct"]["geometry"]
        display = "coronal; retained published source display"
        selection = "Post hoc teaching planes y=144,164,184; center y=164 was selected in an earlier Lite review using kidney reference information, not a Full solver-provided location."
    assert views
    out.mkdir(parents=True)
    warning = d["actual_data_gap"]
    source = {"entry_id": d["entry_id"], "role": "upstream-source-example-not-proven-Full-case",
              "source_case": source_case, "native_geometry": geometry, "views": views,
              "display": display, "selection": selection, "window_hu": [-160, 240],
              "notice": {"label": "Public source example; Full case unverified", "text": warning, "url": d["acquisition_route"]},
              "full_case_membership": "unverified"}
    output = {"role": "required-empty-output-schema", "path": "agents_outputs/{case_id}/dseg.nii.gz",
              "labels": {"0": "background", **d["class_map"]}, "prediction": None, "score": None,
              "same_shape_required": True, "physical_affine_should_match": True, "scorer_checks_affine": False,
              "scorer_boundary": d["scorer_boundary"]}
    dump(out / "source.json", source)
    dump(out / "output.json", output)
    if reference:
        dump(out / "reference.json", reference)
    (out / "NOTICE.md").write_text("Public source example; Full case unverified. " + warning + " " + d["acquisition_route"] + "\n")
    license_value = "CC-BY-SA-4.0" if key == "spleen" else "CC-BY-4.0"
    (out / "DATA-LICENSE.txt").write_text(license_value + ". Source-derived local teaching extract. " + d["acquisition_route"] + "\n")
    assets = []
    for name in ("source.json", "output.json", "reference.json", "NOTICE.md", "DATA-LICENSE.txt"):
        p = out / name
        if not p.exists():
            continue
        assets.append({"file": name, "sha256": sha(p), "bytes": p.stat().st_size,
                       "provenance": "source-derived-teaching", "role": "reader-reference-reveal" if name == "reference.json" else "illustration"})
    dump(out / "manifest.json", {"id": f"retained-automed-full-{key}-seg-v1",
          "frame": "native-NIfTI-voxel-ijk" if key == "spleen" else "RAS",
          "units": "voxel" if key == "spleen" else "mm", "license": license_value,
          "label_license": license_value if key == "spleen" else None,
          "reference_policy": d["reference_policy"], "sources": sources,
          "checks": {"full_staged_case_verified": False, "full_private_reference": False,
                     "model_run": False, "scorer_run": False, "selected_source_views": len(views),
                     "full_class_map_count": len(d["class_map"])}, "assets": assets})


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--entry", choices=KEYS, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--receipt", type=Path, required=True)
    a = p.parse_args()
    make(root(), a.entry, a.output, a.receipt)
