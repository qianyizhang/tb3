"""Package unchanged public train image/question and separated educational reference."""

import argparse
import base64
import hashlib
import json
from pathlib import Path

ENTRY = "automedbench-full-pathvqa-task"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def jpeg_size(raw):
    if raw[:2] != b"\xff\xd8":
        raise ValueError("Not JPEG")
    pos = 2
    while pos < len(raw):
        while raw[pos] == 255:
            pos += 1
        marker = raw[pos]
        pos += 1
        length = int.from_bytes(raw[pos : pos + 2], "big")
        if marker in {0xC0, 0xC1, 0xC2}:
            return (
                int.from_bytes(raw[pos + 5 : pos + 7], "big"),
                int.from_bytes(raw[pos + 3 : pos + 5], "big"),
            )
        pos += length
    raise ValueError("Missing JPEG dimensions")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, required=True)
    ap.add_argument("--source-root", type=Path, required=True)
    ap.add_argument("--sample", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()
    out = a.output
    if out.exists():
        raise FileExistsError(out)
    rp = a.root / f"presentation/external-tasks/sources/{ENTRY}-resolution.json"
    bp = a.root / f"presentation/external-tasks/briefs/{ENTRY}.md"
    r = json.loads(rp.read_text())
    assert r["entry_id"] == ENTRY
    assert sha(bp) == r["brief_sha256"]
    for pin in r["source_pins"]:
        raw = (a.source_root / pin["path"]).read_bytes()
        if len(raw) != pin["bytes"] or hashlib.sha256(raw).hexdigest() != pin["sha256"]:
            raise ValueError("Stale source pin")
    assert sha(a.sample) == r["native_example"]["sha256"]
    if jpeg_size(a.sample.read_bytes()) != (309, 272):
        raise ValueError("Native JPEG dimensions changed")
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
            "source_geometry",
        ]
    }
    s["notice"] = {
        "label": "Public train example; Full answer absent",
        "text": r["warning_text"],
        "url": r["acquisition_route"],
        "link_label": "PathVQA dataset route",
    }
    s["preview_data_uri"] = (
        "data:image/jpeg;base64," + base64.b64encode(a.sample.read_bytes()).decode()
    )
    put("source.json", s)
    (out / "source-preview.jpeg").write_bytes(a.sample.read_bytes())
    put("reference.json", r["public_reference"])
    put(
        "operation.json",
        {
            "steps": [
                "Bind image and question",
                "Open-ended metric branches",
                "Schema/scorer boundary",
            ],
            "actual_decode": None,
            "public_calibration_min": 15,
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
    put("fixture.json", r["metric_fixtures"])
    (out / "NOTICE.md").write_text(
        r["warning_text"]
        + "\n"
        + r["actual_data_gap"]
        + "\nreference.json is public train annotation for later reader reveal only, never private Full gold.\n"
    )
    (out / "DATA-LICENSE.txt").write_text(
        "PathVQA distribution flaviagiammarino/path-vqa, pinned HF1685832883334b5bb5beaf4e4b333fdeecaa4ad9; official dataset work XiaomanHe/PathVQA, PathVQA:30000+Questions for Medical Visual Question Answering (2020). MIT declared distribution/task terms; dataset card states original images/captions belong to textbook publishers/authors and PEIR owners. Local pack records image-rights unresolved; native cached training image bytes unchanged, source arrows retained. Cite He, Xuehai; Zhang, Yichen; Mou, Luntian; Xing, Eric; Xie, Pengtao (2020), arXiv2003.10286, and flaviagiammarino distribution. Source image copyright/clinical adjudication not independently established. Local task explanation only; no publication, clinical advice or Full reference recovery implied.\n"
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
            "id": "retained-automed-pathvqa-source-v1",
            "frame": "symbolic-unit-grid",
            "units": "unitless",
            "license": "LicenseRef-PathVQA-MIT-distribution-image-rights-unresolved",
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
