"""CONNECT allowlist used only for the isolated model client transport."""

from __future__ import annotations

import json
import select
import socket
import socketserver
import time


ALLOWED = {"chatgpt.com", "api.openai.com", "auth.openai.com"}
UPSTREAM = ("192.168.5.2", 10808)


class Handler(socketserver.StreamRequestHandler):
    def handle(self) -> None:
        line = self.rfile.readline(8193).decode("ascii", "replace").strip()
        bits = line.split()
        while True:
            header = self.rfile.readline(8193)
            if header in (b"\r\n", b"\n", b""):
                break
        target = bits[1] if len(bits) == 3 else ""
        allowed = (
            len(bits) == 3
            and bits[0] == "CONNECT"
            and target.endswith(":443")
            and target[:-4] in ALLOWED
        )
        print(json.dumps({"time": time.time(), "target": target, "allowed": allowed}), flush=True)
        if not allowed:
            self.wfile.write(b"HTTP/1.1 403 Forbidden\r\nContent-Length: 0\r\n\r\n")
            return
        try:
            remote = socket.create_connection(UPSTREAM, timeout=15)
            with remote:
                request = f"CONNECT {target} HTTP/1.1\r\nHost: {target}\r\n\r\n"
                remote.sendall(request.encode())
                response = b""
                while not response.endswith(b"\r\n\r\n") and len(response) < 8192:
                    response += remote.recv(1)
                if not response.startswith((b"HTTP/1.1 200", b"HTTP/1.0 200")):
                    self.wfile.write(b"HTTP/1.1 502 Bad Gateway\r\nContent-Length: 0\r\n\r\n")
                    return
                self.wfile.write(b"HTTP/1.1 200 Connection Established\r\n\r\n")
                self.wfile.flush()
                remote.settimeout(None)
                while True:
                    ready, _, _ = select.select([self.connection, remote], [], [], 300)
                    if not ready:
                        return
                    for source in ready:
                        data = source.recv(65536)
                        if not data:
                            return
                        destination = remote if source is self.connection else self.connection
                        destination.sendall(data)
        except (OSError, ValueError) as exc:
            print(json.dumps({"time": time.time(), "error": type(exc).__name__}), flush=True)


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


if __name__ == "__main__":
    Server(("0.0.0.0", 3128), Handler).serve_forever()
