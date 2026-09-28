"""Read-only replay of frozen BR-016 inputs, weak regions and saved answers."""

import argparse
import csv
import hashlib
import importlib.util
import json
import tarfile
from pathlib import Path

import nibabel as nib
import numpy as np
from scipy.spatial import cKDTree


def read(path):
    return json.loads(path.read_text())


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def audit(root, destination):
    destination.mkdir(parents=True, exist_ok=False)
    pins = {}

    def pin(path, expected=None):
        path = Path(path)
        relative = path.relative_to(root) if path.is_absolute() else path
        digest = sha(root / relative)
        assert expected is None or digest == expected, relative
        pins[str(relative)] = digest
        return root / relative

    pin(Path(__file__))
    base = Path("runs/br016-aneurysm")
    source = base / "source"
    results = read(pin("docs/evidence/br016-results.json"))
    for name in ["audit", "curation", "trace-reviews", "negative-controls"]:
        pin(f"docs/evidence/br016-{name}.json")
    tree = read(pin(source / "tree.json"))
    description = read(pin(source / "dataset_description.json"))
    assert description["License"] == "CC0"
    participants = list(csv.DictReader(pin(source / "participants.tsv").open(), delimiter="\t"))
    groups = {p["participant_id"]: p["group"] for p in participants}
    receipt = read(pin(source / "receipt.json"))
    assert receipt["git_tree"] == tree["sha"]
    raw = read(pin(source / "raw-receipt.json"))
    selected_subjects = {"013", "022", "000"}
    source_records = []
    for item in receipt["files"] + raw:
        if item["file"].split("_")[0][4:] not in selected_subjects:
            continue
        path = pin(source / item["file"], item["sha256"])
        assert path.stat().st_size == item["bytes"]
        assert hashlib.md5(path.read_bytes()).hexdigest() == item["md5"]
        assert any(x["path"] == item["path"] for x in tree["tree"])
        source_records.append(item)

    cases = {}
    freeze_count = 0
    for number, subject in [(1, "013"), (2, "022"), (3, "000")]:
        case_id = f"n{number:02}"
        name = f"aneurysm-{case_id}"
        snapshots = []
        for suffix in ["", "-v2"]:
            freeze = read(pin(f"docs/evidence/br016-{name}{suffix}-freeze.json"))["tasks"][0]
            for relative, digest in freeze["files"].items():
                pin(Path(freeze["task_path"]) / relative, digest)
                freeze_count += 1
            snapshots.append(freeze)
        v1, v2 = snapshots
        shared = set(v1["files"]) & set(v2["files"])
        differences = [p for p in sorted(shared) if v1["files"][p] != v2["files"][p]]
        assert differences == ["task.toml"]
        assert set(v2["files"]) - set(v1["files"]) == {"tests/Dockerfile"}
        task = Path(v2["task_path"])
        key = read(root / task / "tests/expected.json")
        archive_members = {}
        with tarfile.open(root / task / "environment/data.tar.gz") as archive:
            assert set(archive.getnames()) == {
                "brain.npz",
                "original.npz",
                "volume.json",
                "overview.png",
                "slabs.png",
            }
            for member in archive.getmembers():
                assert member.isfile()
                data = archive.extractfile(member).read()
                archive_members[member.name] = hashlib.sha256(data).hexdigest()
                pin(base / "build" / name / member.name, archive_members[member.name])
                if member.name == "volume.json":
                    metadata = json.loads(data)
        spacing = np.array(metadata["spacing_mm"])
        affine = np.array(metadata["affine_ijk_to_RAS_mm"])
        assert nib.aff2axcodes(affine) == ("R", "A", "S")
        assert np.allclose(affine[:3, :3], np.diag(spacing), rtol=0, atol=1e-10)
        assert key["shape"] == metadata["shape"]
        input_checks = []
        for kind, suffix in [("brain", "brain_mask"), ("original", "angio")]:
            path = next((root / source).glob(f"sub-{subject}*{suffix}.nii.gz"))
            pin(path)
            image = nib.load(path)
            array = np.asanyarray(image.dataobj)
            with np.load(root / base / "build" / name / f"{kind}.npz") as packed:
                np.testing.assert_array_equal(array, packed["volume"])
                np.testing.assert_array_equal(image.affine, packed["affine"])
            np.testing.assert_array_equal(image.affine, affine)
            assert list(array.shape) == key["shape"] and np.isfinite(array).all()
            input_checks.append(
                {"kind": kind, "voxels": int(array.size), "dtype": str(array.dtype), "exact": True}
            )
            if kind == "brain":
                brain = array
        masks = sorted((root / source).glob(f"sub-{subject}*Lesion*nii.gz"))
        assert len(masks) == len(key["regions"])
        regions = []
        for path, region in zip(masks, key["regions"], strict=True):
            pin(path)
            image = nib.load(path)
            np.testing.assert_array_equal(image.affine, affine)
            mask = np.asanyarray(image.dataobj) > 0
            assert mask.shape == brain.shape
            points = np.argwhere(mask)
            pad = np.ceil(1 / spacing).astype(int)
            low, high = (
                np.maximum(0, points.min(0) - pad),
                np.minimum(np.array(mask.shape) - 1, points.max(0) + pad),
            )
            grid = np.stack(
                np.meshgrid(*(np.arange(low[d], high[d] + 1) for d in range(3)), indexing="ij"),
                axis=-1,
            ).reshape(-1, 3)
            distance = cKDTree(points * spacing).query(grid * spacing)[0]
            accepted = {tuple(p) for p in grid[distance <= 1 + 1e-8].tolist()}
            retained = {tuple(map(int, p.split(","))) for p in region["accepted_voxels"]}
            assert accepted == retained
            world = np.sum(points[:, None, :] * affine[None, :3, :3], axis=2) + affine[:3, 3]
            np.testing.assert_allclose((world - affine[:3, 3]) / spacing, points, atol=1e-10)
            regions.append(
                {
                    "source": str(path.relative_to(root)),
                    "source_voxels": len(points),
                    "accepted_voxels": len(accepted),
                    "center_ijk": points.mean(0).tolist(),
                    "extent_mm": ((points.max(0) - points.min(0) + 1) * spacing).tolist(),
                    "brain_nonzero_fraction": float(np.mean(brain[mask] > 0)),
                    "independent_world_distance_region_equal": True,
                    "coordinate_roundtrip": True,
                }
            )
        assert groups[f"sub-{subject}"] == ("control" if number == 3 else "patient")
        manual = [
            x["path"]
            for x in tree["tree"]
            if f"manual_masks/sub-{subject}/" in x["path"]
            and "Lesion" in x["path"]
            and x["path"].endswith(".nii.gz")
        ]
        assert len(manual) == len(regions)
        cases[case_id] = {
            "task": str(task),
            "subject": subject,
            "group": groups[f"sub-{subject}"],
            "metadata": metadata,
            "input_checks": input_checks,
            "archive_members_sha256": archive_members,
            "reference_regions": regions,
            "v1_v2_changes": {
                "changed": differences,
                "added": ["tests/Dockerfile"],
                "inputs_instruction_reference_scorer_equal": True,
            },
        }

    # This retained module is a pure dependency-free scorer; no authoring module is imported.
    score_path = root / cases["n01"]["task"] / "tests/scoring.py"
    spec = importlib.util.spec_from_file_location("retained_br016_score", score_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    replays = []
    traces = {}
    for row in results["rows"]:
        result_path = pin(row["result_path"], row["result_sha256"])
        if row["execution"] != "completed":
            assert (
                row["phase"] == "oracle"
                and row["exception_type"] == "FileNotFoundError"
                and row["reward"] is None
            )
            replays.append(
                {
                    "task": row["task"],
                    "phase": row["phase"],
                    "classification": "retained pre-model verifier setup failure",
                    "replayed": False,
                }
            )
            continue
        answer = read(pin(row["answer_path"], row["answer_sha256"]))
        grade = read(pin(result_path.parent / "verifier/details.json", row["grade_sha256"]))
        assert answer == row["answer"] and grade == row["grade"]
        key = read(root / base / "tasks" / row["task"] / "tests/expected.json")
        try:
            replay = module.score(answer, key)
        except ValueError as error:
            replay = {"passed": False, "error": str(error)}
        assert replay == {k: v for k, v in grade.items() if k != "grading_seconds"}
        assert float(replay["passed"]) == row["reward"]
        replays.append(
            {
                "task": row["task"],
                "phase": row["phase"],
                "answer": answer,
                "score": replay,
                "exact": True,
            }
        )
        if row["phase"] != "sol-xhigh":
            continue
        case_id = row["task"].split("-")[1]
        trace_path = pin(result_path.parent / "agent/trajectory.json", row["trajectory_sha256"])
        trace = read(trace_path)
        for session in row["session_files"]:
            pin(session["path"], session["sha256"])
        # Save only IDs and command-keyword matches, not private reasoning or full raw traces.
        anchors = []
        needles = [
            "cand_k.png",
            "cand_i.png",
            "cand_j.png",
            "cand1_",
            "cand2_",
            "work_k82",
            "fine_j260",
            "eigvalsh",
            "manual_masks",
            "array_equal",
            "answer/answer.json",
            "ds003949-tree",
            "diff",
        ]
        for step in trace["steps"]:
            calls = json.dumps(step.get("tool_calls", []))
            matched = [word for word in needles if word in calls]
            if matched:
                anchors.append(
                    {
                        "step_id": step["step_id"],
                        "timestamp": step.get("timestamp"),
                        "command_tokens": matched,
                    }
                )
        if case_id == "n03":
            assert any("manual_masks" in a["command_tokens"] for a in anchors)
            assert any("array_equal" in a["command_tokens"] for a in anchors)
        traces[case_id] = {
            "path": str(trace_path.relative_to(root)),
            "sha256": sha(trace_path),
            "anchors": anchors,
            "annotation_inventory_exposed": row["annotation_inventory_exposed"],
            "public_source_match_observed": row["public_source_match_observed"],
            "model": row["requested_model"],
            "effort": row["requested_effort"],
            "agent_seconds": row["agent_seconds"],
            "output_tokens": row["output_tokens"],
            "scope": "Observable commands and retained outputs only; selected anchors, not reconstructed private reasoning.",
        }

    controls = []
    for case_id, case in cases.items():
        key = read(root / case["task"] / "tests/expected.json")
        points = [r["center_ijk"] for r in case["reference_regions"]]
        for label, answer, expected in [
            ("oracle", {"aneurysms": points}, True),
            ("empty", {"aneurysms": []}, case_id == "n03"),
            ("extra_corner", {"aneurysms": [*points, [0, 0, 0]]}, False),
            ("duplicate", {"aneurysms": points + points}, case_id == "n03"),
        ]:
            result = module.score(answer, key)
            assert result["passed"] == expected
            controls.append({"case": case_id, "control": label, "score": result})
    n02 = cases["n02"]
    point = np.array(
        next(
            r["answer"]["aneurysms"][0]
            for r in replays
            if r["task"] == "aneurysm-n02-v2" and r["phase"] == "sol-xhigh"
        )
    )
    center = np.array(n02["reference_regions"][0]["center_ijk"])
    n02["submitted_point"] = point.tolist()
    n02["point_to_reference_centroid_mm"] = float(
        np.linalg.norm((point - center) * np.array(n02["metadata"]["spacing_mm"]))
    )
    mask = np.asanyarray(nib.load(root / n02["reference_regions"][0]["source"]).dataobj) > 0
    n02["submitted_point_inside_source_mask"] = bool(mask[tuple(point)])
    assert all(sha(root / path) == digest for path, digest in pins.items())
    out = {
        "schema": 1,
        "review_date": "2026-09-28",
        "reviewer": "assistant",
        "source_tree": tree["sha"],
        "license": description["License"],
        "source_records": source_records,
        "source_pins": pins,
        "frozen_file_checks": freeze_count,
        "cases": cases,
        "replays": replays,
        "controls": controls,
        "traces": traces,
        "scope": "Saved-output and input-byte replay only. No model, download, Docker launch, original authoring import or historical score mutation.",
        "limits": [
            "Weak source regions support coarse point matching, not sac contour adjudication.",
            "Image/array fidelity does not prove clinical reference completeness or visibility.",
            "N03 source exposure is permitted by the historical public-network condition; no negative answer was frozen before lookup.",
            "Three selected cases are not a clinical accuracy estimate; unknown training overlap and independent clinical review remain unresolved.",
        ],
    }
    (destination / "audit.json").write_text(json.dumps(out, indent=2, allow_nan=False) + "\n")
    print(
        json.dumps(
            {
                "out": str(destination),
                "pins": len(pins),
                "frozen_files": freeze_count,
                "replayed": sum(r.get("exact", False) for r in replays),
                "cases": len(cases),
                "n02_center_distance_mm": n02["point_to_reference_centroid_mm"],
                "n02_inside_weak_mask": n02["submitted_point_inside_source_mask"],
            }
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    audit(args.root.resolve(), args.out.resolve())
