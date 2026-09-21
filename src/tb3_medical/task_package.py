"""Portable, selected-input experiment packages. Also runs without the workbench.

The package contains solver tasks, private verifiers and optional saved answers in
separate directories. Only the task environment is exposed to a model execution.
This module never executes historical authoring scripts or downloads data.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import importlib.metadata
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def inside(root, name):
    root = Path(root).resolve()
    candidate = root / name
    path = candidate.resolve()
    if Path(name).is_absolute() or not path.is_relative_to(root):
        raise ValueError("Package path escapes its root: " + str(name))
    if any(
        p.is_symlink()
        for p in [candidate, *candidate.parents]
        if p != root and p.is_relative_to(root)
    ):
        raise ValueError("Package input contains a symlink: " + str(name))
    return path


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def select(manifest, case=None):
    if case is None:
        return list(manifest["cases"])
    if case not in manifest["cases"]:
        raise ValueError("Choose a case from: " + ", ".join(manifest["cases"]))
    return [case]


def verify(root, manifest, case=None, *, saved=True):
    cases = select(manifest, case)
    checked = 0
    seen = set()
    for entry in manifest["files"]:
        if entry["path"] in seen:
            raise ValueError("Duplicate manifest path: " + entry["path"])
        seen.add(entry["path"])
        if entry.get("case") not in [None, *cases]:
            continue
        if not saved and entry.get("role") == "saved_output":
            continue
        path = inside(root, entry["path"])
        if not path.is_file() or path.is_symlink():
            raise ValueError("Missing regular package input: " + entry["path"])
        if path.stat().st_size != entry["size"] or sha(path) != entry["sha256"]:
            raise ValueError("Changed package input: " + entry["path"])
        if os.name == "posix" and path.stat().st_mode & 0o111 != entry["mode"] & 0o111:
            raise ValueError("Changed executable mode: " + entry["path"])
        checked += 1
    return {"verified_files": checked, "cases": cases}


def materialize(
    workspace, manifest_path, destination, *, case=None, input_root=None, assessments=None
):
    """Copy declared inputs into a fresh portable directory; preflight everything."""
    workspace = Path(workspace).resolve()
    manifest = read(inside(workspace, manifest_path))
    cases = select(manifest, case)
    entries = [e for e in manifest["files"] if e.get("case") in [None, *cases]]
    dest = Path(destination).resolve()
    if dest.exists():
        raise ValueError("Choose a fresh destination: " + str(dest))
    sources = []
    names = set()
    for entry in entries:
        if entry["path"] in names or entry["path"] in {
            "manifest.json",
            "reproduce.py",
            "INCOMPLETE",
        }:
            raise ValueError("Duplicate or reserved package path: " + entry["path"])
        names.add(entry["path"])
        inside(dest, entry["path"])
        source = (
            inside(input_root, entry["path"])
            if input_root is not None and entry["origin"] == "artifact"
            else inside(workspace, entry["source"])
        )
        if not source.is_file() or source.is_symlink():
            raise ValueError(
                f"Missing input {entry['path']}; see acquisition.md or supply --input-root "
                "with the prepared input bundle. No historical-directory fallback is used."
            )
        if source.stat().st_size != entry["size"] or sha(source) != entry["sha256"]:
            raise ValueError("Changed preparation input: " + str(source))
        sources.append(source)
    dest.mkdir(parents=True, exist_ok=False)
    try:
        for entry, source in zip(entries, sources):
            target = inside(dest, entry["path"])
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
            target.chmod(entry["mode"])
        portable = {k: v for k, v in manifest.items() if k != "files"}
        portable["cases"] = {k: manifest["cases"][k] for k in cases}
        portable["method_replays"] = {
            k: v for k, v in manifest.get("method_replays", {}).items() if v["case"] in cases
        }
        portable["source_manifest_sha256"] = sha(inside(workspace, manifest_path))
        portable["source_assessments"] = assessments or {}
        portable["submission_status"] = "draft"
        portable["files"] = [
            {k: v for k, v in entry.items() if k not in {"source", "origin"}} for entry in entries
        ]
        # Freeze the selected installed runner at handoff time. Experiment input
        # manifests need not be rewritten whenever shared implementation changes.
        runner = dest / "reproduce.py"
        shutil.copyfile(__file__, runner)
        runner.chmod(0o644)
        portable["files"].append(
            {
                "path": "reproduce.py",
                "sha256": sha(runner),
                "size": runner.stat().st_size,
                "mode": 0o644,
                "case": None,
                "role": "runtime",
            }
        )
        write(dest / "manifest.json", portable)
        return {"destination": str(dest), **verify(dest, portable)}
    except BaseException:
        (dest / "INCOMPLETE").write_text("Preparation failed; use a fresh destination.\n")
        raise


def validate_metadata(workspace, experiment, records):
    """Check declared paths and references without inspecting raw local artifacts."""
    manifest = read(inside(workspace, experiment["reproduction_manifest"]))
    if manifest["experiment_id"] != experiment["id"] or not manifest["cases"]:
        raise ValueError("Reproduction manifest has wrong owner or no cases")
    by_path = {}
    for entry in manifest["files"]:
        inside(workspace, entry["source"])
        inside(workspace, entry["path"])
        if entry["path"] in by_path:
            raise ValueError("Duplicate reproduction input: " + entry["path"])
        if entry["origin"] not in {"git", "artifact"}:
            raise ValueError("Reproduction inputs require git or artifact origin")
        if entry.get("case") is not None and entry["case"] not in manifest["cases"]:
            raise ValueError("Input references unknown case")
        if entry["origin"] == "git" and not inside(workspace, entry["source"]).is_file():
            raise ValueError("Missing maintained recipe source: " + entry["source"])
        by_path[entry["path"]] = entry
    for spec in manifest["cases"].values():
        if spec["evaluator"] not in by_path:
            raise ValueError("Case evaluator is not in its input manifest")
        for obs in spec.get("observations", []):
            if obs["attempt_id"] not in records or obs["source_evaluation"] not in records:
                raise ValueError("Replay must reference an existing attempt and observation")
            if records[obs["source_evaluation"]].get("attempt_id") != obs["attempt_id"]:
                raise ValueError("Replay source observation belongs to another attempt")
            if obs["expected"] not in by_path:
                raise ValueError("Replay expected metrics are not a declared input")
    for spec in manifest.get("method_replays", {}).values():
        if spec["case"] not in manifest["cases"] or spec["source_attempt"] not in records:
            raise ValueError("Transfer must reference a declared case and original attempt")
        for field in ("evaluator", "expected"):
            if spec[field] not in by_path:
                raise ValueError("Transfer scorer and expected metrics must be declared inputs")
        for field in ("input", "program", "saved", "environment"):
            inside(workspace, spec[field])
            if not any(name.startswith(spec[field] + "/") for name in by_path):
                raise ValueError("Transfer directory has no declared inputs: " + spec[field])
    return len(manifest["cases"])


def evaluate(root, manifest, case, answer, python=sys.executable):
    select(manifest, case)
    verify(root, manifest, case, saved=False)
    spec = manifest["cases"][case]
    answer = Path(answer).resolve()
    command = [
        str(python),
        "-B",
        str(inside(root, spec["evaluator"])),
        "--answer",
        str(answer),
    ]
    proc = subprocess.run(
        command, capture_output=True, text=True, timeout=spec.get("timeout_sec", 900)
    )
    if proc.returncode:
        raise ValueError("Evaluator process failed: " + proc.stderr[-3000:])
    return json.loads(proc.stdout)


def compare(actual, expected, *, atol=1e-8, rtol=1e-8, path=""):
    """Compare named scientific metrics; timing/error strings are excluded explicitly."""
    if isinstance(expected, dict):
        return (
            isinstance(actual, dict)
            and actual.keys() == expected.keys()
            and all(
                compare(actual[k], v, atol=atol, rtol=rtol, path=f"{path}/{k}")
                for k, v in expected.items()
            )
        )
    if isinstance(expected, list):
        return (
            isinstance(actual, list)
            and len(actual) == len(expected)
            and all(
                compare(a, b, atol=atol, rtol=rtol, path=path) for a, b in zip(actual, expected)
            )
        )
    if isinstance(expected, (int, float)) and not isinstance(expected, bool):
        return (
            isinstance(actual, (int, float))
            and not isinstance(actual, bool)
            and math.isfinite(actual)
            and math.isclose(actual, expected, abs_tol=atol, rel_tol=rtol)
        )
    return type(actual) is type(expected) and actual == expected


def replay(root, manifest, case=None, python=sys.executable):
    verify(root, manifest, case)
    results = []
    for name in select(manifest, case):
        for observation in manifest["cases"][name].get("observations", []):
            answer = inside(root, observation["answer"])
            actual = evaluate(root, manifest, name, answer, python)
            expected = read(inside(root, observation["expected"]))
            excluded = observation.get("excluded_fields", [])
            actual = {k: v for k, v in actual.items() if k not in excluded}
            expected = {k: v for k, v in expected.items() if k not in excluded}
            results.append(
                {
                    "case": name,
                    "attempt_id": observation["attempt_id"],
                    "source_evaluation": observation["source_evaluation"],
                    "matches": compare(actual, expected),
                    "exact_match": actual == expected,
                    "metrics": actual,
                }
            )
    if not results:
        raise ValueError("No saved-output replay is declared for the selected cases")
    return {
        "scope": "Saved-output scoring; absolute and relative tolerance 1e-8 for numeric metrics",
        "all_match": all(r["matches"] for r in results),
        "replays": results,
    }


def controls(root, manifest, case=None, python=sys.executable):
    """Fresh host scorer checks, not Harbor runtime controls or qualification."""
    results = []
    for name in select(manifest, case):
        spec = manifest["cases"][name]
        verify(root, manifest, name, saved=False)
        for role in ("oracle", "nop"):
            answer = inside(root, spec["controls"][role]["answer"])
            answer.mkdir(parents=True, exist_ok=True)
            metrics = evaluate(root, manifest, name, answer, python)
            expected = spec["controls"][role]["reward"]
            reward = metrics.get(
                "reward", int(metrics.get("passed", metrics.get("contract_pass", False)))
            )
            results.append({"case": name, "role": role, "reward": reward, "expected": expected})
    return {
        "scope": "Fresh host scoring controls; no agent execution or Harbor qualification",
        "all_expected": all(r["reward"] == r["expected"] for r in results),
        "controls": results,
    }


def container_controls(root, manifest, case=None):
    """Build the declared solver/verifier environments; execute original oracle/nop."""
    subprocess.run(["docker", "info"], capture_output=True, check=True, timeout=30)
    root = Path(root).resolve()
    results = []
    for name in select(manifest, case):
        verify(root, manifest, name, saved=False)
        spec = manifest["cases"][name]
        task = inside(root, spec["task"])
        tags = {}
        for label, folder in (("solver", "environment"), ("verifier", "tests")):
            signature = sha(task / folder / "Dockerfile")[:12]
            tag = f"tb3-reproduce-{manifest['experiment_id']}-{name}-{label}:{signature}"
            subprocess.run(
                ["docker", "build", "--pull=false", "-t", tag, str(task / folder)],
                check=True,
                stdout=sys.stderr,
                timeout=1800,
            )
            tags[label] = tag
        image_ids = {
            k: subprocess.check_output(
                ["docker", "image", "inspect", "--format", "{{.Id}}", v], text=True
            ).strip()
            for k, v in tags.items()
        }
        with tempfile.TemporaryDirectory(prefix="controls-", dir=root) as temporary:
            base = Path(temporary)
            for role in ("oracle", "nop"):
                answer = base / role / "answer"
                logs = base / role / "logs"
                answer.mkdir(parents=True)
                logs.mkdir()
                # Starter answers belong to the environment and must remain present
                # for nop. Extract them before mounting the writable answer directory.
                starter = spec["controls"]["nop"]["answer"]
                if inside(root, starter).is_dir():
                    shutil.copytree(inside(root, starter), answer, dirs_exist_ok=True)
                if role == "oracle":
                    subprocess.run(
                        [
                            "docker",
                            "run",
                            "--rm",
                            "--network=none",
                            "--cpus=4",
                            "--memory=6g",
                            "-v",
                            f"{task / 'solution'}:/solution:ro",
                            "-v",
                            f"{answer}:/app/answer",
                            tags["solver"],
                            "sh",
                            "/solution/solve.sh",
                        ],
                        check=True,
                        stdout=sys.stderr,
                        timeout=spec.get("timeout_sec", 900),
                    )
                subprocess.run(
                    [
                        "docker",
                        "run",
                        "--rm",
                        "--network=none",
                        "--cpus=4",
                        "--memory=6g",
                        "-v",
                        f"{answer}:/app/answer:ro",
                        "-v",
                        f"{logs}:/logs/verifier",
                        tags["verifier"],
                    ],
                    check=True,
                    stdout=sys.stderr,
                    timeout=spec.get("timeout_sec", 900),
                )
                reward = float((logs / "reward.txt").read_text().strip())
                results.append(
                    {
                        "case": name,
                        "role": role,
                        "reward": reward,
                        "expected": spec["controls"][role]["reward"],
                        "images": image_ids,
                    }
                )
    return {
        "scope": "Fresh Docker oracle/no-op execution; no model attempt",
        "all_expected": all(r["reward"] == r["expected"] for r in results),
        "controls": results,
    }


def method_replay(root, manifest, case=None, python=sys.executable, work_dir=None):
    """Score retained transfers, or reexecute the frozen submitted programs in Docker."""
    cases = select(manifest, case)
    verify(root, manifest, case)
    specs = {k: v for k, v in manifest.get("method_replays", {}).items() if v["case"] in cases}
    if not specs:
        raise ValueError("No submitted-program transfers declared for these cases")
    root = Path(root).resolve()
    if work_dir is not None:
        work_dir = Path(work_dir).resolve()
        if work_dir.exists():
            raise ValueError("Choose a fresh method output directory")
        subprocess.run(["docker", "info"], capture_output=True, check=True, timeout=30)
        work_dir.mkdir(parents=True)
    results = []
    for name, spec in specs.items():
        answer = inside(root, spec["saved"])
        image_id = None
        if work_dir is not None:
            env = inside(root, spec["environment"])
            tag = f"tb3-method-{manifest['experiment_id']}-{name}:{sha(env / 'Dockerfile')[:12]}"
            subprocess.run(
                ["docker", "build", "--pull=false", "-t", tag, str(env)],
                check=True,
                stdout=sys.stderr,
                timeout=1800,
            )
            image_id = subprocess.check_output(
                ["docker", "image", "inspect", "--format", "{{.Id}}", tag], text=True
            ).strip()
            out = inside(work_dir, name)
            answer = out / "answer"
            answer.mkdir(parents=True)
            container = "tb3-method-" + hashlib.sha256(str(out).encode()).hexdigest()[:20]
            command = [
                "docker",
                "run",
                "--rm",
                "--name",
                container,
                "--network=none",
                "--cpus=4",
                "--memory=6g",
                "--read-only",
                "--tmpfs",
                "/tmp:rw,size=2g",
                "-e",
                "OMP_NUM_THREADS=4",
                "-e",
                "OPENBLAS_NUM_THREADS=4",
                "-v",
                f"{inside(root, spec['program'])}:/solver:ro",
                "-v",
                f"{inside(root, spec['input'])}:/app/data:ro",
                "-v",
                f"{answer}:/app/answer:rw",
                "--entrypoint",
                "python",
                tag,
                "/solver/solve.py",
                "--input",
                "/app/data",
                "--output",
                "/app/answer",
            ]
            with (out / "execution.log").open("w") as log:
                try:
                    subprocess.run(
                        command,
                        check=True,
                        stdout=log,
                        stderr=subprocess.STDOUT,
                        timeout=spec.get("timeout_sec", 300),
                    )
                except subprocess.TimeoutExpired:
                    subprocess.run(
                        ["docker", "kill", container],
                        stdout=log,
                        stderr=subprocess.STDOUT,
                        timeout=30,
                    )
                    raise
        proc = subprocess.run(
            [str(python), "-B", str(inside(root, spec["evaluator"])), "--answer", str(answer)],
            capture_output=True,
            text=True,
            timeout=900,
        )
        if proc.returncode:
            raise ValueError("Transfer scorer failed: " + proc.stderr[-3000:])
        metrics = json.loads(proc.stdout)
        expected = read(inside(root, spec["expected"]))
        results.append(
            {
                "method": name,
                "source_attempt": spec["source_attempt"],
                "matches": compare(metrics, expected),
                "exact_match": metrics == expected,
                "metrics": metrics,
                "solver_image": image_id,
                "output_sha256": {
                    str(p.relative_to(answer)): sha(p)
                    for p in sorted(answer.rglob("*"))
                    if p.is_file()
                },
            }
        )
    verify(root, manifest, case)
    return {
        "scope": "Fresh frozen submitted-program execution"
        if work_dir
        else "Saved transfer-output scoring",
        "all_match": all(r["matches"] for r in results),
        "methods": results,
        "clinical_limit": "Cavity references do not establish myocardial material correspondence or etiologic diagnosis.",
    }


def inspect(root, manifest, case, output):
    """A portable inspection page for instructions, data inventory and source notices."""
    verify(root, manifest, case, saved=False)
    spec = manifest["cases"][case]
    task = inside(root, spec["task"])
    entries = [
        e for e in manifest["files"] if e.get("case") == case and "/environment/" in e["path"]
    ]
    body = html.escape((task / "instruction.md").read_text())
    table = "".join(
        f"<tr><td>{html.escape(e['path'])}</td><td>{e['size']}</td><td>{e['sha256']}</td></tr>"
        for e in entries
    )
    text = f"""<!doctype html><meta charset="utf-8"><title>{html.escape(case)}</title>
<style>body{{font:16px system-ui;max-width:1100px;margin:40px auto;padding:20px}}pre{{white-space:pre-wrap}}td{{padding:8px;overflow-wrap:anywhere}}table{{width:100%;table-layout:fixed}}</style>
<h1>{html.escape(manifest["experiment_id"])}: {html.escape(case)}</h1>
<p>Task instructions and solver-visible input inventory. Private references and saved answers are evaluator-only.</p>
<pre>{body}</pre><h2>Input sanity checks</h2><p>Use reproduce.py verify to check exact sizes and SHA-256 values before a run.</p>
<table><tr><th>Solver input</th><th>Bytes</th><th>SHA-256</th></tr>{table}</table>"""
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text)
    return {"output": str(output), "scope": "Task and input inspection; not raw-image rendering"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "operation",
        choices=[
            "verify",
            "evaluate",
            "replay",
            "controls",
            "container-controls",
            "method-replay",
            "inspect",
        ],
    )
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--case")
    parser.add_argument("--answer", type=Path)
    parser.add_argument(
        "--work-dir",
        type=Path,
        help="With method-replay, execute the frozen program into a fresh directory",
    )
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        manifest = read(args.root / "manifest.json")
        if (args.root / "INCOMPLETE").exists():
            raise ValueError("Package preparation is incomplete")
        if args.operation == "evaluate":
            if args.case is None or args.answer is None:
                parser.error("evaluate requires --case and --answer DIRECTORY")
            result = evaluate(args.root, manifest, args.case, args.answer, args.python)
        elif args.operation == "inspect":
            if args.case is None or args.output is None:
                parser.error("inspect requires --case and --output FILE")
            result = inspect(args.root, manifest, args.case, args.output)
        elif args.operation == "verify":
            result = verify(args.root, manifest, args.case)
        elif args.operation == "method-replay":
            result = method_replay(args.root, manifest, args.case, args.python, args.work_dir)
        elif args.operation == "container-controls":
            result = container_controls(args.root, manifest, args.case)
        else:
            function = replay if args.operation == "replay" else controls
            result = function(args.root, manifest, args.case, args.python)
        if args.operation != "inspect" and args.output:
            if args.output.exists():
                raise ValueError("Receipt exists; choose a fresh output path")
            versions = {}
            for package in ("numpy", "scipy", "pillow", "nibabel"):
                try:
                    versions[package] = importlib.metadata.version(package)
                except importlib.metadata.PackageNotFoundError:
                    pass
            write(
                args.output,
                {
                    "observed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                    "experiment_id": manifest["experiment_id"],
                    "manifest_sha256": sha(args.root / "manifest.json"),
                    "runner_sha256": sha(__file__),
                    "driver_python": sys.version,
                    "driver_packages": versions,
                    "evaluator_python": str(args.python),
                    "result": result,
                },
            )
        print(json.dumps(result, indent=2, allow_nan=False))
        return 0 if result.get("all_match", result.get("all_expected", True)) else 1
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
        print("reproduce: " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
