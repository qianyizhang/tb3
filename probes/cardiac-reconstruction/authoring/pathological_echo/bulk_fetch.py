"""Bounded three-exam curation download with verified public LFS digests."""
import argparse,concurrent.futures,hashlib,json,os,tarfile,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];B=ROOT/'runs/br034-pathological-echo/source'
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--screen',default='bounded-screen.json');args=parser.parse_args()
    catalog=json.loads((B/'exam-tree.json').read_text());screen=json.loads((B/args.screen).read_text())
    for _,exam,_,_ in screen['candidates']:
        e=next(x for x in catalog if x['path']==f'exams/{exam}.tar');dest=B/f'{exam}.tar';size=e['size']
        if not dest.exists():
            url='https://huggingface.co/datasets/Ahus-AIM/EchoXFlow/resolve/main/'+e['path']
            fd=os.open(dest,os.O_CREAT|os.O_RDWR,0o600);os.ftruncate(fd,size)
            def part(start):
                end=min(start+8*1024**2,size)-1
                req=urllib.request.Request(url,headers={'Range':f'bytes={start}-{end}'})
                with urllib.request.urlopen(req,timeout=120) as r:
                    assert r.status==206;d=r.read();assert len(d)==end-start+1
                os.pwrite(fd,d,start);return len(d)
            with concurrent.futures.ThreadPoolExecutor(8) as pool:done=sum(pool.map(part,range(0,size,8*1024**2)))
            os.close(fd);assert done==size
        h=hashlib.sha256(dest.read_bytes()).hexdigest();assert h==e['lfs']['oid']
        out=B/exam;out.mkdir(exist_ok=True);members=[]
        with tarfile.open(dest) as tar:
            for m in tar:
                if not m.isfile():continue
                assert not Path(m.name).is_absolute() and '..' not in Path(m.name).parts
                members.append(dict(name=m.name,offset=m.offset_data,size=m.size))
                if m.name.endswith(('.zattrs','.zarray','.zgroup','.zmetadata')) or '3d_left_ventricle_mesh' in m.name:
                    p=out/m.name;p.parent.mkdir(exist_ok=True,parents=True);p.write_bytes(tar.extractfile(m).read())
        (out/'index.json').write_text(json.dumps(members,indent=2)+'\n')
        (out/'archive-receipt.json').write_text(json.dumps(dict(source=e,sha256=h,bytes=size),indent=2)+'\n')
        print(json.dumps(dict(exam=exam,bytes=size,sha256=h,members=len(members))),flush=True)
if __name__=='__main__':main()
