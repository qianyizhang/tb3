"""Read-only dental-v3 saved-output audit; never execute historical solver programs."""

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

import nibabel as nib
import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree

EXPERIMENTS = ["dental-f018-contract-v3-astra-medium", "dental-f018-reference-v3-astra-medium"]
TEETH = [q * 10 + n for q in range(1, 5) for n in range(1, 9)]


def read(path):
    return json.loads(path.read_text())


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def overlap(g, p):
    ng, np_, inter = int(g.sum()), int(p.sum()), int((g & p).sum())
    return {
        "gt_voxels": ng,
        "prediction_voxels": np_,
        "intersection": inter,
        "dice": 2 * inter / (ng + np_) if ng + np_ else None,
        "precision": inter / np_ if np_ else None,
        "recall": inter / ng if ng else None,
    }


def bounds(mask, padding):
    points = np.argwhere(mask)
    lo = np.maximum(points.min(0) - padding, 0)
    hi = np.minimum(points.max(0) + padding + 1, mask.shape)
    return lo, hi, tuple(slice(a, b) for a, b in zip(lo, hi, strict=True))


def audit(root, out):
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

    def load(path):
        return np.load(pin(path), mmap_mode="r")

    group = Path("groups/anatomy-audit")
    base = Path(".local/dental-f018-contract-v3-20260922")
    pin(Path(__file__))
    prior = read(pin(group / "findings/evidence/dental-f018-contract-v3-comparison.json"))
    for path, digest in prior["evidence_sha256"].items():
        pin(path, digest)
    source_contract = read(pin(group / "findings/evidence/dental-dataset-contract-audit.json"))
    for item in source_contract["sources"]:
        pin(item["file"], item["sha256"])
    prep = read(pin(base / "preparation-receipt.json"))
    controls = read(pin(base / "lifecycle-controls.json"))
    historical = read(pin(base / "comparison/analysis.json"))
    common = pin(
        group / "methods/dental-f018-contract-v3/instruction.md",
        prep["common_instruction_sha256"],
    ).read_text()
    tasks = [Path(".local") / e / "task" for e in EXPERIMENTS]
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

    cases = []
    for case, ct_path, mask_path, original_ct, original_mask in [
        (
            "F018",
            tasks[0] / "environment/data/ct.nii.gz",
            tasks[0] / "tests/reference.nii.gz",
            Path(".local/dental-ct-only-astra-medium/task/environment/data/ct.nii.gz"),
            Path(".local/dental-ct-only-astra-medium/task/tests/reference.nii.gz"),
        ),
        (
            "F008",
            tasks[1] / "environment/reference/ct.nii.gz",
            tasks[1] / "environment/reference/segmentation.nii.gz",
            base / "source/ToothFairy3F_008_0000.nii.gz",
            base / "source/ToothFairy3F_008.nii.gz",
        ),
    ]:
        ct, mask = nib.load(pin(ct_path)), nib.load(pin(mask_path))
        for staged, original in [(ct, original_ct), (mask, original_mask)]:
            original = nib.load(pin(original))
            np.testing.assert_array_equal(staged.dataobj, original.dataobj)
            np.testing.assert_array_equal(staged.affine, original.affine)
            for getter in ["get_qform", "get_sform"]:
                a, ac = getattr(staged, getter)(coded=True)
                b, bc = getattr(original, getter)(coded=True)
                np.testing.assert_array_equal(a, b)
                assert ac == bc
        np.testing.assert_array_equal(ct.affine, mask.affine)
        np.testing.assert_allclose(ct.header.get_zooms(), [0.3] * 3, atol=1e-7)
        ids, counts = np.unique(np.asanyarray(mask.dataobj), return_counts=True)
        cases.append(
            {
                "case": case,
                "shape": list(ct.shape),
                "spacing_mm": list(map(float, ct.header.get_zooms())),
                "affine": ct.affine.tolist(),
                "header_axis_codes": list(nib.aff2axcodes(ct.affine)),
                "qform_code": int(ct.header["qform_code"]),
                "sform_code": int(ct.header["sform_code"]),
                "original_ct": str(original_ct),
                "original_mask": str(original_mask),
                "source_arrays_and_grid_exactly_equal": True,
                "reference_counts": {str(int(k)): int(v) for k, v in zip(ids, counts, strict=True)},
                "semantic_axis_contract": "RPI independently of retained header orientation",
                "physical_laterality_adjudicated": False,
            }
        )

    # Invoke only the inspected frozen evaluator's pure scoring function. Its
    # file-writing CLI and all saved solver/preparation programs remain unexecuted.
    scorer = pin(tasks[0] / "tests/score.py")
    namespace = {"__name__": "dental_v3_saved_output_replay"}
    exec(compile(scorer.read_text(), str(scorer), "exec"), namespace)
    replays, freezes, access, model_records = [], {}, [], []
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
            record = {
                "experiment": exp,
                "attempt": obs["attempt_id"],
                "agent": obs["agent"],
                "answer": str(answer.relative_to(root)),
                "score": replay,
                "seconds": obs["timing"]["agent"],
                "usage": obs["usage"],
            }
            if obs["agent"] in ["oracle", "nop"]:
                assert controls[exp][obs["agent"]]["attempt_id"] == obs["attempt_id"]
                assert replay["macro_dice"] == (1.0 if obs["agent"] == "oracle" else 0.0)
            else:
                assert obs["agent"] == "codex" and obs["reasoning_effort"] == "medium"
                assert obs["model"] == "openai/gpt-6-astra"
                assert replay == historical["original_metrics"][len(model_records)]
                output_image = nib.load(answer)
                target_image = nib.load(root / task / "environment/data/ct.nii.gz")
                for getter in ["get_qform", "get_sform"]:
                    np.testing.assert_array_equal(
                        getattr(output_image, getter)(), getattr(target_image, getter)()
                    )
                for field in [
                    "qform_code",
                    "sform_code",
                    "quatern_b",
                    "quatern_c",
                    "quatern_d",
                    "qoffset_x",
                    "qoffset_y",
                    "qoffset_z",
                    "srow_x",
                    "srow_y",
                    "srow_z",
                    "pixdim",
                ]:
                    np.testing.assert_array_equal(
                        output_image.header[field], target_image.header[field]
                    )
                record["native_header_fields_exactly_preserved"] = True
                model_records.append(record)
            replays.append(record)
            print("Exact saved replay:", obs["attempt_id"], flush=True)
        local = Path(".local") / exp
        terminal = read(pin(local / "terminal-review.json"))
        for path, expected in terminal["evidence_sha256"].items():
            pin(path, expected)
        assessment = read(pin(local / "terminal-assessment.json"))
        assert assessment["state"] == "terminal_reviewed"
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
        expected_reference = (
            []
            if exp == EXPERIMENTS[0]
            else ["/app/reference/ct.nii.gz", "/app/reference/segmentation.nii.gz"]
        )
        assert isolation["files"]["reference"] == expected_reference
        access_audit = read(pin(local / "access-audit.json"))
        assert {r["target"] for r in access_audit["transport"] if r["allowed"]} == {
            "chatgpt.com:443"
        }
        trace = pin(Path(isolation["trial_path"]) / "agent/codex.txt")
        types, commands, selected, diagnostic_lines = Counter(), [], [], []
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
            if item["type"] != "command_execution":
                continue
            commands.append(item)
            names = [
                n
                for n in [
                    "register.py",
                    "landmarks.py",
                    "upper.py",
                    "lower.py",
                    "composite2.py",
                    "tooth38.py",
                    "teeth.py",
                    "pulp.py",
                    "canals.py",
                    "assemble.py",
                    "pulp2.py",
                    "smallcanals.py",
                    "save.py",
                ]
                if f"/app/work/{n}" in item["command"]
            ]
            if names:
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
        assert dict(types) == access_audit["completed_item_types"]
        access.append(
            {
                "experiment": exp,
                "isolation": isolation,
                "command_count": len(commands),
                "trace": str(trace.relative_to(root)),
                "selected_method_events": selected,
                "plain_text_diagnostic_lines": diagnostic_lines,
                "retained_access_review": assessment["visible_access_review"],
                "scope": access_audit["scope"],
            }
        )

    assert len(replays) == 6 and len(freezes) == 2 and len(model_records) == 2
    gt = np.asanyarray(nib.load(root / tasks[0] / "tests/reference.nii.gz").dataobj)
    predictions = [np.asanyarray(nib.load(root / r["answer"]).dataobj) for r in model_records]
    work = Path(model_records[1]["answer"]).parent.parent / "work"
    atlas, before, after, canals = [
        load(work / n) for n in ["atlas.npy", "teeth.npy", "teeth_final.npy", "canals.npy"]
    ]
    target, jaws = load(work / "target.npy"), load(work / "jaws.npy")
    np.testing.assert_array_equal(
        target,
        nib.load(root / tasks[0] / "environment/data/ct.nii.gz").get_fdata(dtype=np.float32),
    )
    np.testing.assert_array_equal(
        load(work / "ref.npy"),
        nib.load(root / tasks[1] / "environment/reference/ct.nii.gz").get_fdata(dtype=np.float32),
    )
    np.testing.assert_array_equal(
        load(work / "refseg.npy"),
        nib.load(root / tasks[1] / "environment/reference/segmentation.nii.gz").dataobj,
    )
    np.testing.assert_array_equal(load(work / "final.npy"), predictions[1])

    per_id = [{r["id"]: r for r in m["score"]["per_label"]} for m in model_records]
    pulp_ids = [label for label, r in per_id[0].items() if label > 110 and r["gt_voxels"]]
    assert (
        sum(per_id[1][label]["dice"] > per_id[0][label]["dice"] for label in pulp_ids)
        == historical["improved_pulp_labels"]
        == 20
    )
    assert len(pulp_ids) == historical["total_pulp_labels"] == 29
    pooled = [
        {
            name: overlap(np.isin(gt, ids), np.isin(p, ids))
            for name, ids in [
                ("pulp", pulp_ids),
                ("main_canals", [3, 4]),
                ("small_canals", [103, 104, 105]),
            ]
        }
        for p in predictions
    ]
    assert pooled == historical["pooled"]
    details = []
    for old in historical["diagnostic_details"]:
        label, rows = old["label"], []
        g = gt == label
        for p in predictions:
            item = overlap(g, p == label)
            gc, pc = np.argwhere(g).mean(0), np.argwhere(p == label).mean(0)
            item.update(
                gt_centroid_ijk=gc.tolist(),
                prediction_centroid_ijk=pc.tolist(),
                centroid_displacement_mm=float(np.linalg.norm(pc - gc) * 0.3),
            )
            rows.append(item)
        distances = cKDTree(np.argwhere(atlas == label)).query(np.argwhere(g))[0]
        item = {
            "label": label,
            "conditions": rows,
            "transferred_prior": overlap(g, atlas == label),
            "gt_fraction_within_6_voxels_of_prior": float((distances <= 6).mean()),
        }
        assert item == old, label
        details.append(item)

    # Reproduce the inspected local refinement math on saved inputs, with no
    # solver execution. Record geometric eligibility separately from HU filtering.
    pulp_stages = []
    for label in pulp_ids:
        tooth = label - 100
        lo, hi, sl = bounds((before == tooth) | (before == label), 3)
        m = (before[sl] == tooth) | (before[sl] == label)
        g = gt[sl] == label
        a = ndi.gaussian_filter(target[sl], 0.5)
        inside = ndi.distance_transform_edt(m)
        distance = ndi.distance_transform_edt(atlas[sl] != label)
        old = before[sl] == label
        geometry = m & (inside >= 2.5) & (distance <= 6)
        extra = geometry & (ndi.gaussian_filter(a, 2) - a > 170) & (a < 1750)
        pm = old | extra
        lab, _ = ndi.label(pm)
        counts = np.bincount(lab.ravel())
        valid = counts >= 4
        valid[0] = False
        pm = valid[lab]
        np.testing.assert_array_equal(pm, after[sl] == label)
        assert pm.sum() == (after == label).sum()
        row = {
            "label": label,
            "bounds_ijk_half_open": [lo.tolist(), hi.tolist()],
            "gt_voxels_full_volume": int((gt == label).sum()),
            "gt_voxels_in_tooth_crop": int(g.sum()),
            "gt_in_saved_whole_tooth": int((g & m).sum()),
            "gt_within_six_voxels_of_prior_in_crop": int((g & (distance <= 6)).sum()),
            "gt_in_whole_tooth_at_depth_at_least_2_5": int((g & m & (inside >= 2.5)).sum()),
            "before": overlap(g, old),
            "extra_geometry_eligible": overlap(g, geometry),
            "retained_or_geometry_eligible": overlap(g, old | geometry),
            "extra_after_intensity": overlap(g, extra),
            "after_component_filter": overlap(g, pm),
            "saved_intermediate_exact_reproduction": True,
            "note": "Stage GT denominators are crop-local; full-volume denominator is explicit. Eligibility is not proof of clinical tissue type.",
        }
        pulp_stages.append(row)
        if label in [122, 127]:
            np.savez_compressed(
                out / f"pulp-{label}-stages.npz",
                lo=lo,
                hi=hi,
                old=old,
                geometry=geometry,
                extra=extra,
                after=pm,
            )
    canal_stages = []
    for label in [3, 4, 103, 104, 105]:
        lo, hi, sl = bounds(atlas == label, 4)
        p, g = atlas[sl] == label, gt[sl] == label
        a = ndi.gaussian_filter(target[sl], 0.55)
        if label == 105:
            lab, _ = ndi.label(p, structure=np.ones((3, 3, 3)))
            counts = np.bincount(lab.ravel())
            counts[0] = 0
            p = lab == np.argmax(counts)
            candidate = p & (a < 1650)
        else:
            sd = ndi.distance_transform_edt(p) - ndi.distance_transform_edt(~p)
            candidate = sd + np.clip((450 - a) / 350, -3, 1.1) > 0
        within_jaw = candidate & ndi.binary_dilation(jaws[sl] == 1, iterations=1)
        m = ndi.gaussian_filter(within_jaw.astype(np.float32), 0.4) > 0.4
        lab, _ = ndi.label(m, structure=np.ones((3, 3, 3)))
        counts = np.bincount(lab.ravel())
        valid = counts > 3
        valid[0] = False
        m = valid[lab]
        np.testing.assert_array_equal(m, canals[sl] == label)
        assert m.sum() == (canals == label).sum()
        canal_stages.append(
            {
                "label": label,
                "bounds_ijk_half_open": [lo.tolist(), hi.tolist()],
                "gt_voxels_full_volume": int((gt == label).sum()),
                "gt_voxels_in_search_crop": int(g.sum()),
                "prior": overlap(g, p),
                "intensity_candidate": overlap(g, candidate),
                "within_jaw": overlap(g, within_jaw),
                "after_filters": overlap(g, m),
                "final": overlap(gt == label, predictions[1] == label),
                "saved_intermediate_exact_reproduction": True,
                "note": "Actual algorithm crop is prior bbox plus four voxels; six-voxel distance is a separate descriptive diagnostic, not this canal algorithm.",
            }
        )
        if label == 104:
            np.savez_compressed(
                out / "canal-104-stages.npz",
                lo=lo,
                hi=hi,
                prior=p,
                candidate=candidate,
                within_jaw=within_jaw,
                after=m,
            )

    conditions = []
    for record in model_records:
        metrics = record["score"]
        geometry = metrics["whole_tooth_geometry_and_identity"]
        detected = [r for r in geometry["matches"] if r["dice"] >= 0.5]
        conditions.append(
            {
                "experiment": record["experiment"],
                "original_macro_dice": metrics["macro_dice"],
                "active_labels": sum(r["dice"] is not None for r in metrics["per_label"]),
                "identity_counts": {
                    "gt": geometry["gt_object_count"],
                    "predicted": geometry["predicted_object_count"],
                    "detected": len(detected),
                    "correct_among_detected": sum(r["correct_fdi"] for r in detected),
                },
            }
        )
    for path, digest in pins.items():
        assert sha(root / path) == digest, path
    receipt = {
        "schema": 1,
        "entry": "tb3-dental-v3",
        "reviewer": "assistant",
        "status": "source-audit-complete-story-pending",
        "source_pins": pins,
        "cases": cases,
        "task_digests": freezes,
        "replays": replays,
        "conditions": conditions,
        "access": access,
        "pooled": pooled,
        "diagnostic_details": details,
        "pulp_stages": pulp_stages,
        "canal_stages": canal_stages,
        "local_stage_arrays": {str(p.relative_to(root)): sha(p) for p in out.glob("*.npz")},
        "original_evidence_unchanged": True,
        "new_model_runs": 0,
        "original_scores_exact_replay": True,
        "historical_diagnostics_exact_reproduction": True,
        "saved_pulp_and_canal_refinement_exact_reproduction": True,
        "common_contract_and_target_equal": True,
        "comparability": "matched target/contract/runtime budget; unequal self-chosen methods and realized compute",
        "limits": [
            "One Astra-medium attempt per condition on repeated development case F018; no population or isolated causal effect.",
            "Target GT and prior findings withheld; all target-GT views and crop eligibility measurements are reader-only post-hoc diagnostics.",
            "Nominal 0.3 mm is used only to reproduce historical centroid diagnostics; frozen surface metrics use stored NIfTI spacing.",
            "RPI operational naming is independent of retained target LPI and example LPS headers; physical laterality remains unadjudicated.",
            "No restoration labels in target GT or either output, and no confidently identified treated occupied pulp: v3 convention benefit is untested.",
            "Spatial eligibility bounds an inspected operation; it does not isolate why registration erred or adjudicate clinical reference truth.",
            "Access evidence covers retained commands and proxy host decisions; encrypted payload and pretraining remain unadjudicated.",
            "Publisher CC BY-NC-SA 4.0 retained for local derivations; archive CC-BY-SA discrepancy unresolved; no publication.",
        ],
    }
    (out / "audit.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(
        json.dumps(
            {
                "pins": len(pins),
                "replays": len(replays),
                "conditions": conditions,
                "pulp127": next(r for r in pulp_stages if r["label"] == 127),
                "canal104": canal_stages[3],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    audit(args.root.resolve(), args.output.resolve())
