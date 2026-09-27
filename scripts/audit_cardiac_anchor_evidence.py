"""Audit BR-027 saved predictions and source access; never rerun tracking or fitting."""

import argparse
import json
from pathlib import Path

import numpy as np
from audit_cardiac_contour_evidence import HOLDOUT, dice, dump, read, sha, summary, volume
from PIL import Image, ImageDraw
from scipy.ndimage import binary_erosion, distance_transform_edt

RUN = Path("runs/br027-cardiac")
NATIVE = Path("runs/br025-cardiac/source/native/Patient001")
VIEWS = [0, 9, 18, 27]
PINS = {
    "docs/evidence/br027-cardiac-integrity.json": "158f87a3295dc7deb11a9b7bc6ef4f07d10d4aef29a74aa6c8a4b2342582ea8a",
    "docs/evidence/br027-cardiac-results.json": "f6c09a5241f2e9a9780e5aaaf745d45ceed4a1133e08657585c62c2fc318f65a",
    "datasets/receipts/feecho4d-members.json": "1af472b1aea598fdeb327ff3f063158f9c128915b5a2e7147c74e519be936025",
    "runs/br027-cardiac/evaluation-v2/clean-mesh.npz": "929bb761d17fef3512b9dd4ad8398de22065f6f610bf46cbb4110dc294b5853a",
    "runs/br027-cardiac/evaluation-v2/dense-mesh.npz": "09a8348aa7c61917d6481084c98d41ce48c668843d2e9c405a4df63c51dc4390",
    "runs/br027-cardiac/evaluation-v2/curves.json": "5ac874801b0a7d06edca92b20abdd05ab85c22fe1eaa40cccd7892d03217af16",
}


def compare(actual, expected, path=""):
    if isinstance(expected, dict):
        assert actual.keys() == expected.keys(), path
        for key in expected:
            compare(actual[key], expected[key], path + "/" + key)
    elif expected is None or isinstance(expected, (bool, int, list)):
        assert actual == expected, (path, actual, expected)
    else:
        assert abs(actual - expected) <= 1e-10, (path, actual, expected)


def section(profile, view, geo):
    yy, xx = np.indices(geo["shape_hw"])
    dx, dy = xx - geo["rotation_axis_x_px"], yy - geo["origin_y_px"]
    polar = np.linspace(0, np.pi, 65)
    angle = np.arctan2(np.abs(dx), dy)
    positive = np.interp(angle, polar, profile[view % 72])
    negative = np.interp(angle, polar, profile[(view + 36) % 72])
    return np.hypot(dx, dy) <= np.where(dx >= 0, positive, negative)


def audit(root, out):
    assert not out.exists(), "Use a fresh local destination"
    out.mkdir(parents=True)
    pins = dict(PINS)
    for name, digest in pins.items():
        assert sha(root / name) == digest, name
    integrity = read(root / "docs/evidence/br027-cardiac-integrity.json")
    original = read(root / "docs/evidence/br027-cardiac-results.json")
    for name, digest in integrity["code_sha256"].items():
        assert sha(root / name) == digest, name
        pins[name] = digest
    for version, digest in integrity["results_sha256"].items():
        p = RUN / version / "results.json"
        assert sha(root / p) == digest
        pins[str(p)] = digest
    members = read(root / "datasets/receipts/feecho4d-members.json")["members"]
    assert len(members) == 2251
    for member in members:
        relative = Path(member["name"]).relative_to("FeEcho4D/FeEcho4D_Annotated/Patient001")
        p = root / NATIVE / relative
        assert p.stat().st_size == member["size"] and sha(p) == member["sha256"], p

    def native(kind, view, t):
        return root / NATIVE / kind / f"Patient001_slice{view + 1:03d}time{t + 1:03d}.png"

    masks = {
        (view, t): np.asarray(Image.open(native("mask", view, t))) == 127
        for view in VIEWS + HOLDOUT
        for t in range(30)
    }
    assert not set(VIEWS) & set(HOLDOUT)
    packages = {}
    for condition, frames in [("one_anchor", [2]), ("two_anchors", [2, 17])]:
        folder = root / RUN / "public" / condition
        manifest = read(folder / "manifest.json")
        digest = integrity["public_inputs"][condition]["manifest_sha256"]
        assert sha(folder / "manifest.json") == digest
        pins[str((folder / "manifest.json").relative_to(root))] = digest
        files = {str(p.relative_to(folder)) for p in folder.rglob("*") if p.is_file()}
        assert files == set(manifest) | {"manifest.json"}
        expected = {"TASK.md", "geometry.json"}
        for i, view in enumerate(VIEWS):
            for t in range(30):
                name = f"video/view_{i:02d}/frame_{t + 1:03d}.png"
                expected.add(name)
                assert (folder / name).read_bytes() == native("image", view, t).read_bytes()
            for frame in frames:
                name = f"anchors/view_{i:02d}/frame_{frame:03d}.png"
                expected.add(name)
                anchor = np.asarray(Image.open(folder / name))
                np.testing.assert_array_equal(anchor, masks[view, frame - 1].astype("uint8") * 255)
        assert set(manifest) == expected
        for name, digest in manifest.items():
            assert sha(folder / name) == digest, name
        geo = read(folder / "geometry.json")
        assert geo["anchor_frames_1based"] == frames
        assert geo["rotation_axis_x_px"] == 242 and geo["origin_y_px"] == 184.5
        assert geo["in_plane_spacing_mm"] == 0.08995 and geo["shape_hw"] == [464, 485]
        assert geo["view_angles_degrees"] == [0, 45, 90, 135] and geo["frame_count"] == 30
        rows = np.where(masks[0, 1][:, 242])[0]
        assert (rows.min() + rows.max()) / 2 == geo["origin_y_px"]
        packages[condition] = {
            "manifest_members": len(manifest),
            "files_including_manifest": len(files),
            "video_frames": 120,
            "anchor_masks": 4 * len(frames),
            "anchor_frames_1based": frames,
            "source_images_byte_identical": True,
            "source_cavity_anchor_arrays_equal": True,
            "unexpected_files": [],
        }
    geo = original["geometry"]
    assert read(root / RUN / "public/one_anchor/geometry.json") == geo
    predictions = {}
    for condition, prefix in [("one-anchor-v1", "one"), ("two-anchors-v1", "two")]:
        receipt = read(root / RUN / condition / "solver-receipt.json")
        assert receipt == original["receipts"][condition]
        for method, info in receipt["predictions"].items():
            path = RUN / condition / f"{method}-mesh.npz"
            assert sha(root / path) == info["sha256"]
            pins[str(path)] = info["sha256"]
            predictions[f"{prefix}_{method}"] = dict(np.load(root / path, allow_pickle=False))
    refined_path = RUN / "one-anchor-refined-v1/refined-mesh.npz"
    refined_receipt = read(root / RUN / "one-anchor-refined-v1/solver-receipt.json")
    assert refined_receipt == integrity["refinement_receipt"]
    assert sha(root / refined_path) == refined_receipt["prediction"]["sha256"]
    pins[str(refined_path)] = sha(root / refined_path)
    predictions["one_refined"] = dict(np.load(root / refined_path, allow_pickle=False))
    for name in ["clean", "dense"]:
        path = RUN / "evaluation-v2" / f"{name}-mesh.npz"
        predictions[name] = dict(np.load(root / path, allow_pickle=False))
        # The earlier and later evaluations retain the same controls, despite NPZ container time metadata.
        old = dict(np.load(root / RUN / "evaluation-v1" / f"{name}-mesh.npz", allow_pickle=False))
        assert old.keys() == predictions[name].keys()
        for key in old:
            np.testing.assert_array_equal(old[key], predictions[name][key])
    curves = read(root / RUN / "evaluation-v2/curves.json")
    reference = predictions["dense"]["volume_ml"]

    def ef(values):
        return float(100 * (1 - values.min() / values.max()))

    stats = {}
    for name, pred in predictions.items():
        v, f, curve = pred["vertices"], pred["faces"], pred["volume_ml"]
        assert v.shape == (30, 4538, 3) and f.shape == (9072, 3)
        assert pred["radius_px"].shape == (30, 72, 65)
        np.testing.assert_allclose(volume(v, f), curve, atol=1e-12, rtol=0)
        np.testing.assert_array_equal(curve, curves[name])
        anchors = [1, 16] if name.startswith("two_") else [1]
        if "input_view_masks" in pred:
            assert pred["input_view_masks"].shape == (4, 30, 464, 485)
            for i, view in enumerate(VIEWS):
                for t in anchors:
                    np.testing.assert_array_equal(pred["input_view_masks"][i, t], masks[view, t])
        dd, hh, observed = [], [], []
        for t in range(30):
            for view in HOLDOUT:
                truth, projected = masks[view, t], section(pred["radius_px"][t], view, geo)
                dd.append(dice(truth, projected))
                a, b = truth ^ binary_erosion(truth), projected ^ binary_erosion(projected)
                distances = np.r_[distance_transform_edt(~a)[b], distance_transform_edt(~b)[a]]
                hh.append(float(np.quantile(distances * geo["in_plane_spacing_mm"], 0.95)))
            if "input_view_masks" in pred and t not in anchors:
                observed.extend(
                    dice(masks[view, t], pred["input_view_masks"][i, t])
                    for i, view in enumerate(VIEWS)
                )
        edges = np.sort(np.concatenate([f[:, [0, 1]], f[:, [1, 2]], f[:, [2, 0]]]), axis=1)
        _, counts = np.unique(edges, axis=0, return_counts=True)
        area = (
            np.linalg.norm(
                np.cross(v[:, f[:, 1]] - v[:, f[:, 0]], v[:, f[:, 2]] - v[:, f[:, 0]]), axis=-1
            )
            / 2
        )
        topo = {
            "boundary_edges": int((counts == 1).sum()),
            "nonmanifold_edges": int((counts > 2).sum()),
            "degenerate_triangles": int((area < 1e-10).sum()),
            "positive_volumes": bool((curve > 0).all()),
        }
        s = {
            "heldout_dice": summary(dd),
            "heldout_hd95_mm": summary(hh),
            "unsupplied_input_frame_dice": summary(observed) if observed else None,
            "unsupplied_input_frame_count": len(observed),
            "ef_percent": ef(curve),
            "ef_error_vs_dense_reference_pp": abs(ef(curve) - ef(reference)),
            "volume_curve_mape_vs_dense_percent": float(100 * np.mean(abs(curve / reference - 1))),
            "max_volume_frame_1based": int(curve.argmax()) + 1,
            "min_volume_frame_1based": int(curve.argmin()) + 1,
            "min_volume_ml": float(curve.min()),
            "max_volume_ml": float(curve.max()),
            "topology": topo,
        }
        s["gates"] = {
            "dice": s["heldout_dice"]["mean"] >= 0.9,
            "hd95": s["heldout_hd95_mm"]["mean"] <= 1,
            "volume": s["volume_curve_mape_vs_dense_percent"] <= 10,
            "ef": s["ef_error_vs_dense_reference_pp"] <= 5,
            "topology": topo["positive_volumes"]
            and not any(
                topo[k] for k in ["boundary_edges", "nonmanifold_edges", "degenerate_triangles"]
            ),
        }
        s["pass"] = all(s["gates"].values())
        compare(s, original["stats"][name], name)
        stats[name] = s
        print(f"{name}: original score fields reproduced", flush=True)
    static = predictions["one_control"]["vertices"]
    np.testing.assert_array_equal(static, np.repeat(static[:1], 30, axis=0))
    # Native input-view and withheld-view comparisons; no source image is redistributed.
    visual_files = []
    for view, t in [(27, 16), (27, 24), (7, 16)]:
        canvas = Image.new("RGB", (1455, 520), "white")
        draw = ImageDraw.Draw(canvas)
        for i, name in enumerate(["one_dis", "two_dis", "one_refined"]):
            im = np.asarray(Image.open(native("image", view, t)).convert("RGB")).copy()
            pred = predictions[name]
            region = (
                pred["input_view_masks"][VIEWS.index(view), t]
                if view in VIEWS
                else section(pred["radius_px"][t], view, geo)
            )
            truth = masks[view, t]
            im[truth ^ binary_erosion(truth)] = [237, 194, 61]
            im[region ^ binary_erosion(region)] = [33, 206, 220]
            canvas.paste(Image.fromarray(im), (i * 485, 30))
            role = "input view" if view in VIEWS else "held-out view"
            draw.text(
                (i * 485 + 10, 8), f"{name} | {role} {view + 1} | frame {t + 1}", fill="black"
            )
        reference_role = (
            "This view/frame is supplied ONLY to two_dis"
            if view in VIEWS and t == 16
            else "This frame is unsupplied in every condition"
            if view in VIEWS
            else "All masks from this view are withheld; predictions are mesh sections"
        )
        draw.text(
            (10, 500),
            "Gold: source cavity | Cyan: saved prediction | 0.08995 mm/px | " + reference_role,
            fill="black",
        )
        p = out / f"view-{view + 1}-frame-{t + 1}.png"
        canvas.save(p)
        visual_files.append({"file": p.name, "sha256": sha(p)})
    result = {
        "schema": 1,
        "scope": "BR-027 saved-output and source-package audit; no tracking, fitting, model trial or clinical adjudication",
        "source_pins": pins,
        "source_members_sha256_size_verified": len(members),
        "public_packages": packages,
        "geometry": geo,
        "sparse_heldout_disjoint": True,
        "heldout_pairs_per_condition": 240,
        "original_score_tolerance": 1e-10,
        "recomputed_stats": stats,
        "anchors_preserved_in_all_predictions": True,
        "clean_dense_arrays_equal_between_evaluations": True,
        "visual_files": visual_files,
        "limits": [
            "One previously inspected patient. Public-input-only access was source-reviewed, not OS-isolated or a blind independent trial.",
            "One-anchor unsupplied-input scoring has 116 pairs; two-anchor scoring has 112. Do not pool those denominators.",
            "Dense includes evaluation directions; original fields named heldout for dense are source-fit metrics.",
            "GrabCut was developed after the first screen; its fixed constants were not a blind prespecified method.",
            "Full-curve extrema and origin y=184.5 px differ from BR-025's phase-index EF and y=172 px origin. Use within-round controls.",
            "Supplied frame numbers are anchors, not clinical phase labels. Poses, annotation uncertainty, clinical EF and independent material truth remain unqualified.",
            "Source terms remain unresolved for redistribution. Keep derived images and geometry local; source review is not explainer acceptance.",
        ],
    }
    dump(out / "audit.json", result)
    dump(out / "curves.json", curves)
    print(json.dumps({"output": str(out), "packages": 2, "conditions_replayed": len(stats)}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    audit(args.root.resolve(), args.output)
