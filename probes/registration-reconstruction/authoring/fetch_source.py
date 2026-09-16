"""Retrieve the selected public NLST pair; no credentials or private API.

Chosen before any target construction or registration result: first subject
returned by the public catalogue, first complete B30f/B50f study pair.
"""
import concurrent.futures
import hashlib
import json
from pathlib import Path
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'runs/br020-registration/source'
SERIES = {
    'B30f': '1.2.840.113654.2.55.239171605522909239517180961798868660180',
    'B50f': '1.2.840.113654.2.55.85646041831478784820085978073099583442',
}


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def fetch(item):
    kernel, uid = item
    path = OUT / f'{kernel}.zip'
    url = 'https://nlst.cancerimagingarchive.net/nbia-api/services/v1/getImage?SeriesInstanceUID=' + uid
    if not path.exists():
        temporary = path.with_suffix('.partial')
        with urllib.request.urlopen(url, timeout=120) as response, temporary.open('wb') as stream:
            count = 0
            while block := response.read(1024 * 1024):
                count += len(block)
                assert count < 250_000_000, 'Unexpectedly large series'
                stream.write(block)
        temporary.rename(path)
    members = []
    with zipfile.ZipFile(path) as archive:
        for member in archive.infolist():
            assert not Path(member.filename).is_absolute() and '..' not in Path(member.filename).parts
            destination = OUT / kernel / member.filename
            if member.is_dir():
                destination.mkdir(parents=True, exist_ok=True)
            else:
                destination.parent.mkdir(parents=True, exist_ok=True)
                data = archive.read(member)
                if destination.exists():
                    assert destination.read_bytes() == data
                else:
                    destination.write_bytes(data)
                members.append({'path': str(destination.relative_to(OUT)), 'sha256': sha(destination)})
    return {'kernel': kernel, 'series_uid': uid, 'url': url,
            'zip_sha256': sha(path), 'bytes': path.stat().st_size, 'files': members}


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(2) as pool:
        rows = list(pool.map(fetch, SERIES.items()))
    record = {'collection': 'NLST', 'patient_id': '120547',
              'license': 'CC BY 4.0', 'collection_url': 'https://www.cancerimagingarchive.net/collection/nlst/',
              'selection': 'first returned subject, first complete paired study; before target or solve',
              'series': rows}
    (OUT / 'source-receipt.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps([{k: row[k] for k in ['kernel', 'bytes', 'zip_sha256']} for row in rows]))
