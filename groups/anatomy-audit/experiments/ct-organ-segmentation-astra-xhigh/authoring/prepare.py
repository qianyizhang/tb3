"""Prepare the fixed CT-only organ task from retained source bytes."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from collections import deque
from datetime import datetime, timezone
from pathlib import Path

import nibabel as nib
import numpy as np


ROOT = Path(__file__).resolve().parents[5]
AUTHORING = Path(__file__).resolve().parent
EXPERIMENT = AUTHORING.parent
DEFAULT_BASE = ROOT / ".local/ct-organ-segmentation-astra-xhigh"
DEFAULT_TASK = DEFAULT_BASE / "task"
DEFAULT_SOURCE = ROOT / "runs/br004-v1/source/s1233"
SOURCE_CASE = "s1233"
SOURCE_DIR = EXPERIMENT / "source"
SOURCE_MANIFEST = SOURCE_DIR / "selected-source-manifest.json"

LABELS = [
    {
        "id": 1,
        "name": "spleen",
        "file": "01.nii.gz",
        "convention": "whole spleen",
    },
    {
        "id": 2,
        "name": "kidney_right",
        "file": "02.nii.gz",
        "convention": "patient-right renal organ; exclude separately classed cyst regions",
    },
    {
        "id": 3,
        "name": "kidney_left",
        "file": "03.nii.gz",
        "convention": "patient-left renal organ; exclude separately classed cyst regions",
    },
    {
        "id": 4,
        "name": "gallbladder",
        "file": "04.nii.gz",
        "convention": "whole organ envelope including contained lumen",
    },
    {
        "id": 5,
        "name": "liver",
        "file": "05.nii.gz",
        "convention": "whole liver; exclude adjacent organs and extrahepatic vessels",
    },
    {
        "id": 6,
        "name": "stomach",
        "file": "06.nii.gz",
        "convention": "whole organ envelope including contained lumen or contents",
    },
    {
        "id": 7,
        "name": "pancreas",
        "file": "07.nii.gz",
        "convention": "pancreatic tissue; exclude adjacent vessels, bowel and fat",
    },
    {
        "id": 8,
        "name": "adrenal_gland_right",
        "file": "08.nii.gz",
        "convention": "patient-right adrenal gland",
    },
    {
        "id": 9,
        "name": "adrenal_gland_left",
        "file": "09.nii.gz",
        "convention": "patient-left adrenal gland",
    },
    {
        "id": 10,
        "name": "duodenum",
        "file": "10.nii.gz",
        "convention": "whole duodenal envelope including contained lumen or contents; exclude adjacent bowel",
    },
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def scrubbed_image(source: nib.Nifti1Image, data: np.ndarray) -> nib.Nifti1Image:
    header = source.header.copy()
    for field in ("descrip", "aux_file", "intent_name", "db_name"):
        header[field] = b""
    header.extensions.clear()
    output = nib.Nifti1Image(data, source.affine, header)
    qform, qcode = source.header.get_qform(coded=True)
    sform, scode = source.header.get_sform(coded=True)
    output.set_qform(qform if qform is not None else source.affine, int(qcode))
    output.set_sform(sform if sform is not None else source.affine, int(scode))
    return output


def connected_components(mask: np.ndarray) -> list[int]:
    points = np.argwhere(mask)
    if not len(points):
        return []
    lower = points.min(axis=0)
    upper = points.max(axis=0) + 1
    slices = tuple(slice(int(lower[d]), int(upper[d])) for d in range(3))
    cropped = mask[slices]
    seen = np.zeros(cropped.shape, dtype=bool)
    sizes: list[int] = []
    for seed_array in np.argwhere(cropped):
        seed = tuple(int(value) for value in seed_array)
        if seen[seed]:
            continue
        queue: deque[tuple[int, int, int]] = deque([seed])
        seen[seed] = True
        size = 0
        while queue:
            x, y, z = queue.popleft()
            size += 1
            for dx, dy, dz in (
                (1, 0, 0),
                (-1, 0, 0),
                (0, 1, 0),
                (0, -1, 0),
                (0, 0, 1),
                (0, 0, -1),
            ):
                neighbor = (x + dx, y + dy, z + dz)
                if not (
                    0 <= neighbor[0] < cropped.shape[0]
                    and 0 <= neighbor[1] < cropped.shape[1]
                    and 0 <= neighbor[2] < cropped.shape[2]
                ):
                    continue
                if cropped[neighbor] and not seen[neighbor]:
                    seen[neighbor] = True
                    queue.append(neighbor)
        sizes.append(size)
    return sorted(sizes, reverse=True)


def verify_source_hashes(source: Path, manifest: dict[str, object]) -> None:
    expected = {item["path"]: item for item in manifest["files"]}
    relative_paths = [Path("ct.nii.gz")] + [
        Path("segmentations") / f"{item['name']}.nii.gz" for item in LABELS
    ]
    if set(expected) != {path.as_posix() for path in relative_paths}:
        raise RuntimeError("selected-source manifest does not contain exactly eleven inputs")
    for relative in relative_paths:
        path = source / relative
        item = expected[relative.as_posix()]
        if path.stat().st_size != item["bytes"]:
            raise RuntimeError(f"source size mismatch for {relative.as_posix()}")
        actual = sha256(path)
        if actual != item["sha256"]:
            raise RuntimeError(f"source hash mismatch for {relative.as_posix()}: {actual}")


def write_task_files(task: Path) -> None:
    instruction = """# Segment ten abdominal organs from CT

The CT volume is `/app/data/ct.nii.gz`. The finite target taxonomy, numeric output
filenames and whole-organ conventions are in `/app/data/labels.json`.

Create one binary NIfTI mask for each target under `/app/answer/masks/`, using the
exact filename declared for that target. Every mask must have exactly the CT shape
and affine and contain only values 0 and 1. Masks are independent and may overlap;
do not force each voxel into only one class. All visible anatomy outside the ten
target definitions remains unlabelled.

Right and left mean the patient's anatomical side. The affine maps voxel indices
to RAS physical coordinates: positive world x is right, positive y is anterior and
positive z is superior. Use the affine rather than display position to determine
side. The 1.5-unit source spacing is interpreted in millimetres.

For stomach, gallbladder and duodenum, segment the whole organ envelope including
the lumen or contents inside it, without extending into adjacent bowel. Kidney
masks cover the renal organ but exclude separately classed cyst regions. Pancreas
and adrenal masks exclude adjacent vessels, fat, bowel and kidney.

Also save `/app/answer/method.md` with your method, limitations and uncertainty.
You may inspect the CT and create scripts or intermediate files under `/app/work`.
External data, websites, pretrained segmentation weights, reference masks and
scoring feedback are unavailable. Save the best complete answer you can within
the two-hour ceiling; you may finish sooner.
"""
    (task / "instruction.md").write_text(instruction)
    (task / "task.toml").write_text(
        """version = "1.0"
artifacts = ["/app/answer", "/app/work"]
[metadata]
category = "medical-imaging"
[agent]
timeout_sec = 7200.0
[verifier]
timeout_sec = 600.0
environment_mode = "separate"
[verifier.environment]
docker_image = "tb3-ct-organ-evaluator:v1"
network_mode = "no-network"
cpus = 2
memory_mb = 8192
[environment]
docker_image = "tb3-ct-organ-solver:v1"
build_timeout_sec = 600.0
cpus = 4
memory_mb = 12288
storage_mb = 16384
gpus = 0
network_mode = "public"
"""
    )
    (task / "environment/Dockerfile").write_text(
        """FROM tb3-ct-organ-runtime:v1
WORKDIR /app
COPY data /app/data
RUN mkdir -p /app/answer/masks /app/work && chmod -R a-w /app/data
"""
    )
    (task / "environment/docker-compose.yaml").write_text(
        """services:
  main:
    networks: [isolated]
    cap_drop: [ALL]
    security_opt: [no-new-privileges:true]
    environment:
      HTTP_PROXY: http://transport:3128
      HTTPS_PROXY: http://transport:3128
      http_proxy: http://transport:3128
      https_proxy: http://transport:3128
      NO_PROXY: localhost,127.0.0.1
    depends_on: [transport]
  transport:
    image: tb3-ct-organ-transport:v1
    networks: [isolated, egress]
    read_only: true
    cap_drop: [ALL]
    security_opt: [no-new-privileges:true]
networks:
  isolated:
    internal: true
  egress: {}
"""
    )
    (task / "tests/Dockerfile").write_text(
        "FROM tb3-ct-organ-runtime:v1\nCOPY . /tests\nRUN mkdir -p /app/answer/masks /logs/verifier\n"
    )
    (task / "tests/test.sh").write_text("#!/bin/sh\nset -eu\npython /tests/score.py\n")
    (task / "solution/solve.sh").write_text(
        """#!/bin/sh
set -eu
mkdir -p /app/answer/masks
cp /solution/reference/*.nii.gz /app/answer/masks/
printf '%s\n' 'Exact evaluator reference copied by oracle control.' > /app/answer/method.md
"""
    )
    for path in (task / "tests/test.sh", task / "solution/solve.sh"):
        path.chmod(0o755)


def prepare(source: Path, task: Path) -> dict[str, object]:
    if task.exists() and any(task.iterdir()):
        raise RuntimeError(f"destination is not empty: {task}")
    for relative in (
        "environment/data",
        "tests/reference",
        "solution/reference",
    ):
        (task / relative).mkdir(parents=True, exist_ok=True)

    source_manifest = json.loads(SOURCE_MANIFEST.read_text())
    if (
        source_manifest.get("record") != "10047263"
        or source_manifest.get("version") != "2.0.1"
        or source_manifest.get("selected_member") != SOURCE_CASE
    ):
        raise RuntimeError("unexpected source release")
    verify_source_hashes(source, source_manifest)

    source_ct = nib.load(source / "ct.nii.gz")
    ct_data = np.asanyarray(source_ct.dataobj)
    if ct_data.shape != (265, 265, 401):
        raise RuntimeError(f"unexpected CT shape: {ct_data.shape}")
    if not np.array_equal(np.asarray(source_ct.header.get_zooms()[:3]), [1.5, 1.5, 1.5]):
        raise RuntimeError("unexpected CT spacing")
    if nib.aff2axcodes(source_ct.affine) != ("R", "A", "S"):
        raise RuntimeError("unexpected CT orientation")
    solver_ct_path = task / "environment/data/ct.nii.gz"
    nib.save(scrubbed_image(source_ct, ct_data), solver_ct_path)
    solver_ct = nib.load(solver_ct_path)
    if not np.array_equal(ct_data, np.asanyarray(solver_ct.dataobj)):
        raise RuntimeError("solver CT voxel data changed")
    if not np.array_equal(source_ct.affine, solver_ct.affine):
        raise RuntimeError("solver CT affine changed")
    if source_ct.header["qform_code"] != solver_ct.header["qform_code"]:
        raise RuntimeError("solver CT qform code changed")
    if source_ct.header["sform_code"] != solver_ct.header["sform_code"]:
        raise RuntimeError("solver CT sform code changed")

    label_config = {
        "schema_version": 1,
        "output": "independent binary NIfTI masks on the input CT grid",
        "background": "all anatomy outside the ten target definitions",
        "labels": LABELS,
    }
    label_bytes = json.dumps(label_config, indent=2) + "\n"
    (task / "environment/data/labels.json").write_text(label_bytes)
    (task / "tests/labels.json").write_text(label_bytes)

    source_masks: list[np.ndarray] = []
    mask_qc: list[dict[str, object]] = []
    shape = np.asarray(source_ct.shape)
    for item in LABELS:
        source_path = source / "segmentations" / f"{item['name']}.nii.gz"
        source_mask_image = nib.load(source_path)
        if source_mask_image.shape != source_ct.shape:
            raise RuntimeError(f"shape mismatch for {item['name']}")
        if not np.array_equal(source_mask_image.affine, source_ct.affine):
            raise RuntimeError(f"affine mismatch for {item['name']}")
        values = np.asanyarray(source_mask_image.dataobj)
        if not set(np.unique(values).tolist()).issubset({0, 1}):
            raise RuntimeError(f"nonbinary source mask for {item['name']}")
        mask = values.astype(bool)
        points = np.argwhere(mask)
        if not len(points):
            raise RuntimeError(f"empty source mask for {item['name']}")
        lower = points.min(axis=0)
        upper = points.max(axis=0)
        touches_boundary = bool(np.any(lower == 0) or np.any(upper == shape - 1))
        if touches_boundary:
            raise RuntimeError(f"source mask touches image boundary: {item['name']}")
        component_sizes = connected_components(mask)
        if len(component_sizes) != 1:
            raise RuntimeError(f"source mask is not 6-connected: {item['name']}")
        source_masks.append(mask)
        mask_qc.append(
            {
                "id": item["id"],
                "name": item["name"],
                "source_path": source_path.relative_to(source).as_posix(),
                "source_sha256": sha256(source_path),
                "voxels": int(mask.sum()),
                "volume_ml": float(mask.sum() * 1.5**3 / 1000.0),
                "bbox_min_ijk": lower.tolist(),
                "bbox_max_ijk": upper.tolist(),
                "touches_boundary": False,
                "components_6": 1,
            }
        )
        output_image = scrubbed_image(source_mask_image, mask.astype(np.uint8))
        for relative in ("tests/reference", "solution/reference"):
            nib.save(output_image, task / relative / item["file"])

    stacked = np.stack(source_masks, axis=0)
    overlap_voxels = int(np.count_nonzero(stacked.sum(axis=0) > 1))
    if overlap_voxels != 57:
        raise RuntimeError(f"unexpected inter-mask overlap count: {overlap_voxels}")

    shutil.copy2(AUTHORING / "score.py", task / "tests/score.py")
    write_task_files(task)

    base = task.parent
    runtime = base / "runtime"
    runtime.mkdir(parents=True, exist_ok=True)
    shutil.copy2(AUTHORING / "proxy.py", runtime / "proxy.py")
    shutil.copy2(AUTHORING / "preflight.py", runtime / "preflight.py")
    (runtime / "Proxy.Dockerfile").write_text(
        'FROM tb3-ct-organ-runtime:v1\nCOPY proxy.py /proxy.py\nCMD ["python", "-u", "/proxy.py"]\n'
    )

    license_dir = base / "source-licenses"
    license_dir.mkdir(parents=True, exist_ok=True)
    copied_licenses = {}
    for license_key, license_name in (
        ("image_data", "DATA-LICENSE.txt"),
        ("labels", "LABEL-LICENSE.txt"),
    ):
        license_record = source_manifest["licenses"][license_key]
        source_license = SOURCE_DIR / license_record["file"]
        if source_license.stat().st_size != license_record["bytes"]:
            raise RuntimeError(f"tracked license size mismatch: {license_name}")
        license_hash = sha256(source_license)
        if license_hash != license_record["sha256"]:
            raise RuntimeError(f"tracked license hash mismatch: {license_name}")
        shutil.copy2(source_license, license_dir / license_name)
        copied_licenses[license_name] = license_hash

    files = {}
    for path in sorted(file for file in task.rglob("*") if file.is_file()):
        files[path.relative_to(task).as_posix()] = sha256(path)
    receipt = {
        "schema_version": 1,
        "experiment_id": EXPERIMENT.name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source": {
            "dataset": "TotalSegmentator public CT dataset small subset",
            "record": source_manifest["record"],
            "version": source_manifest["version"],
            "archive_url": source_manifest["archive"]["url"],
            "archive_md5": source_manifest["archive"]["md5"],
            "selected_member": SOURCE_CASE,
            "manifest": SOURCE_MANIFEST.relative_to(ROOT).as_posix(),
            "manifest_sha256": sha256(SOURCE_MANIFEST),
            "ct_sha256": sha256(source / "ct.nii.gz"),
            "data_license": "CC BY 4.0",
            "label_license": "Apache 2.0",
            "license_sha256": copied_licenses,
        },
        "selection": {
            "selected_before_model_result": True,
            "reason": "complete ten-label scope, full field of view, validation split, plausible triplanar author QC",
            "rejected_outlier": "s0915: unusually small duodenum raised reference-completeness concern",
            "clinical_adjudication": False,
        },
        "ct": {
            "shape": list(source_ct.shape),
            "zooms": [float(value) for value in source_ct.header.get_zooms()[:3]],
            "orientation": list(nib.aff2axcodes(source_ct.affine)),
            "source_qform_code": int(source_ct.header["qform_code"]),
            "source_sform_code": int(source_ct.header["sform_code"]),
            "solver_sha256": sha256(solver_ct_path),
            "voxels_exactly_equal": True,
            "affine_exactly_equal": True,
            "metadata_fields_removed": [
                "descrip",
                "aux_file",
                "intent_name",
                "db_name",
                "extensions",
            ],
        },
        "reference": {
            "representation": "ten independent binary NIfTI masks",
            "masks": mask_qc,
            "inter_mask_overlap_voxels": overlap_voxels,
            "source_masks_unchanged": True,
        },
        "isolation": {
            "solver_files": ["data/ct.nii.gz", "data/labels.json"],
            "private_reference_only_in_evaluator_and_oracle": True,
            "pretrained_segmenter_packages_or_weights_included": False,
        },
        "task_path": str(task),
        "task_files": files,
    }
    (base / "preparation-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_TASK)
    args = parser.parse_args()
    receipt = prepare(args.source.resolve(), args.output.resolve())
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
