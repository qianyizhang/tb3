"""Author-only image/reference checks and native-slice illustrations before inference."""

import csv
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / ".local/longitudinal-ct-case02"


def main():
    acquisition = json.loads((BASE / "source/acquisition.json").read_text())
    pid = acquisition["patient"]
    for record in acquisition["files"]:
        assert (
            hashlib.sha256((BASE / "raw" / record["member"]).read_bytes()).hexdigest()
            == record["sha256"]
        )
    rows = list(csv.DictReader((BASE / "raw/inputsTr" / f"{pid}.csv").open()))
    by_id = {int(r["lesion_id"]): r for r in rows}
    assert all(r["linking_unclear"] == "False" for r in rows)
    output = BASE / "review"
    output.mkdir(exist_ok=False)
    result = {
        "patient": pid,
        "visits": {},
        "figures": [],
        "limits": "Geometry/label checks and author visual review do not constitute expert malignancy adjudication. GT-selected slices/crops are author-only; no solver hints.",
    }
    for visit, short, folder in [("baseline", "BL", "inputsTr"), ("followup", "FU", "targetsTr")]:
        image = nib.load(BASE / "raw/inputsTr" / f"{pid}_{short}_img_00.nii.gz")
        reference = nib.load(BASE / "raw" / folder / f"{pid}_{short}_mask_00.nii.gz")
        assert image.shape == reference.shape and np.array_equal(image.affine, reference.affine)
        a = np.asarray(image.dataobj)
        mask = np.asarray(reference.dataobj)
        ids = [int(x) for x in np.unique(mask) if x]
        expected = sorted(
            i
            for i, r in by_id.items()
            if (visit == "baseline" and r["topology_class"] != "NEWLYAPPEARING")
            or (visit == "followup" and r["topology_class"] != "DISAPPEARING")
        )
        assert ids == expected
        voxel_ml = abs(np.linalg.det(image.affine[:3, :3])) / 1000
        labels = []
        for ident in ids:
            where = np.argwhere(mask == ident)
            low = where.min(0)
            high = where.max(0)
            source = by_id[ident]
            declared = float(source["volume_bl" if visit == "baseline" else "volume_fu"]) / 1000
            volume = len(where) * voxel_ml
            k = int(np.bincount(where[:, 2], minlength=image.shape[2]).argmax())
            roi = mask[
                tuple(
                    slice(max(0, lower - 1), min(n, h + 2))
                    for lower, h, n in zip(low, high, image.shape)
                )
            ]
            expanded = ndimage.binary_dilation(
                roi == ident, structure=ndimage.generate_binary_structure(3, 1)
            )
            adjacent = [int(x) for x in np.unique(roi[expanded]) if x not in [0, ident]]
            labels.append(
                {
                    "id": ident,
                    "anatomy": source["lesion_type"],
                    "event": source["topology_class"],
                    "volume_ml": volume,
                    "csv_volume_ml": declared,
                    "csv_difference_voxels": (volume - declared) / voxel_ml,
                    "centroid_ijk": where.mean(0).tolist(),
                    "bbox_ijk": [low.tolist(), high.tolist()],
                    "max_area_k": k,
                    "six_connected_components": int(ndimage.label(roi == ident)[1]),
                    "touching_other_labels_6": adjacent,
                    "edge_margin_voxels": int(
                        min(low.min(), (np.array(image.shape) - 1 - high).min())
                    ),
                    "hu_percentiles_5_50_95": np.percentile(a[mask == ident], [5, 50, 95]).tolist(),
                }
            )
        result["visits"][visit] = {
            "shape": image.shape,
            "spacing_mm": image.header.get_zooms(),
            "axcodes": nib.aff2axcodes(image.affine),
            "affine": image.affine.tolist(),
            "image_mask_geometry_equal": True,
            "labels": labels,
        }
        for page, start in enumerate(range(0, len(labels), 8), 1):
            selected = labels[start : start + 8]
            nrows = (len(selected) + 1) // 2
            fig, axes = plt.subplots(
                nrows, 4, figsize=(14, 3.3 * nrows), squeeze=False, layout="constrained"
            )
            for ax in axes.flat:
                ax.axis("off")
            for n, label in enumerate(selected):
                r = n // 2
                c = (n % 2) * 2
                k = label["max_area_k"]
                ident = label["id"]
                center = np.argwhere(mask[:, :, k] == ident).mean(0)
                half = 45 / float(image.header.get_zooms()[0])
                window = (-200, 1000) if label["anatomy"] == "Skeleton" else (-160, 240)
                for offset in [0, 1]:
                    ax = axes[r, c + offset]
                    ax.imshow(
                        a[:, :, k].T, cmap="gray", vmin=window[0], vmax=window[1], origin="upper"
                    )
                    if offset:
                        ax.contour(
                            (mask[:, :, k] == ident).T,
                            levels=[0.5],
                            colors=["#20c7dc"],
                            linewidths=1,
                        )
                    ax.set_xlim(center[0] - half, center[0] + half)
                    ax.set_ylim(center[1] + half, center[1] - half)
                    ax.set_title(
                        f"{'CT' if not offset else 'GT cyan solid'} | ID {ident}, k={k}\n{label['anatomy']}, {label['volume_ml']:.3f} mL",
                        fontsize=9,
                    )
            fig.suptitle(
                f"Case 02 author review | {visit}, sheet {page}\nGT-selected native axial planes and 90 mm crops; i right, j down. Soft HU [-160,240]; bone HU [-200,1000].\nLongitudinal-CT v3, FDAT / University Hospital Tuebingen, CC BY-NC 4.0. Never solver input.",
                fontsize=11,
            )
            path = output / f"{visit}-{page}.png"
            fig.savefig(path, dpi=130)
            plt.close(fig)
            result["figures"].append(
                {
                    "path": str(path.relative_to(ROOT)),
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                }
            )
    (output / "geometry.json").write_text(
        json.dumps(
            result, indent=2, default=lambda x: x.item() if isinstance(x, np.generic) else list(x)
        )
        + "\n"
    )
    print(
        json.dumps(
            {
                "patient": pid,
                "counts": {v: len(d["labels"]) for v, d in result["visits"].items()},
                "figures": result["figures"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
