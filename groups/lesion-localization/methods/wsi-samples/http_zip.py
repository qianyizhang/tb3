"""Read selected public ZIP members with validated HTTP ranges; never fetch the archive."""

import io

import requests


class HTTPRangeFile(io.RawIOBase):
    def __init__(self, url, size):
        self.url, self.size, self.pos = url, size, 0
        self.session = requests.Session()
        self.bytes_read = 0

    def readable(self):
        return True

    def seekable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, offset, whence=0):
        self.pos = (
            offset if whence == 0 else self.pos + offset if whence == 1 else self.size + offset
        )
        if self.pos < 0:
            raise ValueError("negative seek")
        return self.pos

    def read(self, n=-1):
        if n < 0:
            n = self.size - self.pos
        n = min(n, self.size - self.pos)
        if n <= 0:
            return b""
        if n > 1024 * 1024 * 1024:
            raise ValueError("refuse >1 GB single range")
        end = self.pos + n - 1
        r = self.session.get(
            self.url,
            headers={"Range": f"bytes={self.pos}-{end}", "Accept-Encoding": "identity"},
            timeout=120,
            stream=True,
        )
        r.raise_for_status()
        if (
            r.status_code != 206
            or r.headers.get("Content-Range") != f"bytes {self.pos}-{end}/{self.size}"
        ):
            r.close()
            raise ValueError(f"range not honored: {r.status_code} {r.headers.get('Content-Range')}")
        data = r.content
        if len(data) != n:
            raise ValueError("short range")
        self.pos += n
        self.bytes_read += n
        return data
