"""Build inspectable source-study records from the retained BR-003 audit."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = "groups/anatomy-audit/presentation/sources/history-sourcing-audit.json"
DEST = ROOT / "presentation/task-explorer/history-sourcing"
CANDIDATES = [
    {
        "id": "H01",
        "task": "pdf-table-lineage",
        "label": "Table lineage",
        "lead": "Reported PDF crop defects and parser limitations",
        "source_strength": "Recovered reports; related new fixture",
        "input": "Five-page original synthetic survey PDF; all table values visible",
        "output": "Two tables in JSON: cells, page attribution, notes and fragment boxes",
        "reference": "Private author transcription and content-envelope geometry",
        "limit": "Fixed-document curation permits manual transcription. It does not test authentic vector-diagram crop ownership.",
        "endpoint": "4/4 content and geometry checks",
        "source_ids": ["E01", "E02", "E03"],
    },
    {
        "id": "H02",
        "task": "chat-round-recovery",
        "label": "Chat recovery",
        "lead": "Resident exit, queued work and stale-scope reports",
        "source_strength": "Recovered lifecycle evidence; exact timeout incident missing",
        "input": "Timestamped simulated events, public semantics and one example",
        "output": "JSON state, idempotent effects and per-room lifecycle views",
        "reference": "Private deterministic schedules and expected checkpoints",
        "limit": "No real messaging connection, wall clock or external availability. The recalled verdict-timeout/reroute incident was not recovered.",
        "endpoint": "22/22 deterministic traces",
        "source_ids": ["E04", "E05", "E06", "E07", "E08"],
    },
    {
        "id": "H03",
        "task": "dicom-label-audit",
        "label": "Annotation QA",
        "lead": "User-added coverage-aware anatomical sanity question",
        "source_strength": "Explicit new proposal; not a recovered benchmark failure",
        "input": "CT + BINARY SEG, full vocabulary and requested focus labels",
        "output": "Exact missing / wrong-side / misplaced finding sets",
        "reference": "Private controlled mutations and clean/partial-coverage controls",
        "limit": "Five correlated packets from one CT; gross QA only. No public anatomical rule list; no clinical certification.",
        "endpoint": "5/5 correlated packets",
        "source_ids": [],
    },
    {
        "id": "H04",
        "task": "dicom-triplanar-svg",
        "label": "Patient-plane SVG",
        "lead": "User-recalled SVG difficulty; original incident not recovered",
        "source_strength": "Recollection inspires a separately specified fixture",
        "input": "Tilted CT + sparse SEG, four LPS queries and exact sampling rules",
        "output": "Axial, coronal and sagittal SVGs at each query",
        "reference": "Private masks computed from original NIfTI geometry",
        "limit": "Supplied-mask resampling, not unaided anatomy drawing. Shares the source CT with H03; raster SVG is permitted.",
        "endpoint": "12/12 views; 72 label comparisons",
        "source_ids": [],
    },
    {
        "id": "H05",
        "task": None,
        "label": "Vector crop ownership",
        "lead": "Original diagram boundary versus surrounding prose",
        "source_strength": "Recovered crop reports; authentic compact fixture absent",
        "input": "Authentic vector figure with nearby prose remains to be curated",
        "output": "Complete diagram boundary excluding unrelated prose",
        "reference": "Independent boundary truth remains to be established",
        "limit": "Parked source lead. No authored executable task or model result in this round.",
        "endpoint": "Not tested",
        "source_ids": ["E01", "E02", "E03"],
    },
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    audit = json.loads((ROOT / AUDIT).read_text())
    for path, expected in audit["source_pins"].items():
        assert sha(ROOT / path) == expected, path
    DEST.mkdir(parents=True, exist_ok=True)

    def write(name, value):
        (DEST / name).write_text(
            json.dumps(value, separators=(",", ":"), ensure_ascii=False) + "\n"
        )

    write(
        "source.json",
        {
            "counts": audit["retrieval_counts"],
            "excerpts": [
                {
                    k: row[k]
                    for k in [
                        "id",
                        "session_id",
                        "line",
                        "raw_record_sha256",
                        "role",
                        "excerpt",
                        "evidence_class",
                    ]
                }
                for row in audit["excerpts"]
            ],
            "candidates": CANDIDATES,
        },
    )
    controls = [
        {
            "id": "H01",
            "error": "Crop the whole page",
            "evidence": "Excess-area ratios 2.9799 and 2.7248; allowed maximum 1.20",
            "meaning": "Rejects oversized table boxes; not proof of model difficulty.",
        },
        {
            "id": "H02",
            "error": "Accept a result at its deadline",
            "evidence": "Five named author-control traces reject this change",
            "meaning": "At equality, expiration precedes the event; no real outage is simulated.",
        },
        {
            "id": "H03",
            "error": "Require a heart in every scan",
            "evidence": "The clean partial-coverage packet rejects this rule",
            "meaning": "Absence outside the acquired field of view is not an annotation defect.",
        },
        {
            "id": "H04",
            "error": "Mirror, transpose or draw bounding boxes",
            "evidence": "Targeted controls fail the per-label mask comparisons",
            "meaning": "Checks geometric discrimination; not unaided anatomical reasoning.",
        },
    ]
    write(
        "reference.json", {"tasks": audit["tasks"], "checks": audit["checks"], "controls": controls}
    )
    (DEST / "DATA-LICENSE.txt").write_text(
        "LicenseRef-TB3-retained-records: first-party research records and short previously retained work-history excerpts. No raw conversation export or medical image is redistributed. This provenance label grants no new external redistribution rights.\n"
    )
    (DEST / "NOTICE.md").write_text("""# Historical source-study records

This pack explains BR-003 through exact retained excerpt records, candidate contracts, freeze identities and original verifier results. It is a reader-facing author study, not a solver packet or a renewed history search. Source hashes and the eight verified original JSONL record locations are in `groups/anatomy-audit/presentation/sources/history-sourcing-audit.json`. The builder checks all 182 source pins before writing.

`source.json` contains the recounted index, eight short excerpts from six sessions and five specifically authored candidate summaries. The original study selected nine conversations from 237 navigable records; these are not independent model attempts. Quoted history belongs to the recorded user or assistant and is not automatically a validated defect. The exact timeout/reroute and SVG incidents were not recovered.

`reference.json` holds four sets of retained control/model result records and targeted author-control examples. The reader reveals those outcomes separately. All four prototypes passed once under Terra/high; eight oracle/no-op controls are separate executions. H03 and H04 share one CT. Endpoints remain separate: four PDF checks, 22 chat traces, five QA packets and twelve SVG views with 72 label comparisons. There is no pooled accuracy or new trial.

The diagram uses source-record indices and arrows for documented derivation, not physical coordinates, elapsed time or solver search. Amber selects a record; green indicates a byte-verified provenance connection. Dashed amber marks the untested H05 branch. H01 table lineage does not establish a result for authentic vector-diagram crop ownership. H05 and the retired snapshots remain closed to new execution under this explainer scope. Original scores and frozen files are unchanged.

Rebuild with `python scripts/build_history_sourcing_assets.py` after an explicit read-only source audit. Historical authoring modules are never executed. Raw exports, original sessions, snapshot archives and generated HTML/video remain local. Current verification establishes retained bytes and recorded outcomes, not runtime recovery, fresh execution or clinical ground truth.
""")
    files = ["source.json", "reference.json", "NOTICE.md", "DATA-LICENSE.txt"]
    write(
        "manifest.json",
        {
            "id": "retained-history-sourcing-v1",
            "frame": "source-record",
            "units": "record",
            "license": "LicenseRef-TB3-retained-records",
            "label_license": "LicenseRef-TB3-retained-records",
            "reference_policy": "reader-reference-reveal",
            "sources": {
                AUDIT: sha(ROOT / AUDIT),
                "scripts/build_history_sourcing_assets.py": sha(Path(__file__)),
            },
            "checks": audit["checks"],
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
    print(json.dumps({"assets": files, "candidates": len(CANDIDATES), "excerpts": 8}))


if __name__ == "__main__":
    main()
