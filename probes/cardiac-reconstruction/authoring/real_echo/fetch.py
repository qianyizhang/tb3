"""Bounded retrieval from the official release; never execute downloaded code."""
import hashlib, io, json, urllib.request, zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
OUT=ROOT/'runs/br032-real-echo/source'
COMMIT='78f7085104492d5229b1bb96b7748ad9d950e53d'
URL='https://github.com/echonet/3d-echo/releases/download/v1.0/dataset.zip'
SIZE=1109554913

def get(url,headers=None):
    req=urllib.request.Request(url,headers={'User-Agent':'cardiac-research-case-study',**(headers or {})})
    with urllib.request.urlopen(req,timeout=90) as r:
        body=r.read();return body,r.status,dict(r.headers)

class Remote(io.RawIOBase):
    def __init__(self):self.pos=0;self.total=0
    def readable(self):return True
    def seekable(self):return True
    def tell(self):return self.pos
    def seek(self,offset,whence=0):
        self.pos=offset if whence==0 else self.pos+offset if whence==1 else SIZE+offset
        return self.pos
    def read(self,n=-1):
        n=SIZE-self.pos if n<0 else min(n,SIZE-self.pos)
        if n<=0:return b''
        assert self.total+n<160_000_000,'Bounded source retrieval budget'
        b,status,h=get(URL,{'Range':f'bytes={self.pos}-{self.pos+n-1}'})
        assert status==206 and len(b)==n,(status,len(b),n)
        self.pos+=n;self.total+=n;return b

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'source-receipt.json').exists()
    r=Remote()
    with zipfile.ZipFile(r) as z:
        items=[{'name':x.filename,'bytes':x.file_size,'compressed':x.compress_size,'crc32':x.CRC} for x in z.infolist()]
        (OUT/'archive-index.json').write_text(json.dumps(items,indent=2)+'\n')
        choices=sorted(x.filename for x in z.infolist() if x.filename.lower().endswith('.dcm') and '__MACOSX' not in x.filename and not Path(x.filename).name.startswith('._'))
        assert choices
        chosen=choices[0];print('Selected',chosen,flush=True)
        raw=z.read(chosen);(OUT/'selected.dcm').write_bytes(raw)
    files={}
    for name in ['README.md','extractor/utils_3d.py','extractor/math_utils.py','extractor/extractor.py','extractor/view_planes.csv']:
        b,_,_=get(f'https://raw.githubusercontent.com/echonet/3d-echo/{COMMIT}/{name}')
        target=OUT/Path(name).name;target.write_bytes(b)
        files[name]=hashlib.sha256(b).hexdigest()
    result=dict(source_url=URL,release_published='2025-11-19T19:06:16Z',repo_commit=COMMIT,
                selected_member=chosen,selection='lexicographically first non-resource-fork DICOM',
                source_sha256=hashlib.sha256(raw).hexdigest(),source_bytes=len(raw),range_bytes=r.total,
                author_source_files=files,source_description='29 real volumes from four consenting volunteers; no paired GT reconstruction supplied',
                reuse='Public authors release for research; no explicit dataset redistribution license found; local analysis only',
                pretraining_exposure='unknown; public release is not contamination-free evidence')
    (OUT/'source-receipt.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
