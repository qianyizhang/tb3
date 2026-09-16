"""Read selected public EchoXFlow TAR members; retain an exact archive index."""
import argparse, hashlib, io, json, tarfile, urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
B=ROOT/'runs/br034-pathological-echo/source'
class Remote(io.RawIOBase):
    def __init__(self,url,size):
        self.url=url;self.size=size;self.pos=0;self.cache={};self.fetched=0
    def seekable(self):return True
    def readable(self):return True
    def tell(self):return self.pos
    def seek(self,offset,whence=0):
        self.pos=offset if whence==0 else self.pos+offset if whence==1 else self.size+offset
        return self.pos
    def read(self,n=-1):
        n=min(self.size-self.pos,n if n>=0 else self.size);out=[]
        while n>0:
            block=self.pos//(1<<20);start=block*(1<<20)
            if block not in self.cache:
                end=min(start+(1<<20),self.size)-1
                req=urllib.request.Request(self.url,headers={'Range':f'bytes={start}-{end}'})
                with urllib.request.urlopen(req,timeout=90) as r:
                    assert r.status==206;data=r.read();assert len(data)==end-start+1
                self.cache[block]=data;self.fetched+=len(data)
            data=self.cache[block];offset=self.pos-start;k=min(n,len(data)-offset)
            assert k>0;out.append(data[offset:offset+k]);self.pos+=k;n-=k
        return b''.join(out)

def main():
    p=argparse.ArgumentParser();p.add_argument('exam');p.add_argument('--recording');a=p.parse_args()
    entry=next(x for x in json.loads((B/'exam-tree.json').read_text()) if x['path']==f'exams/{a.exam}.tar')
    url='https://huggingface.co/datasets/Ahus-AIM/EchoXFlow/resolve/main/'+entry['path']
    remote=Remote(url,entry['size']);out=B/a.exam;out.mkdir(exist_ok=True)
    members=[];saved=[]
    with tarfile.open(fileobj=remote,mode='r:') as tar:
        for m in tar:
            if not m.isfile():continue
            parts=Path(m.name).parts;assert '..' not in parts and not Path(m.name).is_absolute()
            members.append(dict(name=m.name,offset=m.offset_data,size=m.size))
            # Metadata and mesh annotations suffice for pre-trial curation.
            keep=(a.recording and a.recording+'.zarr' in parts) or (not a.recording and (m.name.endswith(('.zattrs','.zarray','.zgroup','.zmetadata')) or '3d_left_ventricle_mesh' in m.name))
            if keep:
                dest=out/m.name;dest.parent.mkdir(parents=True,exist_ok=True)
                if not dest.exists():dest.write_bytes(tar.extractfile(m).read())
                saved.append(dict(name=m.name,size=m.size,sha256=hashlib.sha256(dest.read_bytes()).hexdigest()))
    suffix=a.recording or 'metadata'
    (out/f'{suffix}-receipt.json').write_text(json.dumps(dict(url=url,archive_metadata=entry,downloaded_bytes=remote.fetched,saved=saved),indent=2)+'\n')
    (out/'index.json').write_text(json.dumps(members,indent=2)+'\n')
    print(json.dumps(dict(exam=a.exam,recording=a.recording,members=len(members),saved=len(saved),fetched=remote.fetched)),flush=True)
if __name__=='__main__':main()
