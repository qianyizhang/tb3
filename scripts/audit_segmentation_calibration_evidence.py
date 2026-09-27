"""Read-only replay of the saved SAM2/LiteMedSAM slice calibration; no inference."""

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import nibabel as nib
import numpy as np
from scipy import ndimage
from scipy.spatial import cKDTree

ORGANS = ["liver", "kidney_right", "gallbladder", "pancreas", "adrenal_gland_right", "duodenum"]
TAGS = ["sam2-mps", "lite-mps", "sam2-cpu-subset", "lite-cpu-subset", "sam2-cpu"]


def read(path):
    return json.loads(path.read_text())


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def metrics(pred, ref, spacing):
    """Same 2D definition, independently evaluate distances with nearest neighbours."""
    p, r = int(pred.sum()), int(ref.sum())
    inter = int((pred & ref).sum())
    distances = None
    if p and r:
        a = np.argwhere(pred ^ ndimage.binary_erosion(pred)) * spacing
        b = np.argwhere(ref ^ ndimage.binary_erosion(ref)) * spacing
        distances = np.concatenate([cKDTree(a).query(b)[0], cKDTree(b).query(a)[0]])
    return {
        "dice": 2 * inter / (p + r) if p + r else None,
        "precision": inter / p if p else 0.0,
        "recall": inter / r if r else None,
        "hd95_mm": float(np.percentile(distances, 95)) if distances is not None else None,
        "pred_pixels": p,
        "gt_pixels": r,
        "intersection": inter,
        "false_positive_pixels": p - inter,
        "false_negative_pixels": r - inter,
    }


def audit(root, out):
    out.mkdir(parents=True, exist_ok=False)
    pins = {}

    def pin(path, expected=None):
        path = Path(path)
        relative = path.relative_to(root) if path.is_absolute() else path
        digest = sha(root / relative)
        if expected is not None:
            assert digest == expected, str(relative)
        pins[str(relative)] = digest
        return root / relative

    group = Path("groups/anatomy-audit")
    experiment = group / "experiments/sam-litemedsam-slice-calibration"
    base = Path(".local/sam-lite-bench-20260921")
    pin(Path(__file__))
    pin(experiment / "protocol.md")
    pin(experiment / "summarize.py")
    bench = pin(experiment / "bench.py")
    original = read(pin(group / "findings/evidence/sam-litemedsam-slice-calibration.json"))
    local_summary = read(pin(base / "summary/summary.json"))
    assert {k: original[k] for k in local_summary} == local_summary
    manifest = read(pin(base / "samples/manifest.json"))
    assert manifest["source_hashes"] == original["source_hashes"]
    assert sha(bench) == original["bench_script_sha256"]
    assert sha(root / experiment / "summarize.py") == original["analysis_script_sha256"]
    assert sha(root / base / "samples/manifest.json") == original["sample_manifest_sha256"]
    data = np.load(pin(base / "samples/arrays.npz", manifest["arrays_sha256"]))
    authority_path = group / "experiments/ct-organ-segmentation-astra-xhigh/source"
    authority = read(pin(authority_path / "selected-source-manifest.json"))
    source_hashes = {row["path"]: row["sha256"] for row in authority["files"]}
    for item in authority["licenses"].values():
        license_file = pin(authority_path / item["file"], item["sha256"])
        assert license_file.stat().st_size == item["bytes"]
    source = Path("runs/br004-v1/source/s1233")
    assert len(manifest["source_hashes"]) == 7
    for name, digest in manifest["source_hashes"].items():
        assert digest == source_hashes[name]
        pin(source / name, digest)
    ct = nib.load(root / source / "ct.nii.gz")
    image = np.asarray(ct.dataobj, dtype=np.float32)
    assert list(ct.shape) == manifest["shape"] == [265, 265, 401]
    np.testing.assert_array_equal(ct.affine, manifest["affine"])
    np.testing.assert_array_equal(ct.header.get_zooms(), manifest["spacing_mm"])
    assert manifest["spacing_mm"] == [1.5, 1.5, 1.5]
    samples, reconstruction = [], []
    for organ in ORGANS:
        ref_image = nib.load(root / source / "segmentations" / (organ + ".nii.gz"))
        np.testing.assert_array_equal(ref_image.affine, ct.affine)
        ref = np.asarray(ref_image.dataobj) > 0
        assert ref.shape == image.shape
        indices = np.flatnonzero(ref.any(axis=(0, 1)))
        for q in [0.25, 0.5, 0.75]:
            k = int(indices[int(np.rint((len(indices) - 1) * q))])
            key = f"{organ}_q{int(q * 100)}"
            gt = ref[:, :, k].T
            rgb = np.repeat(
                ((np.clip(image[:, :, k].T, -160, 240) + 160) / 400 * 255).astype(np.uint8)[
                    ..., None
                ],
                3,
                axis=-1,
            )
            np.testing.assert_array_equal(data[key + "_gt"], gt)
            np.testing.assert_array_equal(data[key + "_image"], rgb)
            assert data[key + "_gt"].dtype == bool and data[key + "_image"].dtype == np.uint8
            y, x = np.where(gt)
            boxes = {
                name: [
                    max(0, int(x.min()) - margin),
                    max(0, int(y.min()) - margin),
                    min(265, int(x.max()) + 1 + margin),
                    min(265, int(y.max()) + 1 + margin),
                ]
                for name, margin in [("tight", 2), ("loose", 10)]
            }
            samples.append(
                {
                    "id": key,
                    "organ": organ,
                    "q": q,
                    "slice_k": k,
                    "boxes": boxes,
                    "gt_pixels": int(gt.sum()),
                }
            )
            reconstruction.append(
                {
                    "id": key,
                    "nonempty_slice_count": len(indices),
                    "quantile_list_index": int(np.rint((len(indices) - 1) * q)),
                    "reference_components_4_connected": int(ndimage.label(gt)[1]),
                }
            )
    assert samples == manifest["samples"] and len(samples) == 18
    assert set(data.files) == {s["id"] + suffix for s in samples for suffix in ["_gt", "_image"]}
    sample_index = {s["id"]: s for s in samples}
    provision = read(pin(base / "provisioning.json"))
    assert provision == original["provenance"]
    pin(base / "requirements-resolved.txt", provision["requirements_sha256"])
    for weight in provision["weights"]:
        file = pin(base / "weights" / weight["name"], weight["sha256"])
        assert file.stat().st_size == weight["bytes"]
    for repo in provision["repos"]:
        vendor = root / base / "vendor" / repo["name"]
        head = subprocess.check_output(
            ["git", "-C", str(vendor), "rev-parse", "HEAD"], text=True
        ).strip()
        diff = subprocess.check_output(["git", "-C", str(vendor), "diff", "HEAD", "--"], text=True)
        assert head == repo["commit"] and diff == repo["tracked_diff"] == ""
        pin(vendor / "LICENSE", repo["license_sha256"])
    for name in [
        "sam2/utils/transforms.py",
        "sam2/sam2_image_predictor.py",
        "sam2/configs/sam2.1/sam2.1_hiera_s.yaml",
    ]:
        pin(base / "vendor/sam2" / name)

    receipts, masks, replays, aggregates, timing = {}, {}, [], {}, {}
    max_errors = dict.fromkeys(["dice", "precision", "recall", "hd95_mm"], 0.0)
    spacing = np.asarray(manifest["spacing_mm"][:2][::-1])
    for tag in TAGS:
        folder = base / "results" / tag
        receipt = read(pin(folder / "receipt.json", original["files"][tag]["receipt_sha256"]))
        predictions = np.load(pin(folder / "masks.npz", receipt["masks_sha256"]))
        rows = [json.loads(line) for line in pin(folder / "rows.jsonl").read_text().splitlines()]
        assert rows == receipt["rows"]
        assert receipt["script_sha256"] == sha(bench)
        assert receipt["sample_manifest_sha256"] == sha(root / base / "samples/manifest.json")
        assert receipt["dtype"] == "float32" and receipt["threads"] == 4
        assert receipt["torch_version"] == "2.10.0"
        weight = provision["weights"][0 if tag.startswith("sam2") else 1]
        assert receipt["weights_sha256"] == weight["sha256"]
        assert receipt["weights_bytes"] == weight["bytes"]
        assert receipt["model"] + "-" + receipt["device"] == tag.removesuffix("-subset")
        selected = (
            samples
            if not tag.endswith("subset")
            else [
                s
                for s in samples
                if s["q"] == 0.5 and s["organ"] in ["liver", "adrenal_gland_right"]
            ]
        )
        expected = [s["id"] + "_" + c for s in selected for c in ["tight", "loose"]]
        assert len(rows) == receipt["prediction_count"] == len(expected)
        assert set(predictions.files) == set(expected)
        assert [r["id"] + "_" + r["condition"] for r in rows] == expected
        encodings = {}
        for row in rows:
            s = sample_index[row["id"]]
            assert row["organ"] == s["organ"] and row["slice_k"] == s["slice_k"]
            assert row["box"] == s["boxes"][row["condition"]]
            pred, gt = predictions[row["id"] + "_" + row["condition"]], data[row["id"] + "_gt"]
            assert pred.shape == (265, 265) and pred.dtype == bool
            scored = metrics(pred, gt, spacing)
            for key in [*max_errors, "pred_pixels", "gt_pixels"]:
                if scored[key] is None:
                    assert row[key] is None
                else:
                    error = abs(scored[key] - row[key])
                    assert error < 1e-10, (tag, row["id"], key, error)
                    if key in max_errors:
                        max_errors[key] = max(max_errors[key], error)
            if row["id"] in encodings:
                assert row["encode_seconds"] == encodings[row["id"]]
            encodings[row["id"]] = row["encode_seconds"]
            x0, y0, x1, y1 = row["box"]
            rectangle = np.zeros_like(pred)
            rectangle[y0:y1, x0:x1] = True
            replays.append(
                {
                    "tag": tag,
                    "id": row["id"],
                    "condition": row["condition"],
                    **scored,
                    "pixels_outside_prompt": int((pred & ~rectangle).sum()),
                }
            )
        timing[tag] = {
            "unique_image_encodes": len(encodings),
            "cached_box_decodes": len(rows),
            "first_measured_encode_ms": next(iter(encodings.values())) * 1000,
            "encode_min_ms": min(encodings.values()) * 1000,
            "encode_max_ms": max(encodings.values()) * 1000,
        }
        agg = {
            "count": len(rows),
            "load_seconds": receipt["load_seconds"],
            "warmup_seconds": receipt["warmup_seconds"],
            "process_peak_rss_mib": receipt["process_peak_rss_bytes"] / 2**20,
            "encode_median_ms": float(np.median(list(encodings.values()))) * 1000,
            "prompt_median_ms": float(np.median([r["decode_seconds"] for r in rows])) * 1000,
            "driver_memory_max_observed_mib": max(
                r.get("mps_driver_allocated_bytes_observed", 0) for r in rows
            )
            / 2**20,
        }
        for condition in ["tight", "loose"]:
            subset = [r for r in replays if r["tag"] == tag and r["condition"] == condition]
            agg[condition] = {
                "mean_dice": float(np.mean([r["dice"] for r in subset])),
                "median_dice": float(np.median([r["dice"] for r in subset])),
                "mean_hd95_mm": float(
                    np.mean([r["hd95_mm"] for r in subset if r["hd95_mm"] is not None])
                ),
            }
        assert agg == original["aggregates"][tag]
        aggregates[tag], receipts[tag], masks[tag] = agg, receipt, predictions

    control_rows = []
    for sample in samples:
        gt = data[sample["id"] + "_gt"]
        assert metrics(gt, gt, spacing)["dice"] == 1
        assert metrics(np.zeros_like(gt), gt, spacing)["dice"] == 0
        for condition, (x0, y0, x1, y1) in sample["boxes"].items():
            rectangle = np.zeros_like(gt)
            rectangle[y0:y1, x0:x1] = True
            control_rows.append(
                {"id": sample["id"], "condition": condition, **metrics(rectangle, gt, spacing)}
            )
    controls = {
        "exact_mask_dice": 1.0,
        "empty_mask_dice": 0.0,
        "independent_mask_replays": len(replays),
        "filled_box_mean_dice": {
            c: float(np.mean([r["dice"] for r in control_rows if r["condition"] == c]))
            for c in ["tight", "loose"]
        },
    }
    assert controls == original["controls"] and len(replays) == 116
    parity, repeat = [], []
    for model, cpu_tag in [("sam2", "sam2-cpu"), ("lite", "lite-cpu-subset")]:
        for row in receipts[cpu_tag]["rows"]:
            key = row["id"] + "_" + row["condition"]
            cpu, mps = masks[cpu_tag][key], masks[model + "-mps"][key]
            parity.append(
                {
                    "model": model,
                    "id": row["id"],
                    "condition": row["condition"],
                    "differing_pixels": int((cpu != mps).sum()),
                    "cpu_mps_mask_dice": metrics(cpu, mps, spacing)["dice"],
                }
            )
    assert parity == original["parity"]
    for row in receipts["sam2-cpu-subset"]["rows"]:
        key = row["id"] + "_" + row["condition"]
        a, b = masks["sam2-cpu-subset"][key], masks["sam2-cpu"][key]
        repeat.append(
            {
                "id": row["id"],
                "condition": row["condition"],
                "differing_pixels": int((a != b).sum()),
                "mask_dice": metrics(a, b, spacing)["dice"],
            }
        )
    per_organ = []
    for organ in ORGANS:
        row = {"organ": organ}
        for model in ["sam2", "lite"]:
            for condition in ["tight", "loose"]:
                row[model + "_" + condition] = float(
                    np.mean(
                        [
                            r["dice"]
                            for r in replays
                            if r["tag"] == model + "-mps"
                            and sample_index[r["id"]]["organ"] == organ
                            and r["condition"] == condition
                        ]
                    )
                )
        per_organ.append(row)
    assert per_organ == original["per_organ"]
    pairs = []
    for sample in samples:
        row = {"id": sample["id"]}
        for model in ["sam2", "lite"]:
            selected = {
                r["condition"]: r
                for r in replays
                if r["tag"] == model + "-mps" and r["id"] == sample["id"]
            }
            row[model + "_loose_minus_tight_dice"] = (
                selected["loose"]["dice"] - selected["tight"]["dice"]
            )
        pairs.append(row)
    backend = [r["cpu_mps_mask_dice"] for r in parity if r["model"] == "sam2"]
    result = {
        "schema": 1,
        "entry": "tb3-segmentation-calibration",
        "status": "source-audit-complete-story-pending",
        "source_pins": pins,
        "scope": "Retained 2026-09-21 direct tool inference; saved-output replay, no new inference",
        "geometry": {
            "shape_ijk": manifest["shape"],
            "spacing_mm": manifest["spacing_mm"],
            "affine": manifest["affine"],
            "display": "x=i, y=j increasing down, native k; no flips",
        },
        "source_and_reference": {
            "record": authority["record_url"],
            "version": authority["version"],
            "case": "s1233",
            "licenses": authority["licenses"],
            "fitness": "Exact source grids and binary masks verified; clinical annotation intent not adjudicated",
            "prompt_privilege": "GT selects slices and boxes; dense GT and organ names are not model inputs",
        },
        "samples": samples,
        "selection_reconstruction": reconstruction,
        "sample_arrays_reconstructed_exactly": True,
        "metrics_max_absolute_error": max_errors,
        "hd95_definition": "95th percentile of concatenated bidirectional 2D surface distances, 4-connected erosion, 1.5 mm pixels",
        "aggregates": aggregates,
        "timing_denominators": timing,
        "controls": controls,
        "control_rows": control_rows,
        "per_organ": per_organ,
        "replays": replays,
        "paired_box_differences": pairs,
        "backend_pairs": parity,
        "sam2_backend": {
            "count": len(backend),
            "median_mask_dice": float(np.median(backend)),
            "below_095": sum(d < 0.95 for d in backend),
            "minimum": min(
                (r for r in parity if r["model"] == "sam2"), key=lambda r: r["cpu_mps_mask_dice"]
            ),
        },
        "sam2_cpu_subset_vs_full_repeat": repeat,
        "not_established": [
            "autonomous localization",
            "whole-volume segmentation",
            "population accuracy",
            "training non-overlap",
            "clinical reference adjudication",
            "backend numerical cause",
            "general CPU/MPS parity",
            "sustained throughput or total peak unified memory",
        ],
    }
    for path, digest in pins.items():
        assert sha(root / path) == digest, path
    (out / "audit.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(
        json.dumps(
            {
                "output": str(out / "audit.json"),
                "source_pins": len(pins),
                "saved_masks": len(replays),
                "samples": len(samples),
                "errors": max_errors,
                "sam2_backend": result["sam2_backend"],
                "cpu_repeat": repeat,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    audit(args.root.resolve(), args.output)
