"""Build a local BR-042 evidence showcase from immutable saved artifacts; no trials."""

import argparse
import base64
import gzip
import hashlib
import json
import shutil
from pathlib import Path

import nibabel as nib
import numpy as np
from markdown_it import MarkdownIt

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
AUDIT = Path("groups/tubular-anatomy/experiments/br042-v4-6h/resume1")
FROZEN = Path("runs/br042-all-vessels-v4-6h/tasks/all-vessels")
LABELS = {
    "1": "LM",
    "2": "LAD",
    "3": "LCx",
    "4": "D1",
    "5": "D2",
    "6": "OM1",
    "7": "OM2",
    "8": "Ramus",
    "9": "RCA",
    "10": "R-PDA",
    "11": "R-PLA",
    "12": "L-PDA",
    "13": "L-PLA",
    "14": "Other",
}
MODELS = [
    (
        "v2-medium",
        "V2 · Astra / medium",
        "V2",
        "Completed",
        1676.19,
        3600,
        "runs/br042-all-vessels-astra-medium-v2-20260920/all-vessels__5Wo8h5i",
    ),
    (
        "v3-sol",
        "V3 · Sol / xhigh",
        "V3",
        "Completed",
        2495.871709,
        3600,
        "runs/br042-all-vessels-sol-xhigh-v3-20260920/all-vessels__5U7REa4",
    ),
    (
        "v3-medium",
        "V3 · Astra / medium",
        "V3",
        "Completed",
        2794.14597,
        3600,
        "runs/br042-all-vessels-astra-medium-v3-20260920-setup-recovery1/all-vessels__tvkf3rA",
    ),
    (
        "v3-xhigh",
        "V3 · Astra / xhigh",
        "V3",
        "Timeout · partial",
        3600.166052,
        3600,
        "runs/br042-all-vessels-astra-xhigh-v3-20260920-setup-recovery1/all-vessels__6wwRK7K",
    ),
    (
        "v4-2h",
        "V4 · Astra / xhigh · 2h",
        "V4",
        "Timeout · partial",
        7200,
        7200,
        "runs/br042-all-vessels-astra-xhigh-v4-2h-attempt1/all-vessels__WjMQM7j",
    ),
    (
        "v4-6h",
        "V4 · Astra / xhigh · 6h",
        "V4",
        "Transport stop · partial",
        10065.189254,
        21600,
        "runs/br042-all-vessels-astra-xhigh-v4-6h-attempt2/all-vessels__xZ2JU6T",
    ),
    (
        "resumed",
        "V4 · Astra / xhigh · resumed",
        "V4",
        "Completed continuation",
        15232.252927,
        21600,
        "runs/br042-all-vessels-astra-xhigh-v4-6h-resume1/all-vessels__cr5kdch",
    ),
]
METHODS = [
    (
        "V2 / Astra medium",
        "Image inspection → intensity/tubular features → image-derived waypoints → traced and named courses.",
        "Broad vessel extraction was demonstrated; branch discovery and numbering remained incomplete. V2 used a different original label-matching rule.",
        "v2-medium-method.md",
    ),
    (
        "V3 / Sol xhigh",
        "Multiscale Frangi vesselness and skeleton paths; geodesics between image-derived waypoints; smooth RAS export.",
        "Recovered much of RCA, but its submitted left main, LAD and LCx had 0% reference geometry coverage at 1 mm. This is a localization failure, not just a naming error.",
        "v3-sol-method.md",
    ),
    (
        "V3 / Astra medium",
        "HU-based blood-pool removal; multiscale Hessian features; pruned skeleton graph; constrained geodesics; local cross-section centering; anatomical review.",
        "Best recorded geometry: 95.5% by length. Small D2/OM1 absent, OM2 recovered under OM1, and an extra diagonal labeled D2 instead of Other.",
        "v3-medium-method.md",
    ),
    (
        "V3 / Astra xhigh",
        "Saved extract.py refines agent-reviewed voxel paths in normal planes, attaches nearby parent junctions and resamples to RAS; separate work files retain candidate exploration.",
        "Timed out. A final method.md is absent. Saved output includes a D1/Ramus confusion and weak small branches; incomplete documentation limits methodological comparison.",
        "v3-xhigh-extract.py",
    ),
    (
        "V4 / Astra xhigh",
        "Physical-scale Hessian vesselness; image-derived control points; local HU/vesselness geodesics; lumen centering; low-threshold residual-candidate review; larger-vessel tracing.",
        "More broad-scope output, persistent coronary omissions and numbering shifts. The resumed rebuild replays saved controls; it does not repeat blind discovery.",
        "resumed-method.md",
    ),
]


def read_json(path):
    return json.loads((ROOT / path).read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    if out.exists():
        raise SystemExit("Use a fresh output directory; retained builds are never overwritten.")
    out.mkdir(parents=True)
    src = out / "sources"
    src.mkdir()
    receipts = []

    def retain(path, name):
        origin = ROOT / path
        target = src / name
        shutil.copyfile(origin, target)
        digest = sha(origin)
        assert digest == sha(target)
        receipts.append({"path": str(path), "copy": "sources/" + name, "sha256": digest})
        return digest

    comparison_path = Path(
        "groups/tubular-anatomy/experiments/br042-v4-6h/evaluations/saved-output-review.json"
    )
    comparison = read_json(comparison_path)["comparison"]
    resume = read_json(AUDIT / "evaluation.json")
    retain(comparison_path, "comparison.json")
    for name in [
        "evaluation.json",
        "trace-audit.json",
        "trace-audit.md",
        "candidate-funnel.json",
        "protocol.md",
    ]:
        retain(AUDIT / name, name)
    retain(FROZEN / "tests/reference.json", "reference.json")
    retain(FROZEN / "tests/score.py", "frozen-score.py")
    retain(FROZEN / "instruction.md", "instruction.md")
    retain(FROZEN / "environment/SOURCE_NOTICE.md", "SOURCE_NOTICE.md")
    retain(FROZEN / "environment/DATA-LICENSE.txt", "DATA-LICENSE.txt")
    for name in [
        "BR-042-results.md",
        "BR-042-v3-results.md",
        "BR-042-v3-branch-review.md",
        "BR-042-v4-plan.md",
    ]:
        retain(Path("docs/research-rounds") / name, name)

    image_path = ROOT / FROZEN / "environment/data/image.nii.gz"
    nii = nib.load(image_path)
    hu = nii.get_fdata(dtype=np.float32)
    assert hu.shape == (512, 512, 275)
    affine = nii.affine
    inv = np.linalg.inv(affine)
    window = (-120, 600)
    display = np.rint(np.clip((hu - window[0]) / (window[1] - window[0]), 0, 1) * 255).astype(
        np.uint8
    )
    # x fastest, followed by y then z: browser index = x + nx * (y + ny*z).
    raw = display.transpose(2, 1, 0).copy().tobytes()
    packed = gzip.compress(raw, compresslevel=6, mtime=0)
    volume = base64.b64encode(packed).decode("ascii")
    receipts.append(
        {
            "path": str(image_path.relative_to(ROOT)),
            "sha256": sha(image_path),
            "copy": None,
            "display_cache_sha256": hashlib.sha256(raw).hexdigest(),
            "display_cache": "embedded, gzip uint8; full native grid, fixed HU window [-120,600]",
        }
    )

    def curves(answer):
        result = []
        for c in answer["centerlines"]:
            points = np.asarray(c["points_ras_mm"], dtype=float)
            v = nib.affines.apply_affine(inv, points)
            result.append(
                {
                    "id": c["id"],
                    "name": c.get("vessel_name", c["id"]),
                    "p": np.round(v, 5).tolist(),
                    "labels": c["labels"],
                }
            )
        return result

    models = []
    for i, (mid, title, revision, status, seconds, allowance, run) in enumerate(MODELS):
        path = Path(run) / "artifacts/app/answer"
        metrics = comparison[i]["metrics"] if i < 6 else resume["metrics"]
        digest = retain(path / "centerlines.json", mid + "-centerlines.json")
        expected = (
            comparison[i]["answer_sha256"]
            if i < 6
            else "b88be6300213139ef6126d49988500b99d389378642dbe477abaf481c96994dd"
        )
        assert digest == expected, (mid, digest, expected)
        method = path / "method.md"
        if (ROOT / method).exists():
            retain(method, mid + "-method.md")
        if mid == "v3-xhigh":
            retain(path / "extract.py", mid + "-extract.py")
        models.append(
            {
                "id": mid,
                "title": title,
                "revision": revision,
                "status": status,
                "seconds": seconds,
                "allowance": allowance,
                "metrics": metrics,
                "curves": curves(read_json(path / "centerlines.json")),
                "sha256": digest,
                "answer": "sources/" + mid + "-centerlines.json",
            }
        )
    reference = read_json(FROZEN / "tests/reference.json")
    refs = curves(reference)
    branch_points = {}
    for key in models[-1]["metrics"]["per_reference_category"]:
        p = np.concatenate(
            [
                np.array(c["p"])[np.array(c["labels"]) == int(key)]
                for c in refs
                if int(key) in c["labels"]
            ]
        )
        branch_points[key] = np.median(p, axis=0).round().astype(int).tolist()
    data = {
        "models": models,
        "reference": refs,
        "labels": LABELS,
        "shape": list(hu.shape),
        "spacing": list(map(float, nii.header.get_zooms())),
        "affine": affine.tolist(),
        "axis_codes": list(nib.aff2axcodes(affine)),
        "window": window,
        "branches": branch_points,
        "funnel": read_json(AUDIT / "candidate-funnel.json"),
        "audit": read_json(AUDIT / "trace-audit.json"),
    }
    summary = {**data, "models": [{k: v for k, v in m.items() if k != "curves"} for m in models]}
    summary.pop("reference")
    (out / "data.json").write_text(json.dumps(summary, indent=2) + "\n")
    manifest = {
        "schema_version": 1,
        "scope": "Six fresh attempts, seven saved outputs, one public development case. Read-only post-hoc presentation; no new trial.",
        "source_files": receipts,
        "volume": {
            "shape": data["shape"],
            "spacing_mm": data["spacing"],
            "affine_ras_mm": data["affine"],
            "axis_codes": data["axis_codes"],
            "display_window_hu": window,
            "raw_bytes": len(raw),
            "gzip_bytes": len(packed),
        },
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    table = "| Saved output | State | Actual wall time | Geometry, length | Labeled, length | Geometry, category mean | Labeled, category mean | Courses |\n| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |\n"
    htmlrows = ""
    for m in models:
        metrics = m["metrics"]
        g = metrics["geometry"]
        labeled = metrics["labeled"]
        seconds = round(m["seconds"])
        duration = f"{seconds // 3600}:{seconds // 60 % 60:02}:{seconds % 60:02}"
        vals = [
            g["length_weighted_recall_1mm"],
            labeled["length_weighted_recall_1mm"],
            g["macro_recall_1mm"],
            labeled["macro_recall_1mm"],
        ]
        table += (
            f"| {m['title']} | {m['status']} | {duration} | "
            + " | ".join(f"{100 * x:.1f}%" for x in vals)
            + f" | {metrics['polylines']} |\n"
        )
        htmlrows += (
            f'<tr><th scope="row">{m["title"]}</th><td>{m["status"]}</td><td>{duration}</td>'
            + "".join(f"<td>{100 * x:.1f}%</td>" for x in vals)
            + f"<td>{metrics['polylines']}</td></tr>"
        )
    report = (HERE / "report.md").read_text().replace("{{RESULTS_TABLE}}", table)
    (out / "report.md").write_text(report)
    md = MarkdownIt("commonmark", {"html": False}).enable("table")
    (out / "report.html").write_text(
        '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>BR-042 · Technical report</title><style>body{max-width:1000px;margin:50px auto;padding:0 24px;color:#1b2933;font:17px/1.65 system-ui}img{max-width:100%;height:auto}h1,h2,h3{line-height:1.15;margin-top:2em}a{color:#006864}table{border-collapse:collapse;width:100%;font-size:13px}th,td{padding:10px;border-bottom:1px solid #ccd3d5;text-align:left}code{font-size:.9em}blockquote{border-left:3px solid #007d72;padding-left:20px}@media print{body{font-size:11px;margin:0}a{color:inherit}h2,h3{break-after:avoid}table{font-size:9px}}</style><body>'
        + md.render(report)
        + "</body></html>"
    )
    methodcards = "".join(
        f'<article class="method"><h3>{title}</h3><p>{method}</p><p class="muted">{limit}</p><a href="sources/{source}">Retained method / code ↗</a></article>'
        for title, method, limit, source in METHODS
    )
    html = (HERE / "index.html").read_text()
    replacements = {
        "{{STYLE}}": (HERE / "style.css").read_text(),
        "{{SCRIPT}}": (HERE / "app.js").read_text(),
        "{{DATA}}": json.dumps(data, separators=(",", ":")).replace("</", "<\\/"),
        "{{VOLUME}}": volume,
        "{{STATIC_ROWS}}": htmlrows,
        "{{METHODS}}": methodcards,
    }
    for token, value in replacements.items():
        html = html.replace(token, value)
    assert "{{" not in html
    (out / "index.html").write_text(html)
    # Assert none of the retained evidence changed during the build.
    for receipt in receipts:
        assert sha(ROOT / receipt["path"]) == receipt["sha256"], receipt["path"]
    print(
        json.dumps(
            {
                "output": str(out),
                "html_mb": round(len(html.encode()) / 1e6, 2),
                "sources": len(receipts),
                "axis_codes": data["axis_codes"],
                "model_outputs": len(models),
                "all_answer_hashes_match": True,
            }
        )
    )


if __name__ == "__main__":
    main()
