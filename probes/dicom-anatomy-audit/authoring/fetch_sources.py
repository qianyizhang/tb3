"""Fetch only selected members of the licensed TotalSegmentator small v2.0.1 ZIP.
Source inputs remain local. Byte ranges, ZIP CRCs, and SHA-256 receipts are retained.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import time
import urllib.request
import zipfile

URL = 'https://zenodo.org/records/10047263/files/Totalsegmentator_dataset_small_v201.zip'
SIZE = 3244617817
BLOCK = 4 * 1024 * 1024

class RemoteZip(io.RawIOBase):
    def __init__(self, cache):
        self.pos = 0
        self.cache = cache
        self.transferred = 0
        cache.mkdir(parents=True, exist_ok=True)
    def seekable(self): return True
    def tell(self): return self.pos
    def seek(self, offset, whence=0):
        self.pos = offset if whence == 0 else self.pos + offset if whence == 1 else SIZE + offset
        return self.pos
    def read(self, n=-1):
        end = min(SIZE, self.pos + n if n >= 0 else SIZE)
        chunks = []
        while self.pos < end:
            block = self.pos // BLOCK
            a, b = block * BLOCK, min(SIZE, (block + 1) * BLOCK)
            path = self.cache / f'{block}.bin'
            if not path.exists():
                for attempt in range(3):
                    try:
                        req = urllib.request.Request(URL, headers={'Range': f'bytes={a}-{b-1}'})
                        with urllib.request.urlopen(req, timeout=45) as response:
                            if response.status != 206: raise ValueError('byte range not honored')
                            data = response.read(BLOCK + 1)
                        if len(data) != b-a: raise ValueError('wrong range length')
                        path.write_bytes(data)
                        self.transferred += len(data)
                        break
                    except Exception:
                        if attempt == 2: raise
                        time.sleep(2)
            data = path.read_bytes()
            if len(data) != b-a: raise ValueError('invalid cached block')
            stop = min(end, b)
            chunks.append(data[self.pos-a:stop-a])
            self.pos = stop
        return b''.join(chunks)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('subjects', nargs='+')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    remote = RemoteZip(args.output / '_range_cache')
    with zipfile.ZipFile(remote) as archive:
        for subject in args.subjects:
            assert subject.startswith('s') and subject[1:].isdigit()
            selected = [n for n in archive.namelist() if n.startswith(subject + '/') and not n.endswith('/')]
            assert selected, subject
            receipt = []
            for name in selected:
                path = args.output / name
                path.parent.mkdir(parents=True, exist_ok=True)
                if not path.exists(): path.write_bytes(archive.read(name))
                data = path.read_bytes()
                receipt.append({'member': name, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
            (args.output / subject / 'source-receipt.json').write_text(json.dumps({
                'url': URL, 'record': '10047263', 'version': '2.0.1', 'license': 'CC-BY-4.0',
                'files': receipt,
            }, indent=2) + '\n')
            print(subject, 'files', len(receipt), 'network_bytes', remote.transferred, flush=True)

if __name__ == '__main__': main()
