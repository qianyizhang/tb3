"""Download pinned public source members, with size/CRC and local hashes."""
from concurrent.futures import ThreadPoolExecutor
import hashlib,json,urllib.request,zlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'runs/br030-vessel-geometry'

def fetch(e):
    p=BASE/'sources'/e['key'];p.parent.mkdir(parents=True,exist_ok=True)
    if not p.exists():
        with urllib.request.urlopen(e['links']['content'],timeout=120) as response:
            with p.with_suffix(p.suffix+'.partial').open('wb') as f:
                while chunk:=response.read(4*1024*1024):f.write(chunk)
        p.with_suffix(p.suffix+'.partial').rename(p)
    raw=p.read_bytes();assert len(raw)==e['size'] and zlib.crc32(raw)==e['crc'],e['key']
    r={'path':str(p.relative_to(ROOT)),'url':e['links']['content'],'bytes':len(raw),
       'sha256':hashlib.sha256(raw).hexdigest(),'zip_crc32_verified':True}
    print(p.name,len(raw),flush=True);return r

def main():
    claim=json.loads((BASE/'claim-container.json').read_text())['entries']
    cow=json.loads((ROOT/'runs/br025-vessel-curation/topcow-container.json').read_text())['entries']
    graphs=json.loads((ROOT/'runs/br025-vessel-curation/centerlines-container.json').read_text())['entries']
    selection=[e for e in claim if e['key'].endswith(('plans.json','dataset.json','dataset_fingerprint.json','fold_0/checkpoint_final.pth'))]
    selection += [e for e in cow if 'topcow_ct_012' in e['key']]
    selection += [e for e in graphs if 'topcow_ct_012' in e['key'] and '/cow_nodes/' in e['key']]
    print('Selected',len(selection),'files',sum(e['size'] for e in selection),'bytes',flush=True)
    receipt=[]
    with ThreadPoolExecutor(max_workers=3) as pool:
        for r in pool.map(fetch,selection):
            receipt.append(r);(BASE/'source-manifest.json').write_text(json.dumps(receipt,indent=2)+'\n')

if __name__=='__main__':main()
