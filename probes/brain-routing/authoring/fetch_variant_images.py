"""Acquire two TopCoW originals whose bytes match retained TopBrain ZIP metadata."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import hashlib, json, requests, zlib

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'runs/br033-brain-routing'


def main():
    original = json.loads((ROOT / 'runs/br025-vessel-curation/topcow-container.json').read_text())['entries']
    current = json.loads((BASE / 'data-inventory.json').read_text())
    def fetch(case):
        old = next(x for x in original if x['key'].endswith(f'imagesTr/topcow_mr_{case}_0000.nii.gz'))
        new = next(x for x in current if x['name'].endswith(f'imagesTr_topbrain/topcow_mr_{case}_0000.nii.gz'))
        assert old['size'] == new['bytes'] and old['crc'] == new['crc32']
        dst = BASE / 'sources' / new['name']
        if dst.exists():
            raw = dst.read_bytes()
        else:
            with requests.get(old['links']['content'], stream=True, timeout=(10,40)) as r:
                r.raise_for_status()
                blocks=[]; count=0
                for block in r.iter_content(1024*1024):
                    count += len(block)
                    assert count <= new['bytes']
                    blocks.append(block)
                raw=b''.join(blocks)
            assert len(raw) == new['bytes'] and zlib.crc32(raw) == new['crc32']
            dst.write_bytes(raw)
        assert len(raw) == new['bytes'] and zlib.crc32(raw) == new['crc32']
        return {'case': case, 'url': old['links']['content'], 'member': new['name'],
            'bytes': len(raw), 'crc32': new['crc32'], 'sha256': hashlib.sha256(raw).hexdigest(),
            'matches_topbrain_size_crc': True,
            'selection': 'Reference inventory shows third-A2/third-A3 anatomy; targeted development selection.'}
    with ThreadPoolExecutor(2) as pool:
        records = list(pool.map(fetch, ['006', '011']))
    (BASE / 'variant-image-receipt.json').write_text(json.dumps(records, indent=2) + '\n')
    print(json.dumps(records, indent=2), flush=True)


if __name__ == '__main__':
    main()
