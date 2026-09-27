"""Verify frozen landmark inputs, coordinate references and saved outputs; no trials."""

import argparse
import csv
import gzip
import hashlib
import importlib.util
import json
import tomllib
import zipfile
from pathlib import Path

import nibabel as nib
import numpy as np
import SimpleITK as sitk

BASES = {
    "036": "br036-semantic-landmarks",
    "038": "br038-volume-landmarks",
    "039": "br039-ct-landmarks",
}
REPRO = Path("groups/anatomical-landmarks/experiments/br040/reproduction")


def read(path):
    return json.loads(path.read_text())


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def load_functions(path):
    """Only called for inspected frozen score.py or public volume_tools.py."""
    spec = importlib.util.spec_from_file_location("landmark_audit_module", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def compare(actual, expected, path=""):
    if isinstance(expected, dict):
        assert actual.keys() == expected.keys(), path
        for key in expected:
            compare(actual[key], expected[key], path + "/" + key)
    elif isinstance(expected, list):
        assert len(actual) == len(expected), path
        for i, value in enumerate(expected):
            compare(actual[i], value, path + f"/{i}")
    elif isinstance(expected, (str, bool)) or expected is None:
        assert actual == expected, (path, actual, expected)
    else:
        assert abs(actual - expected) < 1e-9, (path, actual, expected)


def fcsv(path):
    assert "# CoordinateSystem = 0" in path.read_text()
    rows = csv.reader(
        line for line in path.read_text().splitlines() if line and not line.startswith("#")
    )
    return {row[11]: np.array(row[1:4], float) for row in rows}


def nifti_blocks(path):
    """Sequential decode bounds memory even for the original float64 spine CT."""
    ni = nib.load(path)
    proxy = ni.dataobj
    assert len(ni.shape) == 3 and proxy.order == "F"
    with gzip.open(path, "rb") as stream:
        stream.seek(proxy.offset)
        for start in range(0, ni.shape[2], 8):
            depth = min(8, ni.shape[2] - start)
            count = ni.shape[0] * ni.shape[1] * depth
            raw = stream.read(count * proxy.dtype.itemsize)
            assert len(raw) == count * proxy.dtype.itemsize
            block = np.frombuffer(raw, proxy.dtype).reshape((*ni.shape[:2], depth), order="F")
            if proxy.slope != 1 or proxy.inter != 0:
                block = block * proxy.slope + proxy.inter
            yield start, block


def audit(root, out):
    out.mkdir(parents=True, exist_ok=False)
    pins, tasks, inode_hashes = {}, {}, {}

    def pin(path, expected=None):
        path = Path(path)
        st = (root / path).stat()
        key = (st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns)
        value = inode_hashes.get(key)
        if value is None:
            value = inode_hashes[key] = sha(root / path)
        if expected is not None:
            assert value == expected, str(path)
        pins[str(path)] = value

    for number in ["036", "038", "039", "040"]:
        record = root / f"groups/anatomical-landmarks/experiments/br{number}/experiment.toml"
        for item in tomllib.loads(record.read_text())["evidence"]:
            pin(item["path"], item["sha256"])
    for number, name in [
        ("036", "freeze"),
        ("036", "expanded-freeze"),
        ("038", "freeze"),
        ("039", "freeze"),
    ]:
        freeze = read(root / f"docs/evidence/br{number}-{name}.json")
        for task in freeze["tasks"]:
            tasks[(number, task["task"])] = Path(task["task_path"])
            for name, digest in task["files"].items():
                pin(Path(task["task_path"]) / name, digest)
    for item in read(root / "docs/evidence/br040-plan.json")["conditions"]:
        task = item["task"]
        tasks[("040", item["case"])] = Path(task["task_path"])
        for name, digest in task["files"].items():
            pin(Path(task["task_path"]) / name, digest)
    manifest = read(root / REPRO / "manifest.json")
    pin(REPRO / "manifest.json")
    for item in manifest["files"]:
        pin(item["source"], item["sha256"])
        assert (root / item["source"]).stat().st_size == item["size"]
    source = Path("runs/br036-semantic-landmarks/source")
    for name, digest in read(root / "docs/evidence/br036-curation.json")["source_sha256"].items():
        pin(source / name, digest)
    vertebra = Path(
        "runs/br012-curation/source/files/20training/dataset-01training/derivatives/sub-verse823"
    )
    centroids = vertebra / "sub-verse823_dir-iso_seg-subreg_ctd.json"
    mask_path = vertebra / "sub-verse823_dir-iso_seg-vert_msk.nii.gz"
    curation = read(root / "docs/evidence/br039-curation.json")
    pin(centroids, curation["source_centroids_sha256"])
    pin("runs/br039-ct-landmarks/source/verse/ct.nii.gz", curation["source_ct_receipt"]["sha256"])
    pin(mask_path, read(root / "docs/evidence/br040-ct-diagnostic.json")["source_mask_sha256"])
    for path, digest in read(
        root / "groups/anatomical-landmarks/presentation/sources/landmark-provenance.json"
    )["evidence"].items():
        pin(path, digest)
    pin("runs/br012-curation/source/verse2020-supplement.pdf")
    pin("runs/br012-curation/source/verse2020-supplement.txt")
    print(f"Verified {len(pins)} frozen/source file fingerprints", flush=True)

    # Source FCSV coordinates are explicitly RAS. Check consensus and selected definitions.
    mri = fcsv(root / source / "mri-C001.fcsv")
    ct = fcsv(root / source / "0522c0001/Landmarks_0001.fcsv")
    raters = [fcsv(root / source / f"mri-rater{i}.fcsv") for i in range(1, 4)]
    rater_distances = {}
    for key, point in mri.items():
        values = np.array([r[key] for r in raters])
        np.testing.assert_allclose(values.mean(0), point, atol=1e-12, rtol=0)
        rater_distances[key] = float(np.linalg.norm(values - values.mean(0), axis=1).max())
    # Public PDDCA NRRD conversion: compare all intensities and the independent LPS affine.
    nrrd = sitk.ReadImage(str(root / source / "0522c0001/img.nrrd"))
    ct_source = nib.load(root / source / "ct-C001.nii.gz")
    ct_array = np.asarray(ct_source.dataobj)
    np.testing.assert_array_equal(sitk.GetArrayFromImage(nrrd).transpose(2, 1, 0), ct_array)
    lps = np.eye(4)
    lps[:3, :3] = np.array(nrrd.GetDirection()).reshape(3, 3) @ np.diag(nrrd.GetSpacing())
    lps[:3, 3] = nrrd.GetOrigin()
    np.testing.assert_allclose(np.diag([-1, -1, 1, 1]) @ lps, ct_source.affine, atol=2e-6, rtol=0)
    mri_source = nib.load(root / source / "mri-C001.nii.gz")
    mri_array = np.asarray(mri_source.dataobj)
    old_audit = {
        x["case"]: x
        for x in read(root / "docs/evidence/br038-original-audit.json")["original_checks"]
    }
    source_checks = {}
    for (number, case), task in tasks.items():
        if number == "040":
            continue  # Byte-identical to the audited 038/039 task above.
        path = root / task / "environment/volume.nii.gz"
        ni = nib.load(path)
        target = (
            np.load(root / task / "environment/volume.npy", mmap_mode="r")
            if (root / task / "environment/volume.npy").exists()
            else None
        )
        if number == "039":
            src = nib.load(root / "runs/br039-ct-landmarks/source/verse/ct.nii.gz")
            np.testing.assert_array_equal(ni.affine, src.affine)
        else:
            raw = mri_array if case.startswith("mri") else ct_array
            src = mri_source if case.startswith("mri") else ct_source
            offset = old_audit[case]["crop_start_k"] if number == "036" else 0
            want = src.affine.copy()
            want[:3, 3] = nib.affines.apply_affine(src.affine, [0, 0, offset])
            np.testing.assert_allclose(ni.affine, want, atol=1e-5, rtol=0)
        for start, block in nifti_blocks(path):
            end = start + block.shape[2]
            if target is not None:
                np.testing.assert_array_equal(block, target[:, :, start:end])
            if number != "039":
                np.testing.assert_array_equal(block, raw[:, :, start + offset : end + offset])
        truth = read(root / task / "tests/truth.json")
        if number == "036":
            points = truth.get("points_ras_mm", truth.get("points"))
            named = (
                mri
                if case == "mri32-crop"
                else ct
                if case.startswith("ct")
                else {
                    k: np.array(v)
                    for k, v in read(root / "docs/evidence/br036-curation.json")["cases"][1][
                        "points_ras_mm"
                    ].items()
                }
            )
            for key, point in points.items():
                np.testing.assert_array_equal(point, named[key])
            if "outside" in truth:
                voxels = {
                    k: nib.affines.apply_affine(np.linalg.inv(ni.affine), p)
                    for k, p in points.items()
                }
                outside = [
                    k
                    for k, v in voxels.items()
                    if np.any((v < -0.5) | (v > np.array(ni.shape) - 0.5))
                ]
                assert outside == truth["outside"]
        else:
            g = read(root / task / "environment/geometry.json")
            np.testing.assert_array_equal(ni.affine, g["voxel_to_ras_mm"])
            np.testing.assert_array_equal(ni.affine[:3, :3], truth["linear_voxel_to_mm"])
            assert list(ni.shape) == g["shape_ijk"] == truth["shape_ijk"]
            assert list(nib.aff2axcodes(ni.affine)) == g["positive_array_axes_patient_directions"]
            for example in g["nonanatomical_coordinate_examples"]:
                np.testing.assert_allclose(
                    nib.affines.apply_affine(ni.affine, example["ijk"]),
                    example["ras_mm"],
                    atol=1e-12,
                    rtol=0,
                )
            if number == "038":
                references = mri if case.startswith("mri") else ct
                for key, point in truth["points_ijk"].items():
                    np.testing.assert_allclose(
                        nib.affines.apply_affine(ni.affine, point),
                        references[key],
                        atol=1e-12,
                        rtol=0,
                    )
            helper = load_functions(root / task / "environment/volume_tools.py")
            ramp = np.indices((7, 11, 13))
            ramp = ramp[0] * 10000 + ramp[1] * 100 + ramp[2]
            for axis in range(3):
                plane, axes = helper.plane(ramp, axis, 3)
                for row in range(plane.shape[0]):
                    for col in range(plane.shape[1]):
                        q = [0, 0, 0]
                        q[axis] = 3
                        q[axes[0]] = col
                        q[axes[1]] = row
                        assert plane[row, col] == ramp[tuple(q)]
        source_checks[f"{number}/{case}"] = {
            "shape_ijk": list(ni.shape),
            "affine_ras_mm": ni.affine.tolist(),
            "positive_axes": list(nib.aff2axcodes(ni.affine)),
            "all_native_intensities_verified": True,
            "reference_coordinates_verified": True,
        }
        print(
            f"{number}/{case}: native arrays, geometry and reference contract verified", flush=True
        )
    del ct_array, mri_array, nrrd
    full = np.load(root / tasks[("039", "ct-full")] / "environment/volume.npy", mmap_mode="r")
    partial = np.load(root / tasks[("039", "ct-partial")] / "environment/volume.npy", mmap_mode="r")
    for start, block in nifti_blocks(root / "runs/br039-ct-landmarks/source/verse/ct.nii.gz"):
        end = start + block.shape[2]
        np.testing.assert_array_equal(block, full[:, :, start:end])
        if start < partial.shape[2]:
            stop = min(end, partial.shape[2])
            np.testing.assert_array_equal(block[:, :, : stop - start], partial[:, :, start:stop])
    points = read(root / centroids)
    ni = nib.load(root / tasks[("039", "ct-full")] / "environment/volume.nii.gz")
    assert tuple(points[0]["direction"]) == nib.aff2axcodes(ni.affine)
    mask = nib.load(root / mask_path)
    assert mask.shape == ni.shape
    np.testing.assert_array_equal(mask.affine, ni.affine)
    mask_array = np.asarray(mask.dataobj)
    for number, case in [("039", "ct-full"), ("039", "ct-partial")]:
        truth = read(root / tasks[(number, case)] / "tests/truth.json")
        for p in points[1:]:
            label = p["label"]
            key = (
                f"C{label}" if label <= 7 else f"T{label - 7}" if label <= 19 else f"L{label - 19}"
            )
            ijk = np.array([p[x] for x in "XYZ"])
            np.testing.assert_array_equal(ijk, truth["targets"][key]["ijk"])
            status = "observed" if -0.5 <= ijk[2] <= truth["shape_ijk"][2] - 0.5 else "out_of_fov"
            assert truth["targets"][key]["status"] == status
            if label != 1:
                assert mask_array[tuple(np.rint(ijk).astype(int))] == label
        assert (
            truth["targets"]["T13"] == truth["targets"]["L6"] == {"status": "absent", "ijk": None}
        )
    del mask_array

    all_scores, unique_attempts = {}, {}
    for number in ["036", "038", "039", "040"]:
        results = read(root / f"docs/evidence/br{number}-results.json")
        for t in results["trials"]:
            task = tasks[(number, t["case"])]
            run = Path(t["result_path"]).parent
            answer = Path(t.get("answer_path", str(run / "artifacts/app/answer/landmarks.json")))
            value = read(root / answer) if (root / answer).exists() else None
            if value is not None:
                pin(answer)
            pin(t["result_path"])
            if t.get("trajectory_sha256"):
                pin(run / "agent/trajectory.json", t["trajectory_sha256"])
            for path, digest in t.get("trace_audit", {}).get("raw_session_sha256", {}).items():
                pin(path, digest)
            assert read(root / t["result_path"])["task_checksum"] == t["task_checksum"]
            truth = read(root / task / "tests/truth.json")
            grade = load_functions(root / task / "tests/score.py").score(value, truth)
            compare(
                grade, t["score"], f"{number}/{t['case']}/{t.get('phase', t.get('model_setting'))}"
            )
            # Independent vector calculation in world coordinates verifies scored distances.
            affine = nib.load(root / task / "environment/volume.nii.gz").affine
            for key, expected in grade.get("errors_mm", {}).items():
                if number == "036":
                    predicted = np.array(value[key])
                    reference = np.array(truth.get("points", truth.get("points_ras_mm"))[key])
                else:
                    p = value["landmarks"][key]
                    predicted = nib.affines.apply_affine(
                        affine, p["ijk"] if isinstance(p, dict) else p
                    )
                    q = (
                        truth["targets"][key]["ijk"]
                        if "targets" in truth
                        else truth["points_ijk"][key]
                    )
                    reference = nib.affines.apply_affine(affine, q)
                assert abs(np.linalg.norm(predicted - reference) - expected) < 1e-9
            key = f"{number}/{t['case']}/{t.get('phase', t.get('model_setting'))}"
            all_scores[key] = grade
            unique_attempts[str(run)] = t.get("phase", t.get("model_setting"))
        print(f"BR-{number}: all retained scores and physical distances reproduced", flush=True)
    atlas = read(root / "docs/evidence/br040-source-audit.json")
    archives = {}
    for name, item in atlas["archives"].items():
        path = Path("runs/br040-sol-landmarks/source-audit") / name
        pin(path, item["sha256"])
        with zipfile.ZipFile(root / path) as archive:
            assert len(archive.infolist()) == item["entries"]
            assert [x for x in archive.namelist() if x.endswith(".fcsv")] == item["fcsv_entries"]
            archives[name] = {
                "entries": len(archive.infolist()),
                "fiducial_files": item["fcsv_entries"],
            }
    dump(out / "replayed-results.json", all_scores)
    data = {
        "schema": 1,
        "scope": "Source arrays, private coordinates, all saved scores and archived assistance; no model or solver execution",
        "source_pins": pins,
        "reproduction_manifest_files": len(manifest["files"]),
        "task_checks": source_checks,
        "saved_score_records": len(all_scores),
        "unique_execution_records": len(unique_attempts),
        "model_attempts": sum(x in ["terra-high", "sol-xhigh"] for x in unique_attempts.values()),
        "rater_max_distance_to_mean_mm": rater_distances,
        "atlas_archives": archives,
        "atlas_image_gap": "The runtime TemplateFlow image bytes and SHA-256 remain unavailable; archive NIfTI entry is an annex pointer, not an audited image.",
        "score_absolute_tolerance": 1e-9,
        "script_sha256": sha(Path(__file__)),
        "environment": {
            "numpy": np.__version__,
            "nibabel": nib.__version__,
            "SimpleITK": sitk.Version_VersionString(),
        },
    }
    dump(out / "audit.json", data)
    print(
        f"Complete: {len(pins)} files; {len(all_scores)} score records; {len(unique_attempts)} unique executions",
        flush=True,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    audit(args.root.resolve(), args.output.resolve())
