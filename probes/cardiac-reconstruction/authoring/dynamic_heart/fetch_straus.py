"""Download one public STRAUS US sequence with per-file metadata/hash receipts."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import time
from urllib.request import urlopen

API = 'https://humanheart-project.creatis.insa-lyon.fr/database/api/v1'


def get(url):
    for attempt in range(3):
        try:
            with urlopen(url, timeout=90) as r:
                return r.read()
        except Exception:
            if attempt == 2:
                raise
            time.sleep(1 + attempt)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--mesh-items', type=Path, required=True)
    p.add_argument('--image-items', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=True)
    items = [(i, 'mesh') for i in json.loads(a.mesh_items.read_text())]
    items += [(i, 'image') for i in json.loads(a.image_items.read_text()) if i['name'].endswith(('.mhd', '.raw'))]
    def download(entry):
        item, category = entry
        metadata = json.loads(get(f'{API}/item/{item["_id"]}/files'))
        assert len(metadata) == 1
        f = metadata[0]
        assert f['name'] == item['name'] and f['size'] == item['size']
        out = a.output / category / f['name']
        out.parent.mkdir(exist_ok=True)
        url = f'{API}/file/{f["_id"]}/download'
        if not out.exists():
            content = get(url)
            assert len(content) == f['size'], (f['name'], len(content), f['size'])
            out.write_bytes(content)
        content = out.read_bytes()
        assert len(content) == f['size']
        result = dict(path=str(out.relative_to(a.output)), bytes=len(content),
                      sha256=hashlib.sha256(content).hexdigest(), item_id=item['_id'], file_id=f['_id'], url=url)
        print(result['path'], result['bytes'], flush=True)
        return result
    with ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(download, items))
    (a.output / 'download-manifest.json').write_text(json.dumps(dict(source='STRAUS '+a.output.name,
        metadata_origin=[str(a.mesh_items), str(a.image_items)], files=results), indent=2)+'\n')


if __name__ == '__main__':
    main()
