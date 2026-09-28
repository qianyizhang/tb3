"""Read-only BR-003 source-study audit; no authoring imports or task execution."""

import argparse
import hashlib
import json
import tarfile
from collections import Counter
from itertools import pairwise
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASK_ROOTS = {
    "pdf-table-lineage": "archive/legacy/pre-medical/probes/pdf-table-lineage",
    "chat-round-recovery": "archive/legacy/pre-medical/probes/chat-round-recovery",
    "dicom-label-audit": "probes/dicom-label-audit",
    "dicom-triplanar-svg": "probes/dicom-triplanar-svg",
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit("Use a fresh audit destination.")
    pins = {}

    def read(path):
        p = ROOT / path
        data = p.read_bytes()
        pins[str(path)] = digest(data)
        return data

    def load(path):
        return json.loads(read(path))

    source = load("docs/evidence/br003-source-audit.json")
    summary = load("docs/evidence/br003-round-summary.json")
    index = load("runs/br003-history/session-index.json")
    counts = {
        "indexed_records": len(index),
        "automatic_reviews": sum(r["model"] == "codex-auto-review" for r in index),
        "other_long_titles": sum(
            r["model"] != "codex-auto-review" and len(r["title"]) >= 1000 for r in index
        ),
        "navigable_records": sum(
            r["model"] != "codex-auto-review" and len(r["title"]) < 1000 for r in index
        ),
    }
    assert list(counts.values()) == [395, 142, 16, 237], counts
    exports = sorted((ROOT / "runs/br003-history").glob("*.messages.json"))
    assert len(exports) == source["retrieval"]["selected_original_conversations"] == 9
    for path in exports:
        read(path.relative_to(ROOT))
    counts["retained_selected_exports"] = len(exports)
    excerpts = []
    for number, row in enumerate(source["excerpts"], 1):
        path = Path(row["source_path"])
        # Match the original receipt's hash convention: a JSONL record without newline.
        raw = path.read_bytes().splitlines()[row["line"] - 1]
        assert digest(raw) == row["raw_record_sha256"], (path, row["line"])
        record = json.loads(raw)
        payload = record["payload"]
        assert payload["role"] == row["role"]
        text = "\n".join(c.get("text", "") for c in payload["content"])
        assert row["excerpt"] in text, (path, row["line"])
        assert row["benchmark_trial"] is False
        excerpts.append({"id": f"E{number:02}", **row, "original_record_verified": True})
    counts["exact_original_excerpt_records"] = len(excerpts)
    counts["excerpt_sessions"] = len({r["session_id"] for r in excerpts})
    tasks = []
    for task, root in TASK_ROOTS.items():
        spec = summary["freezes"][task]
        freeze = load(spec["freeze"])
        assert pins[spec["freeze"]] == spec["freeze_sha256"]
        assert len(freeze["files"]) == spec["source_file_count"]
        for name, expected in freeze["files"].items():
            assert digest(read(f"{root}/{name}")) == expected, (task, name)
        snapshot = ROOT / spec["local_snapshot"]
        assert digest(read(spec["local_snapshot"])) == spec["snapshot_sha256"]
        with tarfile.open(snapshot) as archive:
            files = {m.name.removeprefix("./"): m for m in archive.getmembers() if m.isfile()}
            for name, expected in freeze["files"].items():
                candidates = [
                    m for key, m in files.items() if key == name or key.endswith("/" + name)
                ]
                assert len(candidates) == 1, (task, name)
                member = archive.extractfile(candidates[0])
                assert member is not None and digest(member.read()) == expected, (task, name)
        trials = []
        for trial in [r for r in summary["trials"] if r["task"] == task]:
            result = load(trial["source"])
            assert pins[trial["source"]] == trial["source_sha256"]
            assert (
                result["task_checksum"]
                == trial["task_checksum"]
                == spec["matched_harbor_task_checksum"]
            )
            assert result["verifier_result"]["rewards"]["reward"] == trial["reward"]
            assert result["exception_info"] is None and trial["exception"] is None
            for path, expected in trial["evidence_files"].items():
                assert digest(read(path)) == expected, path
            verifier = Path(trial["source"]).parent / "verifier"
            report = load(str(verifier / "test-stdout.txt"))
            assert float(read(str(verifier / "reward.txt"))) == trial["reward"]
            row = {
                k: trial[k]
                for k in [
                    "job",
                    "source",
                    "task_checksum",
                    "agent",
                    "model",
                    "reasoning_effort",
                    "started_at",
                    "finished_at",
                    "agent_seconds",
                    "reward",
                ]
            }
            row["report"] = report
            if task == "dicom-triplanar-svg":
                dice = load(str(verifier / "dice.json"))
                values = [v["dice"] for labels in dice.values() for v in labels.values()]
                row["label_comparisons"] = len(values)
                row["minimum_dice"] = min(values) if values else None
                if trial["agent"] != "nop":
                    assert len(values) == 72 and min(values) == 1
            trials.append(row)
        assert Counter(r["agent"] for r in trials) == {"nop": 1, "oracle": 1, "codex": 1}
        assert {r["agent"]: r["reward"] for r in trials} == {"nop": 0, "oracle": 1, "codex": 1}
        tasks.append(
            {
                "task": task,
                "source_root": root,
                "source_files": len(freeze["files"]),
                "freeze": spec["freeze"],
                "snapshot": spec["local_snapshot"],
                "task_checksum": spec["matched_harbor_task_checksum"],
                "trials": trials,
            }
        )
    for name in ["chat", "pdf", "audit", "svg"]:
        load(f"docs/evidence/br003-{name}-author-controls.json")
    for name in [
        "docs/research-rounds/BR-003-work-history.md",
        "docs/evidence/br003-medical-source.json",
        "docs/evidence/br003-svg-provenance-audit.json",
        "archive/legacy/pre-medical/catalog/analyses/br003-work-history.md",
        "archive/legacy/pre-medical/catalog/analyses/br003-svg-provenance-audit.md",
        "groups/anatomy-audit/ideas/idea-dicom-triplanar-svg.md",
        "groups/anatomy-audit/ideas/idea-dicom-label-audit.md",
    ]:
        read(name)
    read("scripts/audit_history_sourcing.py")
    model_runs = sorted(
        (t for task in tasks for t in task["trials"] if t["agent"] == "codex"),
        key=lambda t: t["started_at"],
    )
    assert all(a["finished_at"] <= z["started_at"] for a, z in pairwise(model_runs))
    output = {
        "schema": 1,
        "entry_id": "tb3-history-sourcing",
        "date": "2026-09-28",
        "scope": "Read-only source-study provenance and retained outcome audit. No fresh model run, saved-code replay, medical inference or historical authoring execution.",
        "source_pins": pins,
        "retrieval_counts": counts,
        "excerpts": excerpts,
        "tasks": tasks,
        "checks": {
            "frozen_files_exact": sum(t["source_files"] for t in tasks),
            "snapshot_archives_exact": len(tasks),
            "original_results_exact": 12,
            "model_attempts": 4,
            "model_passes": 4,
            "model_exceptions": 0,
            "control_attempts": 8,
            "model_runs_sequential": True,
        },
        "limits": [
            "Eight exact excerpt records cover six sessions; the retained selection has nine exports, not an exhaustive audit of 237 records.",
            "History reports are uncontrolled evidence involving different earlier models, not Terra benchmark failures.",
            "H01 table lineage does not test authentic vector-diagram crop ownership. H05 remains parked.",
            "Exact historical verdict-timeout/reroute and SVG incidents were not recovered.",
            "Four different endpoints cannot be pooled. H03 and H04 share one CT; their observations are correlated.",
            "Current check verifies retained bytes and recorded outcomes, not container recovery, scorer reexecution or clinical truth.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n")
    print(
        json.dumps(
            {
                "output": str(args.output),
                "pins": len(pins),
                "counts": counts,
                "checks": output["checks"],
            }
        )
    )


if __name__ == "__main__":
    main()
