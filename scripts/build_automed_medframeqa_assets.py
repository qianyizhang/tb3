"""Build native upstream frames plus a symbolic Full contract, without execution."""

import argparse
import hashlib
import json
from pathlib import Path

import yaml

ENTRY = "automedbench-full-medframeqa-task"
PACK = "retained-automed-medframeqa-v1"


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
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source-root", type=Path, required=True)
    ap.add_argument("--receipt", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()
    root = a.source_root.resolve()
    r = json.loads(a.receipt.read_text())
    if r["entry_id"] != ENTRY:
        raise ValueError("Wrong receipt")
    brief = a.receipt.parents[3] / f"presentation/external-tasks/briefs/{ENTRY}.md"
    if hashlib.sha256(brief.read_bytes()).hexdigest() != r["brief_sha256"]:
        raise ValueError("Stale maintained brief")
    for row in r["source_pins"]:
        raw = (root / row["path"]).read_bytes()
        if len(raw) != row["bytes"] or hashlib.sha256(raw).hexdigest() != row["sha256"]:
            raise ValueError("Stale source pin: " + row["path"])
    cfgpin = next(
        x for x in r["source_pins"] if x["path"].endswith("/tasks/medframeqa-task/config.yaml")
    )
    cfg = yaml.safe_load((root / cfgpin["path"]).read_text())
    if cfg["answer_mode"] != "multiple_choice" or cfg["valid_labels"] != list("ABCDE"):
        raise ValueError("Unexpected answer mode/labels")
    if a.output.exists():
        raise FileExistsError(a.output)
    rowpin = next(x for x in r["source_pins"] if x["path"].endswith("/source-evidence/row.bin"))
    retained = next(x for x in r["source_pins"] if x["path"].endswith("/medframe-row.json"))
    upstream = json.loads((root / rowpin["path"]).read_text())["rows"][0]["row"]
    original = json.loads((root / retained["path"]).read_text())["rows"][0]["row"]
    if upstream["question_id"] != original["question_id"] or len(upstream["options"]) != 6:
        raise ValueError("Changed upstream question/option identity; not a Full mapping")
    if sum(bool(upstream.get(f"image_{i}")) for i in range(1, 6)) != 2:
        raise ValueError("Changed upstream native frame count")
    out = a.output.resolve()
    out.mkdir(parents=True)

    def put(name, data):
        (out / name).write_text(json.dumps(data, sort_keys=True, indent=2) + "\n")

    for i in (1, 2):
        pin = next(x for x in r["source_pins"] if x.get("role") == f"upstream-input-frame-{i}")
        raw = (root / pin["path"]).read_bytes()
        if jpeg_size(raw) != (1280, 720):
            raise ValueError("Changed native frame geometry")
        (out / f"frame-{i}.jpg").write_bytes(raw)
    put(
        "source.json",
        {
            "notice": r["top_warning"],
            "basis": "mixed",
            "role": "public-upstream-input-not-Full-case",
            "revision": r["upstream_example"]["upstream_revision"],
            "source_partition": "test",
            "frames": ["frame-1.jpg", "frame-2.jpg"],
            "shape_px": [1280, 720],
            "order": "Source image_1/image_2 slots only; no video time or DICOM slice order",
            "geometry": "JPEG display pixels; no HU, spacing, orientation or native CT measurement",
            "source_options": 6,
            "full_membership": None,
            "full_question": None,
            "patient_identity": None,
            "private_reference": None,
        },
    )
    put(
        "helper.json",
        {
            "valid_labels": cfg["valid_labels"],
            "source_options": 6,
            "mapping": "Full list normalizer maps only first 5 slots to A..E; sixth is dropped. Do not silently adapt this six-option upstream row into a Full question.",
            "tiers": {
                "lite": "Fixed microsoft/llava-med-v1.5-mistral-7b via LLaVA-Med helper and conversation prompt. No weights or inference used.",
                "standard": "Bounded candidate selection with loader/prompt/access guidance; source priority is not measured performance or current availability.",
            },
            "tools": [
                "inspect_image: dimensions/intent/log, not a diagnosis",
                "public_medical_search: whitelist/sanitization, not proved isolation",
                "submit_answer: WORKSPACE_DIR/<question_id>/answer.json",
            ],
            "calibration": "S3 guide requests 15 public calibration rows and reads reference_answer/reasoning_chain.answer when present. Actual verifier accepts>=10; public-gold visibility and separation remain unaudited.",
            "public_reference": None,
        },
    )
    put(
        "operation.json",
        {
            "steps": [
                "Verify question.json and all listed frame paths",
                "Build method-specific prompt with one token per supplied frame",
                "Run provisioned method; parse raw text to A..E",
                "Map label to exact option text and write six-field record",
            ],
            "full_frame_count": None,
            "executed": False,
            "raw_output": None,
        },
    )
    fields = {
        "question_id": "matching question string",
        "predicted_label": "A..E",
        "predicted_answer": "selected option text",
        "raw_model_output": "string from genuine model call",
        "model_name": "nonempty string",
        "runtime_s": "nonnegative number, seconds",
    }
    put(
        "output.json",
        {
            "path": "<agent_dir>/<question_id>/answer.json",
            "fields": fields,
            "values": dict.fromkeys(fields),
            "score": None,
            "rating": None,
            "private_reference": None,
            "format": "Matching question_id, six required keys (extra keys accepted), stripped/uppercased A..E, string fields and truthy model name. Numeric runtime >=0; no finite or boolean exclusion guard. Nonempty option text must equal selected option. Empty text loophole is not an output recommendation.",
            "accuracy": "Correct normalized label / all evaluator-selected question_ids (explicit list or discovered split), rounded 4, zero when empty. Missing/invalid/placeholder remain denominator. Not frame/video/patient accuracy.",
            "format_gate": "output_format_valid: every file strict-valid. submission_format_valid: strict-valid fraction>=0.5; denominator max(expected,1). Scorer label-valid is weaker than format-valid.",
            "completion": "Prediction files / all questions; existence is not valid inference. Parse/valid/placeholder rates also use all questions.",
            "rating_rule": "F if graded format gate false, no scorer-valid answers or file completion<0.5; otherwise A accuracy>=.40, B>=.25, else C. No measured rating.",
            "workflow": "Non-None step weights renormalized. S2 mean env/model-call/smoke evidence. S4 half completion/parse with placeholder/model-call/low-quality caps; S5 half anyvalid/gradedformat. Overall half workflow/half accuracy.",
            "limits": "Exact private label agreement is not clinical validation. Public test questions/frames do not establish video-disjoint or patient-independent generalization. Open-ended scoring exists but is not this configured task.",
            "checker_difference": "Scorer label-valid is weaker than strict schema. Both-empty text with a retained valid A..E label can pass both checks and receive label credit; evidence/log guards are separate. Neither validity nor accuracy proves genuine inference.",
        },
    )
    (out / "NOTICE.md").write_text(
        r["actual_data_gap"]
        + "\n"
        + r["acquisition_route"]
        + "\nTwo public upstream test frames, not mapped Full cases. No public gold/reasoning, private reference or generated answer.\n"
    )
    (out / "DATA-LICENSE.txt").write_text(
        "MedFrameQA by SuhaoYu1020; pinned official dataset card declares CC BY4.0.\nSource: https://huggingface.co/datasets/SuhaoYu1020/MedFrameQA/tree/96083ae9405b2fdb687005c65902f2ee3d7c9f12\nLicense: https://creativecommons.org/licenses/by/4.0/\nTwo native JPEG frames copied byte-identically from upstream public test row0; no image edits, source answer text or derived finding. Original task-specific symbolic teaching records accompany them. Full case membership/option conversion absent.\n"
    )
    names = [
        "DATA-LICENSE.txt",
        "NOTICE.md",
        "helper.json",
        "operation.json",
        "output.json",
        "source.json",
        "frame-1.jpg",
        "frame-2.jpg",
    ]
    assets = [
        {
            "file": name,
            "bytes": (out / name).stat().st_size,
            "sha256": hashlib.sha256((out / name).read_bytes()).hexdigest(),
            "provenance": "source-derived-teaching",
            "role": "illustration",
        }
        for name in names
    ]
    put(
        "manifest.json",
        {
            "id": PACK,
            "frame": "MedFrameQA-upstream-JPEG-frames-plus-Full-contract",
            "units": "px",
            "license": "CC-BY-4.0",
            "label_license": None,
            "reference_policy": "no-reference-assets",
            "illustration_basis": "mixed",
            "sources": {
                f"presentation/external-tasks/sources/{ENTRY}-resolution.json": hashlib.sha256(
                    a.receipt.read_bytes()
                ).hexdigest()
            },
            "assets": assets,
            "checks": {
                "matching_Full_case": False,
                "model_run": False,
                "scorer_run": False,
                "private_reference": False,
                "upstream_input_frames": True,
            },
        },
    )


if __name__ == "__main__":
    main()
