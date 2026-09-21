"""Run offline scorer controls without modifying the prepared task."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from types import ModuleType

import nibabel as nib
import numpy as np


def load_scorer(path: Path):
    # Execute the retained source without creating __pycache__ inside the task.
    # Control runs must not mutate the prepared bytes they are intended to test.
    module = ModuleType("ct_organ_score")
    code = compile(path.read_text(), str(path), "exec")
    exec(code, module.__dict__)
    return module


def save_like(data: np.ndarray, reference: nib.Nifti1Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    output = nib.Nifti1Image(data.astype(np.uint8), reference.affine, reference.header)
    output.set_qform(*reference.header.get_qform(coded=True))
    output.set_sform(*reference.header.get_sform(coded=True))
    nib.save(output, path)


def erode_once(mask: np.ndarray) -> np.ndarray:
    result = mask.copy()
    for axis in range(3):
        lower = np.zeros_like(mask)
        upper = np.zeros_like(mask)
        lower_slice = [slice(None)] * 3
        upper_slice = [slice(None)] * 3
        source_lower = [slice(None)] * 3
        source_upper = [slice(None)] * 3
        lower_slice[axis] = slice(1, None)
        source_lower[axis] = slice(None, -1)
        upper_slice[axis] = slice(None, -1)
        source_upper[axis] = slice(1, None)
        lower[tuple(lower_slice)] = mask[tuple(source_lower)]
        upper[tuple(upper_slice)] = mask[tuple(source_upper)]
        result &= lower & upper
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    task = args.task.resolve()
    workspace = args.output.resolve().parent / "ct-organ-scorer-controls"
    if workspace.exists():
        raise RuntimeError(f"control workspace already exists: {workspace}")
    workspace.mkdir(parents=True)

    labels_path = task / "tests/labels.json"
    labels = json.loads(labels_path.read_text())["labels"]
    names = [item["file"] for item in labels]
    reference_dir = task / "tests/reference"
    first = nib.load(reference_dir / names[0])
    scorer = load_scorer(task / "tests/score.py")

    cases: dict[str, Path] = {}
    oracle = workspace / "oracle"
    shutil.copytree(reference_dir, oracle)
    cases["oracle"] = oracle

    empty = workspace / "empty"
    empty.mkdir()
    for name in names:
        save_like(np.zeros(first.shape, dtype=np.uint8), first, empty / name)
    cases["empty"] = empty

    kidney_swap = workspace / "kidney-swap"
    shutil.copytree(reference_dir, kidney_swap)
    right = nib.load(reference_dir / "02.nii.gz")
    left = nib.load(reference_dir / "03.nii.gz")
    save_like(np.asanyarray(left.dataobj), first, kidney_swap / "02.nii.gz")
    save_like(np.asanyarray(right.dataobj), first, kidney_swap / "03.nii.gz")
    cases["kidney_swap"] = kidney_swap

    cyclic = workspace / "cyclic-permutation"
    cyclic.mkdir()
    for index, name in enumerate(names):
        source = reference_dir / names[(index + 1) % len(names)]
        shutil.copy2(source, cyclic / name)
    cases["cyclic_permutation"] = cyclic

    translated = workspace / "translated"
    translated.mkdir()
    for name in names:
        mask = np.asanyarray(nib.load(reference_dir / name).dataobj).astype(bool)
        shifted = np.zeros_like(mask)
        shifted[5:, :, :] = mask[:-5, :, :]
        save_like(shifted, first, translated / name)
    cases["translated_7_5mm"] = translated

    eroded = workspace / "eroded"
    eroded.mkdir()
    for name in names:
        mask = np.asanyarray(nib.load(reference_dir / name).dataobj).astype(bool)
        save_like(erode_once(mask), first, eroded / name)
    cases["eroded_one_voxel"] = eroded

    unknown = workspace / "unknown-file"
    shutil.copytree(reference_dir, unknown)
    save_like(np.zeros(first.shape, dtype=np.uint8), first, unknown / "11.nii.gz")
    cases["unknown_file"] = unknown

    nonbinary = workspace / "nonbinary"
    shutil.copytree(reference_dir, nonbinary)
    bad = np.asanyarray(nib.load(nonbinary / names[0]).dataobj).astype(np.uint8)
    bad.flat[0] = 2
    save_like(bad, first, nonbinary / names[0])
    cases["nonbinary"] = nonbinary

    wrong_grid = workspace / "wrong-grid"
    shutil.copytree(reference_dir, wrong_grid)
    smaller = np.zeros(tuple(value - 1 for value in first.shape), dtype=np.uint8)
    nib.save(nib.Nifti1Image(smaller, first.affine), wrong_grid / names[0])
    cases["wrong_grid"] = wrong_grid

    results = {name: scorer.score(path, reference_dir, labels_path) for name, path in cases.items()}
    missing = scorer.score(workspace / "does-not-exist", reference_dir, labels_path)
    results["missing_output"] = missing

    assert results["oracle"]["semantic_macro_dice"] == 1.0
    assert results["oracle"]["matched_macro_dice"] == 1.0
    assert results["empty"]["semantic_macro_dice"] == 0.0
    assert results["empty"]["identity_accuracy"] is None
    assert results["kidney_swap"]["foreground_dice"] == 1.0
    assert results["kidney_swap"]["matched_macro_dice"] == 1.0
    assert results["kidney_swap"]["semantic_macro_dice"] < 1.0
    assert results["cyclic_permutation"]["foreground_dice"] == 1.0
    assert results["cyclic_permutation"]["matched_macro_dice"] == 1.0
    assert results["cyclic_permutation"]["semantic_macro_dice"] == 0.0
    assert results["translated_7_5mm"]["matched_macro_dice"] < 1.0
    assert results["eroded_one_voxel"]["foreground_recall"] < 1.0
    for name in ("unknown_file", "nonbinary", "wrong_grid", "missing_output"):
        assert not results[name]["valid"]
        assert results[name]["semantic_macro_dice"] == 0.0

    args.output.write_text(json.dumps(results, indent=2) + "\n")
    print(
        json.dumps({key: value["semantic_macro_dice"] for key, value in results.items()}, indent=2)
    )


if __name__ == "__main__":
    main()
