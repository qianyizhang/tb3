"""Pack audited BR-034 images and retained surfaces for teaching; no solver execution."""

import argparse
import base64
import io
import json
from pathlib import Path

import numpy as np
from audit_clinical_cavity_evidence import BASE, CASES, RESULT, read, sections, sha, signed_volumes
from PIL import Image

AUDIT = Path("groups/cardiac-motion/presentation/sources/clinical-cavity-audit.json")
AUDIT_SHA = "0ee985362ca1f01fb8b1db5a3267ae5b0892456843670e02e5bd136b1adc2ca1"


def dump(path, value):
    path.write_text(json.dumps(value, separators=(",", ":")) + "\n")


def packed(array, dtype):
    data = np.ascontiguousarray(array, dtype=dtype)
    encoded = base64.b64encode(data.tobytes()).decode()
    recovered = np.frombuffer(base64.b64decode(encoded), dtype=dtype).reshape(data.shape)
    np.testing.assert_array_equal(data, recovered)
    return encoded


def build(root, out):
    audit_path = root / AUDIT
    if sha(audit_path) != AUDIT_SHA:
        raise ValueError("Clinical-cavity audit changed; review it before rebuilding")
    audit = read(audit_path)
    sources = {str(AUDIT): AUDIT_SHA}

    def retained(relative):
        key = str(relative)
        path = root / key
        if key not in audit["source_pins"] or sha(path) != audit["source_pins"][key]:
            raise ValueError(f"Unaudited or changed source: {key}")
        sources[key] = audit["source_pins"][key]
        return path

    result = read(retained(RESULT))
    trial = next(t for t in result["trials"] if t["phase"] == "sol-xhigh")
    primary_answer = Path(trial["result_path"]).parent / "artifacts/app/answer"
    source, output, reference = {}, {}, {}
    max_packing_error = 0.0
    plane_checks = 0

    def mesh(points, faces, cal):
        nonlocal max_packing_error
        points = np.asarray(points)
        if points.ndim == 2:
            points = points[None]
        error = float(np.max(np.abs(points.astype("<f4").astype(float) - points)))
        max_packing_error = max(max_packing_error, error)
        assert error < 0.00001 and faces.max() < 65536
        lo = np.array(cal["origin_xyz_mm"])
        index = np.rint(-lo).astype(int)
        return {
            "frames": len(points),
            "vertices": points.shape[1],
            "points_f32le": packed(points, "<f4"),
            "faces_u16le": packed(faces, "<u2"),
            "volume_ml": abs(signed_volumes(points, faces)).tolist(),
            "sections": [
                [
                    np.round(sections(p, faces, axis, lo[axis] + index[axis], lo, axes), 3).tolist()
                    for p in points
                ]
                for axis, axes in [(1, [0, 2]), (0, [1, 2]), (2, [0, 1])]
            ],
        }

    for key, (folder, _, _) in CASES.items():
        base = BASE / folder
        cal = read(retained(base / "input/geometry.json"))
        prep = read(retained(base / "preparation.json"))
        initial = dict(np.load(retained(base / "input/initial_mesh.npz"), allow_pickle=False))
        volumes = np.load(retained(base / "input/volumes.npy"), allow_pickle=False, mmap_mode="r")
        lo = np.array(cal["origin_xyz_mm"])
        index = np.rint(-lo).astype(int)
        planes = []
        for j, (axis, axes, name) in enumerate(
            [(1, [0, 2], "XZ"), (0, [1, 2], "YZ"), (2, [0, 1], "XY")]
        ):
            origin = lo.copy()
            origin[axis] += index[axis]
            frames = []
            for t, volume in enumerate(volumes):
                pixels = np.take(volume, index[axis], axis=2 - axis)
                png = retained(base / f"input/previews/plane{j + 1}_{t:03d}.png")
                np.testing.assert_array_equal(np.asarray(Image.open(png).convert("L")), pixels)
                data = png.read_bytes()
                np.testing.assert_array_equal(
                    np.asarray(Image.open(io.BytesIO(data)).convert("L")), pixels
                )
                frames.append(
                    {
                        "png": "data:image/png;base64," + base64.b64encode(data).decode(),
                        "gray_u8": packed(pixels, "u1"),
                    }
                )
                plane_checks += 1
            planes.append(
                {
                    "name": name,
                    "width": pixels.shape[1],
                    "height": pixels.shape[0],
                    "origin_mm": origin.tolist(),
                    "dx_mm": np.eye(3)[axes[0]].tolist(),
                    "dy_mm": np.eye(3)[axes[1]].tolist(),
                    "frames": frames,
                }
            )
        source[key] = {
            "recording": prep["recording"],
            "frames": len(volumes),
            "native_indices": prep["selected_native_frame_indices_zero_based"],
            "timestamps_s": cal["timestamps_s"],
            "shape_tzyx": cal["shape_tzyx"],
            "initial": mesh(initial["points"], initial["faces"], cal),
            "planes": planes,
            # Fixed public input bounds, shared by every frame and paired surface.
            "bounds_mm": [lo.tolist(), (lo + np.array(cal["shape_tzyx"][1:][::-1]) - 1).tolist()],
            "public_files": audit["cases"][key]["public_file_count"],
        }
        answer = primary_answer if key == "primary" else BASE / "replays" / key / "output"
        prediction = dict(np.load(retained(answer / "prediction.npz"), allow_pickle=False))
        output[key] = {
            "mesh": mesh(prediction["points"], prediction["faces"], cal),
            "summary": read(retained(answer / "summary.json")),
        }
        truth = dict(np.load(retained(base / "reference.npz"), allow_pickle=False))
        metric_key = "sol-xhigh" if key == "primary" else key
        reference[key] = {
            "mesh": mesh(truth["points"], truth["faces"], cal),
            "grade": audit["recomputed_grades"][metric_key],
        }
        np.testing.assert_array_equal(initial["points"], truth["points"][0])
        np.testing.assert_allclose(
            output[key]["mesh"]["volume_ml"],
            reference[key]["grade"]["volume_ml"],
            rtol=0,
            atol=1e-8,
        )
    cal = read(retained(BASE / "input/geometry.json"))
    for key in ["static", "shift", "static_initialization"]:
        answer = BASE / (
            "static-control" if key == "static_initialization" else f"replays/{key}/output"
        )
        data = dict(np.load(retained(answer / "prediction.npz"), allow_pickle=False))
        output[key] = {
            "mesh": mesh(data["points"], data["faces"], cal),
            "summary": read(retained(answer / "summary.json")),
        }
    # Retained controls are displayed directly, not generated animations.
    original = np.frombuffer(
        base64.b64decode(output["primary"]["mesh"]["points_f32le"]), "<f4"
    ).reshape(18, 1946, 3)
    for key, expected in [
        ("static", np.repeat(original[:1], 18, axis=0)),
        ("shift", np.roll(original, 5, axis=0)),
        ("static_initialization", np.repeat(original[:1], 18, axis=0)),
    ]:
        actual = np.frombuffer(
            base64.b64decode(output[key]["mesh"]["points_f32le"]), "<f4"
        ).reshape(18, 1946, 3)
        np.testing.assert_array_equal(actual, expected)
    reference["static_initialization"] = {
        "grade": audit["recomputed_grades"]["static_initialization"]
    }
    reference["controls"] = audit["retained_replays"]
    reference["limits"] = audit["scorer_limits"]
    license_path = retained(BASE / "source/LICENSE")
    retained(BASE / "source/croissant.json")
    retained(BASE / "source/readme.md")
    out.mkdir(parents=True, exist_ok=False)
    dump(out / "source.json", {"cases": source, "frame": "initial-cavity-local", "units": "mm"})
    dump(
        out / "output.json",
        {
            "cases": output,
            "model_attempts": 1,
            "model": "gpt-5.6-sol",
            "effort": "xhigh",
            "original_reward": 0,
        },
    )
    dump(out / "reference.json", reference)
    (out / "DATA-LICENSE.txt").write_bytes(license_path.read_bytes())
    (out / "NOTICE.md").write_text("""# EchoXFlow clinical cavity teaching assets

Elias Stenhede et al. EchoXFlow.
https://huggingface.co/datasets/Ahus-AIM/EchoXFlow
https://github.com/Ahus-AIM/EchoXFlow
Data and labels: CC BY-NC-SA 4.0; see DATA-LICENSE.txt.

Derived locally from three selected recordings and retained BR-034 outputs.
Changes: published (-X,Z,Y) convention, initial-surface PCA coordinates,
1 mm Cartesian resampling and crop, orthogonal sections, float32 display
positions and float64 original-volume integration. Local axes are not RAS/LPS.
Source images remain unchanged from the audited prepared inputs. Source arrays
are not distributed here. All frames retain a fixed public-input coordinate scale.

The supplied initial surface is public assistance. reference.json is private
source annotation revealed for the reader, not additional solver input. It is
operator/software derived, not independently adjudicated cardiology, material
motion or etiology. Source archive hashes match; publisher per-array serialization
versus raw C-order hashes remains unresolved. Pretraining exposure is unknown.
One model attempt and retained executable replays are not independent model trials.
This teaching build executes no solver, flow fitting or model and changes no scores.

Rebuild into a fresh local destination with:
.venv-br034/bin/python scripts/build_clinical_cavity_assets.py --out NEW_DIRECTORY
""")
    names = ["source.json", "output.json", "reference.json", "NOTICE.md", "DATA-LICENSE.txt"]
    checks = {
        "cases": 3,
        "native_frames": 101,
        "pixel_equal_previews": plane_checks,
        "position_encoding": "base64 IEEE754 float32 little endian; shared faces uint16 little endian",
        "maximum_display_position_error_mm": max_packing_error,
        "volume_arithmetic": "original float64; never display-packed coordinates",
        "static_and_shift_arrays_equal": True,
        "model_execution": False,
    }
    dump(
        out / "manifest.json",
        {
            "schema": 1,
            "id": "retained-clinical-cavity-v1",
            "frame": "initial-cavity-local",
            "units": "mm",
            "license": "CC-BY-NC-SA-4.0",
            "label_license": "CC-BY-NC-SA-4.0",
            "reference_policy": "reader-reference-reveal",
            "sources": sources,
            "checks": checks,
            "assets": [
                {
                    "file": name,
                    "sha256": sha(out / name),
                    "bytes": (out / name).stat().st_size,
                    "provenance": "source-derived-teaching",
                    "role": "reader-reference-reveal"
                    if name == "reference.json"
                    else "illustration",
                }
                for name in names
            ],
        },
    )
    print(
        json.dumps(
            {
                "out": str(out),
                "checks": checks,
                "bytes": sum((out / name).stat().st_size for name in names),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    build(args.root.absolute(), args.out.absolute())
