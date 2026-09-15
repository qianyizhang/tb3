"""Read selected public VerSe ZIP members with bounded, validated HTTP ranges.

Raw bytes and source receipts stay in the supplied local output directory.
No CT volume is fetched unless explicitly selected with --member.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import urllib.request
import zipfile


class RemoteZip(io.RawIOBase):
    def __init__(self, url, cache):
        self.url, self.cache, self.pos = url, cache, 0
        self.cache.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(urllib.request.Request(url, method='HEAD'), timeout=30) as r:
            self.size = int(r.headers['Content-Length'])
            self.etag = r.headers.get('ETag')
        self.transferred = 0

    def seekable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, offset, whence=0):
        self.pos = offset + (0 if whence == 0 else self.pos if whence == 1 else self.size)
        return self.pos

    def read(self, n=-1):
        end = min(self.size, self.pos + n if n >= 0 else self.size)
        n = end - self.pos
        if n <= 0:
            return b''
        if n > 32 * 1024 * 1024:
            raise ValueError('Refusing a read larger than 32 MiB')
        key = f'{self.pos}-{end - 1}.bin'
        path = self.cache / key
        if not path.exists():
            req = urllib.request.Request(self.url, headers={'Range': f'bytes={self.pos}-{end-1}', 'If-Match': self.etag})
            with urllib.request.urlopen(req, timeout=45) as r:
                if r.status != 206 or r.headers.get('Content-Range') != f'bytes {self.pos}-{end-1}/{self.size}':
                    raise ValueError('Server did not honor exact range')
                data = r.read(n+1)
            if len(data) != n:
                raise ValueError('Truncated or excessive range response')
            path.write_bytes(data)
            self.transferred += n
        data = path.read_bytes()
        if len(data) != n:
            raise ValueError('Invalid cached range')
        self.pos = end
        return data


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--split', required=True, choices=['19training','19validation','19test','20training','20validation','20test'])
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--member', action='append', default=[])
    a = p.parse_args()
    url = f'https://s3.bonescreen.de/public/VerSe-complete/dataset-verse{a.split}.zip'
    a.output.mkdir(parents=True, exist_ok=True)
    remote = RemoteZip(url, a.output / '_ranges' / a.split)
    with zipfile.ZipFile(remote) as z:
        rows = [{'name': x.filename, 'bytes': x.file_size, 'compressed_bytes': x.compress_size, 'crc32': f'{x.CRC:08x}'} for x in z.infolist()]
        index = {'url': url, 'archive_bytes': remote.size, 'etag': remote.etag, 'license': 'CC-BY-SA-4.0', 'members': rows}
        (a.output / f'{a.split}-index.json').write_text(json.dumps(index, indent=2)+'\n')
        for name in a.member:
            target = (a.output / 'files' / a.split / name).resolve()
            if not target.is_relative_to((a.output / 'files' / a.split).resolve()):
                raise ValueError('Invalid member path')
            data = z.read(name)  # ZipFile checks CRC.
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            receipt = {**{k:v for k,v in index.items() if k != 'members'}, 'member': name, 'bytes':len(data), 'sha256':hashlib.sha256(data).hexdigest(), 'zip_crc_verified':True}
            target.with_name(target.name+'.receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
            print(json.dumps(receipt), flush=True)
    print(json.dumps({'split':a.split, 'members':len(rows), 'network_bytes':remote.transferred}), flush=True)


if __name__ == '__main__':
    main()
