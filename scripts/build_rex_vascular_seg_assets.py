"""Build four source-derived ReX vascular teaching packs; never run a ReX adapter."""

from __future__ import annotations

import argparse
import colorsys
import gzip
import hashlib
import json
import re
import struct
import zlib
from pathlib import Path

import numpy as np

ENTRIES = {
    "rexmle-seg-a": (
        "rex-vascular-seg-a",
        "retained-rex-seg-a-v1",
        "SEG.A-native-NRRD-LPS",
        "CC-BY-4.0",
        "no-reference-assets",
    ),
    "rexmle-topbrain-track1": (
        "rex-vascular-topbrain-ct",
        "retained-rex-topbrain-ct-v1",
        "TopBrain2025-native-NIfTI-RAS",
        "LicenseRef-TopBrain2025-noncommercial",
        "no-reference-assets",
    ),
    "rexmle-topbrain-track2": (
        "rex-vascular-topbrain-mr",
        "retained-rex-topbrain-mr-v1",
        "TopBrain2025-native-NIfTI-RAS",
        "LicenseRef-TopBrain2025-noncommercial",
        "no-reference-assets",
    ),
    "rexmle-topcow-track2-task1": (
        "rex-vascular-topcow-mr-seg",
        "retained-rex-topcow-mr-seg-v1",
        "TopCoW2024-native-NIfTI-RAS",
        "LicenseRef-TopCoW2024-noncommercial",
        "reader-reference-reveal",
    ),
}


def root_default() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "pyproject.toml").is_file() and (parent / "src/tb3_medical").is_dir():
            return parent
    raise RuntimeError("Pass --repo-root when running the staged script before integration")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path: Path, record: object) -> None:
    path.write_text(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")


def png(path: Path, array: np.ndarray) -> None:
    h, w = array.shape[:2]
    channels = 1 if array.ndim == 2 else 4

    def chunk(tag: bytes, body: bytes) -> bytes:
        return (
            struct.pack(">I", len(body))
            + tag
            + body
            + struct.pack(">I", zlib.crc32(tag + body) & 0xFFFFFFFF)
        )

    pixels = array.astype(np.uint8, copy=False).tobytes()
    rows = b"".join(b"\0" + pixels[y * w * channels : (y + 1) * w * channels] for y in range(h))
    raw = b"\x89PNG\r\n\x1a\n"
    raw += chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 0 if channels == 1 else 6, 0, 0, 0))
    raw += chunk(b"IDAT", zlib.compress(rows, 9)) + chunk(b"IEND", b"")
    path.write_bytes(raw)


def read_nifti(path: Path) -> tuple[np.ndarray, dict]:
    raw = gzip.decompress(path.read_bytes())
    if struct.unpack_from("<i", raw)[0] != 348 or raw[344:348] != b"n+1\0":
        raise ValueError(f"Unsupported NIfTI {path}")
    dimensions = struct.unpack_from("<8h", raw, 40)
    if dimensions[0] != 3:
        raise ValueError("Expected 3D NIfTI")
    shape = tuple(dimensions[1:4])
    datatype = struct.unpack_from("<h", raw, 70)[0]
    dtype = {2: "u1", 4: "<i2", 16: "<f4"}.get(datatype)
    if not dtype:
        raise ValueError(f"Unsupported NIfTI datatype {datatype}")
    offset = int(struct.unpack_from("<f", raw, 108)[0])
    slope, intercept = struct.unpack_from("<ff", raw, 112)
    array = np.frombuffer(raw, dtype=dtype, count=int(np.prod(shape)), offset=offset).reshape(
        shape, order="F"
    )
    affine = [list(struct.unpack_from("<4f", raw, 280 + 16 * i)) for i in range(3)] + [
        [0.0, 0.0, 0.0, 1.0]
    ]
    spacing = list(struct.unpack_from("<3f", raw, 80))
    return array, {
        "shape_ijk": list(shape),
        "spacing_ijk_mm": spacing,
        "affine_ijk_to_ras_mm": affine,
        "scalar_type": str(array.dtype),
        "scaling": [slope, intercept],
        "orientation": "NIfTI RAS world mm",
    }


def read_nrrd(path: Path) -> tuple[np.ndarray, dict]:
    raw = path.read_bytes()
    header, data = raw.split(b"\n\n", 1)
    lines = header.decode().splitlines()

    def field(prefix: str) -> str:
        return next(
            line.split(":", 1)[1].strip() for line in lines if line.startswith(prefix + ":")
        )

    shape = tuple(int(v) for v in field("sizes").split())
    if shape != (512, 512, 94) or field("encoding") != "gzip":
        raise ValueError("Changed SEG.A native NRRD geometry or encoding")
    kind = field("type")
    dtype = {"unsigned short": "<u2", "unsigned char": "u1"}[kind]
    array = np.frombuffer(gzip.decompress(data), dtype=dtype).reshape(shape, order="F")
    vectors = [
        [float(v) for v in tuple_text.strip("()").split(",")]
        for tuple_text in re.findall(r"\([^()]+\)", field("space directions"))
    ]
    origin = [float(v) for v in field("space origin").strip("()").split(",")]
    affine = [[vectors[j][i] for j in range(3)] + [origin[i]] for i in range(3)] + [
        [0.0, 0.0, 0.0, 1.0]
    ]
    return array, {
        "shape_ijk": list(shape),
        "spacing_ijk_mm": [float(np.linalg.norm(v)) for v in vectors],
        "affine_ijk_to_lps_mm": affine,
        "scalar_type": str(array.dtype),
        "orientation": "NRRD LPS world mm",
    }


def display_plane(array: np.ndarray, k: int, size: int = 384) -> np.ndarray:
    nx, ny, _ = array.shape
    scale = min(1.0, size / max(nx, ny))
    xi = np.rint(np.linspace(0, nx - 1, max(1, round(nx * scale)))).astype(int)
    yj = np.rint(np.linspace(ny - 1, 0, max(1, round(ny * scale)))).astype(int)
    return array[np.ix_(xi, yj, [k])][:, :, 0].T


def build(root: Path, entry: str, receipt_path: Path, output: Path) -> None:
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite existing output: {output}")
    receipt = json.loads(receipt_path.read_text())
    if receipt["entry_id"] != entry or receipt["illustration_basis"] != "mixed":
        raise ValueError("Wrong or unreviewed source receipt")
    for pin in receipt["adapter_files"]:
        if sha(root / pin["local_path"]) != pin["sha256"]:
            raise ValueError(f"Changed ReX adapter {pin['local_path']}")
    for a in receipt["assets"]:
        if sha(root / a["path"]) != a["sha256"]:
            raise ValueError(f"Changed native source {a['path']}")
    directory, pack_id, frame, license_id, reference_policy = ENTRIES[entry]
    if output.name != directory:
        raise ValueError(f"Output must end in {directory}")
    input_path, label_path = [root / a["path"] for a in receipt["assets"]]
    reader = read_nrrd if entry == "rexmle-seg-a" else read_nifti
    image, geometry = reader(input_path)
    label, label_geometry = reader(label_path)
    if image.shape != label.shape:
        raise ValueError("Source image and label grids differ")
    affine_key = "affine_ijk_to_lps_mm" if reader == read_nrrd else "affine_ijk_to_ras_mm"
    if not np.allclose(geometry[affine_key], label_geometry[affine_key], atol=1e-4):
        raise ValueError("Source image and label physical maps differ")
    nz = image.shape[2]
    indices = np.rint(np.linspace(nz * 0.20, nz * 0.80, 9)).astype(int).tolist()
    assert len(set(indices)) == 9
    scalar = image.astype(np.float32)
    slope, intercept = geometry.get("scaling", [1, 0])
    scalar = scalar * (slope if slope else 1) + intercept
    finite = scalar[np.isfinite(scalar)]
    # One fixed window for all slices of the case, never per-slice autoscale.
    if entry == "rexmle-seg-a":
        lo, hi = 0.0, float(np.quantile(finite, 0.995))
    elif "topbrain-track1" in entry:
        lo, hi = float(np.quantile(finite, 0.01)), float(np.quantile(finite, 0.995))
    else:
        lo, hi = float(np.quantile(finite, 0.01)), float(np.quantile(finite, 0.995))
    if hi <= lo:
        raise ValueError("Invalid fixed display window")
    output.mkdir(parents=True)
    (output / "images").mkdir()
    samples = []
    mask_samples = []
    created = []
    private = reference_policy == "reader-reference-reveal"
    present_values = [int(v) for v in np.unique(label)]
    class_colors = {}
    for value in present_values:
        if value == 0:
            continue
        rgb = colorsys.hsv_to_rgb((value * 0.61803398875) % 1, 0.82, 1.0)
        class_colors[str(value)] = "#" + "".join(f"{round(channel * 255):02x}" for channel in rgb)
    for n, k in enumerate(indices):
        plane = display_plane(scalar, k)
        gray = np.rint(255 * np.clip((plane - lo) / (hi - lo), 0, 1)).astype(np.uint8)
        image_name = f"images/input-{n:02d}.png"
        png(output / image_name, gray)
        created.append(image_name)
        world = np.asarray(geometry[affine_key]) @ np.asarray(
            [(image.shape[0] - 1) / 2, (image.shape[1] - 1) / 2, k, 1.0]
        )
        samples.append(
            {
                "file": image_name,
                "native_k_zero_based": k,
                "center_world_mm": [round(float(v), 3) for v in world[:3]],
                "display_shape_xy": [gray.shape[1], gray.shape[0]],
            }
        )
        lp = display_plane(label, k)
        rgba = np.zeros((*lp.shape, 4), dtype=np.uint8)
        visible = [int(v) for v in np.unique(lp) if v > 0]
        for value in visible:
            rgb = bytes.fromhex(class_colors[str(value)][1:])
            rgba[lp == value] = [rgb[0], rgb[1], rgb[2], 180]
        mask_name = f"images/{'reference' if private else 'helper'}-{n:02d}.png"
        png(output / mask_name, rgba)
        created.append(mask_name)
        mask_samples.append(
            {
                "file": mask_name,
                "native_k_zero_based": k,
                "nonzero_display_pixels": int(np.count_nonzero(lp)),
                "visible_label_values": visible,
            }
        )
    source = {
        "entry_id": entry,
        "case_id": "K20" if entry == "rexmle-seg-a" else "012",
        "modality": "CTA" if entry in {"rexmle-seg-a", "rexmle-topbrain-track1"} else "MRA",
        "source_role": "public training input"
        if not private
        else "held-out test input; static split only",
        "native_input_sha256": receipt["assets"][0]["sha256"],
        "geometry": geometry,
        "fixed_window_scaled_native_values": [round(lo, 6), round(hi, 6)],
        "sample_rule": "9 fixed 20%-to-80% native k indices; no label-guided selection or cross-grid resampling",
        "display_mapping": "PNG x=i, y=ny-1-j; nearest-neighbor downsample to longest axis <=384 pixels",
        "samples": samples,
        "source_split": receipt["static_split"],
    }
    output_record = {
        "status": "not-retained",
        "participant_prediction": None,
        "submission": None,
        "score": None,
        "csv": "submission.csv",
        "columns": receipt["output_contract"]["columns"],
        "relative_prediction_pattern": receipt["output_contract"]["path_template"],
        "required_file": "binary NRRD mask" if entry == "rexmle-seg-a" else "multiclass NIfTI mask",
        "illustrative_row_not_a_file": True,
    }
    support = {
        "role": "private ReX test reference; reader-only"
        if private
        else "public training label helper",
        "source_sha256": receipt["assets"][1]["sha256"],
        "geometry": label_geometry,
        "classes_present": present_values,
        "class_colors": class_colors,
        "samples": mask_samples,
        "prediction_or_score": None,
    }
    dump(output / "source.json", source)
    dump(output / "output.json", output_record)
    support_name = "reference.json" if private else "helper.json"
    dump(output / support_name, support)
    notice = (
        f"# {entry} local source teaching pack\n\nSource: {receipt['source_url']}. "
        f"{receipt['source_terms']} Exact single-case source image and source annotation were verified "
        "by SHA-256 against the resolution receipt. Nine native-index fixed-window sample images "
        "show display derivatives only; full arrays remain local. Source label overlays are "
        + (
            "private ReX test reference and require explicit reader reveal. "
            if private
            else "public training helpers, not held-out answers. "
        )
        + "No participant prediction, model run, preparer run, grader run or score was retained.\n"
    )
    (output / "NOTICE.md").write_text(notice)
    created += ["source.json", "output.json", support_name, "NOTICE.md"]
    # The staged receipt is byte-identical to the file that integration copies here.
    # Pin the final repository path, rather than this scratch draft location.
    sources = {f"presentation/external-tasks/sources/{entry}-resolution.json": sha(receipt_path)}
    sources.update({a["path"]: a["sha256"] for a in receipt["assets"]})
    sources.update({p["local_path"]: p["sha256"] for p in receipt["adapter_files"]})
    license_source = None
    license_sha = None
    if entry.startswith("rexmle-topbrain-"):
        license_source = (
            root / ".local/explainers/core-20260929/rex-vascular-source/topbrain-2025-license.txt"
        )
        license_sha = "ff112837d8c701c0933f0aea73d4b7a0ca8bfd6f666d25d1f0234aa05e50f53c"
    elif entry == "rexmle-topcow-track2-task1":
        license_source = root / "presentation/task-explorer/rex-topcow/DATA-LICENSE.txt"
        license_sha = "6b527078226cc70d90f6938b55002961e8b311aa57fb720e0d4cc8f180919690"
    if license_source is not None:
        if sha(license_source) != license_sha:
            raise ValueError("Changed original source license")
        (output / "DATA-LICENSE.txt").write_bytes(license_source.read_bytes())
        created.append("DATA-LICENSE.txt")
        sources[str(license_source.relative_to(root))] = license_sha
    manifest = {
        "schema": 1,
        "id": pack_id,
        "frame": frame,
        "units": "mm",
        "license": license_id,
        "label_license": license_id,
        "reference_policy": reference_policy,
        "runtime_geometry": "source-slices",
        "source_class": "source-derived-teaching",
        "illustration_basis": "mixed",
        "sources": sources,
        "checks": {
            "native_source_verified": True,
            "native_label_verified": True,
            "native_grid_matches": True,
            "participant_prediction_retained": False,
            "display_samples": 9,
        },
        "assets": [
            {
                "file": name,
                "bytes": (output / name).stat().st_size,
                "sha256": sha(output / name),
                "provenance": "source-derived-teaching",
                "role": "reader-reference-reveal"
                if private and (name == "reference.json" or name.startswith("images/reference-"))
                else "illustration",
            }
            for name in created
        ],
    }
    dump(output / "manifest.json", manifest)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path)
    parser.add_argument("--entry", choices=ENTRIES, required=True)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = (args.repo_root or root_default()).resolve()
    receipt = (
        args.receipt
        or root / "presentation/external-tasks/sources" / f"{args.entry}-resolution.json"
    ).resolve()
    build(root, args.entry, receipt, args.output.resolve())


if __name__ == "__main__":
    main()
