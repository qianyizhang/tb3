"""Build an exact public VQA-RAD pair and symbolic Full contract; never run a scorer."""

import argparse
import hashlib
import json
from pathlib import Path

import yaml

ENTRY = "automedbench-full-vqa-rad-task"
PACK = "retained-automed-vqa-rad-v1"
FRAME = "VQA-RAD-native-train-question-plus-Full-contract"


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
    if r["entry_id"] != ENTRY or a.output.exists():
        raise ValueError("Wrong entry or nonfresh output")
    brief = a.receipt.parent.parent / "briefs" / f"{ENTRY}.md"
    if hashlib.sha256(brief.read_bytes()).hexdigest() != r["brief_sha256"]:
        raise ValueError("Stale brief pin")
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

    cfg = yaml.safe_load(read("/tasks/vqa-rad-task/config.yaml"))
    if cfg["answer_mode"] != "open_ended" or cfg["dataset"] != "VQA-RAD":
        raise ValueError("Changed Full mode")
    row = json.loads(read("/vqarad-row.json"))["rows"][0]["row"]
    fresh = json.loads(read("/source-evidence/row.bin"))["rows"][0]["row"]
    for key in ["question", "answer"]:
        if row[key] != fresh[key]:
            raise ValueError("Changed public row/question/annotation pairing")
    for key in ["width", "height"]:
        if row["image"][key] != fresh["image"][key]:
            raise ValueError("Changed upstream image dimensions")
    if row["image"]["src"].split("?")[0] != fresh["image"]["src"].split("?")[0]:
        raise ValueError("Changed upstream cached image identity")
    native = read("/source-evidence/image.bin")
    if native != read("/vqarad-train-0.jpg") or (
        fresh["image"]["width"],
        fresh["image"]["height"],
    ) != (566, 555):
        raise ValueError("Native viewer JPEG differs from retained source")
    if jpeg_size(native) != (566, 555):
        raise ValueError("Changed actual JPEG pixel dimensions")
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
            "source_question_id": "upstream train row0; no native qid field",
            "source_image_path": fresh["image"]["src"].split("?")[0],
            "source_image_id": None,
            "shape_px": [566, 555],
            "full_membership": None,
            "full_question": None,
            "private_reference": None,
            "geometry": "Public mirror viewer JPEG pixels; original MedPix markings retained; no DICOM geometry, physical spacing, trustworthy orientation or patient identity",
            "options": None,
            "question_unit": "Question IDs; repeated images/patients are different units",
        },
    )
    put(
        "helper.json",
        {
            "public_answer": row["answer"],
            "public_answer_role": "Public train annotation · educational reveal only; not Full gold, diagnosis or model output",
            "initially_visible": False,
            "reset": "Scene exit and backward replay; explicit hide",
            "tiers": {
                "lite": "Fixed microsoft/llava-med-v1.5-mistral-7b via LLaVA-Med loader/conversation prompt. No inference used.",
                "standard": "Standard S1 compares six candidates incl LLaVA; model_info lists five and wrongly says multiple-choice. Config/S1 open-ended; availability/performance unverified.",
            },
            "calibration": "Task S3 first15 with public gold; missing gold dropped, checklist requires >=15 but example lacks top-up. Generic verifier >=10 with optional gold; smoke1-10 separate. Calibration/private separation unaudited.",
            "tools": [
                "inspect_image: dimensions/intent/log, not diagnosis",
                "public_medical_search: whitelist/sanitization, not proof of isolation",
                "submit_answer: WORKSPACE_DIR/<question_id>/answer.json",
            ],
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
            "format": "Six keys, exact ID, nonempty string answer, raw string, nonempty model, nonnegative numeric runtime; label ignored. No five-word or schema word-count limit. Extra keys/bool/nonfinite-runtime type limitations are not recommendations.",
            "accuracy": "Heuristic: strict normalized yes/no for binary gold, otherwise0.5EM+0.5tokenF1; mean over all discovered question_ids by default, explicitly supplied IDs otherwise; IDs not deduplicated. Missing/invalid/placeholder remain denominator. Binary diagnostic denominator: yes/no gold subset.",
            "judge": "Optional answer judge replaces primary accuracy: sum judge scores/all evaluator-supplied question IDs (default discovered split); heuristic diagnostics remain. Only parsed records judged; backend fallback reported. --llm-judge workflow route is separate.",
            "format_gate": "Every file strict-valid for output_format_valid; strict-valid fraction>=0.5 for submission_format_valid, denominator max(expected,1).",
            "completion": "Prediction files/all questions; existence is not valid inference. Scorer-valid is weaker than strict schema.",
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
        "VQA-RAD by Jason J Lau, Soumya Gayen, Asma Ben Abacha and Dina Demner-Fushman; public mirror curated by flaviagiammarino; pinned flaviagiammarino/vqa-rad mirror card declares CC0 1.0.\nSource: https://huggingface.co/datasets/flaviagiammarino/vqa-rad/tree/bcf91e7654fb9d51c8ab6a5b82cacf3fafd2fae9\nProject: https://osf.io/89kps/\nLicense: https://creativecommons.org/publicdomain/zero/1.0/\nPublic train row0 viewer JPEG copied byte-identically; original MedPix source/uploader/date markings retained, no image edits. English question and annotation preserved for local noncommercial teaching with reader reveal. Original OSF terms not independently inspected; mirror CC0 declaration alone retained. Exact Full membership unverified. Task-specific symbolic contract text accompanies them.\n"
    )
    names = [
        "DATA-LICENSE.txt",
        "NOTICE.md",
        "helper.json",
        "image.jpg",
        "operation.json",
        "output.json",
        "source.json",
    ]
    assets = [
        {
            "file": n,
            "bytes": (out / n).stat().st_size,
            "sha256": hashlib.sha256((out / n).read_bytes()).hexdigest(),
            "provenance": "source-derived-teaching",
            "role": "illustration",
        }
        for n in names
    ]
    put(
        "manifest.json",
        {
            "id": PACK,
            "frame": FRAME,
            "units": "px",
            "license": "CC0-1.0",
            "label_license": None,
            "reference_policy": "no-reference-assets",
            "illustration_basis": "mixed",
            "sources": {
                f"presentation/external-tasks/briefs/{ENTRY}.md": hashlib.sha256(
                    brief.read_bytes()
                ).hexdigest(),
                f"presentation/external-tasks/sources/{ENTRY}-resolution.json": hashlib.sha256(
                    a.receipt.read_bytes()
                ).hexdigest(),
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
