"""Retry bounded public HTTP range reads and retain exact blocks locally."""
from pathlib import Path
import requests

def read_range(url, start, size, total, cache):
    cache=Path(cache);cache.mkdir(parents=True,exist_ok=True)
    p=cache/f'{start}-{size}.bin'
    if p.exists() and p.stat().st_size==size:return p.read_bytes()
    for attempt in range(4):
        try:
            end=start+size-1
            with requests.get(url,headers={'Range':f'bytes={start}-{end}'},timeout=(10,30),stream=True) as r:
                r.raise_for_status()
                assert r.status_code==206 and r.headers['Content-Range']==f'bytes {start}-{end}/{total}'
                chunks=[];received=0
                for block in r.iter_content(1024*1024):
                    received+=len(block)
                    assert received<=size, 'Oversized range response'
                    chunks.append(block)
                raw=b''.join(chunks)
                assert len(raw)==size
            tmp=p.with_suffix('.part');tmp.write_bytes(raw);tmp.replace(p)
            return raw
        except (requests.RequestException,AssertionError):
            if attempt==3:raise
