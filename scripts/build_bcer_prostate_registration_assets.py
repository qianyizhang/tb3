"""Build a source-backed, mixed-basis BCER medium prostate registration explainer.

Uses retained PI-CAI inputs and pinned source receipts. No BCER tool or model runs.
The builder requires a fresh output directory and never overwrites an existing pack.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "workbench.toml").is_file())
AUDIT = ROOT / "presentation/external-tasks/sources/bcer-workflow-audit.json"
INPUTS = ROOT / "presentation/task-explorer/bcer-workflow/inputs.json"
INPUT_LICENSE = ROOT / "presentation/task-explorer/bcer-workflow/DATA-LICENSE.txt"
CODE_LICENSE = ROOT / "presentation/task-explorer/bcer-workflow/BCER-LICENSE.txt"
SOURCE_DRAFT = (
    ROOT
    / ".local/explainers/core-20260929/bcer-source/bcer-medium-register-prostate/source-resolution-draft.json"
)
PINS = {
    AUDIT: "d927b7f053943b14cedfabe6f616e96a80a604cf7edb67a721e4581f7ec8190d",
    INPUTS: "7ea306dcc3876a1bf2387eba1b72a269285ccf24ea5df2a60efe1f729cf5e14b",
    INPUT_LICENSE: "2f9a445451b5a2e9c8c91a89e4254c9dc359b388929fbd2678c96c368049dbf3",
    CODE_LICENSE: "b1099da8a60c97630f5e5f65a523fe21085e27c00a6b025ff0ef96055e7414a5",
}


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(pack: Path, name: str, value: object) -> None:
    (pack / name).write_text(json.dumps(value, separators=(",", ":"), ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path, help="fresh pack directory")
    args = parser.parse_args()
    pack = args.output.resolve()
    if pack.exists():
        parser.error(f"refusing to overwrite existing output: {pack}")
    for path, expected in PINS.items():
        assert sha(path) == expected, f"pin mismatch: {path}"
    resolved = json.loads(SOURCE_DRAFT.read_text())
    prior = json.loads(INPUTS.read_text())
    assert resolved["entry_id"] == "bcer-medium-register-prostate"
    assert [s["name"] for s in prior["sequences"]] == ["T2w", "ADC", "DWI_highb"]
    case = resolved["input_case"]
    assert len(prior["sequences"]) == len(case["sequences"]) == 3
    for built, pinned in zip(prior["sequences"], case["sequences"]):
        assert built["name"] == pinned["name"]
        assert built["size_xyz"] == pinned["size_xyz"]
        assert built["origin_lps_mm"] == pinned["origin_lps_mm"]
        assert built["witness_ijk"] == pinned["witness_ijk"]
        for name, key in (("original", "original_sha256"), ("prepared", "prepared_sha256")):
            path = ROOT / pinned[name]
            assert sha(path) == pinned[key], f"case input changed: {path}"
    witness = case["witness_lps_mm"]
    assert len(witness) == 3
    # The selected witness differs from the prior pack's three demonstration points.
    # Its inverse-affine indices are pinned by the source audit, not measured landmarks.
    pack.mkdir(parents=True, exist_ok=False)
    write_json(
        pack,
        "source.json",
        {
            "case": case["id"],
            "role": case["role"],
            "frame": "LPS",
            "units": "mm",
            "sequences": [
                {
                    k: v
                    for k, v in s.items()
                    if k
                    in (
                        "name",
                        "original",
                        "prepared",
                        "size_xyz",
                        "spacing_xyz_mm",
                        "origin_lps_mm",
                        "direction_lps",
                        "witness_ijk",
                        "slice_k",
                        "display_range",
                        "png",
                    )
                }
                for s in prior["sequences"]
            ],
            "witness_lps_mm": witness,
            "original_sha256": {s["name"]: s["original_sha256"] for s in case["sequences"]},
            "prepared_sha256": {s["name"]: s["prepared_sha256"] for s in case["sequences"]},
            "warning": {
                "text": "Real PI-CAI input images; no BCER medium-task transform, resampled patient image, or independent alignment reference is retained.",
                "source_url": "https://zenodo.org/records/6624726",
                "source_label": "PI-CAI source",
                "run_url": "https://github.com/Albertlongzi/BCER/tree/d10816712793a9e27f2e70640f9afc06f08a0c5c",
                "run_label": "pinned BCER task route",
            },
        },
    )
    write_json(
        pack,
        "operation.json",
        {
            "status": "symbolic; no patient resample computed",
            "fixed": "T2w",
            "moving_choices": ["ADC", "DWI_highb"],
            "default_method": "identity",
            "default_interpolation": "linear",
            "supported_not_run": ["rigid", "affine"],
            "physical_transform": "identity in LPS millimeters",
            "mapping": [
                "p_LPS = A_T2w × [i,j,k,1]",
                "q_moving = inverse(A_moving) × p_LPS",
                "sample moving intensity at q_moving with linear interpolation",
            ],
            "witness": {
                "lps_mm": witness,
                "t2w_ijk": case["sequences"][0]["witness_ijk"],
                "adc_ijk": case["sequences"][1]["witness_ijk"],
                "dwi_highb_ijk": case["sequences"][2]["witness_ijk"],
            },
            "output": {
                "resampled_path": None,
                "transform_path": None,
                "expected_space": "fixed T2w grid",
                "saved_medium_run": False,
            },
            "required_stages": ["identify_sequences", "register_to_reference"],
            "checks": [
                "stage success",
                "resampled_path exists",
                "transform_path exists",
                "resampled_exists",
                "resampled_non_empty",
            ],
            "alignment_quality_reference": None,
            "swap_counterexample": "Reversing fixed and moving can produce files on the ADC/DWI grid rather than the requested T2w grid; structural checks alone do not prove alignment.",
        },
    )
    (pack / "NOTICE.md").write_text(
        "# BCER medium prostate registration teaching pack\n\n"
        "Actual representative PI-CAI 10001_1000001 T2w, ADC and DWI_highb input "
        "planes are reused from the pinned bcer-workflow teaching extract. They are "
        "not an official BCER medium split, task run, registered output, or alignment reference. "
        "The physical-coordinate and interpolation operation is symbolic. The default "
        "tool method is identity header resampling; rigid/affine optimization was not run.\n\n"
        "PI-CAI data license: CC-BY-NC-4.0 (see DATA-LICENSE.txt). BCER source license "
        "is retained separately (BCER-LICENSE.txt). Local noncommercial interpretation.\n"
    )
    (pack / "DATA-LICENSE.txt").write_bytes(INPUT_LICENSE.read_bytes())
    (pack / "BCER-LICENSE.txt").write_bytes(CODE_LICENSE.read_bytes())
    assets = []
    for name in (
        "source.json",
        "operation.json",
        "NOTICE.md",
        "DATA-LICENSE.txt",
        "BCER-LICENSE.txt",
    ):
        path = pack / name
        assets.append(
            {
                "file": name,
                "sha256": sha(path),
                "bytes": path.stat().st_size,
                "provenance": "source-derived-teaching",
                "role": "illustration",
            }
        )
    write_json(
        pack,
        "manifest.json",
        {
            "id": "retained-bcer-prostate-registration-v1",
            "frame": "LPS",
            "units": "mm",
            "license": "CC-BY-NC-4.0",
            "label_license": None,
            "reference_policy": "no-reference-assets",
            "sources": {
                "presentation/task-explorer/bcer-workflow/inputs.json": PINS[INPUTS],
                "presentation/external-tasks/sources/bcer-workflow-audit.json": PINS[AUDIT],
                "scripts/build_bcer_prostate_registration_assets.py": sha(Path(__file__)),
            },
            "checks": {
                "retained_modalities": 3,
                "source_native_geometry": True,
                "original_and_prepared_hashes_verified": 6,
                "saved_medium_run": False,
                "symbolic_operation_only": True,
                "independent_alignment_reference": False,
            },
            "assets": assets,
        },
    )
    print(f"built {pack}: 3 native MRI inputs, symbolic operation, empty artifacts")


if __name__ == "__main__":
    main()
