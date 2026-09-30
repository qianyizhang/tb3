import argparse
import hashlib
import json
from pathlib import Path


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--fixture", required=True, type=Path)
    a = ap.parse_args()
    root = a.root
    out = a.output
    if out.exists():
        raise FileExistsError(out)
    rp = root / "presentation/external-tasks/sources/radagent-vqa-resolution.json"
    r = json.loads(rp.read_text())
    brief = root / "presentation/external-tasks/briefs/radagent-vqa.md"
    assert r["entry_id"] == "radagent-vqa" and sha(brief) == r["brief_sha256"]
    out.mkdir(parents=True)

    def put(name, x):
        (out / name).write_text(json.dumps(x, sort_keys=True, separators=(",", ":")) + "\n")

    source = {
        k: r[k]
        for k in [
            "entry_id",
            "illustration_basis",
            "source_commit",
            "actual_data_gap",
            "acquisition_route",
            "task_contract",
            "source_roles",
        ]
    }
    source["notice"] = {
        "label": "Symbolic VQA · CT/case absent",
        "text": r["warning_text"],
        "url": "https://huggingface.co/datasets/ibrahimhamamci/CT-RATE",
        "link_label": "Official CT-RATE access",
    }
    put("source.json", source)
    put(
        "operation.json",
        {
            "field_map": [
                ["question", "task text"],
                ["qid", "task_id"],
                ["image_id", "configured CT path"],
                ["answer", "host gt, evaluator role"],
            ],
            "tool_scopes": [
                "whole CT volume → ct_vqa_tool",
                "selected 2D axial images → slice_vqa_tool",
                "question + independent model-derived evidence → full option string",
            ],
            "private_values": None,
            "observed_tool_result": None,
        },
    )
    put(
        "output.json",
        {
            "role": "Actual participant output absent",
            "final_action": "final_answer",
            "participant_answer": None,
            "participant_trace": None,
            "actual_score": None,
            "private_reference": None,
            "format_contract": "Full option text including prefix, no explanation",
        },
    )
    put("formatting-fixture.json", json.loads(a.fixture.read_text()))
    (out / "NOTICE.md").write_text(
        r["warning_text"]
        + "\n\n"
        + r["actual_data_gap"]
        + "\n\nAuthored nonclinical option syntax only. No original question, CT, reference, tool output, participant response or score.\n"
    )
    (out / "DATA-LICENSE.txt").write_text(
        "Authored symbolic mechanism; no patient data or upstream runtime code included. RadAgent README links MIT but root LICENSE absent at pinned commit; CT-RATE has separate gated terms.\n"
    )
    assets = [
        {
            "file": p.name,
            "sha256": sha(p),
            "bytes": p.stat().st_size,
            "role": "illustration",
            "provenance": "symbolic-protocol",
        }
        for p in sorted(out.iterdir())
    ]
    put(
        "manifest.json",
        {
            "schema": 1,
            "id": "retained-radagent-vqa-contract-v2",
            "frame": "symbolic-unit-grid",
            "units": "none",
            "license": "LicenseRef-RadAgent-source-terms-unresolved",
            "label_license": None,
            "source_class": "symbolic-protocol",
            "runtime_geometry": "source-records",
            "reference_policy": "no-reference-assets",
            "sources": {
                "presentation/external-tasks/sources/radagent-vqa-resolution.json": sha(rp),
                "presentation/external-tasks/briefs/radagent-vqa.md": sha(brief),
            },
            "assets": assets,
        },
    )


if __name__ == "__main__":
    main()
