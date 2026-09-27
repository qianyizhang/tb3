"""Audit saved dental-v2 evidence without executing a solver or modifying a run."""

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

import nibabel as nib
import numpy as np

EXPERIMENTS = ["dental-f002-contract-v2-astra-medium", "dental-f002-reference-v2-astra-medium"]
TEETH = [q * 10 + n for q in range(1, 5) for n in range(1, 9)]


def read(path):
    return json.loads(path.read_text())


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def pooled(gt, prediction, ids):
    g, p = np.isin(gt, ids), np.isin(prediction, ids)
    ng, np_, overlap = int(g.sum()), int(p.sum()), int((g & p).sum())
    return {
        "gt_voxels": ng,
        "prediction_voxels": np_,
        "intersection": overlap,
        "precision": overlap / np_ if np_ else None,
        "recall": overlap / ng if ng else None,
        "dice": 2 * overlap / (ng + np_) if ng + np_ else None,
    }


def audit(root, out, fine):
    out.mkdir(parents=True, exist_ok=False)
    pins = {}

    def pin(path, expected=None):
        path = Path(path)
        relative = path.relative_to(root) if path.is_absolute() else path
        digest = sha(root / relative)
        if expected is not None:
            assert digest == expected, str(relative)
        pins[str(relative)] = digest
        return root / relative

    group = Path("groups/anatomy-audit")
    pin(Path(__file__))
    method = group / "methods/dental-reference-ablation"
    base = Path(".local/dental-reference-ablation-20260921")
    prep = read(pin(base / "preparation-receipt.json"))
    selection = read(pin(base / "reference-selection.json"))
    common = pin(method / "instruction.md", prep["common_instruction_sha256"]).read_text()
    comparison = read(pin(base / "comparison/comparison.json"))
    controls = read(pin(base / "lifecycle-controls.json"))
    pin(base / "scorer-controls.json")
    pin(base / "image-pins.json")
    prior = read(pin(group / "findings/evidence/dental-reference-example-comparison.json"))
    mechanism = read(pin(group / "findings/evidence/dental-fine-structure-failure-analysis.json"))
    source_contract = read(pin(group / "findings/evidence/dental-dataset-contract-audit.json"))
    for item in source_contract["sources"]:
        pin(item["file"], item["sha256"])
    for path, digest in mechanism["input_sha256"].items():
        pin(path, digest)
    for name in ["diagnose_fine_structures.py", "render_fine_diagnosis.py", "render_comparison.py"]:
        pin(method / name)

    fresh = {}
    for name in ["diagnostics.json", "prior-clipping.json", "supplement.json"]:
        a = read(pin(fine / name))
        b = read(pin(base / "fine-structure-diagnosis" / name))
        if name == "supplement.json":
            for path, digest in a["figures"].items():
                pin(fine / path, digest)
            for path, digest in b["figures"].items():
                pin(base / "fine-structure-diagnosis" / path, digest)
            # Font/image encoding can differ; every numerical and source field must match.
            a = {k: v for k, v in a.items() if k != "figures"}
            b = {k: v for k, v in b.items() if k != "figures"}
        assert a == b, name
        fresh[name] = a
    for path, digest in fresh["diagnostics.json"]["input_sha256"].items():
        pin(path, digest)

    tasks = [Path(".local") / exp / "task" for exp in EXPERIMENTS]
    labels = read(pin(tasks[0] / "environment/data/labels.json"))
    assert len(labels) == 78 and max(map(int, labels)) == 148
    for name in [
        "environment/data/ct.nii.gz",
        "environment/data/labels.json",
        "tests/reference.nii.gz",
        "tests/score.py",
    ]:
        assert sha(pin(tasks[0] / name)) == sha(pin(tasks[1] / name))
    for task in tasks:
        instruction = pin(task / "instruction.md").read_text()
        assert instruction.split("## Available example data")[0].strip() == common.strip()
    assert "No annotated example" in (root / tasks[0] / "instruction.md").read_text()
    assert "/app/reference/segmentation.nii.gz" in (root / tasks[1] / "instruction.md").read_text()

    target = nib.load(pin(tasks[0] / "environment/data/ct.nii.gz"))
    reference = nib.load(pin(tasks[0] / "tests/reference.nii.gz"))
    gt = np.asanyarray(reference.dataobj).astype(np.uint8)
    cases = []
    for case, ct, mask, original_ct, original_mask in [
        (
            "F002",
            target,
            reference,
            Path(".local/dental-followups-20260921/source/ToothFairy3F_002_0000.nii.gz"),
            Path(".local/dental-followups-20260921/source/ToothFairy3F_002.nii.gz"),
        ),
        (
            "F008",
            nib.load(pin(tasks[1] / "environment/reference/ct.nii.gz")),
            nib.load(pin(tasks[1] / "environment/reference/segmentation.nii.gz")),
            base / "source/ToothFairy3F_008_0000.nii.gz",
            base / "source/ToothFairy3F_008.nii.gz",
        ),
    ]:
        source_ct = nib.load(pin(original_ct, selection["ct_sha256"] if case == "F008" else None))
        source_mask = nib.load(
            pin(original_mask, selection["gt_sha256"] if case == "F008" else None)
        )
        for staged, original in [(ct, source_ct), (mask, source_mask)]:
            np.testing.assert_array_equal(staged.dataobj, original.dataobj)
            np.testing.assert_array_equal(staged.affine, original.affine)
            for getter in ["get_qform", "get_sform"]:
                a, ac = getattr(staged, getter)(coded=True)
                b, bc = getattr(original, getter)(coded=True)
                np.testing.assert_array_equal(a, b)
                assert ac == bc
        np.testing.assert_array_equal(ct.affine, mask.affine)
        np.testing.assert_allclose(ct.header.get_zooms(), [0.3] * 3, atol=1e-7)
        assert nib.aff2axcodes(ct.affine) == ("L", "P", "S")
        ids, counts = np.unique(np.asanyarray(mask.dataobj), return_counts=True)
        counts = {str(int(k)): int(v) for k, v in zip(ids, counts, strict=True)}
        if case == "F008":
            assert counts == selection["counts"]
        cases.append(
            {
                "case": case,
                "shape": list(ct.shape),
                "spacing_mm": list(map(float, ct.header.get_zooms())),
                "affine": ct.affine.tolist(),
                "header_axis_codes": list(nib.aff2axcodes(ct.affine)),
                "original_ct": str(original_ct),
                "original_mask": str(original_mask),
                "source_arrays_and_grid_exactly_equal": True,
                "reference_counts": counts,
                "semantic_axis_contract": "RPI, explicitly specified independently of retained LPS header",
                "physical_laterality_adjudicated": False,
            }
        )

    # Only this inspected, frozen evaluator's pure function is invoked. The CLI
    # logging path and all saved solver programs remain unexecuted.
    scorer = pin(tasks[0] / "tests/score.py")
    namespace = {"__name__": "dental_v2_saved_output_replay"}
    exec(compile(scorer.read_text(), str(scorer), "exec"), namespace)
    replays, freezes, access, models = [], {}, [], []
    for exp, task in zip(EXPERIMENTS, tasks, strict=True):
        exp_dir = group / "experiments" / exp
        pin(exp_dir / "protocol.md")
        for path in (root / exp_dir / "freezes").glob("*.json"):
            freeze = read(pin(path))
            digest = hashlib.sha256(
                json.dumps(freeze["files"], sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest()
            assert digest == freeze["task_digest"]
            assert freeze["files"] == prep["experiments"][exp]["files"]
            for name, expected in freeze["files"].items():
                pin(Path(freeze["snapshot_path"]) / name, expected)
                pin(Path(freeze["source_path"]) / name, expected)
            freezes[digest] = {"experiment": exp, "file_count": len(freeze["files"])}
        for path in sorted((root / exp_dir / "evaluations").glob("observation-*.json")):
            obs = read(pin(path))
            for item in obs["evidence"]:
                pin(item["path"], item["sha256"])
            assert obs["exception_type"] is None
            trial = pin(obs["source_result"]).parent
            saved = read(pin(trial / "verifier/metrics.json"))
            answer = trial / "artifacts/app/answer/segmentation.nii.gz"
            if answer.exists():
                pin(answer)
            replay = namespace["score"](answer, root / task / "tests/reference.nii.gz", labels)
            assert replay == saved, obs["attempt_id"]
            if obs["agent"] in ["oracle", "nop"]:
                assert controls[exp][obs["agent"]]["attempt_id"] == obs["attempt_id"]
                assert replay["macro_dice"] == (1.0 if obs["agent"] == "oracle" else 0.0)
            else:
                assert obs["agent"] == "codex" and obs["reasoning_effort"] == "medium"
                assert obs["model"] == "openai/gpt-6-astra"
                models.append((exp, replay, answer))
            replays.append(
                {
                    "experiment": exp,
                    "attempt": obs["attempt_id"],
                    "agent": obs["agent"],
                    "score": replay,
                    "answer": str(answer.relative_to(root)),
                    "seconds": obs["timing"]["agent"],
                    "usage": obs["usage"],
                }
            )
            print("Exact saved replay:", obs["attempt_id"], flush=True)
        local = Path(".local") / exp
        terminal = read(pin(local / "terminal-review.json"))
        for path, expected in terminal["evidence_sha256"].items():
            pin(path, expected)
        assert terminal["execution"]["execution_state"] == "completed"
        assert terminal["execution"]["frozen_payload_unchanged"]
        assert terminal["execution"]["exit_code"] == 0 and terminal["exception"] is None
        assert terminal["missing_evidence"] == []
        isolation = read(pin(local / "runtime-isolation.json"))
        assert all(n["internal"] for n in isolation["networks"].values())
        assert {m["Destination"] for m in isolation["mounts"]} == {
            "/logs/agent",
            "/logs/artifacts",
            "/logs/verifier",
        }
        assert all(isolation["files"]["private_absent"].values())
        assert {"/tests", "/solution", "/Users", "/var/run/docker.sock"} <= isolation["files"][
            "private_absent"
        ].keys()
        audit_access = read(pin(local / "access-audit.json"))
        assert {r["target"] for r in audit_access["transport"] if r["allowed"]} == {
            "chatgpt.com:443"
        }
        if exp == EXPERIMENTS[0]:
            assert isolation["files"]["private_absent"]["/app/reference"]
        else:
            assert set(isolation["files"]["reference"]) == {
                "/app/reference/ct.nii.gz",
                "/app/reference/segmentation.nii.gz",
            }
        trace = pin(Path(isolation["trial_path"]) / "agent/codex.txt")
        types, commands, diagnostic_lines = Counter(), [], []
        for lineno, line in enumerate(trace.read_text().splitlines(), 1):
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                assert line.startswith(("WARNING:", "Reading additional input")) or (
                    " ERROR codex_core::tools::router:" in line
                    or " ERROR codex_models_manager::manager:" in line
                ), (trace, lineno)
                diagnostic_lines.append(lineno)
                continue
            if event.get("type") != "item.completed":
                continue
            item = event["item"]
            types[item["type"]] += 1
            if item["type"] == "command_execution":
                commands.append((lineno, item))
        assert dict(types) == audit_access["completed_item_types"]
        selected = []
        for lineno, item in commands:
            command = item["command"]
            names = [
                name
                for name in [
                    "register2.py",
                    "pulp_calibrate.py",
                    "pulps.py",
                    "assemble.py",
                    "canals_refine.py",
                ]
                if f"cat > /app/work/{name}" in command
            ]
            for name in names:
                pin(Path(isolation["trial_path"]) / "artifacts/app/work" / name)
            if names or "pip install" in command:
                selected.append(
                    {
                        "line": lineno,
                        "scripts": names,
                        "exit_code": item["exit_code"],
                        "event_sha256": hashlib.sha256(
                            json.dumps(item, sort_keys=True).encode()
                        ).hexdigest(),
                    }
                )
            if "pip install" in command:
                assert "SimpleITK" in command and item["exit_code"] == 1
                assert "403 Forbidden" in item["aggregated_output"]
        access.append(
            {
                "experiment": exp,
                "isolation": isolation,
                "command_count": len(commands),
                "trace": str(trace.relative_to(root)),
                "selected_method_events": selected,
                "plain_text_diagnostic_lines": diagnostic_lines,
                "retained_access_review": terminal["access_review"],
                "scope": audit_access["scope"],
            }
        )

    assert len(replays) == 6 and len(freezes) == 2 and len(models) == 2
    common_ids = sorted(
        {r["id"] for _, m, _ in models for r in m["per_label"] if r["dice"] is not None}
    )
    conditions = []
    for (exp, metrics, answer), prior_condition in zip(models, prior["conditions"], strict=True):
        prediction = np.asanyarray(nib.load(answer).dataobj).astype(np.uint8)
        by_id = {r["id"]: r for r in metrics["per_label"]}
        condition = {
            "experiment": exp,
            "original_macro_dice": metrics["macro_dice"],
            "active_labels": sum(r["dice"] is not None for r in by_id.values()),
            "posthoc_common_label_macro_dice": float(
                np.mean([by_id[k]["dice"] or 0 for k in common_ids])
            ),
            "common_label_set": common_ids,
            "pulp_pooled": pooled(gt, prediction, [t + 100 for t in TEETH]),
            "main_canals_pooled": pooled(gt, prediction, [3, 4]),
            "small_canals_pooled": pooled(gt, prediction, [103, 104, 105]),
        }
        assert condition == next(c for c in comparison["conditions"] if c["experiment"] == exp)
        assert prior_condition["experiment"] == exp
        assert metrics["macro_dice"] == prior_condition["macro_dice"]
        geometry = metrics["whole_tooth_geometry_and_identity"]
        detected = [
            m for m in geometry["matches"] if m["dice"] >= geometry["detection_threshold_dice"]
        ]
        correct = [m for m in detected if m["correct_fdi"]]
        condition["identity_counts"] = {
            "gt": geometry["gt_object_count"],
            "predicted": geometry["predicted_object_count"],
            "detected": len(detected),
            "correct_among_detected": len(correct),
        }
        condition["tooth_matches"] = geometry["matches"]
        conditions.append(condition)

    for path, digest in pins.items():
        assert sha(root / path) == digest, path
    receipt = {
        "schema": 1,
        "entry": "tb3-dental-v2",
        "reviewer": "assistant",
        "status": "source-audit-complete-story-pending",
        "source_pins": pins,
        "cases": cases,
        "task_digests": freezes,
        "replays": replays,
        "conditions": conditions,
        "access": access,
        "fine_diagnostics": fresh,
        "original_evidence_unchanged": True,
        "new_model_runs": 0,
        "original_scores_exact_replay": True,
        "fine_diagnostics_exact_reproduction": True,
        "common_contract_and_target_equal": True,
        "limits": [
            "One selected F002 target; one Astra-medium attempt per condition; no population or isolated causal effect.",
            "Different self-chosen methods and realized compute (22m55s versus 49m04s).",
            "Active macro denominators differ (61/59); common-union macro assigns both-empty zero only in a labeled diagnostic.",
            "Target GT, score feedback and source findings were withheld; post-hoc GT views are reader-only.",
            "F008 supplies 32 teeth/pulps and five canals, no restoration labels; sampled views are not clinical certification.",
            "RPI is the operational naming convention; acquisition laterality, restoration subtypes and occupied-pulp conventions remain unadjudicated.",
            "Retained commands and proxy host decisions cannot adjudicate encrypted transport payload or model pretraining.",
            "Local source derivations retain publisher CC BY-NC-SA 4.0; archive CC-BY-SA discrepancy remains unresolved; no publication.",
        ],
    }
    (out / "audit.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(
        json.dumps(
            {"pins": len(pins), "saved_replays": len(replays), "conditions": conditions}, indent=2
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--fine", type=Path, required=True)
    args = parser.parse_args()
    audit(args.root.resolve(), args.output.resolve(), args.fine)
