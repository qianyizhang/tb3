"""Reproduce pinned ReX-MLE TopCoW preparation and selected metric contracts.

Uses filename-only staging fixtures and tiny nonclinical label arrays. No upstream
module import, medical trial, model training, download, or MONAI installation.
HD95 and the complete grader are deliberately not executed.
"""

from __future__ import annotations

import argparse
import ast
import contextlib
import hashlib
import io
import json
import shutil
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import SimpleITK as sitk
from skimage import measure
from skimage.morphology import skeletonize
from sklearn.metrics import balanced_accuracy_score
from sklearn.model_selection import train_test_split

COMMIT = "b3d8f7c3ff1df5af46d8f3e5312760af3ad18a53"
CHALLENGE = "rex-mle/rexmle/challenges/topcow-track1-task1"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def functions(path, names, namespace):
    nodes = [
        n
        for n in ast.parse(path.read_text()).body
        if isinstance(n, ast.FunctionDef) and n.name in names
    ]
    assert {n.name for n in nodes} == set(names)
    assert all(not n.decorator_list for n in nodes)
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), "exec"), namespace)
    return [{"name": n.name, "start_line": n.lineno, "end_line": n.end_lineno} for n in nodes]


def no_download(*_args, **_kwargs):
    raise RuntimeError("This audit never downloads or prepares medical data")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    source = args.sources / CHALLENGE
    receipt = json.loads((args.sources / "fetch-receipt.json").read_text())
    tree = json.loads((args.sources / "tree.json").read_text())
    assert receipt["revision"] == tree["sha"] == COMMIT and not tree["truncated"]
    blobs = {r["path"]: r for r in tree["tree"] if r["type"] == "blob"}
    for row in receipt["files"]:
        raw = (args.sources / row["path"]).read_bytes()
        assert len(raw) == row["bytes"] == blobs[row["path"]]["size"]
        assert (
            hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
            == row["git_blob_sha1"]
            == blobs[row["path"]]["sha"]
        )
        assert hashlib.sha256(raw).hexdigest() == row["sha256"]

    inventory = json.loads(args.inventory.read_text())
    assert inventory["truncated"] is False
    keys = {r["key"] for r in inventory["entries"]}
    image_keys = sorted(k for k in keys if "/imagesTr/topcow_ct_" in k)
    label_keys = sorted(k for k in keys if "/cow_seg_labelsTr/topcow_ct_" in k)
    matched = [
        k
        for k in image_keys
        if k.replace("/imagesTr/", "/cow_seg_labelsTr/").replace("_0000.nii.gz", ".nii.gz") in keys
    ]
    assert len(image_keys) == len(label_keys) == len(matched) == 125

    fixture_root = args.output / "filename-fixture"
    raw = fixture_root / "topcow-track1-task1" / "raw"
    shared = fixture_root / "topcow-shared" / "raw"
    public, private = fixture_root / "public", fixture_root / "private"
    for folder, paths in [("imagesTr", image_keys), ("cow_seg_labelsTr", label_keys)]:
        (shared / folder).mkdir(parents=True)
        for path in paths:
            (shared / folder / Path(path).name).write_text(
                "NONCLINICAL FILENAME-ONLY STAGING FIXTURE\n"
            )
    ns = {
        "Path": Path,
        "pd": pd,
        "shutil": shutil,
        "train_test_split": train_test_split,
        "ZenodoDownloader": no_download,
        "download_data": no_download,
        "__file__": str(source / "prepare.py"),
    }
    selections = {
        "prepare.py": functions(source / "prepare.py", ["get_shared_raw_dir", "prepare"], ns)
    }
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        ns["prepare"](raw, public, private)
    train_ids = sorted(p.name.split("_")[2] for p in (public / "train/images").glob("*.nii.gz"))
    test_ids = sorted(p.name.split("_")[2] for p in (public / "test/images").glob("*.nii.gz"))
    assert len(train_ids) == 100 and len(test_ids) == 25
    assert "012" in test_ids and "012" not in train_ids
    assert (private / "test/labels/topcow_ct_012.nii.gz").is_file()
    assert not (public / "train/labels/topcow_ct_012.nii.gz").exists()
    assert not (public / "test/labels").exists()
    sample = pd.read_csv(public / "sample_submission.csv", dtype=str)
    assert set(sample.image_id) == set(test_ids)

    ns = {
        "np": np,
        "pd": pd,
        "sitk": sitk,
        "skeletonize": skeletonize,
        "measure": measure,
        "balanced_accuracy_score": balanced_accuracy_score,
        "Dict": dict,
    }
    metric_tree = ast.parse((source / "grade.py").read_text())
    for node in metric_tree.body:
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
        ):
            ns[node.targets[0].id] = ast.literal_eval(node.value)
    names = [
        "calculate_positions_and_mean",
        "compute_dice_per_class",
        "compute_class_average_dice",
        "convert_multiclass_to_binary",
        "cl_score",
        "compute_cldice",
        "connected_components",
        "compute_b0_error_per_class",
        "compute_class_average_b0_error",
        "compute_iou_single_label",
        "compute_detection_dict",
        "compute_f1_from_detection_dicts",
        "compute_topology_dict",
        "compute_topology_accuracy_from_dicts",
    ]
    selections["grade.py"] = functions(source / "grade.py", names, ns)
    sitk.ProcessObject_SetGlobalDefaultNumberOfThreads(1)
    gt = np.zeros((9, 9, 9), dtype=np.uint8)
    gt[2:7, 3, 4] = 11
    gt[2:7, 6, 4] = 12
    cases = {
        "exact": gt.copy(),
        "broken-vessel": gt.copy(),
        "swapped-names": gt.copy(),
        "extra-absent-class": gt.copy(),
        "all-background": np.zeros_like(gt),
    }
    cases["broken-vessel"][4, 3, 4] = 0
    cases["swapped-names"][gt == 11] = 12
    cases["swapped-names"][gt == 12] = 11
    cases["extra-absent-class"][2:5, 0, 0] = 15
    observed = []
    for name, pred in cases.items():
        gt_img, pred_img = sitk.GetImageFromArray(gt), sitk.GetImageFromArray(pred)
        detection = ns["compute_detection_dict"](gt_img, pred_img)
        topology = ns["compute_topology_dict"](gt_img, pred_img)
        with warnings.catch_warnings(record=True) as captured:
            warnings.simplefilter("always")
            ant, post, ant_top, post_top = ns["compute_topology_accuracy_from_dicts"]([topology])
        row = {
            "id": name,
            "dice": ns["compute_class_average_dice"](pred, gt),
            "cldice": ns["compute_cldice"](pred, gt),
            "b0_error": ns["compute_class_average_b0_error"](gt, pred),
            "f1_grp2": ns["compute_f1_from_detection_dicts"]([detection]),
            "anterior_graph_acc": ant,
            "posterior_graph_acc": post,
            "anterior_topology": ant_top,
            "posterior_topology": post_top,
            "hd95": None,
            "detection": detection,
            "warnings": [str(w.message) for w in captured],
            "reference_voxels": np.argwhere(gt > 0).tolist(),
            "prediction_voxels": [
                {"ijk": [int(x) for x in index], "label": int(pred[tuple(index)])}
                for index in np.argwhere(pred > 0)
            ],
        }
        observed.append(row)
    by_id = {r["id"]: r for r in observed}
    assert by_id["exact"]["dice"] > 0.99999
    assert (
        by_id["broken-vessel"]["b0_error"] == 0.5
        and by_id["broken-vessel"]["anterior_topology"] == 1
    )
    assert by_id["swapped-names"]["dice"] == 0 and by_id["swapped-names"]["cldice"] == 1
    assert (
        by_id["extra-absent-class"]["dice"] > 0.99999
        and by_id["extra-absent-class"]["anterior_topology"] == 0
    )
    assert by_id["all-background"]["dice"] == 0
    empty_gt_score = ns["compute_class_average_dice"](gt, np.zeros_like(gt))
    assert empty_gt_score == 1

    # Execute only the inspected preprocessing fragment, stopping before metrics.
    full_metric = next(
        n
        for n in metric_tree.body
        if isinstance(n, ast.FunctionDef) and n.name == "compute_topcow_metrics"
    )
    fragment = []
    for node in full_metric.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "metrics" for t in node.targets
        ):
            break
        fragment.append(node)
    geom_ns = {
        **ns,
        "gt_sitk": sitk.GetImageFromArray(gt),
        "pred_sitk": sitk.GetImageFromArray(gt.astype(np.float32) + (gt > 0) * 0.5),
    }
    geom_ns["pred_sitk"].SetOrigin((100.0, 0.0, 0.0))
    exec(
        compile(ast.Module(body=fragment, type_ignores=[]), str(source / "grade.py"), "exec"),
        geom_ns,
    )
    assert geom_ns["pred_sitk"].GetOrigin() == geom_ns["gt_sitk"].GetOrigin()
    assert np.array_equal(geom_ns["pred_arr"], gt)
    geometry = {
        "executed_fragment_lines": [fragment[0].lineno, fragment[-1].end_lineno],
        "input_origin_mm": [100, 0, 0],
        "output_origin_mm": list(geom_ns["pred_sitk"].GetOrigin()),
        "input_label_values": [0, 11.5, 12.5],
        "output_label_values": np.unique(geom_ns["pred_arr"]).tolist(),
        "note": "Source UInt8 cast and CopyInformation fragment only; not whole-grader acceptance.",
    }
    leaderboard = pd.read_csv(source / "leaderboard.csv")
    first_metrics = {key: float(leaderboard.iloc[0][key]) for key in ns["METRIC_DIRECTIONS"]}
    positions = ns["calculate_positions_and_mean"](first_metrics, leaderboard)
    assert len(positions) == 10 and np.isfinite(positions["mean_position"])
    result = {
        "schema": 1,
        "source_commit": COMMIT,
        "source_files": len(receipt["files"]),
        "script_sha256": sha(Path(__file__)),
        "source_receipt_sha256": sha(args.sources / "fetch-receipt.json"),
        "selected_functions": selections,
        "split": {
            "inventory": str(args.inventory),
            "inventory_sha256": sha(args.inventory),
            "inventory_root_truncated": inventory.get("truncated"),
            "image_count": 125,
            "matched_count": 125,
            "train_ids": train_ids,
            "test_ids": test_ids,
            "case012": "test",
            "method": "Actual pinned prepare function on filename-only placeholders from the complete ZIP64 directory. Assumes all matched cases from this named release are supplied unchanged; no native case bytes were staged by this fixture.",
            "public_label_012": False,
            "private_label_012": True,
            "sample_submission_012": sample[sample.image_id == "012"].iloc[0].to_dict(),
        },
        "label_map": ns["MUL_CLASS_LABEL_MAP"],
        "metric_directions": ns["METRIC_DIRECTIONS"],
        "fixtures": observed,
        "empty_reference_dice_with_nonempty_prediction": empty_gt_score,
        "geometry_fragment": geometry,
        "ranking_fixture": {
            "kind": "First leaderboard metric row reused as a constructed tie, not a new run",
            "competitors": len(leaderboard),
            "metrics": first_metrics,
            "positions": positions,
        },
        "limits": [
            "HD95 requires MONAI, absent from the existing environment; no installation or HD95 execution.",
            "Selected-function fixtures do not execute the whole grader or certify runtime isolation.",
            "No medical model, training, held-out prediction, or clinical performance measurement.",
        ],
    }
    (args.output / "preparation.log").write_text(log.getvalue())
    (args.output / "audit.json").write_text(json.dumps(result, indent=2) + "\n")
    print(
        json.dumps(
            {
                "source_files": len(receipt["files"]),
                "train": len(train_ids),
                "test": len(test_ids),
                "case012": "test",
                "fixtures": len(observed),
                "all_assertions_passed": True,
            }
        )
    )


if __name__ == "__main__":
    main()
