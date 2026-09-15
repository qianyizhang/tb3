"""Inspect ZIP inventory and two bounded NRRD headers; no full cohort download."""
import json
import sys
import zipfile
import urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'probes/revisions/br012/authoring'))
from fetch_verse import RemoteZip

class OptionalETagZip(RemoteZip):
    def read(self,n=-1):
        end=min(self.size,self.pos+n if n>=0 else self.size);n=end-self.pos
        if n<=0:return b''
        if n>32*1024*1024:raise ValueError('Range exceeds 32 MiB')
        path=self.cache/f'{self.pos}-{end-1}.bin'
        if not path.exists():
            headers={'Range':f'bytes={self.pos}-{end-1}'}
            if self.etag:headers['If-Match']=self.etag
            with urllib.request.urlopen(urllib.request.Request(self.url,headers=headers),timeout=45) as r:
                assert r.status==206 and r.headers.get('Content-Range')==f'bytes {self.pos}-{end-1}/{self.size}'
                data=r.read(n+1)
            assert len(data)==n;path.write_bytes(data);self.transferred+=n
        data=path.read_bytes();assert len(data)==n;self.pos=end;return data

def main():
    out=ROOT/'runs/br015-clinical/source/colonvessels';out.mkdir(parents=True,exist_ok=True)
    url='https://zenodo.org/records/17407158/files/data.zip?download=1'
    remote=OptionalETagZip(url,out/'ranges')
    with zipfile.ZipFile(remote) as z:
        rows=[{'name':i.filename,'bytes':i.file_size,'compressed_bytes':i.compress_size,'crc32':f'{i.CRC:08x}'} for i in z.infolist()]
        (out/'index.json').write_text(json.dumps({'url':url,'size':remote.size,'etag':remote.etag,'members':rows},indent=2)+'\n')
        selected=[i for i in z.infolist() if i.filename.endswith('.seg.nrrd')][:2]
        headers=[]
        for i in selected:
            with z.open(i) as f:b=f.read(65536)
            marker=b.find(b'\n\n');assert marker>=0,'Header exceeds bounded read'
            h=b[:marker].decode('ascii');headers.append({'member':i.filename,'header':h,'partial_member_only':True,'full_member_crc_verified':False})
        record={'url':url,'archive_bytes':remote.size,'etag':remote.etag,'members':len(rows),'headers':headers,'network_bytes':remote.transferred}
        (out/'header-review.json').write_text(json.dumps(record,indent=2)+'\n')
        print(json.dumps(record,indent=2))

if __name__=='__main__':main()
