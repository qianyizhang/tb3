"""Associate successful image observations with statically documented slice coordinates."""

import argparse
import ast
import collections
import json
import re
import shlex
from pathlib import Path
from analyze import ATTEMPTS, literal


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, required=True)
    ap.add_argument("--analysis", type=Path, required=True)
    args = ap.parse_args()
    result = {}
    for condition, aid in ATTEMPTS.items():
        ev = json.loads((args.analysis / (condition + "-events.json")).read_text())
        known = {}
        views = []
        unknown = []
        work = (
            next((args.root / ".local/attempts" / ("attempt-" + aid) / "job").glob("task__*"))
            / "artifacts/app/work"
        )

        def put(path, axis, zs, step, method):
            known[path] = {"axis": axis, "indices": list(zs), "render_step": step, "source": method}

        for e in ev:
            step = e["step"]
            text = e["text"]
            if e["type"] == "command":
                # Literal sheet/review calls, including saved script's guarded entrypoint.
                for line in text.splitlines():
                    line = line.strip()
                    if re.match(r"(sheet|review)\(", line):
                        try:
                            call = ast.parse(line).body[0].value
                            axis, zs, name = [literal(x) for x in call.args[:3]]
                            put("/app/work/" + name, axis, zs, step, line)
                        except (ValueError, SyntaxError, TypeError):
                            pass
                if condition == "astra-xhigh":
                    # Calls in saved review.py are executed again at step 47.
                    if step == 47:
                        for path in ["review_ax.png", "review_cor.png"]:
                            known["/app/work/" + path]["render_step"] = step
                for line in text.splitlines():
                    if not re.match(r"\s*python(?:3)? /app/work/", line):
                        continue
                    expanded = re.sub(
                        r"\$\(seq (\d+) (\d+) (\d+)\)",
                        lambda m: " ".join(map(str, range(int(m[1]), int(m[3]) + 1, int(m[2])))),
                        line,
                    )
                    try:
                        t = shlex.split(expanded)
                    except ValueError:
                        continue
                    script = Path(t[1]).name
                    argv = t[2:]
                    if condition == "sol-xhigh" and script in ["montage.py", "overlay.py"]:
                        axis = (
                            {0: "x", 1: "y", 2: "z"}[int(argv[argv.index("--axis") + 1])]
                            if "--axis" in argv
                            else "z"
                        )
                        start = argv.index("--indices") + 1
                        zs = []
                        for tok in argv[start:]:
                            if not tok.isdigit():
                                break
                            zs.append(int(tok))
                        put(argv[argv.index("--out") + 1], axis, zs, step, line)
                    if condition == "astra-medium":
                        spec = {
                            "axial.py": ("z", "axial.png"),
                            "crop.py": ("z", "crop.png"),
                            "detail.py": ("z", "detail.png"),
                            "adrenalview.py": ("z", "detail.png"),
                            "gbview.py": ("z", "detail.png"),
                            "kidneyview.py": ("z", "detail.png"),
                            "overlay.py": ("z", "overlay.png"),
                            "cor.py": ("y", "cor.png"),
                            "cor2.py": ("y", "cor.png"),
                            "sag.py": ("x", "sag.png"),
                            "orthoview.py": ("y", "ortho.png"),
                        }
                        if script in spec and argv:
                            axis, name = spec[script]
                            put(
                                "/app/work/" + name,
                                axis,
                                [int(v) for v in argv if v.isdigit()],
                                step,
                                line,
                            )
                        if script == "view.py":
                            put(
                                "/app/work/coronal.png",
                                "y",
                                [80, 100, 120, 140, 160, 180, 200, 220],
                                step,
                                line,
                            )
                    if condition.endswith("litemedsam"):
                        if script == "montage.py":
                            put("/app/work/overview.jpg", "z", range(40, 345, 16), step, line)
                        elif script in [
                            "show.py",
                            "cropseries.py",
                            "adrenalseries.py",
                            "gbseries.py",
                        ]:
                            put(argv[0], "z", map(int, argv[1:]), step, line)
                        elif script == "single.py":
                            for z in map(int, argv):
                                put(f"/app/work/detail{z}.png", "z", [z], step, line)
                        elif script == "review.py":
                            put(argv[1], "z", map(int, argv[2:]), step, line)
                        elif script == "overlay.py":
                            put("/app/work/o" + argv[0] + ".png", "z", [int(argv[0])], step, line)
                        elif script == "final_review.py":
                            put(
                                "/app/work/final_axial.jpg",
                                "z",
                                [155, 170, 185, 195, 200, 205, 210, 220, 230, 240, 250, 260],
                                step,
                                line,
                            )
                            put(
                                "/app/work/final_coronal.jpg",
                                "y",
                                [174, 159, 144, 129, 114, 99],
                                step,
                                line,
                            )
                        elif script in ["coronal.py", "sag.py", "right_detail.py"]:
                            source = (work / script).read_text()
                            d = {}
                            for n in ast.walk(ast.parse(source)):
                                if isinstance(n, ast.Assign):
                                    for target in n.targets:
                                        if isinstance(target, ast.Name):
                                            try:
                                                d[target.id] = literal(n.value)
                                            except (ValueError, TypeError):
                                                pass
                            # Fixed coordinate arrays in the retained renderer.
                            if script == "coronal.py":
                                put(
                                    "/app/work/coronal.jpg",
                                    "y",
                                    [194, 179, 164, 149, 134, 119, 104, 89],
                                    step,
                                    line,
                                )
                            elif script == "sag.py":
                                put(
                                    "/app/work/sag.jpg",
                                    "x",
                                    [115, 125, 140, 155, 165, 175],
                                    step,
                                    line,
                                )
                            else:
                                put(
                                    "/app/work/right_detail.png",
                                    "z",
                                    [190, 195, 200, 205, 210, 215],
                                    step,
                                    line,
                                )
            elif e["type"] == "view" and e["image_observed_in_step"]:
                if text in known:
                    views.append({"step": step, "path": text, **known[text]})
                else:
                    unknown.append(e)
        assert not unknown, unknown
        assert all(v["indices"] for v in views), views
        count = collections.Counter(z for v in views if v["axis"] == "z" for z in set(v["indices"]))
        axis = collections.Counter(v["axis"] for v in views)
        result[condition] = {
            "successful_images": sum(
                e["type"] == "view" and e["image_observed_in_step"] for e in ev
            ),
            "view_calls": sum(e["type"] == "view" for e in ev),
            "mapped_images": len(views),
            "by_plane": dict(axis),
            "axial_unique_slices": len(count),
            "axial_total_plane_exposures": sum(count.values()),
            "axial_revisited_slices": sum(n > 1 for n in count.values()),
            "axial_slice_counts": dict(sorted(count.items())),
            "views": views,
            "unmapped": unknown,
        }
    (args.analysis / "views.json").write_text(json.dumps(result, indent=2) + "\n")
    print(
        json.dumps(
            {
                k: {x: v for x, v in r.items() if x not in ["views", "axial_slice_counts"]}
                for k, r in result.items()
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
