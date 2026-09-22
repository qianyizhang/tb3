"""Replay frozen scoring and render a local comparison from saved model outputs only."""

import base64
import hashlib
import html
import io
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / ".local/longitudinal-ct-image-only-v1"
COLORS = ["#45d5e8", "#ffb34d", "#ef7bae"]
NAMES = ["Reference", "Astra · medium", "Sol · xhigh"]
SLUGS = ["astra-medium", "sol-xhigh"]


def sha(p):
    with p.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def uri(a, fmt="PNG"):
    f = io.BytesIO()
    Image.fromarray(a).save(f, format=fmt)
    return "data:image/" + fmt.lower() + ";base64," + base64.b64encode(f.getvalue()).decode()


def pct(v):
    return "—" if v is None else f"{v:.3f}"


def overlay(mask, color):
    plane = mask.T
    rgba = np.zeros((*plane.shape, 4), np.uint8)
    rgb = tuple(int(color[i : i + 2], 16) for i in [1, 3, 5])
    for label in np.unique(plane):
        if not label:
            continue
        region = plane == label
        edge = region & ~ndimage.binary_erosion(region)
        rgba[region] = (*rgb, 45)
        rgba[edge] = (*rgb, 255)
    return rgba


def replay_differences(a, b, path="root"):
    if isinstance(a, dict) and isinstance(b, dict):
        assert a.keys() == b.keys(), f"Replay keys differ at {path}"
        return [x for k in a for x in replay_differences(a[k], b[k], path + "." + k)]
    if isinstance(a, list) and isinstance(b, list):
        assert len(a) == len(b), f"Replay length differs at {path}"
        return [
            x
            for i, (u, v) in enumerate(zip(a, b))
            for x in replay_differences(u, v, path + f"[{i}]")
        ]
    if a == b:
        return []
    if isinstance(a, float) and isinstance(b, float) and abs(a - b) <= 1e-12:
        return [dict(path=path, original=a, replay=b, absolute_difference=abs(a - b))]
    raise AssertionError(f"Frozen verifier replay differs at {path}: {a!r} versus {b!r}")


def main():
    out = BASE / "review"
    if out.exists():
        raise SystemExit("Use a fresh output destination; existing review is retained")
    out.mkdir()
    states = {s: json.loads((BASE / s / "operator-state.json").read_text()) for s in SLUGS}
    metrics, arrays, records = {}, {}, {}
    for s in SLUGS:
        state = states[s]
        trial = Path(state["trial_path"])
        config = json.loads((trial / "config.json").read_text())
        task = ROOT / ".local/freezes" / state["task_digest"] / "task"
        if not task.exists():
            task = Path(config["task"]["path"])
        answer = trial / "artifacts/app/answer"
        target = out / ("replay-" + s)
        command = [
            str(ROOT / ".venv-br037/bin/python"),
            str(task / "tests/score.py"),
            "--answer",
            str(answer),
            "--reference",
            str(task / "tests/reference"),
            "--output",
            str(target),
        ]
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        (out / (s + "-replay.log")).write_text(result.stdout + result.stderr)
        if not (target / "metrics.json").is_file():
            raise RuntimeError("Replay failed " + s)
        replay = json.loads((target / "metrics.json").read_text())
        original = json.loads((trial / "verifier/metrics.json").read_text())
        differences = replay_differences(original, replay)
        metrics[s] = original
        records[s] = dict(
            attempt_id=state["attempt_id"],
            trial_path=str(trial),
            task_digest=state["task_digest"],
            metrics=original,
            independent_replay_equal=(replay == original),
            replay_absolute_tolerance=1e-12,
            replay_float_differences=differences,
            predictions={p.name: sha(p) for p in answer.iterdir() if p.is_file()},
            trial_result=json.loads((trial / "result.json").read_text()),
            live_isolation=json.loads(Path(state["live_isolation_path"]).read_text()),
        )
        arrays[s] = {
            v: np.asarray(nib.load(answer / (v + "_instances.nii.gz")).dataobj).astype(np.uint16)
            for v in ["baseline", "followup"]
        }
    task = BASE / "task"
    visits = {}
    for v in ["baseline", "followup"]:
        im = nib.load(task / "environment/data" / (v + ".nii.gz"))
        visits[v] = {
            "im": im,
            "ct": np.asarray(im.dataobj),
            "masks": [
                np.asarray(
                    nib.load(task / "tests/reference" / (v + "_instances.nii.gz")).dataobj
                ).astype(np.uint16),
                arrays[SLUGS[0]][v],
                arrays[SLUGS[1]][v],
            ],
        }
    rows = []
    for v, entry in visits.items():
        g = entry["masks"][0]
        for label in np.unique(g):
            if label == 0:
                continue
            counts = np.count_nonzero(g == label, axis=(0, 1))
            k = int(counts.argmax())
            xy = np.argwhere(g[:, :, k] == label).mean(axis=0)
            rows.append((v, int(label), k, xy))
    fig, axes = plt.subplots(
        len(rows), 4, figsize=(14, len(rows) * 3.25), layout="constrained", squeeze=False
    )
    for row, (v, label, k, xy) in enumerate(rows):
        entry = visits[v]
        plane = np.clip((entry["ct"][:, :, k].T.astype(float) + 160) / 400, 0, 1)
        half = 75 / float(entry["im"].header.get_zooms()[0])
        for col, ax in enumerate(axes[row]):
            ax.imshow(plane, cmap="gray", vmin=0, vmax=1, origin="upper")
            if col:
                mask = entry["masks"][col - 1][:, :, k]
                ax.imshow(overlay(mask, COLORS[col - 1]), origin="upper")
                for ident in np.unique(mask):
                    if not ident:
                        continue
                    c = np.argwhere(mask == ident).mean(axis=0)
                    if abs(c[0] - xy[0]) < half and abs(c[1] - xy[1]) < half:
                        ax.text(
                            c[0],
                            c[1],
                            str(ident),
                            color=COLORS[col - 1],
                            fontsize=9,
                            weight="bold",
                            bbox={
                                "facecolor": "black",
                                "alpha": 0.65,
                                "edgecolor": "none",
                                "pad": 1,
                            },
                        )
            ax.set_xlim(xy[0] - half, xy[0] + half)
            ax.set_ylim(xy[1] + half, xy[1] - half)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_title(
                ["CT only", *NAMES][col] + (f" | {v}, GT {label}, k={k}" if col == 0 else ""),
                fontsize=10,
            )
            if col == 0:
                ax.set_ylabel("Native j ↓ / native i →", fontsize=8)
    fig.suptitle(
        "Image-only paired CT: saved predictions versus private reference\n"
        "Cyan: reference • Orange: Astra medium • Pink: Sol xhigh • Solid contour, faint fill\n"
        "GT-selected maximal-area axial planes; 150 mm crops, soft-tissue window [−160, 240] HU.\n"
        "IDs are local to each mask. Crops omit distant false positives; use the full-volume reader.\nSource: Longitudinal-CT v3 (FDAT), CC BY-NC 4.0; derived evaluation views.",
        fontsize=11,
    )
    fig.savefig(out / "native-comparison.png", dpi=150)
    plt.close(fig)
    extra_rows = []
    for s in SLUGS:
        for v in ["baseline", "followup"]:
            matched = {int(k) for k in metrics[s]["visits"][v]["mapping"]}
            for label in metrics[s]["visits"][v]["ids"]:
                if label in matched:
                    continue
                selected = arrays[s][v] == label
                k = int(selected.sum(axis=(0, 1)).argmax())
                xy = np.argwhere(selected[:, :, k]).mean(axis=0)
                extra_rows.append((s, v, label, k, xy))
    if extra_rows:
        fig, axes = plt.subplots(
            len(extra_rows),
            4,
            figsize=(14, 3.2 * len(extra_rows)),
            layout="constrained",
            squeeze=False,
        )
        for row, (s, v, label, k, xy) in enumerate(extra_rows):
            entry = visits[v]
            half = 90 / float(entry["im"].header.get_zooms()[0])
            for col, ax in enumerate(axes[row]):
                ax.imshow(entry["ct"][:, :, k].T, cmap="gray", vmin=-160, vmax=240, origin="upper")
                if col:
                    ax.imshow(
                        overlay(entry["masks"][col - 1][:, :, k], COLORS[col - 1]), origin="upper"
                    )
                ax.set_xlim(xy[0] - half, xy[0] + half)
                ax.set_ylim(xy[1] + half, xy[1] - half)
                ax.set_xticks([])
                ax.set_yticks([])
                ax.set_title(
                    ["CT only", *NAMES][col]
                    + (f" | {s}, {v}, P{label}, k={k}" if col == 0 else ""),
                    fontsize=9,
                )
        fig.suptitle(
            "Unmatched predicted instances: regions without a localization match to dataset GT\n"
            "Prediction-selected maximal-area native axial planes; 180 mm crops; HU [−160, 240].\n"
            "Cyan: reference • Orange: Astra • Pink: Sol • Solid contour, faint fill. Reference disagreement is not clinical adjudication.",
            fontsize=11,
        )
        fig.savefig(out / "unmatched-predictions.png", dpi=150)
        plt.close(fig)
    measures = [
        ("Detection F1", lambda m: m["detection_micro"]["f1"]),
        ("Instance Dice", lambda m: m["segmentation_gt_macro_dice"]),
        ("Link F1", lambda m: m["association"].get("links_end_to_end", {}).get("f1")),
        ("Event F1", lambda m: m["association"].get("events_end_to_end", {}).get("f1")),
    ]
    fig, ax = plt.subplots(figsize=(9, 3.5), layout="constrained")
    for i, s in enumerate(SLUGS):
        values = [f(metrics[s]) for _, f in measures]
        bars = ax.bar(
            np.arange(len(measures)) + (i - 0.5) * 0.34,
            [v or 0 for v in values],
            0.32,
            label=NAMES[i + 1],
            color=COLORS[i + 1],
        )
        ax.bar_label(bars, labels=[pct(v) for v in values], padding=3)
    ax.set_xticks(np.arange(len(measures)), [n for n, _ in measures])
    ax.set_ylim(0, 1.12)
    ax.set_ylabel("Score (0–1)")
    ax.set_title("One full CT pair • no supplied masks or lesion hints")
    ax.legend()
    ax.spines[["right", "top"]].set_visible(False)
    fig.savefig(out / "score-comparison.png", dpi=180)
    plt.close(fig)
    payload = {}
    for v, e in visits.items():
        ct = e["ct"]
        planes = []
        for k in range(ct.shape[2]):
            gray = np.rint(np.clip((ct[:, :, k].T.astype(float) + 160) / 400, 0, 1) * 255).astype(
                np.uint8
            )
            planes.append(
                {
                    "ct": uri(gray, "JPEG"),
                    "masks": [uri(overlay(m[:, :, k], c)) for m, c in zip(e["masks"], COLORS)],
                }
            )
        first = next(k for visit, label, k, _ in rows if visit == v and label == 4)
        payload[v] = {
            "planes": planes,
            "initial": first,
            "shape": list(ct.shape),
            "affine": e["im"].affine.tolist(),
        }
    table = "<table><thead><tr><th>Endpoint</th><th>Astra medium</th><th>Sol xhigh</th></tr></thead><tbody>"
    table += (
        "".join(
            "<tr><th>"
            + name
            + "</th>"
            + "".join("<td>" + pct(fn(metrics[s])) + "</td>" for s in SLUGS)
            + "</tr>"
            for name, fn in measures
        )
        + "</tbody></table>"
    )
    table += "<table><thead><tr><th>Visit / metric</th><th>Astra medium</th><th>Sol xhigh</th></tr></thead><tbody>"
    for v in ["baseline", "followup"]:
        for field in ["foreground_dice", "gt_macro_dice"]:
            table += (
                "<tr><th>"
                + v
                + " "
                + field.replace("_", " ")
                + "</th>"
                + "".join(
                    "<td>" + pct(metrics[s]["visits"][v]["segmentation"][field]) + "</td>"
                    for s in SLUGS
                )
                + "</tr>"
            )
        table += (
            "<tr><th>"
            + v
            + " detected GT / predicted</th>"
            + "".join(
                "<td>"
                + str(metrics[s]["visits"][v]["detection"]["tp"])
                + "/"
                + str(metrics[s]["visits"][v]["detection"]["gt_count"])
                + " GT; "
                + str(metrics[s]["visits"][v]["detection"]["prediction_count"])
                + " predicted</td>"
                for s in SLUGS
            )
            + "</tr>"
        )
    table += '</tbody></table><p>Raw separate metrics, matching details, provenance and replay equality: <a href="comparison.json">comparison.json</a>.</p>'
    conditional_table = "<table><thead><tr><th>Conditional association</th><th>Astra medium</th><th>Sol xhigh</th></tr></thead><tbody>"
    for field, title, eligible, total in [
        ("links_conditional_on_detection", "Link F1", "eligible_gt_edges", "total_gt_edges"),
        (
            "events_conditional_on_detection",
            "Exact-event F1",
            "eligible_gt_groups",
            "total_gt_groups",
        ),
    ]:
        conditional_table += "<tr><th>" + title + "</th>"
        for slug in SLUGS:
            m = metrics[slug]["association"][field]
            value = pct(m["f1"]) if m[eligible] else "Not assessable"
            conditional_table += f"<td>{value}; {m[eligible]}/{m[total]} GT eligible</td>"
        conditional_table += "</tr>"
    conditional_table += "</tbody></table>"
    table += conditional_table
    details = ""
    for s in SLUGS:
        answer = Path(states[s]["trial_path"]) / "artifacts/app/answer"
        details += (
            "<details><summary>"
            + html.escape(s)
            + " · submitted report and events</summary><pre>"
            + html.escape((answer / "report.md").read_text())
            + "</pre><pre>"
            + html.escape((answer / "events.json").read_text())
            + "</pre></details>"
        )
    document = """<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Image-only Longitudinal CT comparison</title>
<style>body{font:16px system-ui;margin:0;background:#0d1320;color:#e7edf6}main{max-width:1360px;margin:auto;padding:28px}h1{font-size:32px}p{line-height:1.6;max-width:1000px}table{border-collapse:collapse;background:#192335;margin:20px 0}th,td{padding:12px 24px;border-bottom:1px solid #34425b;text-align:left}.legend span{display:inline-block;margin-right:22px;font-weight:650}section{background:#151e2e;padding:20px;border-radius:12px;margin:24px 0}.controls{display:flex;gap:16px;align-items:center;flex-wrap:wrap}input[type=range]{flex:1;min-width:180px}.views{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}canvas{width:100%;image-rendering:auto;background:#000}h3{font-size:16px}button{background:#34425b;color:white;border:0;border-radius:6px;padding:9px;cursor:pointer}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#192335;padding:16px;font-size:13px}a{color:#8cd5ff}.note{color:#b5c1d4}img{max-width:100%}@media(max-width:800px){.views{grid-template-columns:1fr}main{padding:16px}th,td{padding:8px}}</style>
<main><h1>Find, segment, then link</h1><p>One Longitudinal-CT v3 pair, inspected for source and geometry consistency. Two fresh attempts saw only the full CT volumes and a generic format example. Reference annotations, lesion counts, locations and event expectations were private. Each attempt had up to two hours.</p>
<p class="note"><strong>Instance/event interpretation is under review.</strong> Three baseline reference labels touch, while the generic task says a confluent region is one instance. Connectivity alone does not resolve that annotation convention. The original fine-instance scores are preserved.</p><div class="legend"><span style="color:#45d5e8">━ Reference</span><span style="color:#ffb34d">━ Astra medium</span><span style="color:#ef7bae">━ Sol xhigh</span></div>TABLE
<p class="note">Detection uses centroid-to-reference matching within 3 mm; instance Dice includes missed GT lesions as zero. Link/event F1 is end-to-end. Artifact-contract validity is not scientific success. Independent saved-output replay matches the frozen metrics within 1e−12; discrete outcomes match exactly. The tables retain original verifier values.</p>
<div id="reader"></div><p class="note">Full native axial fields: i increases rightward on this display, j downward; this is an index view, not an anatomical laterality label. Visit sliders are independent; equal slice numbers do not imply registration. Reference-selected jump buttons are evaluation aids and were never solver inputs. Window: −160 to 240 HU.</p>
<h2>Selected reference planes</h2><img src="native-comparison.png" alt="Native CT reference and prediction comparison"><p class="note">Selected crops do not establish full-volume accuracy; inspect missed and extra instances in the reader.</p>
<h2>Submitted evidence</h2>DETAILS
<p>Source: <a href="https://fdat.uni-tuebingen.de/records/qe950-g4h94">Longitudinal-CT v3, FDAT</a>, CC BY-NC 4.0. Derived images retain native geometry. This one pair tests persistence and merging; new/disappearing event accuracy is unmeasured. Potential annotation-completeness disagreements require separate review, without rewriting frozen scores.</p>
</main><script>const DATA=PAYLOAD;const FOCI=FOCI_DATA;const NAMES=['Reference','Astra · medium','Sol · xhigh'];
for(const [visit,d] of Object.entries(DATA)){
 const section=document.createElement('section');section.innerHTML=`<h2>${visit==='baseline'?'Baseline':'Follow-up'}</h2><div class="controls"><label>Native k <output>${d.initial}</output></label><input type="range" min="0" max="${d.planes.length-1}" value="${d.initial}" aria-label="${visit} native slice"><label><input type="checkbox" checked class="overlay"> Show masks</label><span class="world"></span></div><p class="jumps"></p><div class="views">${NAMES.map(n=>`<div><h3>${n}</h3><canvas width="512" height="512" aria-label="${visit} ${n}"></canvas></div>`).join('')}</div>`;
 document.querySelector('#reader').append(section);let generation=0;
 const slider=section.querySelector('input[type=range]'), toggle=section.querySelector('.overlay');
 async function draw(){const stamp=++generation,k=Number(slider.value),frame=d.planes[k];section.querySelector('output').value=k;section.querySelector('.world').textContent=`World z ${((d.affine[2][2]*k)+d.affine[2][3]).toFixed(1)} mm`;
 const load=src=>new Promise((resolve,reject)=>{const i=new Image();i.onload=()=>resolve(i);i.onerror=reject;i.src=src});
 const images=await Promise.all([load(frame.ct),...frame.masks.map(load)]);if(stamp!==generation)return;
 section.querySelectorAll('canvas').forEach((c,i)=>{const x=c.getContext('2d');x.clearRect(0,0,512,512);x.drawImage(images[0],0,0);if(toggle.checked)x.drawImage(images[i+1],0,0)});}
 for(const f of FOCI.filter(x=>x.visit===visit)){const b=document.createElement('button');b.textContent=`GT ${f.id} · k=${f.k}`;b.onclick=()=>{slider.value=f.k;draw()};section.querySelector('.jumps').append(b,' ')}
 slider.oninput=draw;toggle.onchange=draw;draw();
}
</script></html>"""
    document = (
        document.replace("TABLE", table)
        .replace("DETAILS", details)
        .replace("PAYLOAD", json.dumps(payload))
        .replace(
            "FOCI_DATA", json.dumps([{"visit": v, "id": label, "k": k} for v, label, k, _ in rows])
        )
    )
    (out / "index.html").write_text(document)
    receipt = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "conditions": records,
        "selection": "one preselected patient pair, reviewed source case 0a09c8844b",
        "source": {
            "dataset": "Longitudinal-CT",
            "release": "v3",
            "url": "https://fdat.uni-tuebingen.de/records/qe950-g4h94",
            "license": "CC BY-NC 4.0",
            "derived_figures": "Native CT reslices with original reference and independently generated model contours",
        },
        "figures": {p.name: sha(p) for p in out.glob("*.png")},
        "figures_gt_selected_for_posthoc_review_only": True,
    }
    (out / "comparison.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(
        json.dumps(
            {
                "review": str(out),
                "replays_equal": all(r["independent_replay_equal"] for r in records.values()),
                "metrics": {
                    s: {
                        "detection": m["detection_micro"],
                        "segmentation_dice": m["segmentation_gt_macro_dice"],
                        "association": m["association"],
                    }
                    for s, m in metrics.items()
                },
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
