"""Pin existing local images, then validate the two authorized task packages."""

import argparse
import hashlib
import json
import subprocess as sp
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BATCH = ROOT / ".local/dental-f018-contract-v3-20260922"
EXPS = ["dental-f018-contract-v3-astra-medium", "dental-f018-reference-v3-astra-medium"]
RUNTIME = "sha256:3de5f01c3d98a0ed47c9c6ac2ef202807e2761e0ece826d0b514c994f033f107"


def run(args, **kwargs):
    return sp.run(args, check=True, text=True, capture_output=True, timeout=900, **kwargs).stdout


def save(path, value):
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(value, indent=2) + "\n")
    tmp.replace(path)


def free():
    if (BATCH / "queue.json").exists():
        assert not json.loads((BATCH / "queue.json").read_text()).get("no_further_dispatch"), (
            "User/operator stop"
        )
    active = run(
        ["docker", "ps", "-q", "--filter", "label=com.docker.compose.service=main"]
    ).strip()
    if active:
        raise SystemExit("CAPACITY_WAIT: another Docker solver is active; no attempt dispatched")


def pin():
    assert (
        run(["docker", "image", "inspect", "tb3-dental-runtime:v1", "--format", "{{.Id}}"]).strip()
        == RUNTIME
    )
    receipt = json.loads((BATCH / "preparation-receipt.json").read_text())
    if (BATCH / "image-pins.json").exists():
        for exp in EXPS:
            for name, digest in receipt["experiments"][exp]["files"].items():
                path = ROOT / ".local" / exp / "task" / name
                assert hashlib.file_digest(path.open("rb"), "sha256").hexdigest() == digest, name
        return json.loads((BATCH / "image-pins.json").read_text())
    verifier = run(
        ["docker", "image", "inspect", "tb3-dental-f018-v3-evaluator:v3", "--format", "{{.Id}}"]
    ).strip()
    pins = {"runtime": RUNTIME, "verifier": verifier, "solvers": {}}
    for exp in EXPS:
        task = ROOT / ".local" / exp / "task"
        image = run(["docker", "image", "inspect", f"tb3-{exp}:v3", "--format", "{{.Id}}"]).strip()
        pins["solvers"][exp] = image
        cfg = task / "task.toml"
        cfg.write_text(
            cfg.read_text()
            .replace(f"tb3-{exp}:v3", image)
            .replace("tb3-dental-f018-v3-evaluator:v3", verifier)
        )
        receipt["experiments"][exp]["files"] = {
            str(p.relative_to(task)): hashlib.file_digest(p.open("rb"), "sha256").hexdigest()
            for p in task.rglob("*")
            if p.is_file()
        }
    receipt["status"] = "final_pinned_pre_controls"
    receipt["runtime_image_id"] = RUNTIME
    save(BATCH / "preparation-receipt.json", receipt)
    save(BATCH / "image-pins.json", pins)
    return pins


def preflight(i, exp, image):
    pre = BATCH / f"preflight-{i}"
    if (pre / "passed.json").exists():
        return
    free()
    pre.mkdir(exist_ok=True)
    base = pre / "base.yaml"
    base.write_text(f'services:\n  main:\n    image: {image}\n    command: ["sleep", "infinity"]\n')
    task = ROOT / ".local" / exp / "task"
    compose = [
        "docker",
        "compose",
        "-p",
        f"dental-f018-v3-preflight-{i}",
        "-f",
        str(base),
        "-f",
        str(task / "environment/docker-compose.yaml"),
    ]
    script = (
        Path(__file__)
        .with_name("probe.py")
        .read_text()
        .replace("EXAMPLE_EXPECTED = False", f"EXAMPLE_EXPECTED = {bool(i)!r}")
    )
    (pre / "probe.py").write_text(script)
    try:
        run(compose + ["up", "-d"])
        cid = run(compose + ["ps", "-q", "main"]).strip()
        result = run(["docker", "exec", "-i", cid, "python", "-"], input=script)
        (pre / "result.json").write_text(result)
        raw = json.loads(run(["docker", "inspect", cid]))[0]
        state = {
            "image": raw["Image"],
            "networks": raw["NetworkSettings"]["Networks"],
            "mounts": raw["Mounts"],
            "cap_drop": raw["HostConfig"]["CapDrop"],
        }
        assert not state["mounts"]
        networks = [
            json.loads(run(["docker", "network", "inspect", n]))[0] for n in state["networks"]
        ]
        assert len(networks) == 1 and networks[0]["Internal"]
        state["networks_internal"] = {n["Name"]: n["Internal"] for n in networks}
        save(pre / "isolation.json", state)
    finally:
        (pre / "transport.log").write_text(run(compose + ["logs", "--no-color", "transport"]))
        run(compose + ["down"])
    save(pre / "passed.json", {"passed": True, "solver_image": image})
    print(exp, "isolation preflight passed", flush=True)


def controls(exp, records):
    row = records.setdefault(exp, {"passed": False})
    for agent, expected in [("oracle", 1.0), ("nop", 0.0)]:
        if agent in row:
            assert row[agent]["passed"]
            continue
        free()
        marker = BATCH / f"{exp}-{agent}-once.json"
        with marker.open("x") as handle:
            json.dump({"experiment": exp, "agent": agent}, handle)
        attempts = ROOT / "groups/anatomy-audit/experiments" / exp / "attempts"
        before = set(attempts.glob("*.json"))
        cmd = [
            str(ROOT / ".venv/bin/med"),
            "run",
            exp,
            "--agent",
            agent,
            "--harbor",
            str(ROOT / ".venv/bin/harbor"),
        ]
        with (BATCH / f"{exp}-{agent}.log").open("x") as log:
            sp.run(cmd, cwd=ROOT, stdout=log, stderr=sp.STDOUT, check=True, timeout=900)
        created = set(attempts.glob("*.json")) - before
        assert len(created) == 1
        attempt = json.loads(created.pop().read_text())
        folder = ROOT / ".local/attempts" / attempt["id"]
        execution = json.loads((folder / "execution.json").read_text())
        trials = list((folder / "job").glob("task__*/result.json"))
        assert len(trials) == 1
        result = json.loads(trials[0].read_text())
        reward = result["verifier_result"]["rewards"]["reward"]
        passed = (
            execution["execution_state"] == "completed"
            and execution["frozen_payload_unchanged"]
            and result["exception_info"] is None
            and reward == expected
        )
        row[agent] = {
            "attempt_id": attempt["id"],
            "task_digest": attempt["task_digest"],
            "reward": reward,
            "passed": passed,
        }
        save(BATCH / "lifecycle-controls.json", records)
        assert passed, "Control failed; retain evidence for review before any inference"
        print(exp, agent, "passed", flush=True)
    row["passed"] = True
    save(BATCH / "lifecycle-controls.json", records)


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--pin-only", action="store_true")
    args = parser.parse_args()
    pins = pin()
    if args.pin_only:
        print(json.dumps(pins, indent=2))
        return
    for i, exp in enumerate(EXPS):
        preflight(i, exp, pins["solvers"][exp])
    path = BATCH / "lifecycle-controls.json"
    records = json.loads(path.read_text()) if path.exists() else {}
    for exp in EXPS:
        controls(exp, records)
    save(BATCH / "setup-complete.json", {"passed": True, "experiments": EXPS})
    print(
        "Both task packages ready; monitor must recheck quota and dispatch the first condition.",
        flush=True,
    )


if __name__ == "__main__":
    main()
