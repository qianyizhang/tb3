"""Audit retained CT context inference and schema-only diagnostics; no model calls."""

import argparse
import copy
import csv
import hashlib
import importlib.util
import json
import tempfile
from pathlib import Path

import nibabel as nib

ROOT = Path(__file__).resolve().parents[1]
GROUP = Path("groups/longitudinal-reading")
EXPERIMENT = GROUP / "experiments/longitudinal-ct-context-inference-astra-medium"
ATTEMPT = "attempt-0a8df9d2ca4a4034"
JOB = Path(f".local/attempts/{ATTEMPT}/job/task__Rzm9L2L")


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path):
    return json.loads((ROOT / path).read_text())


def audit():
    pins = {}

    def pin(path, expected=None):
        path = Path(path)
        digest = sha(ROOT / path)
        if expected is not None:
            assert digest == expected, str(path)
        pins[str(path)] = digest
        return digest

    freeze_path = next((ROOT / EXPERIMENT / "freezes").glob("*.json")).relative_to(ROOT)
    freeze = read(freeze_path)
    task = Path(freeze["snapshot_path"])
    for base in [task, Path(freeze["source_path"])]:
        for name, digest in freeze["files"].items():
            pin(base / name, digest)
    for path in (ROOT / EXPERIMENT).rglob("*"):
        if path.is_file():
            pin(path.relative_to(ROOT))
    old_path = GROUP / "findings/evidence/longitudinal-ct-context-inference.json"
    old = read(old_path)
    for name, digest in old["source_hashes"].items():
        pin(Path(name).relative_to(ROOT), digest)
    for name, digest in old["audit"]["artifacts"].items():
        pin(JOB / name, digest)
    for path in (ROOT / JOB / "artifacts/app/work").glob("*"):
        if path.is_file() and path.suffix != ".npy":
            pin(path.relative_to(ROOT))
    for path in [
        old_path,
        GROUP / "findings/longitudinal-ct-context-hypothesis.md",
        GROUP / "methods/longitudinal-ct-context-v1/protocol.md",
        GROUP / "methods/longitudinal-ct-context-v1/inference-instruction.md",
        GROUP / "methods/longitudinal-ct-context-v1/context-block.md",
        Path("scripts/audit_ct_context.py"),
    ]:
        pin(path)
    assert (ROOT / task / "instruction.md").read_bytes() == (
        ROOT / GROUP / "methods/longitudinal-ct-context-v1/inference-instruction.md"
    ).read_bytes()
    demo = Path(old["source_provenance"]["demographics_file"])
    pin(demo, old["source_provenance"]["demographics_sha256"])
    rows = list(csv.DictReader((ROOT / demo).open()))
    row = next(r for r in rows if r["ID"] == old["source_provenance"]["patient"])
    assert row == old["source_provenance"]["demographics_row"]
    answer = ROOT / JOB / "artifacts/app/answer"
    payload = read(JOB / "artifacts/app/answer/context.json")
    assert payload["fields"] == old["fields"]
    score = ROOT / task / "tests/score.py"
    spec = importlib.util.spec_from_file_location("retained_context_score", score)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    replay = module.validate(answer)
    assert replay == read(JOB / "verifier/metrics.json")
    diagnostics = []
    for name in ["all-unknown", "unsupported-assertions", "unknown-with-value", "missing-report"]:
        altered = copy.deepcopy(payload)
        for field in altered["fields"].values():
            field.update(
                status="unknown",
                value=None,
                confidence=1.0,
                basis="Author diagnostic: no evidence assessment performed.",
                alternatives=[],
            )
        if name == "unsupported-assertions":
            for field in altered["fields"].values():
                field.update(status="observed", value="Unsupported invented claim")
        if name == "unknown-with-value":
            altered["fields"]["age_years"]["value"] = 99
        with tempfile.TemporaryDirectory(prefix="tb3-context-validator-") as directory:
            folder = Path(directory)
            (folder / "context.json").write_text(json.dumps(altered))
            if name != "missing-report":
                (folder / "report.md").write_text(
                    "Author-created schema diagnostic; not a clinical assessment."
                )
            result = module.validate(folder)
        expected = name in {"all-unknown", "unsupported-assertions"}
        assert result["contract_valid"] == expected
        diagnostics.append(
            {
                "id": name,
                "contract_valid": expected,
                "scientific_score": result["scientific_score"],
                "errors": [
                    e.replace(str(folder), "<temporary-author-diagnostic>")
                    for e in result["errors"]
                ],
            }
        )
    controls = []
    for attempt_id in [ATTEMPT, "attempt-f27395e6240b4c61", "attempt-427be2c34fc347aa"]:
        base = ROOT / ".local/attempts" / attempt_id
        execution = read((base / "execution.json").relative_to(ROOT))
        pin((base / "execution.json").relative_to(ROOT))
        result_path = next((base / "job").glob("task__*/result.json"))
        result = read(result_path.relative_to(ROOT))
        pin(result_path.relative_to(ROOT))
        assert execution["execution_state"] == "completed"
        assert execution["frozen_payload_unchanged"]
        assert result["exception_info"] is None
        controls.append(
            {
                "attempt_id": attempt_id,
                "execution": execution,
                "reward": result["verifier_result"]["rewards"]["reward"],
            }
        )
    assert [r["reward"] for r in controls] == [1.0, 1.0, 0.0]
    geometry = []
    for visit in ["baseline", "followup"]:
        image = nib.load(ROOT / task / f"environment/data/{visit}.nii.gz")
        h = image.header
        assert all(bytes(h[k]).rstrip(b"\0") == b"" for k in ["descrip", "aux_file", "intent_name"])
        assert len(h.extensions) == 0
        geometry.append(
            {
                "visit": visit,
                "shape": list(image.shape),
                "spacing_mm": [float(x) for x in h.get_zooms()],
                "affine": image.affine.tolist(),
                "axes": list(nib.aff2axcodes(image.affine)),
                "descrip": "",
                "aux_file": "",
                "intent_name": "",
                "extensions": 0,
                "toffset": float(h["toffset"]),
                "time_pixdim": float(h["pixdim"][4]),
            }
        )
        assert list(nib.aff2axcodes(image.affine)) == ["L", "P", "S"]
    trajectory = read(JOB / "agent/trajectory.json")
    observations = [
        r.get("content", "")
        for step in trajectory["steps"]
        for r in step.get("observation", {}).get("results", [])
    ]
    blocks = sum(
        str(x).count("'type': 'input_image'") + str(x).count('"type": "input_image"')
        for x in observations
    )
    assert blocks == 14, blocks
    counts = {
        status: sum(f["status"] == status for f in payload["fields"].values())
        for status in ["observed", "inferred", "unknown"]
    }
    assert counts == {"observed": 0, "inferred": 2, "unknown": 7}
    return {
        "schema": 1,
        "task_digest": freeze["task_digest"],
        "task": str(task),
        "job": str(JOB),
        "source_pins": pins,
        "geometry": geometry,
        "fields": payload["fields"],
        "status_counts": counts,
        "source_provenance": old["source_provenance"],
        "diagnostics": diagnostics,
        "controls": controls,
        "checks": {
            "frozen_files": len(freeze["files"]) * 2,
            "exact_saved_validator_replay": True,
            "image_observation_blocks": blocks,
            "agent_seconds": old["agent_seconds"],
            "schema_diagnostics": 4,
            "no_new_model_execution": True,
        },
        "limits": "One retained context attempt. Schema checks do not assess diagnosis or calibration. Patient metadata and cohort descriptions are separate; individual surgical records are unavailable. Saved-output diagnostics are author-created, not model trials.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = audit()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as stream:
        stream.write(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"pins": len(result["source_pins"]), "checks": result["checks"]}))
