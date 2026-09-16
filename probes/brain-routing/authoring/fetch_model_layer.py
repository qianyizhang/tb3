"""Download and verify the official OCI layer with the model and source code."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import hashlib,json,tarfile,time
from ranges import read_range
ROOT=Path(__file__).resolve().parents[3];B=ROOT/'runs/br033-brain-routing'

if __name__=='__main__':
    f=next(x for x in json.loads((B/'topbrain-models.json').read_text())['files'] if x['key'].endswith('.tar'))
    e=next(x for x in json.loads((B/'ta36-tar-inventory.json').read_text()) if x['name'].endswith('e085598729f2486a82c9a046b24d4dc24394ec28bf0b6b8a61fb4f95d835fc91'))
    url='https://zenodo.org/api/records/21959166/files/'+f['key']+'/content';cache=B/'model-layer-parts';chunk=8*1024*1024
    offsets=list(range(0,e['bytes'],chunk));start=time.monotonic()
    def fetch(i):
        size=min(chunk,e['bytes']-i)
        read_range(url,e['offset']+i,size,f['size'],cache)
        return i
    with ThreadPoolExecutor(4) as pool:
        futures=[pool.submit(fetch,i) for i in offsets]
        for n,fut in enumerate(as_completed(futures),1):
            fut.result()
            if n%4==0:print(json.dumps({'parts':n,'total_parts':len(offsets),'seconds':round(time.monotonic()-start)}),flush=True)
    dest=B/'ta36-model-source-layer.tar.gz';h=hashlib.sha256()
    with dest.open('wb') as out:
        for i in offsets:
            raw=(cache/f'{e["offset"]+i}-{min(chunk,e["bytes"]-i)}.bin').read_bytes();h.update(raw);out.write(raw)
    assert h.hexdigest()==e['name'].split('/')[-1], 'OCI layer digest mismatch'
    outroot=B/'ta36-source';outroot.mkdir(exist_ok=True);manifest=[]
    with tarfile.open(dest,'r:gz') as archive:
        for m in archive:
            if not m.isfile() or not m.name.startswith('app/nnUNet/'):continue
            rel=Path(m.name).relative_to('app/nnUNet');p=outroot/rel
            assert p.resolve().is_relative_to(outroot.resolve())
            p.parent.mkdir(parents=True,exist_ok=True);raw=archive.extractfile(m).read()
            p.write_bytes(raw);manifest.append({'path':str(rel),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
    # Later OCI layers replace the inference entry point; retain that exact final file.
    patch=B/'ta36-metadata/cf88416ff563816017e6ca27d1bc7283745b85a2b3484051ce5a35e527a6e052'
    with tarfile.open(patch) as t:
        m=t.getmember('app/nnUNet/run_inference.py');raw=t.extractfile(m).read();(outroot/'run_inference.py').write_bytes(raw)
        manifest=[x for x in manifest if x['path']!='run_inference.py']+[{'path':'run_inference.py','bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}]
    (B/'ta36-source-manifest.json').write_text(json.dumps({'source_file':f,'layer':e,'layer_sha256_verified':True,'files':manifest},indent=2)+'\n')
    print('Layer digest verified; extracted',len(manifest),'source/model files',flush=True)
