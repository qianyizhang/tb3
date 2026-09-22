"""Verify a live owned solver without exposing credentials or providing feedback."""

import argparse
import json
import subprocess as sp
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BATCH = ROOT / ".local/dental-f018-contract-v3-20260922"
EXPS = ["dental-f018-contract-v3-astra-medium", "dental-f018-reference-v3-astra-medium"]


def run(args, **kwargs):
    return sp.run(args, check=True, capture_output=True, text=True, timeout=30, **kwargs).stdout


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("experiment", choices=EXPS)
    args = parser.parse_args()
    base = ROOT / ".local" / args.experiment
    state = json.loads((base / "operator-state.json").read_text())
    assert state["state"] == "running", "Reconcile terminal state instead of live inspection"
    project = state["compose_project"]
    cid = run(
        [
            "docker",
            "ps",
            "-q",
            "--filter",
            "label=com.docker.compose.project=" + project,
            "--filter",
            "label=com.docker.compose.service=main",
        ]
    ).strip()
    assert cid and "\n" not in cid
    raw = json.loads(run(["docker", "inspect", cid]))[0]
    pins = json.loads((BATCH / "image-pins.json").read_text())
    assert raw["Image"] == pins["solvers"][args.experiment]
    networks = {}
    for name in raw["NetworkSettings"]["Networks"]:
        network = json.loads(run(["docker", "network", "inspect", name]))[0]
        networks[name] = {"internal": network["Internal"]}
    assert len(networks) == 1 and all(n["internal"] for n in networks.values())
    trial = Path(state["trial_path"])
    allowed = {
        "/logs/agent": trial / "agent",
        "/logs/artifacts": trial / "artifacts/logs/artifacts",
        "/logs/verifier": trial / "verifier",
    }
    assert len(raw["Mounts"]) == len(allowed)
    for mount in raw["Mounts"]:
        assert mount["Type"] == "bind"
        assert Path(mount["Source"]) == allowed[mount["Destination"]]
    assert "ALL" in raw["HostConfig"]["CapDrop"]
    assert "no-new-privileges:true" in raw["HostConfig"]["SecurityOpt"]
    script = """import pathlib,json
paths=['/tests','/solution','/Users','/var/run/docker.sock']
print(json.dumps({'private_absent':{p:not pathlib.Path(p).exists() for p in paths},
'data':sorted(str(p) for p in pathlib.Path('/app/data').rglob('*') if p.is_file()),
'reference':sorted(str(p) for p in pathlib.Path('/app/reference').rglob('*') if p.is_file())}))
"""
    files = json.loads(run(["docker", "exec", "-i", cid, "python", "-"], input=script))
    assert all(files["private_absent"].values())
    assert files["data"] == ["/app/data/ct.nii.gz", "/app/data/labels.json"]
    expected = (
        []
        if args.experiment == EXPS[0]
        else ["/app/reference/ct.nii.gz", "/app/reference/segmentation.nii.gz"]
    )
    assert files["reference"] == expected
    trace = trial / "agent/codex.txt"
    commands = 0
    if trace.exists():
        for line in trace.read_text().splitlines():
            try:
                item = json.loads(line).get("item", {})
            except ValueError:
                continue
            commands += item.get("type") == "command_execution"
    log = base / "model-transport.log"
    assert log.is_file() and log.stat().st_size > 0
    assert commands > 0, "No actual inference command yet; recheck shortly without relaunching"
    receipt = {
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "attempt_id": state["attempt_id"],
        "trial_path": str(trial),
        "container_id": cid,
        "image": raw["Image"],
        "networks": networks,
        "mounts": raw["Mounts"],
        "cap_drop": raw["HostConfig"]["CapDrop"],
        "security_opt": raw["HostConfig"]["SecurityOpt"],
        "files": files,
        "transport_log_retained": True,
        "inference_command_events": commands,
    }
    path = base / "runtime-isolation.json"
    if not path.exists():
        with path.open("x") as handle:
            json.dump(receipt, handle, indent=2)
    print(
        json.dumps(
            {
                "attempt_id": state["attempt_id"],
                "verified": True,
                "command_events": commands,
                "image": raw["Image"],
            }
        )
    )


if __name__ == "__main__":
    main()
