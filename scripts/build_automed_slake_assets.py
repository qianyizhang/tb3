"""Build an exact public SLAKE pair and symbolic Full contract; never run a scorer."""

import argparse
import hashlib
import json
import struct
import zlib
from pathlib import Path

import yaml

ENTRY = "automedbench-full-slake-task"
PACK = "retained-automed-slake-v1"
FRAME = "SLAKE-native-train-question-plus-Full-contract"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source-root", type=Path, required=True)
    ap.add_argument("--receipt", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()
    root = a.source_root.resolve()
    r = json.loads(a.receipt.read_text())
    if r["entry_id"] != ENTRY or a.output.exists():
        raise ValueError("Wrong entry or nonfresh output")
    pins = r["source_pins"]
    for pin in pins:
        raw = (root / pin["path"]).read_bytes()
        if len(raw) != pin["bytes"] or hashlib.sha256(raw).hexdigest() != pin["sha256"]:
            raise ValueError("Stale source pin: " + pin["path"])

    def read(suffix):
        matches = [p for p in pins if p["path"].endswith(suffix)]
        if len(matches) != 1:
            raise ValueError("Ambiguous source " + suffix)
        return (root / matches[0]["path"]).read_bytes()

    cfg = yaml.safe_load(read("/tasks/slake-task/config.yaml"))
    if cfg["answer_mode"] != "open_ended" or cfg["dataset"] != "SLAKE-EN":
        raise ValueError("Changed Full mode")
    row = json.loads(read("/slake-row.json"))["rows"][0]["row"]
    fresh = json.loads(read("/source-evidence/row.bin"))["rows"][0]["row"]
    if row != fresh or (row["qid"], row["img_name"], row["q_lang"], row["answer_type"]) != (
        0,
        "xmlab1/source.jpg",
        "en",
        "OPEN",
    ):
        raise ValueError("Changed public row/image join")
    member = read("/slake-member.bin")
    signature, _, _, compression, _, _, _, _, _, nlen, xlen = struct.unpack(
        "<4s5H3I2H", member[:30]
    )
    if (
        signature != b"PK\x03\x04"
        or compression != 8
        or member[30 : 30 + nlen] != b"imgs/xmlab1/source.jpg"
    ):
        raise ValueError("Changed ZIP member identity")
    native = zlib.decompress(member[30 + nlen + xlen :], -15)
    if zlib.crc32(native) != int(r["zip_member"]["crc32"], 16) or native != read(
        "/slake-train-0.jpg"
    ):
        raise ValueError("Native image CRC or retained bytes differ")
    out = a.output.resolve()
    out.mkdir(parents=True)

    def put(name, data):
        (out / name).write_text(json.dumps(data, sort_keys=True, indent=2) + "\n")

    (out / "image.jpg").write_bytes(native)
    put(
        "source.json",
        {
            "notice": r["top_warning"],
            "basis": "mixed",
            "source_partition": "train",
            "revision": r["upstream_revision"],
            "question": row["question"],
            "source_question_id": "train qid0",
            "source_image_path": row["img_name"],
            "source_image_id": row["img_id"],
            "shape_px": [256, 256],
            "full_membership": None,
            "full_question": None,
            "private_reference": None,
            "geometry": "Native JPEG display pixels; no physical spacing, orientation, acquisition geometry or patient identity",
            "options": None,
            "question_unit": "Question IDs; repeated images/patients are different units",
        },
    )
    put(
        "helper.json",
        {
            "initially_visible": False,
            "reset": "Scene exit and backward replay; explicit hide",
            "tiers": {
                "lite": "Fixed microsoft/llava-med-v1.5-mistral-7b via LLaVA-Med loader/conversation prompt. No inference used.",
                "standard": "S1 lists six candidates; model_info lists five. Copied PathVQA pathology/MCQ wording is unresolved, not SLAKE input evidence. No access/runtime/model comparison verified.",
            },
            "calibration": "Lite: exactly 15 / checklist ≥15; first 15 drops invalid gold, no top-up. Standard: 1-10 smoke/schema. Generic verifier: ≥10, optional gold; invalid gold/raw each fail only above 20%. No private isolation proof.",
            "tools": [
                "inspect_image: dimensions/intent/log, not diagnosis",
                "public_medical_search: whitelist/sanitization, not proof of isolation",
                "submit_answer: WORKSPACE_DIR/<question_id>/answer.json",
            ],
        },
    )
    put(
        "reference.json",
        {
            "public_answer": row["answer"],
            "public_answer_role": "Public train annotation · explicit reader reveal only; not Full gold, diagnosis or model output",
        },
    )
    put(
        "operation.json",
        {
            "steps": [
                "Read exact question and referenced images",
                "Build declared method prompt; preserve raw decoded text",
                "Normalize a short phrase or exact yes/no; do not impose five-word cap",
                "Write six-field answer with model/runtime provenance",
            ],
            "normalization": "Lowercase; remove punctuation; collapse whitespace; map selected yes/no synonyms, number words and standalone medical abbreviations.",
            "configured_mode": "open_ended",
            "options": None,
            "executed": False,
            "raw_output": None,
        },
    )
    fields = {
        "question_id": "matching question string",
        "predicted_label": "conventionally empty; ignored in open mode",
        "predicted_answer": "nonempty short phrase or exact yes/no",
        "raw_model_output": "string from genuine model call",
        "model_name": "nonempty string",
        "runtime_s": "nonnegative numeric seconds",
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
            "format": "Six keys, exact ID, nonempty string answer, raw string, nonempty model, nonnegative numeric runtime; label ignored. No five-word or schema word-count limit. Extra keys, bool runtime and nonfinite runtime have no explicit rejection guard; not recommendations.",
            "accuracy": "Heuristic: strict normalized yes/no for binary gold, otherwise0.5EM+0.5tokenF1; mean over all evaluator-supplied question IDs (default: discovered split IDs). Missing/invalid/placeholder remain denominator. Binary diagnostic denominator: yes/no gold subset.",
            "judge": "Optional answer judge replaces primary accuracy: sum judge scores/all evaluator-supplied question IDs (default: discovered split IDs); heuristic diagnostics remain. Only parsed records judged; backend fallback reported. --llm-judge workflow route is separate.",
            "format_gate": "Every file strict-valid for output_format_valid; strict-valid fraction>=0.5 for submission_format_valid, denominator max(expected,1).",
            "completion": "Prediction files/all evaluator-supplied question IDs (default: discovered split IDs); existence is not valid inference. Scorer-valid is weaker than strict schema.",
            "rating_rule": "F if graded gate false, no scorer-valid or filecompletion<0.5; otherwise A primaryaccuracy>=.40, B>=.25, else C. No measured rating.",
            "workflow": "Active non-None weights renormalized; guarded S4 halfcompletion/halfparse, S5 halfanyvalid/halfgradedformat. Overall halfworkflow/halfprimaryaccuracy.",
            "limits": "Source train annotation is not Full test gold, independent diagnosis or clinical/model performance. Image/patient split independence unknown.",
            "checker_difference": "Both-empty answer/raw is not placeholder but invalid in open mode, earning no credit. Nonempty answer with empty raw is placeholder; scorer string-coerces text and validates fewer fields than format checker.",
        },
    )
    (out / "NOTICE.md").write_text(
        r["actual_data_gap"]
        + "\n"
        + r["acquisition_route"]
        + "\nPublic training annotation is hidden by default; explicit reader reveal is educational, never a prediction/private reference.\n"
    )
    (out / "DATA-LICENSE.txt").write_text(
        "SLAKE by Bo Liu and Xiao-Ming Wu; official BoKelvin/SLAKE card declares CC BY4.0.\nSource: https://huggingface.co/datasets/BoKelvin/SLAKE/tree/a9083ce6c34ac3ffb17671a605962924d8a8f9e9\nProject: https://www.med-vqa.com/slake/\nLicense: https://creativecommons.org/licenses/by/4.0/\nNative imgs/xmlab1/source.jpg copied byte-identically; no image edits. Train qid0 English question and annotation preserved for local noncommercial teaching with reader reveal. Exact Full membership unverified. Task-specific symbolic contract text accompanies them.\n"
    )
    names = [
        "DATA-LICENSE.txt",
        "NOTICE.md",
        "helper.json",
        "image.jpg",
        "operation.json",
        "output.json",
        "source.json",
        "reference.json",
    ]
    assets = [
        {
            "file": n,
            "bytes": (out / n).stat().st_size,
            "sha256": hashlib.sha256((out / n).read_bytes()).hexdigest(),
            "provenance": "source-derived-teaching",
            "role": "reader-reference-reveal"
            if n == "reference.json"
            else "input-preview"
            if n == "image.jpg"
            else "illustration",
        }
        for n in names
    ]
    put(
        "manifest.json",
        {
            "id": PACK,
            "frame": FRAME,
            "units": "px",
            "license": "CC-BY-4.0",
            "label_license": None,
            "reference_policy": "reader-reference-reveal",
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
                "native_image": True,
                "public_annotation_reader_reveal": True,
            },
        },
    )


if __name__ == "__main__":
    main()
