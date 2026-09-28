"""Read retained MR fixtures and replay saved code without regenerating frozen files."""

import argparse
import base64
import copy
import hashlib
import importlib.util
import itertools
import json
import platform
import sys
from pathlib import Path

import numpy as np
import pydicom
from pydicom.dataset import Dataset, FileMetaDataset
from pydicom.uid import ExplicitVRLittleEndian

TASK = Path("probes/mr-frame-association")
JOBS = {
    "model": Path("runs/mr-terra-high-v1-20260914/mr-frame-association__5L3qSjg"),
    "oracle": Path("runs/mr-oracle-v1-20260914/mr-frame-association__rRCx2Ei"),
    "starter": Path("runs/mr-nop-v1-20260914/mr-frame-association__SQN2Xkd"),
}


def read(path):
    return json.loads(path.read_text())


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def load_code(path, name):
    # Only the inspected answer/reference/check modules are loaded, never authoring.
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def dataset(value):
    ds = Dataset.from_json(value)
    ds.file_meta = FileMetaDataset()
    ds.file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
    return ds


def reconstructed_truth(seed, simple):
    """Independent in-memory reproduction of the pinned pre-serialization recipe."""
    rng = np.random.default_rng(seed)
    nt, ne, nz = (2, 2, 3) if simple else tuple(rng.integers([1, 1, 2], [4, 4, 6]))
    nr, nc = (3, 4) if simple else tuple(rng.integers([3, 4], [8, 9]))
    basis = np.eye(3) if simple else np.linalg.qr(rng.normal(size=(3, 3)))[0]
    spacing = np.ones(2) if simple else rng.uniform(0.4, 2.5, 2)
    dz = 2.0 if simple else float(rng.uniform(1, 4))
    affine = np.eye(4)
    affine[:3, 3] = rng.uniform(-80, 80, 3)
    affine[:3, 0] = basis[:, 0] * spacing[1]
    affine[:3, 1] = basis[:, 1] * spacing[0]
    affine[:3, 2] = np.cross(basis[:, 0], basis[:, 1]) * dz
    pixels = rng.integers(-3000, 3000, (nt, ne, nz, nr, nc), dtype=np.int16)
    times = sorted(rng.choice(np.arange(2, 40), nt, replace=False).tolist())
    echoes = sorted((rng.choice(np.arange(1, 60), ne, replace=False) * 1.25).tolist())
    return {"pixels": pixels, "affine_lps": affine, "temporal_indices": times, "echo_ms": echoes}


def plain(value):
    return {k: np.asarray(v).tolist() for k, v in value.items()}


def inspect_case(case):
    value, truth = case["input"], case["expected"]
    ds = dataset(value)
    groups = ds.PerFrameFunctionalGroupsSequence
    shared = ds.SharedFunctionalGroupsSequence[0]
    geometry = shared if hasattr(shared, "PlaneOrientationSequence") else groups[0]
    iop = np.asarray(geometry.PlaneOrientationSequence[0].ImageOrientationPatient, float)
    spacing = np.asarray(geometry.PixelMeasuresSequence[0].PixelSpacing, float)
    normal = np.cross(iop[:3], iop[3:])
    positions = np.asarray([g.PlanePositionSequence[0].ImagePositionPatient for g in groups], float)
    levels = sorted(set((positions @ normal).tolist()))
    raw = np.frombuffer(base64.b64decode(value["7FE00010"]["InlineBinary"]), dtype="<i2")
    pixels = raw.reshape(len(groups), ds.Rows, ds.Columns)
    assert np.array_equal(pixels, ds.pixel_array)
    wanted = np.asarray(truth["pixels"], dtype=np.int16)
    seen, rows, ordinal_maps = set(), [], [{} for _ in ds.DimensionIndexSequence]
    for i, group in enumerate(groups):
        assert not set(shared.keys()) & set(group.keys())
        content = group.FrameContentSequence[0]
        t = int(content.TemporalPositionIndex)
        echo = float(group.MREchoSequence[0].EffectiveEchoTime)
        projection = float(positions[i] @ normal)
        target = [
            truth["temporal_indices"].index(t),
            truth["echo_ms"].index(echo),
            levels.index(projection),
        ]
        assert tuple(target) not in seen
        seen.add(tuple(target))
        assert np.array_equal(pixels[i], wanted[tuple(target)])
        expected_position = np.asarray(truth["affine_lps"]) @ [0, 0, target[2], 1]
        assert np.max(abs(positions[i] - expected_position[:3])) < 1e-10
        if hasattr(group, "PlaneOrientationSequence"):
            assert np.array_equal(group.PlaneOrientationSequence[0].ImageOrientationPatient, iop)
            assert np.array_equal(group.PixelMeasuresSequence[0].PixelSpacing, spacing)
        for j, desc in enumerate(ds.DimensionIndexSequence):
            container = group if desc.FunctionalGroupPointer in group else shared
            actual = container[desc.FunctionalGroupPointer][0][desc.DimensionIndexPointer].value
            ordinal = int(content.DimensionIndexValues[j])
            assert ordinal_maps[j].setdefault(ordinal, float(actual)) == float(actual)
        rows.append(
            {
                "storage": i,
                "target": target,
                "time": t,
                "echo_ms": echo,
                "projection_mm": projection,
                "position_lps": positions[i].tolist(),
                "ordinals": list(content.DimensionIndexValues),
                "pixels": pixels[i].tolist(),
            }
        )
    assert len(seen) == int(np.prod(wanted.shape[:3]))
    for mapping in ordinal_maps:
        assert sorted(mapping) == list(range(1, len(mapping) + 1))
        assert len(set(mapping.values())) == len(mapping)
    return {
        "name": case["name"],
        "shape": list(wanted.shape),
        "rows": rows,
        "temporal_indices": truth["temporal_indices"],
        "echo_ms": truth["echo_ms"],
        "orientation": iop.tolist(),
        "spacing_row_column_mm": spacing.tolist(),
        "normal": normal.tolist(),
        "levels_mm": levels,
        "descriptors": [
            {
                "tag": str(d.DimensionIndexPointer),
                "keyword": pydicom.datadict.keyword_for_tag(d.DimensionIndexPointer),
                "group": str(d.FunctionalGroupPointer),
                "ordinal_to_actual": ordinal_maps[i],
            }
            for i, d in enumerate(ds.DimensionIndexSequence)
        ],
        "geometry_placement": "shared" if geometry is shared else "per-frame",
    }


def landmark_error(expected, result):
    _, _, nz, nr, nc = np.shape(expected["pixels"])
    points = np.array(
        [[c, r, z, 1] for c, r, z in itertools.product((0, nc - 1), (0, nr - 1), (0, nz - 1))]
    )
    delta = points @ (np.asarray(result["affine_lps"]) - expected["affine_lps"]).T
    return float(np.max(np.linalg.norm(delta[:, :3], axis=1)))


def audit(root, output, work):
    if output.exists() or work.exists():
        raise FileExistsError("Use fresh audit and work destinations")
    work.mkdir(parents=True)
    pins = {}

    def pin(path, expected=None):
        digest = sha(root / path)
        if expected:
            assert digest == expected, path
        pins[str(path)] = digest

    freeze_path = Path("docs/evidence/mr-pilot-freeze.json")
    pin(freeze_path)
    freeze = read(root / freeze_path)
    for name, digest in freeze["files"].items():
        pin(TASK / name, digest)
    for path in [
        "docs/evidence/mr-trial-summary.json",
        "datasets/receipts/synthetic-mr-fixtures.json",
        "scripts/audit_mri_importer_evidence.py",
    ]:
        pin(Path(path))
    private = read(root / TASK / "tests/cases.json")
    public = read(root / TASK / "environment/examples.json")
    assert len(private) == 36 and len(public) == 4
    inspected = [inspect_case(c) for c in public + private]
    sample_count = 0
    for cases, stride, seeds in [(private, 3, range(3101, 3113)), (public, 2, [101, 202])]:
        for i, seed in enumerate(seeds):
            rebuilt = reconstructed_truth(seed, i == 0)
            for case in cases[i * stride : (i + 1) * stride]:
                for key, wanted in case["expected"].items():
                    assert np.array_equal(rebuilt[key], wanted), (case["name"], key)
                sample_count += int(np.size(rebuilt["pixels"]))
    grade = load_code(root / TASK / "tests/verifier.py", "mr_grade")
    results, model = {}, None
    for name, job in JOBS.items():
        for rel in [
            "result.json",
            "verifier/test-stdout.txt",
            "verifier/reward.txt",
            "artifacts/app/answer/solution.py",
        ]:
            pin(job / rel)
        result = read(root / job / "result.json")
        assert result["task_checksum"] == freeze["controls"][0]["task_checksum"]
        assert result["exception_info"] is None
        module = load_code(root / job / "artifacts/app/answer/solution.py", "mr_" + name)
        if name == "model":
            model = module
        passed, failures, outputs, errors = [], [], [], []
        for case in private:
            try:
                answer = plain(module.reconstruct(dataset(case["input"])))
            except Exception as exc:
                answer = {"error": f"{type(exc).__name__}: {exc}"}
            outputs.append(answer)
            try:
                grade.check(case["expected"], answer)
                passed.append(case["name"])
                errors.append(landmark_error(case["expected"], answer))
            except Exception as exc:
                failures.append(
                    f"{case['name']}: {type(exc).__name__}: {exc}; {answer.get('error', '')}"
                )
        fresh = {"passed": passed, "failures": failures}
        saved = json.loads((root / job / "verifier/test-stdout.txt").read_text().splitlines()[0])
        assert fresh == saved, name
        (work / f"{name}-outputs.json").write_text(json.dumps(outputs) + "\n")
        results[name] = {
            "job": str(job),
            "exact_report_replay": True,
            "passed": len(passed),
            "total": 36,
            "report": saved,
            "max_passed_landmark_error_mm": max(errors),
            "original_reward": float((root / job / "verifier/reward.txt").read_text()),
        }
    diagnostics = {}
    for mode in ["spacing-swap", "logical-echo"]:
        passed, errors = [], []
        for case in private:
            answer = copy.deepcopy(case["expected"])
            if mode == "spacing-swap":
                affine = np.asarray(answer["affine_lps"], float)
                sx, sy = np.linalg.norm(affine[:3, 0]), np.linalg.norm(affine[:3, 1])
                affine[:3, 0] *= sy / sx
                affine[:3, 1] *= sx / sy
                answer["affine_lps"] = affine.tolist()
            else:
                answer["echo_ms"] = list(range(1, len(answer["echo_ms"]) + 1))
            try:
                grade.check(case["expected"], answer)
                passed.append(case["name"])
            except Exception as exc:
                errors.append(str(exc))
        diagnostics[mode] = {"passed": passed, "failures": errors}
    assert len(diagnostics["spacing-swap"]["passed"]) == 3
    assert not diagnostics["logical-echo"]["passed"]
    # Reproduce the trace's public macro relocation without changing any source.
    relocated = copy.deepcopy(public[0]["input"])
    shared = relocated["52009229"]["Value"][0]
    for frame in relocated["52009230"]["Value"]:
        for tag in ["00209116", "00289110"]:
            frame[tag] = copy.deepcopy(shared[tag])
    for tag in ["00209116", "00289110"]:
        del shared[tag]
    relocated_answer = plain(model.reconstruct(dataset(relocated)))
    grade.check(public[0]["expected"], relocated_answer)
    relocation = {
        "exact_dictionary_equal": relocated_answer == public[0]["expected"],
        "pixel_equal": np.array_equal(relocated_answer["pixels"], public[0]["expected"]["pixels"]),
        "max_affine_entry_error": float(
            np.max(
                abs(np.array(relocated_answer["affine_lps"]) - public[0]["expected"]["affine_lps"])
            )
        ),
        "max_landmark_error_mm": landmark_error(public[0]["expected"], relocated_answer),
        "frozen_numerical_check": "pass",
    }
    trace = JOBS["model"] / "agent/trajectory.json"
    pin(trace)
    public_answers = [plain(model.reconstruct(dataset(c["input"]))) for c in public]
    for case, answer in zip(public, public_answers, strict=True):
        grade.check(case["expected"], answer)
    data = {
        "schema": 1,
        "scope": "Retained synthetic importer; source audit and local saved-code replay, no fresh model execution.",
        "runtime": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "pydicom": pydicom.__version__,
            "frozen_pydicom": "3.0.1",
            "note": "Local replay uses existing pydicom 3.0.2; exact reports reproduced. No runtime installation or container-equivalence claim.",
        },
        "source_pins": pins,
        "frozen_files_verified": len(freeze["files"]),
        "fixture_checks": {
            "private_acquisitions": 12,
            "private_encodings": 36,
            "public_acquisitions": 2,
            "public_encodings": 4,
            "sample_values_exact": sample_count,
            "pre_serialization_truth_exact": True,
            "raw_bytes_and_pydicom_exact": True,
            "complete_unique_association": True,
            "ordinal_bijections": True,
            "private_frame_counts": [len(c["rows"]) for c in inspected[4:]],
        },
        "results": results,
        "diagnostics": diagnostics,
        "public_relocation": relocation,
        "public_cases": inspected[:4],
        "public_outputs": public_answers,
        "private_shapes": [
            {"name": c["name"], "shape": np.shape(c["expected"]["pixels"])} for c in private[::3]
        ],
        "trace": {
            "path": str(trace),
            "public_checks_step": 13,
            "tolerance_edit_step": 15,
            "exact_comparison_failure_step": 16,
            "numerical_difference_step": 17,
            "final_step": 19,
            "original_agent_seconds": 150.284386,
        },
        "fitness": {
            "reference": "Original generated canonical arrays before serialization; all 40 exact reconstructions reproduced in memory without executing historical authoring code.",
            "context": "Complete actual time/echo and plane geometry supplied with every frame; private references withheld, four public expected outputs supplied.",
            "specification": "Exact array shape, samples and temporal labels; echo <=1e-9 ms; eight corner landmarks <=1e-5 mm; finite affine with exact homogeneous row.",
            "boundary": "Documented synthetic reconstruction profile, not complete Enhanced MR IOD conformance, clinical interpretation, compression, missing frames or multiple stacks.",
            "comparison": "Matched three encodings per acquisition; controls and model share retained task checksum. Encodings are correlated, not 36 independent acquisitions.",
            "support": "One normal Terra/high pass does not support the proposed frame-association failure hypothesis; parked by user, not reopened by this explanation.",
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(data, indent=2, default=lambda x: x.item()) + "\n")
    print(
        json.dumps(
            {
                "audit": str(output),
                "frozen_files": len(freeze["files"]),
                "samples": sample_count,
                "results": {k: v["passed"] for k, v in results.items()},
                "relocation": relocation,
            }
        )
    )


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    args = parser.parse_args()
    audit(Path.cwd(), args.output, args.work)
