"""Read selected members of a public ZIP using ordinary HTTP range requests."""
import io,json,urllib.request,zipfile,hashlib
from pathlib import Path

class RemoteFile(io.RawIOBase):
    def __init__(self,url,size):
        self.url=url;self.size=size;self.pos=0;self.transferred=0;self.cache=[]
    def seekable(self):return True
    def readable(self):return True
    def tell(self):return self.pos
    def seek(self,n,whence=0):
        self.pos=n if whence==0 else self.pos+n if whence==1 else self.size+n
        return self.pos
    def read(self,n=-1):
        n=self.size-self.pos if n<0 else min(n,self.size-self.pos)
        if n<=0:return b''
        start=self.pos;end=start+n-1
        for offset,data in self.cache:
            if offset<=start and offset+len(data)>end:
                self.pos+=n;return data[start-offset:start-offset+n]
        a=max(0,start-65536);z=min(self.size-1,max(end,start+131071))
        req=urllib.request.Request(self.url,headers={'Range':f'bytes={a}-{z}'})
        with urllib.request.urlopen(req,timeout=120) as r:
            assert r.status==206,(r.status,self.url)
            assert r.headers['Content-Range']==f'bytes {a}-{z}/{self.size}',r.headers['Content-Range']
            b=r.read(z-a+2)
        assert len(b)==z-a+1,(len(b),z-a+1)
        self.cache.append((a,b));self.pos+=n;self.transferred+=len(b);return b[start-a:start-a+n]

def inventory(url,size,dest):
    r=RemoteFile(url,size)
    with zipfile.ZipFile(r) as z:
        out=[{'name':e.filename,'bytes':e.file_size,'compressed_bytes':e.compress_size,
              'crc32':e.CRC,'header_offset':e.header_offset,'compression':e.compress_type} for e in z.infolist()]
    Path(dest).write_text(json.dumps(out,indent=2)+'\n');return out

if __name__=='__main__':
    base=Path('runs/br030-vessel-geometry');record=json.loads((base/'imagecas-x-record.json').read_text())
    for e in record['files']:
        rows=inventory(e['links']['self'],e['size'],base/(e['key']+'.inventory.json'))
        print(e['key'],len(rows),flush=True)
        print([(r['name'],r['bytes']) for r in rows[:16]],flush=True)
