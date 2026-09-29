"""Build source-pinned, display-only ISLES22 teaching assets; no ReX code is executed."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import struct
import zlib
from pathlib import Path

import numpy as np

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "workbench.toml").is_file())
SOURCE_ROOT = Path(".local/explainers/core-20260929/rex-dentex-isles-source/isles22")
RECEIPT = Path("presentation/external-tasks/sources/rexmle-isles22-resolution.json")
PACK_ID = "retained-rex-isles22-v1"
CASE = "sub-strokecase0186_ses-0001"
SAMPLES = {
    "dwi": [0, 3, 6, 9, 12, 15, 18, 21, 24],
    "adc": [0, 3, 6, 9, 12, 15, 18, 21, 24],
    "flair": [0, 3, 6, 9, 12, 15, 18, 21, 23],
    "mask": [0, 3, 6, 9, 12, 15, 18, 21, 24],
}
FILES = {
    "dwi": f"{CASE}_dwi.nii.gz",
    "adc": f"{CASE}_adc.nii.gz",
    "flair": f"{CASE}_FLAIR.nii.gz",
    "mask": f"{CASE}_msk.nii.gz",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n")


def read_nifti(path: Path):
    raw = gzip.decompress(path.read_bytes())
    if struct.unpack_from("<i", raw, 0)[0] != 348 or raw[344:348] != b"n+1\0":
        raise ValueError(f"Unsupported NIfTI header: {path}")
    dims = struct.unpack_from("<8h", raw, 40)
    if dims[0] != 3 or struct.unpack_from("<hh", raw, 70) != (4, 16):
        raise ValueError(f"Expected 3D int16 NIfTI: {path}")
    shape = tuple(dims[1:4])
    offset, slope, intercept = struct.unpack_from("<fff", raw, 108)
    affine = [list(struct.unpack_from("<4f", raw, 280 + 16 * i)) for i in range(3)]
    affine.append([0.0, 0.0, 0.0, 1.0])
    spacing = list(struct.unpack_from("<3f", raw, 80))
    array = np.frombuffer(raw, dtype="<i2", count=int(np.prod(shape)), offset=int(offset)).reshape(
        shape, order="F"
    )
    scaled = array.astype(np.float64) * (slope if slope else 1.0) + intercept
    return scaled, {
        "shape_ijk": shape,
        "spacing_ijk_mm": spacing,
        "affine_ijk_to_ras_mm": affine,
        "native_axis_codes": ["L", "A", "S"],
        "nifti_scaling": [slope, intercept],
        "source_file": path.name,
        "source_sha256": sha(path),
    }


def png(path: Path, width: int, height: int, pixels: bytes, channels: int) -> None:
    color_type = 0 if channels == 1 else 6

    def chunk(tag: bytes, body: bytes) -> bytes:
        return (
            struct.pack(">I", len(body))
            + tag
            + body
            + struct.pack(">I", zlib.crc32(tag + body) & 0xFFFFFFFF)
        )

    rows = b"".join(
        b"\0" + pixels[y * width * channels : (y + 1) * width * channels] for y in range(height)
    )
    data = b"\x89PNG\r\n\x1a\n" + chunk(
        b"IHDR", struct.pack(">IIBBBBB", width, height, 8, color_type, 0, 0, 0)
    )
    data += chunk(b"IDAT", zlib.compress(rows, 9)) + chunk(b"IEND", b"")
    path.write_bytes(data)


def world_at(meta: dict, i: float, j: float, k: int) -> list[float]:
    affine = np.asarray(meta["affine_ijk_to_ras_mm"])
    return [round(float(x), 3) for x in (affine @ np.asarray([i, j, k, 1.0]))[:3]]


def build(repo_root: Path, source_root: Path, receipt_path: Path, output: Path) -> None:
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite existing output: {output}")
    receipt = json.loads(receipt_path.read_text())
    if (
        receipt.get("entry_id") != "rexmle-isles22"
        or receipt.get("illustration_basis") != "source-derived"
    ):
        raise ValueError("Wrong ISLES22 source receipt")
    if any(not a.get("attempted_at") for a in receipt["attempts"]):
        raise ValueError("Source attempt lacks timestamp")
    pins = receipt["selected_case"]["sha256"]
    arrays, geometry, sources = {}, {}, {}
    for modality, name in FILES.items():
        source = source_root / "case-0186" / name
        if sha(source) != pins[modality]:
            raise ValueError(f"Changed native {modality} source")
        arrays[modality], geometry[modality] = read_nifti(source)
        sources[str(source.relative_to(repo_root))] = pins[modality]
    for modality in ("adc", "mask"):
        if geometry[modality]["shape_ijk"] != geometry["dwi"]["shape_ijk"] or not np.allclose(
            geometry[modality]["affine_ijk_to_ras_mm"],
            geometry["dwi"]["affine_ijk_to_ras_mm"],
            atol=1e-5,
        ):
            raise ValueError(f"{modality} does not align with DWI")
    if geometry["flair"]["shape_ijk"] != (224, 256, 24) or geometry["dwi"]["shape_ijk"] != (
        128,
        128,
        25,
    ):
        raise ValueError("Unexpected source grids")
    binary = np.rint(arrays["mask"]).astype(np.uint8)
    if set(np.unique(binary)) != {0, 1} or int(binary.sum()) != 718:
        raise ValueError("Changed private label content")
    geometry["mask"]["role"] = "private-reference"
    sources[str(RECEIPT)] = sha(receipt_path)
    adapter_root = (
        repo_root
        / ".local/explainers/core-20260929/rex-dentex-isles-source/pinned/rex-mle/rexmle/challenges/isles22"
    )
    for name, expected in receipt["pinned_adapter_files"].items():
        adapter = adapter_root / name
        if sha(adapter) != expected:
            raise ValueError(f"Changed pinned ReX adapter {name}")
        sources[str(adapter.relative_to(repo_root))] = expected
    output.mkdir(parents=True)
    (output / "images").mkdir()
    assets = []
    modalities = {}
    for modality in ("dwi", "adc", "flair"):
        array, meta = arrays[modality], geometry[modality]
        nz = array[np.isfinite(array) & (array != 0)]
        lo, hi = [float(x) for x in np.percentile(nz, [1, 99])]
        if hi <= lo:
            raise ValueError(f"Invalid {modality} window")
        samples = []
        for n, k in enumerate(SAMPLES[modality]):
            # Display x=i, y=(ny-1-j); no silent cross-modality resampling.
            plane = array[:, :, k].T[::-1, :]
            gray = np.rint(np.clip((plane - lo) / (hi - lo), 0, 1) * 255).astype(np.uint8)
            name = f"images/{modality}-{n:02d}.png"
            png(output / name, gray.shape[1], gray.shape[0], gray.tobytes(), 1)
            assets.append(name)
            samples.append(
                {
                    "image": name,
                    "native_k_zero_based": k,
                    "center_ras_mm": world_at(
                        meta, (gray.shape[1] - 1) / 2, (gray.shape[0] - 1) / 2, k
                    ),
                    "shape_xy_pixels": [gray.shape[1], gray.shape[0]],
                }
            )
        modalities[modality] = {
            **meta,
            "sample_rule": "fixed native k indices, no interpolation or cross-grid resampling",
            "display_window_scaled_native_values": [round(lo, 6), round(hi, 6)],
            "display_mapping": "grayscale clamp((scaled-lo)/(hi-lo)); PNG x=i, y=ny-1-j",
            "samples": samples,
        }
    ref_samples = []
    for n, k in enumerate(SAMPLES["mask"]):
        plane = binary[:, :, k].T[::-1, :]
        rgba = np.zeros((plane.shape[0], plane.shape[1], 4), dtype=np.uint8)
        rgba[plane > 0] = [255, 190, 75, 190]
        name = f"images/reference-mask-{n:02d}.png"
        png(output / name, plane.shape[1], plane.shape[0], rgba.tobytes(), 4)
        assets.append(name)
        ref_samples.append(
            {"image": name, "native_k_zero_based": k, "positive_voxels_in_slice": int(plane.sum())}
        )
    source = {
        "frame": "ISLES22-native-NIfTI-RAS",
        "units": "mm",
        "case_id": "sub-strokecase0186",
        "source_case_id": CASE,
        "source_role": "public ReX test inputs; source masks private in ReX staging",
        "modalities": modalities,
        "split": {
            "complete_official_cases": 250,
            "train": 200,
            "test": 50,
            "rule": "sorted case IDs; sklearn train_test_split(test_size=0.2,random_state=42,shuffle=True)",
            "selected_case_partition": "test; statically reproduced, preparer not executed",
        },
        "cross_grid_resampling": False,
    }
    answer = {
        "status": "not-retained",
        "agent_prediction": None,
        "submission_csv": None,
        "score": None,
        "required_csv_header": ["case_id", "predicted_mask_path"],
        "illustrative_row": ["sub-strokecase0186", "predictions/sub-strokecase0186_pred.nii.gz"],
        "mask_contract": "binary NIfTI on DWI/ADC 128x128x25 grid with corresponding affine",
    }
    reference = {
        "role": "reader-only private ReX test mask; not agent input",
        "native_grid_matches": "DWI and ADC, not FLAIR",
        "source_file": FILES["mask"],
        "source_sha256": pins["mask"],
        "positive_voxels": 718,
        "total_voxels": 409600,
        "samples": ref_samples,
        "prediction_or_score": None,
    }
    dump(output / "source.json", source)
    dump(output / "output.json", answer)
    dump(output / "reference.json", reference)
    (output / "NOTICE.md").write_text(
        "# ISLES22 local teaching pack\n\nExact selected source case from official ISLES-2022 v2.3.1, "
        "https://zenodo.org/records/7960856, CC-BY-4.0. Display PNGs are fixed-window derivatives "
        "of source NIfTI volumes. DWI/ADC and private mask share a grid; FLAIR does not. PNG x=i and "
        "y=ny-1-j; native affines and source hashes are in source.json. The mask PNGs and reference.json "
        "are reader-only and must not mount before explicit reveal. No model, grader, or ReX preparer ran.\n"
    )
    assets += ["source.json", "output.json", "reference.json", "NOTICE.md"]
    manifest = {
        "schema": 1,
        "id": PACK_ID,
        "frame": "ISLES22-native-NIfTI-RAS",
        "units": "mm",
        "license": "CC-BY-4.0",
        "label_license": "CC-BY-4.0",
        "reference_policy": "reader-reference-reveal",
        "source_class": "source-derived-teaching",
        "illustration_basis": "source-derived",
        "sources": sources,
        "checks": {
            "native_case_recovered": True,
            "dwi_adc_mask_same_grid": True,
            "flair_different_grid": True,
            "agent_prediction_retained": False,
            "sampled_slices_per_modality": 9,
        },
        "assets": [
            {
                "file": name,
                "bytes": (output / name).stat().st_size,
                "sha256": sha(output / name),
                "provenance": "source-derived-teaching",
                "role": "reader-reference-reveal"
                if name == "reference.json" or name.startswith("images/reference-mask-")
                else "illustration",
            }
            for name in assets
        ],
    }
    dump(output / "manifest.json", manifest)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--repo-root", type=Path, default=ROOT)
    p.add_argument("--source-root", type=Path)
    p.add_argument("--receipt", type=Path)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    root = a.repo_root.resolve()
    build(
        root,
        (a.source_root or root / SOURCE_ROOT).resolve(),
        (a.receipt or root / RECEIPT).resolve(),
        a.output.resolve(),
    )


if __name__ == "__main__":
    main()
