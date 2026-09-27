"""Derive native source sections and retained point outputs for the landmark story."""

import argparse
import base64
import hashlib
import io
import json
import shutil
from pathlib import Path

import nibabel as nib
import numpy as np
from PIL import Image


def read(path):
    return json.loads(path.read_text())


def sha(path):
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, separators=(",", ":"), allow_nan=False) + "\n")


def build(root, out):
    out.mkdir(parents=True, exist_ok=False)
    audit = read(
        root / "groups/anatomical-landmarks/presentation/sources/named-landmark-audit.json"
    )
    sources = {}

    def load(path):
        path = Path(path)
        digest = sha(root / path)
        assert digest == audit["source_pins"][str(path)], str(path)
        sources[str(path)] = digest
        return root / path

    tasks = {
        "full": Path("runs/br039-ct-landmarks/tasks/ct-full"),
        "partial": Path("runs/br039-ct-landmarks/tasks/ct-partial"),
        "pddca": Path("runs/br038-volume-landmarks/tasks/ct-full"),
        "mri": Path("runs/br038-volume-landmarks/tasks/mri32-full"),
    }
    cases, arrays, refs, outputs = {}, {}, {}, {}
    for key, task in tasks.items():
        image = nib.load(load(task / "environment/volume.nii.gz"))
        arrays[key] = np.load(load(task / "environment/volume.npy"), mmap_mode="r")
        truth = read(load(task / "tests/truth.json"))
        refs[key] = truth.get("targets") or {
            name: {"status": "observed", "ijk": point}
            for name, point in truth["points_ijk"].items()
        }
        cases[key] = {
            "shape": list(image.shape),
            "affine": image.affine.tolist(),
            "spacing": nib.affines.voxel_sizes(image.affine).tolist(),
            "positive_axes": list(nib.aff2axcodes(image.affine)),
            "queries": list(refs[key]),
        }
    for trial in read(root / "docs/evidence/br040-results.json")["trials"]:
        case = {"ct-full": "full", "ct-partial": "partial", "mri32-full": "mri"}[trial["case"]]
        model = "terra" if trial["model_setting"] == "terra-high" else "sol"
        points = read(load(trial["answer_path"]))["landmarks"]
        outputs.setdefault(case, {})[model] = {
            "points": {
                k: v if isinstance(v, dict) else {"status": "observed", "ijk": v}
                for k, v in points.items()
            },
            "success_counts": trial["success_counts_mm"],
            "score": trial["score"],
        }
    pddca_trial = next(
        t
        for t in read(root / "docs/evidence/br038-results.json")["trials"]
        if t["case"] == "ct-full" and "terra" in str(t.get("agent_info"))
    )
    answer = Path(pddca_trial["result_path"]).parent / "artifacts/app/answer/landmarks.json"
    outputs["pddca"] = {
        "terra": {
            "points": {
                k: {"status": "observed", "ijk": v}
                for k, v in read(load(answer))["landmarks"].items()
            },
            "score": pddca_trial["score"],
        }
    }
    # Reference coordinates and all evaluative scores are absent from the input file.
    grades = {
        k: {m: {n: value for n, value in row.items() if n != "points"} for m, row in models.items()}
        for k, models in outputs.items()
    }
    predictions = {
        k: {m: row["points"] for m, row in models.items()} for k, models in outputs.items()
    }
    checked_pixels = 0

    def plane(case, axis, index, bounds, step=1):
        nonlocal checked_pixels
        array = arrays[case]
        dims = [a for a in range(3) if a != axis]
        u, v = dims
        ii = [np.arange(lo, hi, step) for lo, hi in bounds]
        ii[axis] = np.array([index])
        pixels = np.asarray(array[np.ix_(*ii)]).squeeze(axis=axis).T
        # Independently sample actual source array, with row zero at the lowest index.
        for row, col in [
            (0, 0),
            (pixels.shape[0] - 1, pixels.shape[1] - 1),
            (pixels.shape[0] // 2, pixels.shape[1] // 2),
        ]:
            ijk = [0, 0, 0]
            ijk[axis], ijk[u], ijk[v] = index, int(ii[u][col]), int(ii[v][row])
            assert pixels[row, col] == array[tuple(ijk)]
        low, high = (0, 3500) if case == "mri" else (-200, 1300)
        gray = np.round(np.clip((pixels - low) / (high - low), 0, 1) * 255).astype("uint8")
        image = Image.fromarray(gray)
        stream = io.BytesIO()
        image.save(stream, format="PNG", optimize=True)
        encoded = stream.getvalue()
        np.testing.assert_array_equal(np.asarray(Image.open(io.BytesIO(encoded))), gray)
        checked_pixels += gray.size
        spacing = cases[case]["spacing"]
        return {
            "window": [low, high],
            "axis": axis,
            "index": index,
            "u_axis": u,
            "v_axis": v,
            "origin_uv": [int(ii[u][0]), int(ii[v][0])],
            "step": step,
            "width": gray.shape[1],
            "height": gray.shape[0],
            "extent_mm": [gray.shape[1] * step * spacing[u], gray.shape[0] * step * spacing[v]],
            "png": "data:image/png;base64," + base64.b64encode(encoded).decode(),
        }

    def orthogonal(case, centre, half_mm):
        bounds = [
            [max(0, int(np.floor(c - half_mm / s))), min(int(n), int(np.ceil(c + half_mm / s)) + 1)]
            for c, s, n in zip(centre, cases[case]["spacing"], cases[case]["shape"], strict=True)
        ]
        return [plane(case, a, round(centre[a]), bounds) for a in range(3)]

    views = {}
    for key in tasks:
        shape = cases[key]["shape"]
        bounds = [[0, n] for n in shape]
        views[key + "-input"] = [plane(key, 0, shape[0] // 2, bounds, 2)]
    # These diagnostic views are explicitly reader-selected, never supplied hints.
    views["partial-T5"] = orthogonal("partial", refs["partial"]["T5"]["ijk"], 36)
    views["pddca-condyle"] = orthogonal("pddca", refs["pddca"]["mand_r"]["ijk"], 48)
    for key in ["1", "20"]:
        views["mri-" + key] = orthogonal("mri", refs["mri"][key]["ijk"], 28)
    # Animate section selection around T5, not invented point movement or solver search.
    t5 = refs["partial"]["T5"]["ijk"]
    bounds = [[220, 321], [100, 211], [850, 920]]
    views["partial-sweep"] = [plane("partial", 2, k, bounds) for k in range(857, 920, 4)]
    # Mapping sanity at exact native locations and the cropped voxel-cell boundary.
    for case, points in refs.items():
        a = np.array(cases[case]["affine"])
        for row in points.values():
            if row["ijk"] is not None:
                p = np.array([*row["ijk"], 1.0])
                np.testing.assert_allclose(np.linalg.inv(a) @ (a @ p), p, rtol=0, atol=1e-10)
    wrong = np.array(predictions["partial"]["terra"]["T4"]["ijk"])
    assert (
        abs(
            np.linalg.norm(np.array(cases["partial"]["affine"])[:3, :3] @ (wrong - t5))
            - 2.1424121135234606
        )
        < 0.001
    )
    dump(
        out / "source.json",
        {
            "cases": cases,
            "views": views,
            "view_policy": "Input views use native centre sections; diagnostic views are reference-selected reader views. Positive native index right/down, physical aspect preserved. Nearest native samples, fixed window; no rendered image is a solver trajectory.",
        },
    )
    dump(out / "output.json", predictions)
    dump(
        out / "reference.json",
        {
            "points": refs,
            "grades": grades,
            "rater_max_distance_mm": audit["rater_max_distance_to_mean_mm"],
        },
    )
    shutil.copyfile(
        root / "groups/anatomical-landmarks/presentation/sources/afids-cc0-license.txt",
        out / "AFIDS-CC0.txt",
    )
    shutil.copyfile(
        root / "presentation/task-explorer/anatomy-curation/DATA-LICENSE.txt",
        out / "VERSE-CC-BY-SA.txt",
    )
    (out / "NOTICE.md").write_text("""# Native named-landmark teaching assets

Actual retained inputs: PDDCA 1.4.1 subject 0522c0001, AFIDs SNSX sub-C001 and
VerSe sub-verse823. No model calls or new scans. Source hashes are in the manifest.

- VerSe CT and derived sections/points: CC BY-SA 4.0, Sekuboyina et al. and Liebl
  et al.; [source](https://github.com/anjany/verse#license). The included terms
  apply to these derivatives.
- AFIDs MRI and released fiducials: CC0-1.0 at OpenNeuro ds004470 revision
  53f2c2caecf346b620971a5dd4672ca538441ede. Retain acknowledgements to Lau et al.
  and Taha et al.; [source](https://openneuro.org/datasets/ds004470).
  This corrects older CC BY labels; original experiment receipts are preserved.
- PDDCA: public-domain database, Gregory C. Sharp and collaborators;
  [source and release](https://www.imagenglab.com/newsite/pddca/),
  Raudaschl et al., Medical Physics 2017. No CC license is invented for this source.

The manifest's LicenseRef names this mixture, not a replacement license. Source
records and verified terms live in the owning group's presentation/sources folder.

`source.json` contains native sections, affines, query names and display mappings.
Input sections are native midline views; later diagnostic views are explicitly
reference-selected. PNG row/column increase along the recorded native axes. The
viewer preserves physical aspect and prints signed point offsets from each plane.
Images use a fixed intensity window, nearest native samples and optional stride 2;
scoring uses original native coordinates, never these display pixels.

`output.json` contains saved submitted points/statuses, not a solver trajectory.
`reference.json` holds private evaluation points and grades behind a reader reveal.
All visible-target denominators include misses. A point projected onto a section
need not lie in that plane. The full/cropped CT reuses one subject; no atlas image
or unretained registration intermediate is synthesized. MRI atlas assistance,
source uncertainty and the original runtime atlas recovery gap remain explicit.

Rebuild with the existing imaging environment:

```sh
.venv-br033/bin/python -B scripts/build_named_landmark_assets.py --out .local/NEW-LANDMARK-ASSETS
```

The read-only source audit must pass first. Generated story/video outputs stay local.
""")
    names = [
        "source.json",
        "output.json",
        "reference.json",
        "NOTICE.md",
        "AFIDS-CC0.txt",
        "VERSE-CC-BY-SA.txt",
    ]
    dump(
        out / "manifest.json",
        {
            "schema": 1,
            "id": "retained-named-landmarks-v1",
            "frame": "RAS",
            "units": "mm",
            "license": "LicenseRef-NamedLandmarkSources",
            "label_license": "LicenseRef-NamedLandmarkSources",
            "reference_policy": "reader-reference-reveal",
            "sources": sources,
            "source_licenses": {
                "full": "CC-BY-SA-4.0",
                "partial": "CC-BY-SA-4.0",
                "mri": "CC0-1.0",
                "pddca": "Public-domain source statement",
            },
            "checks": {
                "png_pixels_roundtrip": checked_pixels,
                "native_coordinate_roundtrip_mm": 1e-10,
                "partial_t4_to_t5_mm": float(
                    np.linalg.norm(np.array(cases["partial"]["affine"])[:3, :3] @ (wrong - t5))
                ),
                "view_count": sum(map(len, views.values())),
                "source_audit_sha256": sha(
                    root
                    / "groups/anatomical-landmarks/presentation/sources/named-landmark-audit.json"
                ),
                "builder_sha256": sha(root / "scripts/build_named_landmark_assets.py"),
            },
            "assets": [
                {
                    "file": name,
                    "sha256": sha(out / name),
                    "bytes": (out / name).stat().st_size,
                    "provenance": "source-derived-teaching",
                    "role": "reader-reference-reveal"
                    if name == "reference.json"
                    else "illustration",
                }
                for name in names
            ],
        },
    )
    print(
        json.dumps(
            {"out": str(out), "bytes": {name: (out / name).stat().st_size for name in names}}
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    build(args.root.absolute(), args.out.absolute())
