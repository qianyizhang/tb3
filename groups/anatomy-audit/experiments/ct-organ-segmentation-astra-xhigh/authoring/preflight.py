"""Run inside the solver image to audit visible files and network boundaries."""

from __future__ import annotations

import importlib.util
import json
import pathlib
import socket


def proxy_probe(host: str) -> str:
    connection = socket.create_connection(("transport", 3128), timeout=5)
    request = f"CONNECT {host}:443 HTTP/1.1\r\nHost: {host}\r\n\r\n"
    connection.sendall(request.encode())
    result = connection.recv(500).splitlines()[0].decode()
    connection.close()
    return result


def main() -> None:
    app_files = sorted(str(path) for path in pathlib.Path("/app").rglob("*") if path.is_file())
    expected = ["/app/data/ct.nii.gz", "/app/data/labels.json"]
    private_paths = [
        "/tests",
        "/solution",
        "/Users",
        "/var/run/docker.sock",
        "/root/.totalsegmentator",
        "/models",
        "/weights",
    ]
    absent = {path: not pathlib.Path(path).exists() for path in private_paths}
    forbidden_modules = {
        name: importlib.util.find_spec(name) is None
        for name in ("totalsegmentator", "nnunet", "nnunetv2")
    }
    network = []
    for host in ("zenodo.org", "huggingface.co", "github.com"):
        result = proxy_probe(host)
        network.append({"probe": host, "result": result})
        assert "403" in result
    for host, port in (("1.1.1.1", 443), ("192.168.5.2", 10808)):
        try:
            connection = socket.create_connection((host, port), timeout=3)
            connection.close()
            result = "UNEXPECTED_CONNECTED"
        except OSError as exc:
            result = type(exc).__name__
        network.append({"probe": f"direct:{host}:{port}", "result": result})
        assert result != "UNEXPECTED_CONNECTED"
    allowed_result = proxy_probe("chatgpt.com")
    network.append({"probe": "chatgpt.com transport", "result": allowed_result})
    assert "200" in allowed_result
    assert app_files == expected
    assert all(absent.values())
    assert all(forbidden_modules.values())
    result = {
        "files": app_files,
        "private_paths_absent": absent,
        "pretrained_segmenter_modules_absent": forbidden_modules,
        "network": network,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
