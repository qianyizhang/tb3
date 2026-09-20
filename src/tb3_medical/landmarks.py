"""Native CT/MRI landmark preparation, saved-output replay and review views."""

from pathlib import Path
import hashlib
import html
import json
import shutil

from . import core as c, score_ct, score_mri


def case_inputs(root, experiment, case):
    manifest = c.read(c.inside(root, experiment["input_manifest"]))
    try:
        return manifest["cases"][case]
    except KeyError:
        raise c.MedicalError("Unknown landmark case: " + str(case)) from None


def prepare_case(root, experiment, spec, execute):
    inputs = case_inputs(root, experiment, spec["id"])
    if execute:
        c.verify_inputs(root, inputs["files"])
        target = c.inside(root, spec["task_path"])
        if target.exists():
            from .workflow import task_files

            if task_files(target) != {f["destination"]: f["sha256"] for f in inputs["files"]}:
                raise c.MedicalError(
                    "Prepared task differs; choose a fresh task_path before preparing"
                )
        else:
            for entry in inputs["files"]:
                output = c.inside(target, entry["destination"])
                output.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(c.inside(root, entry["path"]), output)
    return {
        "case": spec["id"],
        "task_path": spec["task_path"],
        "files": len(inputs["files"]),
        "executed": execute,
        "inputs": [e["path"] for e in inputs["files"]],
    }


def replay(root, experiment, case=None):
    manifest = c.read(c.inside(root, experiment["input_manifest"]))
    cases = [case] if case else list(manifest["cases"])
    results = []
    for name in cases:
        inputs = case_inputs(root, experiment, name)
        truth_entry = next(e for e in inputs["files"] if e["destination"] == "tests/truth.json")
        c.verify_inputs(root, [truth_entry])
        truth = c.read(c.inside(root, truth_entry["path"]))
        scorer = score_mri if inputs["scorer"] == "mri" else score_ct
        scorer_hash = c.sha(Path(scorer.__file__))
        for observation in inputs["observations"]:
            answer = observation["answer"]
            c.verify_inputs(root, [answer])
            metrics = scorer.score(c.read(c.inside(root, answer["path"])), truth)
            matches = metrics == observation["expected"]
            signature = json.dumps(
                [
                    observation["attempt_id"],
                    answer["sha256"],
                    truth_entry["sha256"],
                    scorer_hash,
                    observation["expected"],
                ],
                sort_keys=True,
            )
            key = "replay-" + hashlib.sha256(signature.encode()).hexdigest()[:24]
            row = {
                "schema_version": 2,
                "kind": "evaluation",
                "id": key,
                "group_id": experiment["group_id"],
                "experiment_id": experiment["id"],
                "attempt_id": observation["attempt_id"],
                "source_evaluation": observation["source_evaluation"],
                "case": name,
                "condition": observation["condition"],
                "evaluation_kind": "saved_output_replay",
                "execution_state": observation["execution_state"],
                "outcome": "pass" if metrics["reward"] == 1 else "fail",
                "collected_at": c.now(),
                "metrics": metrics,
                "replay_matches": matches,
                "scorer_sha256": scorer_hash,
                "evidence": [truth_entry, answer],
                "scope": "Exact saved-output metric comparison; no new model execution or qualification.",
            }
            target = (
                Path(root)
                / Path(experiment["record_path"]).parent
                / "evaluations"
                / (key + ".json")
            )
            if not target.exists():
                c.write_new(target, row)
            results.append(
                {
                    "id": key,
                    "case": name,
                    "condition": observation["condition"],
                    "exact_match": matches,
                }
            )
    return {"replays": results, "all_match": all(r["exact_match"] for r in results)}


def view(root, experiment, case, output=None):
    """Render a native i-plane with physical j/k aspect and projected markers."""
    import numpy as np
    from PIL import Image, ImageDraw

    inputs = case_inputs(root, experiment, case)
    wanted = {"tests/truth.json", "environment/geometry.json", "environment/volume.npy"}
    files = {e["destination"]: e for e in inputs["files"] if e["destination"] in wanted}
    c.verify_inputs(root, [*files.values(), *(o["answer"] for o in inputs["observations"])])
    truth = c.read(c.inside(root, files["tests/truth.json"]["path"]))
    geometry = c.read(c.inside(root, files["environment/geometry.json"]["path"]))
    volume = np.load(c.inside(root, files["environment/volume.npy"]["path"]), mmap_mode="r")
    if list(volume.shape) != truth["shape_ijk"] or list(volume.shape) != geometry["shape_ijk"]:
        raise c.MedicalError("Native volume and geometry shapes differ")
    points = truth.get("points_ijk") or {
        k: v["ijk"] for k, v in truth["targets"].items() if v["status"] == "observed"
    }
    index = int(round(np.mean(list(points.values()), axis=0)[0]))
    lo, hi = geometry["display_window"]
    plane = np.flipud(np.uint8(np.clip((volume[index, :, :].T - lo) / (hi - lo), 0, 1) * 255))
    spacing = geometry["spacing_ijk_mm"]
    width = 700
    height = round(width * volume.shape[2] * spacing[2] / (volume.shape[1] * spacing[1]))
    image = Image.fromarray(plane).convert("RGB").resize((width, height))
    draw = ImageDraw.Draw(image)

    def marker(point, color):
        x = (point[1] + 0.5) / volume.shape[1] * width
        y = (1 - (point[2] + 0.5) / volume.shape[2]) * height
        draw.ellipse((x - 3, y - 3, x + 3, y + 3), outline=color, width=2)

    for p in points.values():
        marker(p, "#48e6c7")
    summaries = []
    for n, observation in enumerate(inputs["observations"]):
        color = ("#ffcd6b", "#fa80bc")[n % 2]
        predictions = c.read(c.inside(root, observation["answer"]["path"]))["landmarks"]
        for p in predictions.values():
            if isinstance(p, dict):
                p = p["ijk"] if p["status"] == "observed" else None
            if p is not None:
                marker(p, color)
        summaries.append(f'<p style="color:{color}">{html.escape(observation["condition"])}</p>')
    out = Path(output) if output else Path(root) / ".local/views" / experiment["id"] / case
    if not out.is_absolute():
        out = Path(root) / out
    if out.exists():
        raise c.MedicalError("Choose a fresh view output directory")
    out.mkdir(parents=True)
    image.save(out / "native-plane.png")
    (out / "index.html").write_text(
        '<!doctype html><meta charset="utf-8"><title>Landmark review</title>'
        '<body style="background:#151a20;color:#eee;font:16px system-ui;max-width:900px;margin:40px auto">'
        f"<h1>{html.escape(case)} · native i={index}</h1><p>Reference: teal. Projected markers on a native i-plane; "
        "off-plane displacement is not shown. Image preserves physical j/k aspect. These views do not rescore an attempt.</p>"
        + "".join(summaries)
        + '<img style="max-width:100%" src="native-plane.png">'
    )
    return {"output": str(out / "index.html"), "plane_index": index, "case": case}
