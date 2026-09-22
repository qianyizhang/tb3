"""Pin local images, exercise the data-only environment, and freeze a file manifest."""

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / ".local/longitudinal-ct-image-only-v1"
TASK = BASE / "task"


def run(args, **kwargs):
    return subprocess.run(
        args, cwd=ROOT, text=True, capture_output=True, check=True, **kwargs
    ).stdout


def main():
    expected_runtime = json.loads((BASE / "preparation.json").read_text())["runtime_image"]
    tags = {
        "runtime": "tb3-longitudinal-runtime:validated-v1",
        "solver": "tb3-longitudinal-image-only-solver:v1",
        "evaluator": "tb3-longitudinal-image-only-evaluator:v1",
    }
    identities = {
        k: run(["docker", "image", "inspect", "--format", "{{.Id}}", tag]).strip()
        for k, tag in tags.items()
    }
    assert identities["runtime"] == expected_runtime
    identities["transport"] = json.loads((BASE / "preparation.json").read_text())["transport_image"]
    p = TASK / "task.toml"
    config = p.read_text()
    for k in ("solver", "evaluator"):
        config = config.replace(tags[k], identities[k])
    p.write_text(config)
    (BASE / "image-identities.json").write_text(json.dumps(identities, indent=2) + "\n")
    compose = (TASK / "environment/docker-compose.yaml").read_text()
    compose = compose.replace(
        "  main:\n",
        "  main:\n    image: " + identities["solver"] + '\n    command: ["sleep", "infinity"]\n',
    )
    preflight = BASE / "preflight-compose.yaml"
    preflight.write_text(compose)
    cmd = ["docker", "compose", "-p", "longitudinal-image-only-preflight", "-f", str(preflight)]
    probe = """import json, pathlib, socket
r={"files":sorted(str(p) for p in pathlib.Path("/app").rglob("*") if p.is_file()),
   "private_paths_absent":{p:not pathlib.Path(p).exists() for p in ["/tests","/solution","/Users","/var/run/docker.sock"]},"network":[]}
assert r["files"]==["/app/data/baseline.nii.gz","/app/data/followup.nii.gz"]
assert all(r["private_paths_absent"].values())
for host in ["huggingface.co","fdat.uni-tuebingen.de","chatgpt.com"]:
 s=socket.create_connection(("transport",3128),timeout=5)
 s.sendall(f"CONNECT {host}:443 HTTP/1.1\\r\\nHost: {host}\\r\\n\\r\\n".encode())
 line=s.recv(500).splitlines()[0].decode();s.close()
 r["network"].append({"host":host,"response":line})
 assert ("200" if host=="chatgpt.com" else "403") in line
for host,port in [("1.1.1.1",443),("192.168.5.2",10808)]:
 try:
  s=socket.create_connection((host,port),timeout=3);s.close();outcome="UNEXPECTED_CONNECTED"
 except OSError as e: outcome=type(e).__name__
 r["network"].append({"direct":f"{host}:{port}","result":outcome})
 assert outcome!="UNEXPECTED_CONNECTED"
r["passed"]=True
print(json.dumps(r,indent=2))
"""
    try:
        run(cmd + ["up", "-d", "--no-build", "--pull", "never"])
        result = run(cmd + ["exec", "-T", "main", "python", "-"], input=probe)
        (BASE / "preflight.json").write_text(result)
    finally:
        run(cmd + ["down", "--remove-orphans"])
    manifest = {
        str(p.relative_to(TASK)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(TASK.rglob("*"))
        if p.is_file()
    }
    (BASE / "task-files.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(
        json.dumps(
            {"images": identities, "preflight": json.loads(result), "file_count": len(manifest)},
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
