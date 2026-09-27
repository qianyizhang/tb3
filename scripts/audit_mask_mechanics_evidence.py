"""Audit BR-035 inputs and saved answers without executing a solver or authoring code."""

import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy.ndimage import map_coordinates

BASE = Path("runs/br035-segmentation-mechanics")
REPRO = Path("groups/cardiac-motion/experiments/br035/reproduction")
INPUTS = Path(".local/inputs/reproduction/cardiac-motion-br035")
RESULT = Path("docs/evidence/br035-segmentation-mechanics-results.json")
RESULT_SHA = "12806e221bc93b8400dbe2d950e67ed89b6f2fb396ba7e76b2833fa42e00fed2"


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path):
    return json.loads(path.read_text())


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def compare(actual, expected, path=""):
    if isinstance(expected, dict):
        assert actual.keys() == expected.keys(), path
        for key in expected:
            compare(actual[key], expected[key], path + "/" + key)
    elif isinstance(expected, list):
        assert len(actual) == len(expected), path
        for i, value in enumerate(expected):
            compare(actual[i], value, path + f"/{i}")
    elif isinstance(expected, (str, bool, int)) or expected is None:
        assert actual == expected, (path, actual, expected)
    else:
        assert abs(actual - expected) <= 1e-8, (path, actual, expected)


def audit(root, out):
    out.mkdir(parents=True, exist_ok=False)
    pins = {}

    def pin(path, expected=None):
        value = sha(root / path)
        if expected is not None:
            assert value == expected, str(path)
        pins[str(path)] = value

    pin(RESULT, RESULT_SHA)
    result = read(root / RESULT)
    pin(BASE / "freeze.json", result["freeze_sha256"])
    pin(Path("docs/research-rounds/BR-035-segmentation-mechanics.md"), result["protocol_sha256"])
    freeze = read(root / BASE / "freeze.json")
    pin(REPRO / "manifest.json")
    manifest = read(root / REPRO / "manifest.json")
    for item in manifest["files"]:
        path = Path(item["source"])
        pin(path, item["sha256"])
        assert (root / path).stat().st_size == item["size"], str(path)
        assert (root / path).stat().st_mode & 0o111 == item["mode"] & 0o111, str(path)
    for condition in freeze["conditions"].values():
        for name, digest in condition["files"].items():
            pin(Path(condition["task_path"]) / name, digest)
    for key, folder in [("clinical_files", "clinical"), ("prepared_files", "prepared")]:
        for name, digest in freeze[key].items():
            pin(BASE / folder / name, digest)
    for name, digest in result["authoring_sha256"].items():
        pin(Path(name), digest)
    for trial in result["trials"]:
        pin(Path(trial["result_path"]), trial["result_sha256"])
        for session in trial.get("session_files", []):
            pin(Path(session["path"]), session["sha256"])
    for condition, replay in result["replays"].items():
        for name, digest in replay["output_files_sha256"].items():
            pin(BASE / "replays" / condition / "output" / name, digest)
        for name, digest in replay["input_files_sha256"].items():
            pin(BASE / "clinical" / condition / name, digest)

    parent = Path("runs/br029-dynamic-heart")
    clinical = Path("runs/br034-pathological-echo")
    prep = result["preparation"]
    pin(parent / "analysis-v2/healthy_reference.npz", prep["source_reference_sha256"])
    pin(parent / "public-video/geometry.json", prep["source_geometry_sha256"])
    pin(clinical / "reference.npz", prep["clinical_source_sha256"])
    audit_path = Path("groups/cardiac-motion/presentation/sources/cardiac-material-audit.json")
    pin(audit_path, "51df0ab9c42a48fcbbc75f365a9926ac7920db7d64552393c7e7fc1f508f0f86")
    source_pins = read(root / audit_path)["source_pins"]
    for path, digest in source_pins.items():
        if "/patient01_healthy/image/" in path:
            pin(Path(path), digest)
    clinical_audit = Path("groups/cardiac-motion/presentation/sources/clinical-cavity-audit.json")
    pin(clinical_audit, "0ee985362ca1f01fb8b1db5a3267ae5b0892456843670e02e5bd136b1adc2ca1")
    # The preceding entry audited these prepared arrays against the native archive.
    clinical_pins = read(root / clinical_audit)["source_pins"]
    for name in ["input/volumes.npy", "input/geometry.json"]:
        path = clinical / name
        pin(path, clinical_pins[str(path)])

    geometry_path = root / REPRO / "cases/cardiac-masks/task/tests/geometry.py"
    spec = importlib.util.spec_from_file_location("br035_audit_geometry", geometry_path)
    geometry = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(geometry)
    # This hash-verified portable evaluator module contains functions only.
    truth = dict(np.load(root / BASE / "prepared/truth.npz", allow_pickle=False))
    reference = np.load(root / parent / "analysis-v2/healthy_reference.npz", allow_pickle=False)
    for key in ["points", "tetra", "directions", "cell_labels"]:
        np.testing.assert_array_equal(truth[key], reference[key])
    edges = truth["points"][0][truth["tetra"][:, 1:]] - truth["points"][0][truth["tetra"][:, :1]]
    np.testing.assert_array_equal(truth["weights"], abs(np.linalg.det(edges)) / 6)

    source_checks = {}
    for kind in ["synthetic", "clinical"]:
        masks = np.load(root / BASE / "prepared" / f"{kind}_masks.npz")["masks"]
        images = np.load(root / BASE / "prepared" / f"{kind}_images.npy", mmap_mode="r")
        g = read(root / BASE / "prepared" / f"{kind}_geometry.json")
        assert list(masks.shape) == g["shape_tzyx"] == list(images.shape)
        assert masks.dtype == bool and images.dtype == np.float32
        origin, spacing = np.array(g["origin_xyz_mm"]), np.array(g["spacing_xyz_mm"])
        zz, yy, xx = np.indices(masks.shape[1:])
        grid = origin + np.stack([xx, yy, zz], -1) * spacing
        if kind == "synthetic":
            srcg = read(root / parent / "public-video/geometry.json")
            native = np.einsum("...i,ij->...j", grid, srcg["canonical_to_native_rotation_rows"])
            native = (native + srcg["canonical_to_native_offset"]) / srcg["source_spacing_mm"]
            coords = np.moveaxis(native[..., ::-1], -1, 0)
            points, cells = truth["points"], truth["tetra"]
        else:
            ref = np.load(root / clinical / "reference.npz", allow_pickle=False)
            points, cells = ref["points"], ref["faces"]
            srcg = read(root / clinical / "input/geometry.json")
            coords = np.moveaxis(((grid - origin) / srcg["spacing_xyz_mm"])[..., ::-1], -1, 0)
            volumes = np.load(root / clinical / "input/volumes.npy", mmap_mode="r")
            assert g["timestamps_s"] == srcg["timestamps_s"]
        for t, points_t in enumerate(points):
            if kind == "synthetic":
                mask = geometry.voxelize(points_t, cells, origin, spacing, masks.shape[1:])
                header = root / parent / "source/patient01_healthy/image" / f"usfrm{t:02d}.mhd"
                fields = dict(
                    line.split(" = ", 1)
                    for line in header.read_text().splitlines()
                    if " = " in line
                )
                assert (
                    fields["ElementType"] == "MET_SHORT"
                    and fields["BinaryDataByteOrderMSB"] == "False"
                )
                assert (
                    fields["TransformMatrix"] == "1 0 0 0 1 0 0 0 1" and fields["Offset"] == "0 0 0"
                )
                volume = np.fromfile(
                    header.with_name(fields["ElementDataFile"]), dtype="<i2"
                ).reshape(tuple(np.array(fields["DimSize"].split(), int)[::-1]))
            else:
                mask = geometry.cavity_mask(points_t, cells, origin, spacing, masks.shape[1:])
                volume = volumes[t]
            np.testing.assert_array_equal(mask, masks[t])
            sampled = map_coordinates(volume.astype("float32"), coords, order=1, mode="constant")
            np.testing.assert_array_equal(sampled, images[t])
        source_checks[kind] = {
            "shape_tzyx": list(masks.shape),
            "origin_xyz_mm": origin.tolist(),
            "spacing_xyz_mm": spacing.tolist(),
            "all_masks_equal": True,
            "all_images_equal": True,
            "timestamps_s": g["timestamps_s"],
            "mask_semantics": g["mask_semantics"],
        }
        print(f"{kind}: all {len(masks)} masks and images equal source derivation", flush=True)
    del truth, reference

    # Run only the inspected frozen scorer, never solve.py or a historical authoring module.
    scorer = root / REPRO / "cases/cardiac-masks/task/tests"
    code = "import json,sys; from score import score; print(json.dumps(score(sys.argv[1],sys.argv[2],None if sys.argv[3]=='none' else sys.argv[3]),allow_nan=False))"
    replayed, summaries = {}, {}

    def grade(name, answer, data, truth_path, expected):
        args = [
            sys.executable,
            "-B",
            "-c",
            code,
            str(root / answer),
            str(root / data),
            str(root / truth_path) if truth_path else "none",
        ]
        done = subprocess.run(
            args,
            cwd=scorer,
            capture_output=True,
            text=True,
            check=True,
            timeout=1800,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        (out / f"{name}-stderr.log").write_text(done.stderr)
        actual = json.loads(done.stdout)
        compare(actual, expected, name)
        replayed[name] = actual
        summaries[name] = {
            "reward": actual["reward"],
            "construction_gates": actual.get("construction_gates"),
            "geometry": actual.get("geometry"),
            "material": {
                k: v
                for k, v in actual.get("material", {}).items()
                if k
                not in ["predicted_regional_engineering_pct", "reference_regional_engineering_pct"]
            },
            "cavity_function": actual.get("cavity_function"),
        }
        dump(out / "replayed-results.json", replayed)
        print(f"{name}: full saved score matches within absolute 1e-8", flush=True)

    for condition in ["masks", "masks-images"]:
        case = manifest["cases"][f"cardiac-{condition}"]
        observation = case["observations"][0]
        answer = INPUTS / observation["answer"] / "prediction.npz"
        trial = next(
            t for t in result["trials"] if t["condition"] == condition and t["phase"] == "sol-xhigh"
        )
        assert pins[str(answer)] == trial["artifacts"]["prediction.npz"]
        grade(
            condition,
            answer,
            BASE / "tasks" / f"cardiac-{condition}" / "tests/data",
            BASE / "prepared/truth.npz",
            trial["grade"],
        )
        grade(
            f"clinical-{condition}",
            BASE / "replays" / condition / "output/prediction.npz",
            BASE / "clinical" / condition,
            None,
            {
                **result["replays"][condition]["grade"],
                "cavity_function": {
                    k: v
                    for k, v in result["replays"][condition]["grade"]["cavity_function"].items()
                    if k
                    not in ["clinical_surface_reference_ef_pct", "clinical_surface_ef_error_pp"]
                },
            },
        )
        with np.load(root / answer, allow_pickle=False) as saved:
            points, cells = saved["points"], saved["tetra"]
        faces = geometry.boundary(cells)
        boundary_edges = np.concatenate([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]])
        _, counts = np.unique(np.sort(boundary_edges, axis=1), axis=0, return_counts=True)
        expected_quality = result["posthoc_mesh_quality"][condition]
        assert int((counts != 2).sum()) == expected_quality["boundary_edges_with_incidence_not_two"]
        assert len(faces) == expected_quality["boundary_faces"]
        v0 = abs(np.linalg.det(points[0][cells[:, 1:]] - points[0][cells[:, :1]])) / 6
        low, high = [], []
        for p in points:
            _, _, jacobian = geometry.fields(points[0], p[None], cells)
            low.append(float(100 * v0[jacobian[0] < 0.2].sum() / v0.sum()))
            high.append(float(100 * v0[jacobian[0] > 2].sum() / v0.sum()))
        compare(low, expected_quality["fraction_reference_volume_J_below_point2_pct"])
        compare(high, expected_quality["fraction_reference_volume_J_above_2_pct"])
    for name in ["oracle", "static"]:
        pin(BASE / "controls" / f"{name}.npz")
        grade(
            name,
            BASE / "controls" / f"{name}.npz",
            BASE / "tasks/cardiac-masks/tests/data",
            BASE / "prepared/truth.npz",
            result["controls"][name],
        )
    audit_result = {
        "schema": 1,
        "scope": "Read-only input derivation and saved-output regrading; no solver or model execution",
        "source_pins": pins,
        "reproduction_manifest_files": len(manifest["files"]),
        "source_derivation": source_checks,
        "saved_results": summaries,
        "posthoc_mesh_quality": result["posthoc_mesh_quality"],
        "comparison_absolute_tolerance": 1e-8,
        "implementation_sha256": sha(Path(__file__)),
        "environment": {"python": sys.version.split()[0], "numpy": np.__version__},
    }
    dump(out / "audit.json", audit_result)
    print(f"Audit complete: {len(pins)} pinned files; six saved scores reproduced", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    audit(arguments.root.resolve(), arguments.output.resolve())
