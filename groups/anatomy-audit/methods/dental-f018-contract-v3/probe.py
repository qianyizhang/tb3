"""Read-only in-container file and network-boundary probes; no credentials."""

import socket
import json
import pathlib

EXAMPLE_EXPECTED = False

r = {
    "files": sorted(str(p) for p in pathlib.Path("/app").rglob("*") if p.is_file()),
    "missing_private_paths": {
        p: not pathlib.Path(p).exists()
        for p in ["/tests", "/solution", "/Users", "/var/run/docker.sock"]
    },
    "network": [],
}
for host in ["huggingface.co", "ditto.ing.unimore.it"]:
    s = socket.create_connection(("transport", 3128), timeout=5)
    s.sendall(f"CONNECT {host}:443 HTTP/1.1\r\nHost: {host}\r\n\r\n".encode())
    line = s.recv(500).splitlines()[0].decode()
    s.close()
    r["network"].append({"probe": host, "result": line})
    assert "403" in line
for host, port in [("1.1.1.1", 443), ("192.168.5.2", 10808)]:
    try:
        s = socket.create_connection((host, port), timeout=3)
        s.close()
        result = "UNEXPECTED_CONNECTED"
    except OSError as e:
        result = type(e).__name__
    r["network"].append({"probe": f"direct:{host}:{port}", "result": result})
    assert result != "UNEXPECTED_CONNECTED"
s = socket.create_connection(("transport", 3128), timeout=5)
s.sendall(b"CONNECT chatgpt.com:443 HTTP/1.1\r\nHost: chatgpt.com\r\n\r\n")
line = s.recv(500).splitlines()[0].decode()
s.close()
r["network"].append({"probe": "chatgpt.com transport", "result": line})
assert "200" in line
assert all(r["missing_private_paths"].values())
expected = ["/app/data/ct.nii.gz", "/app/data/labels.json"]
if EXAMPLE_EXPECTED:
    expected += ["/app/reference/ct.nii.gz", "/app/reference/segmentation.nii.gz"]
assert r["files"] == expected
print(json.dumps(r, indent=2))
