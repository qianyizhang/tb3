"""Build source-pinned teaching records from the read-only MR importer audit."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = Path("groups/anatomy-audit/presentation/sources/mri-importer-audit.json")
DEST = ROOT / "presentation/task-explorer/mri-importer"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, value):
    (DEST / name).write_text(json.dumps(value, separators=(",", ":")) + "\n")


def main():
    audit = json.loads((ROOT / AUDIT).read_text())
    for path, digest in audit["source_pins"].items():
        assert sha(ROOT / path) == digest, path
    DEST.mkdir(parents=True, exist_ok=True)
    write("inputs.json", {"cases": audit["public_cases"], "window": [-3000, 3000]})
    write(
        "output.json",
        {
            "cases": audit["public_outputs"],
            "relocation": audit["public_relocation"],
            "trace": audit["trace"],
        },
    )
    write(
        "reference.json",
        {
            "results": audit["results"],
            "diagnostics": audit["diagnostics"],
            "shapes": audit["private_shapes"],
        },
    )
    (DEST / "DATA-LICENSE.txt").write_text(
        "LicenseRef-TB3-authored-fixtures: first-party synthetic metadata and signed pixel arrays authored for this repository. No patient data or upstream image pixels. This identifier records provenance and is not a new grant of external redistribution rights. Retain benchmark source notices.\n"
    )
    (DEST / "NOTICE.md").write_text("""# MRI importer teaching records

These are exact retained synthetic fixture samples, not patient MRI, reconstructed anatomy or a generic ETL schematic. Source fingerprints and independent checks are in `groups/anatomy-audit/presentation/sources/mri-importer-audit.json`; the builder verifies them before writing. No historical authoring module is executed and no frozen input is rewritten.

`inputs.json` retains all four public encodings, their actual pixel values, storage indices, descriptor ordinals, actual time/echo labels and physical geometry. `output.json` retains outputs from local replay of the saved Terra/high answer. The original solver also received the public expected arrays. `reference.json` contains private aggregate grades and diagnostic controls, revealed separately in the reader. The HTML embeds this material and is not a solver packet.

Pixel stamps use a fixed signed sample window [-3000,3000]; they are numerical tiles, not anatomical evidence. Arrays retain [time,echo,slice,row,column] axes. Native pixel geometry uses row/column spacing; the affine maps [column,row,slice,1] to LPS mm. Association highlights traverse actual storage frames and their exact destination indices. They are a teaching traversal, not a solver optimization history. Spatial projections are explicitly labelled diagrams; coordinate arithmetic uses the original full affine.

The three private encodings per acquisition are correlated. One retained Terra/high attempt passed 36/36 fixtures from 12 acquisitions. The oracle passed 36/36 and the starter 12/36. Local saved-code replay uses existing pydicom 3.0.2 versus frozen 3.0.1 and reproduces every report; it does not establish container recovery or a fresh model pass. Full Enhanced MR conformance, clinical robustness, missing slices, multiple stacks and compressed pixels are outside the declared profile. The idea remains parked.
""")
    files = ["inputs.json", "output.json", "reference.json", "NOTICE.md", "DATA-LICENSE.txt"]
    write(
        "manifest.json",
        {
            "id": "retained-mri-importer-v1",
            "frame": "LPS",
            "units": "mm",
            "license": "LicenseRef-TB3-authored-fixtures",
            "label_license": "LicenseRef-TB3-authored-fixtures",
            "reference_policy": "reader-reference-reveal",
            "sources": {
                str(AUDIT): sha(ROOT / AUDIT),
                "scripts/build_mri_importer_assets.py": sha(Path(__file__)),
            },
            "checks": audit["fixture_checks"],
            "assets": [
                {
                    "file": name,
                    "sha256": sha(DEST / name),
                    "bytes": (DEST / name).stat().st_size,
                    "provenance": "source-derived-teaching",
                    "role": "reader-reference-reveal"
                    if name == "reference.json"
                    else "illustration",
                }
                for name in files
            ],
        },
    )
    print(
        json.dumps(
            {"assets": files, "samples_exact": audit["fixture_checks"]["sample_values_exact"]}
        )
    )


if __name__ == "__main__":
    main()
