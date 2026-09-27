"""Check retained BR-022 artifacts and derive teaching views; no solver or optimizer runs."""

import argparse
import json
import shutil
import tomllib
from pathlib import Path

import numpy as np
from build_respiratory_assets import dump, plane, read, sha
from scipy.ndimage import gaussian_filter, map_coordinates


def build(root, output):
    output.mkdir(parents=True, exist_ok=False)
    sources = {}

    def verify(name, expected=None):
        path = root / name
        actual = sha(path)
        if expected and actual != expected:
            raise ValueError(f"Retained artifact changed: {name}")
        sources[name] = actual
        return path

    experiment = tomllib.loads(
        (root / "groups/registration/experiments/br022/experiment.toml").read_text()
    )
    for item in experiment["evidence"]:
        verify(item["path"], item["sha256"])
    manifest = read(
        verify("groups/registration/findings/evidence/respiratory-failure-mechanisms.json")
    )
    for pointer in manifest["artifacts"]["selected_pointers"]:
        verify(pointer["path"], pointer["expected_sha256"])
    analysis = read(root / "docs/evidence/br022-solver-analysis.json")
    results = read(root / "docs/evidence/br022-results.json")
    plan = read(root / "docs/evidence/br022-plan.json")
    verify(plan["protocol_path"], plan["protocol_sha256"])
    verify("docs/evidence/br021-freeze.json", plan["original_freeze_sha256"])
    task = root / plan["task"]["task_path"]
    for name, expected in plan["task"]["files"].items():
        verify(str((task / name).relative_to(root)), expected)
    recovery = analysis["recovery"]
    verify(recovery["trajectory_path"], recovery["trajectory_sha256"])
    retained = root / "runs/br022-registration-postmortem"
    for name, expected in recovery["files"].items():
        verify(str((retained / "recovered" / name).relative_to(root)), expected)
    execution = read(root / "docs/evidence/br022-author-execution.json")
    for name, expected in execution["solver_code_files"].items():
        verify(name, expected)
    # Runtime configs may contain credentials. They are never loaded or copied.
    truth = read(task / "tests/truth.json")
    targets = np.asarray(truth["points_world_mm"])

    def grade(points, expected):
        points = np.asarray(points)
        if points.shape != (8, 3) or not np.isfinite(points).all():
            raise ValueError("Invalid retained coordinates")
        errors = np.linalg.norm(points - targets, axis=1)
        for actual, recorded in [
            (errors, expected["per_point_mm"]),
            (np.sqrt(np.mean(errors**2)), expected["rms_mm"]),
            (np.max(errors), expected["max_mm"]),
        ]:
            if not np.allclose(actual, recorded, atol=1e-10, rtol=0):
                raise ValueError("Retained score differs")
        return errors

    attempts = []
    for row in [results["retrospective_selected_attempt"], *results["prospective_rows"]]:
        verify(row["result_path"], row["result_sha256"])
        if not row.get("answer_path"):
            if row["phase"] != "nop" or row["reward"] != 0:
                raise ValueError("Unexpected missing answer")
            continue
        answer = read(verify(row["answer_path"], row["answer_sha256"]))
        if answer["query_ids"] != truth["query_ids"]:
            raise ValueError("Query identity mismatch")
        grade(answer["points_world_mm"], row["grade"])
        if row["phase"] != "oracle":
            attempts.append({"phase": row["phase"], "answer": answer, "grade": row["grade"]})
    variants = []
    for row in analysis["counterfactuals"]:
        answer = read(verify(row["path"], row["sha256"]))
        grade(answer["points_world_mm"], row["grade"])
        distances = []
        for i, (d, recorded) in enumerate(
            zip(answer["diagnostics"], row["search_geometry"], strict=True)
        ):
            axes = np.array(d["axes"])
            if not np.allclose(np.einsum("ij,ik->jk", axes, axes), np.eye(3), atol=1e-8, rtol=0):
                raise ValueError("Nonorthonormal saved search basis")
            offset = np.einsum("ij,i->j", axes, targets[i] - d["centre"])
            distance = np.linalg.norm(offset - np.clip(offset, -row["bound_mm"], row["bound_mm"]))
            if (
                not np.allclose(offset, recorded["true_offset_local_mm"], atol=1e-10, rtol=0)
                or abs(distance - recorded["distance_to_box_mm"]) > 1e-10
            ):
                raise ValueError("Search support diagnostic differs")
            distances.append(distance)
        if (
            abs(np.sqrt(np.mean(np.array(distances) ** 2)) - row["box_best_possible_rms_mm"])
            > 1e-10
        ):
            raise ValueError("Search support RMS bound differs")
        variants.append(row)
    for row in analysis["author_baseline_ablations"]:
        answer = read(verify(row["path"], row["sha256"]))
        grade(answer["points_world_mm"], row["grade"])
    stages_path = verify("runs/br022-registration-postmortem/replay/stages.json")
    stages = read(stages_path)
    for stage, recorded in analysis["replay"]["stages"].items():
        grade([q[stage] for q in stages["queries"]], recorded)
    final = np.array([q["final"] for q in stages["queries"]])
    drift = np.max(np.linalg.norm(final - attempts[0]["answer"]["points_world_mm"], axis=1))
    if abs(drift - analysis["replay"]["maximum_coordinate_drift_mm"]) > 1e-12:
        raise ValueError("Replay drift differs")
    condition = read(retained / "counterfactuals/original-b9-s17.json")
    queries = read(task / "environment/data/queries.json")
    frame = read(task / "environment/data/view.json")
    view = np.load(task / "environment/data/view.npy", allow_pickle=False)
    with np.load(task / "environment/data/volume.npz", allow_pickle=False) as z:
        volume, affine = z["hu"], z["voxel_to_world"]
    inverse = np.linalg.inv(affine)
    sx, sy = frame["spacing_xy_mm"]
    yy, xx = np.mgrid[-8:8.01:0.8, -8:8.01:0.8]
    pose = np.array(frame["slice_to_world"])
    public_patches, private_patches, maximum_objective_error = {}, {}, 0.0
    for i, (pixel, d, objective_row) in enumerate(
        zip(
            queries["pixels_uv"],
            condition["diagnostics"],
            analysis["objective_diagnostics"],
            strict=True,
        )
    ):
        axes = np.array(d["axes"])
        px, py = pixel
        src = map_coordinates(
            view,
            np.vstack([(py + yy / sy).ravel(), (px + xx / sx).ravel()]),
            order=1,
            mode="nearest",
        ).reshape(xx.shape)
        hs = src - gaussian_filter(src, 1.6)

        def sample(point, axes=axes):
            world = (
                np.array(point)[:, None]
                + axes[:, 0, None] * xx.ravel()
                + axes[:, 1, None] * yy.ravel()
            )
            coords = np.einsum("ij,jn->in", inverse, np.vstack([world, np.ones(world.shape[1])]))[
                :3
            ]
            return map_coordinates(volume, coords, order=1, cval=-1024).reshape(xx.shape)

        def objective(point, sample=sample, src=src, hs=hs):
            patch = sample(point)
            hp = patch - gaussian_filter(patch, 1.6)
            return float(
                0.4 * np.corrcoef(src.ravel(), patch.ravel())[0, 1]
                + 0.6 * np.corrcoef(hs.ravel(), hp.ravel())[0, 1]
            )

        submitted = np.array(attempts[0]["answer"]["points_world_mm"][i])
        for actual, expected in [
            (objective(targets[i]), objective_row["score_at_manual_target"]),
            (objective(submitted), objective_row["score_at_submitted_point"]),
        ]:
            maximum_objective_error = max(maximum_objective_error, abs(actual - expected))
        curve = [
            objective(targets[i] + t * (submitted - targets[i]))
            for t in objective_row["curve_fractions"]
        ]
        maximum_objective_error = max(
            maximum_objective_error,
            float(np.max(np.abs(np.array(curve) - objective_row["curve_reference_to_submission"]))),
        )
        if i in [0, 5]:
            source_centre = pose[:3, 3] + pose[:3, 0] * px * sx + pose[:3, 1] * py * sy

            def encode(patch, centre, a, b):
                result = plane(
                    patch, centre - 8 * (a + b), 0.8 * a, 0.8 * b, "recorded radius-8 patch"
                )
                result.pop("gray_u8")
                return result

            public_patches[queries["query_ids"][i]] = {
                "source": encode(src, source_centre, pose[:3, 0], pose[:3, 1]),
                "submitted": encode(sample(submitted), submitted, axes[:, 0], axes[:, 1]),
            }
            private_patches[queries["query_ids"][i]] = encode(
                sample(targets[i]), targets[i], axes[:, 0], axes[:, 1]
            )
    if maximum_objective_error > 1e-8:
        raise ValueError("Recorded objective samples differ")
    complete = plane(
        view,
        pose[:3, 3],
        pose[:3, 0] * sx,
        pose[:3, 1] * sy,
        "complete solver-visible source slice",
    )
    complete.pop("gray_u8")
    dump(
        output / "geometry.json",
        {
            "frame": "dataset-world",
            "units": "mm",
            "source_view": complete,
            "queries": queries,
            "patches": public_patches,
            "original_diagnostics": condition["diagnostics"],
            "submitted": attempts[0]["answer"],
        },
    )
    dump(
        output / "reference.json",
        {
            "truth": truth,
            "manual_patches": private_patches,
            "attempts": attempts,
            "analysis": analysis,
        },
    )
    shutil.copyfile(
        root / "presentation/task-explorer/respiratory/DATA-LICENSE.txt",
        output / "DATA-LICENSE.txt",
    )
    (output / "NOTICE.md").write_text("""# Registration postmortem teaching views

Learn2Reg LungCT 1.11: Hering, Alessa; Murphy, Keelin; van Ginneken, Bram (2020), Radboud University Medical Center. [Source](https://doi.org/10.5281/zenodo.3835682), CC BY 4.0; exact license text retained. No endorsement implied.

Actual case 1 source and target CT arrays are retained in the frozen BR-021 task. Coordinates are dataset-world millimetres, not asserted native LPS/RAS. Source preview is complete. Selected q01/q06 patches are posthoc teaching comparisons, independently centred on the source, returned point or manual target. They do not show displacement or remove the original search problem. Each 21 by 21 patch samples the recorded radius-8 objective grid at 0.8 mm spacing; source sampling is bilinear, target sampling trilinear, with the saved local target axes. Grayscale window is HU -1000 to 200. The objective uses original HU and a 0.4 raw / 0.6 high-pass NCC mixture, not these display grayscale values.

The author postmortem had privileged references; the original solver did not. Reference targets, reference-centred pixels, scores and diagnosis are separately in reference.json and revealed to the reader. Search boxes use saved orthonormal local axes and half-widths; plots must name their axes and retain the full 3D lower bound. A curve between manual and submitted points is a diagnostic interpolation, never the solver's search path.

The builder checks all frozen task bytes, retained answer hashes, replay stages, fourteen composition/search interventions and four author controls. It recomputes every point error, all 112 query-box distances, and 808 recorded objective-curve samples without rerunning any optimizer, historical authoring module or model. The original replay image was replaced by an identical-Dockerfile retained image; numerical output equivalence is retained separately from original execution. No new scientific trial, annotation correction or regrading is implied.

Rebuild with the existing imaging environment: `python scripts/build_registration_analysis_assets.py --root . --output NEW_DIRECTORY`. Shared pixel encoding comes from the import-safe respiratory builder. This is a reader presentation, not a blind solver packet.
""")
    dump(
        output / "manifest.json",
        {
            "schema": 1,
            "id": "retained-registration-analysis-v1",
            "frame": "dataset-world",
            "units": "mm",
            "license": "CC-BY-4.0",
            "label_license": "CC-BY-4.0",
            "reference_policy": "reader-reference-reveal",
            "sources": sources,
            "checks": {
                "frozen_files": len(plan["task"]["files"]),
                "counterfactuals": len(variants),
                "query_box_distances": 8 * len(variants),
                "author_controls": len(analysis["author_baseline_ablations"]),
                "maximum_coordinate_drift_mm": float(drift),
                "objective_curve_samples": 808,
                "maximum_objective_difference": maximum_objective_error,
            },
            "assets": [
                {
                    "file": p.name,
                    "sha256": sha(p),
                    "bytes": p.stat().st_size,
                    "provenance": "source-derived-teaching",
                    "role": "reader-reference-reveal"
                    if p.name == "reference.json"
                    else "illustration",
                }
                for p in sorted(output.iterdir())
            ],
        },
    )
    print(json.dumps(read(output / "manifest.json")["checks"]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    build(args.root.resolve(), args.output)
