"""Package unchanged public dev image/question and separated educational reference."""

import argparse
import hashlib
import json
from pathlib import Path

ENTRY = "automedbench-full-medxpertqa-mm-task"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, required=True)
    ap.add_argument("--sample", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()
    out = a.output
    if out.exists():
        raise FileExistsError(out)
    rp = a.root / f"presentation/external-tasks/sources/{ENTRY}-resolution.json"
    bp = a.root / f"presentation/external-tasks/briefs/{ENTRY}.md"
    r = json.loads(rp.read_text())
    assert sha(bp) == r["brief_sha256"]
    assert sha(a.sample) == r["native_example"]["sha256"]
    out.mkdir(parents=True)

    def put(n, o):
        (out / n).write_text(json.dumps(o, sort_keys=True, separators=(",", ":")) + "\n")

    s = {
        k: r[k]
        for k in [
            "entry_id",
            "actual_data_gap",
            "acquisition_route",
            "source_roles",
            "task_contract",
            "source_question",
            "native_example",
            "zip_member",
        ]
    }
    s["notice"] = {
        "label": "Public dev example; Full gold absent",
        "text": r["warning_text"],
        "url": r["acquisition_route"],
        "link_label": "Official MedXpertQA",
    }
    put("source.json", s)
    (out / "source-preview.jpeg").write_bytes(a.sample.read_bytes())
    put("reference.json", r["public_reference"])
    put(
        "operation.json",
        {
            "steps": ["Bind image and question", "Letter to option text", "Schema/scorer boundary"],
            "actual_decode": None,
            "public_calibration_request_exact": 15,
            "public_calibration_checklist_min": 15,
            "config_smoke_bounds": [1, 10],
        },
    )
    put(
        "output.json",
        {
            "question_id": None,
            "predicted_label": None,
            "predicted_answer": None,
            "raw_model_output": None,
            "model_name": None,
            "runtime_s": None,
            "private_reference": None,
            "score": None,
        },
    )
    put(
        "fixture.json",
        {
            "role": "authored nonclinical schema teaching only",
            "keys": [
                "question_id",
                "predicted_label",
                "predicted_answer",
                "raw_model_output",
                "model_name",
                "runtime_s",
            ],
            "actual_prediction": None,
            "actual_reference": None,
        },
    )
    (out / "NOTICE.md").write_text(
        r["warning_text"]
        + "\n"
        + r["actual_data_gap"]
        + "\nreference.json is public dev annotation for later reader reveal only, never private Full gold.\n"
    )
    (out / "DATA-LICENSE.txt").write_text(
        "MedXpertQA, TsinghuaC3I, official source https://huggingface.co/datasets/TsinghuaC3I/MedXpertQA and https://github.com/TsinghuaC3I/MedXpertQA . MIT license declared in dataset metadata/task envelope. Public dev MM-2000 source question, image and label, unchanged native JPEG bytes. Cite MedXpertQA dataset authors/official release. Source image copyright/clinical adjudication not independently established. Local task explanation only; no publication, clinical advice or Full reference recovery implied.\n"
    )
    assets = [
        {
            "file": x.name,
            "bytes": x.stat().st_size,
            "sha256": sha(x),
            "role": "reader-reference-reveal"
            if x.name == "reference.json"
            else "input-preview"
            if x.name == "source-preview.jpeg"
            else "illustration",
            "provenance": "symbolic-protocol"
            if x.name == "fixture.json"
            else "source-derived-teaching",
        }
        for x in sorted(out.iterdir())
    ]
    put(
        "manifest.json",
        {
            "schema": 1,
            "id": "retained-automed-medxpert-mm-source-v1",
            "frame": "symbolic-unit-grid",
            "units": "unitless",
            "license": "MIT",
            "label_license": None,
            "source_class": "source-derived-teaching",
            "runtime_geometry": "source-records",
            "reference_policy": "reader-reference-reveal",
            "sources": {str(rp.relative_to(a.root)): sha(rp), str(bp.relative_to(a.root)): sha(bp)},
            "assets": assets,
        },
    )


if __name__ == "__main__":
    main()
