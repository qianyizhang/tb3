"""Pinned public TopBrain source acquisition for BR-033; runtime files only."""
from pathlib import Path
import hashlib, json, sys, time, zipfile
import requests

ROOT = Path(__file__).resolve().parents[3]
B = ROOT / 'runs/br033-brain-routing'
sys.path.insert(0, str(ROOT / 'probes/vessel-geometry/authoring'))
from remote_zip import RemoteFile


def inventory():
    record = json.loads((B/'topbrain-new-data.json').read_text())
    file = record['files'][0]
    remote = RemoteFile(file['links']['self'], file['size'])
    tail=B/'data-tail.bin'
    if tail.exists():remote.cache.append((file['size']-tail.stat().st_size,tail.read_bytes()))
    with zipfile.ZipFile(remote) as z:
        rows = [{'name': x.filename, 'bytes': x.file_size, 'compressed_bytes': x.compress_size,
                 'crc32': x.CRC, 'header_offset': x.header_offset} for x in z.infolist()]
        (B/'data-inventory.json').write_text(json.dumps(rows, indent=2)+'\n')
        manifest = []
        for e in z.infolist():
            if e.is_dir() or not (e.filename.endswith(('.txt', '.json', '.md')) or 'labelsTr_' in e.filename):
                continue
            dest = B/'sources'/e.filename
            assert dest.resolve().is_relative_to((B/'sources').resolve())
            dest.parent.mkdir(parents=True, exist_ok=True)
            if not dest.exists(): dest.write_bytes(z.read(e))
            assert dest.stat().st_size==e.file_size
            manifest.append({'member':e.filename, 'bytes':dest.stat().st_size,
                             'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'crc32':e.CRC})
        (B/'data-members.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'inventory':len(rows),'selected':len(manifest),'transferred':remote.transferred}),flush=True)


def images(ids):
    f=json.loads((B/'topbrain-new-data.json').read_text())['files'][0]
    remote=RemoteFile(f['links']['self'],f['size'])
    with zipfile.ZipFile(remote) as z:
        manifest=json.loads((B/'data-members.json').read_text())
        for e in z.infolist():
            if 'imagesTr_' not in e.filename or not any(e.filename.endswith(f'topcow_{c}_0000.nii.gz') for c in ids): continue
            dest=B/'sources'/e.filename;dest.parent.mkdir(parents=True,exist_ok=True)
            if not dest.exists():
                print('Fetching',e.filename,flush=True);dest.write_bytes(z.read(e))
                manifest.append({'member':e.filename,'bytes':dest.stat().st_size,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'crc32':e.CRC})
                (B/'data-members.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Image bytes transferred',remote.transferred,flush=True)


def model():
    record=json.loads((B/'topbrain-models.json').read_text())
    f=next(x for x in record['files'] if x['key']=='Team_UZH_2025_topbrain_segmentation_ct_mr.tar.gz')
    dest=B/f['key'];assert not dest.exists(), 'Never overwrite a downloaded model'
    partial=dest.with_suffix('.part');start=time.monotonic();last=start;md5=hashlib.md5();sha=hashlib.sha256();n=0
    with requests.get(f['links']['self'],stream=True,timeout=120) as r:
        r.raise_for_status()
        with partial.open('wb') as out:
            for block in r.iter_content(8*1024*1024):
                out.write(block);md5.update(block);sha.update(block);n+=len(block)
                if time.monotonic()-last>25:
                    print(json.dumps({'downloaded_mb':round(n/1e6),'total_mb':round(f['size']/1e6),'seconds':round(time.monotonic()-start)}),flush=True);last=time.monotonic()
    assert n==f['size'] and 'md5:'+md5.hexdigest()==f['checksum']
    partial.rename(dest)
    (B/'model-download.json').write_text(json.dumps({'file':f,'sha256':sha.hexdigest(),'verified_md5':md5.hexdigest(),'seconds':time.monotonic()-start},indent=2)+'\n')
    print('Model archive verified',flush=True)


if __name__=='__main__':
    {'inventory':inventory,'images':lambda:images(sys.argv[2:]),'model':model}[sys.argv[1]]()
