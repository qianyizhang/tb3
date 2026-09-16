"""Selected ImageCAS-X references plus the first original ImageCAS scan."""
import hashlib,json,struct,urllib.request,zlib,zipfile
from pathlib import Path
from remote_zip import RemoteFile

BASE=Path('runs/br030-vessel-geometry');OUT=BASE/'sources/coronary'
def record():
    path=BASE/'imagecas-x-record.json'
    if not path.exists():
        path.parent.mkdir(parents=True,exist_ok=True)
        with urllib.request.urlopen('https://zenodo.org/api/records/21887809',timeout=60) as response:path.write_bytes(response.read())
    return json.loads(path.read_text())

def refs():
    entry=next(e for e in record()['files'] if e['key']=='ImageCAS-X_dataset.zip')
    r=RemoteFile(entry['links']['self'],entry['size']);receipt=[]
    with zipfile.ZipFile(r) as z:
        selected=[n for n in z.namelist() if '/1.' in n or '/filelist/' in n or n.endswith('Descriptors.xlsx')]
        for name in selected:
            if name.endswith('/'):continue
            p=OUT/name;p.parent.mkdir(parents=True,exist_ok=True)
            if not p.exists():p.write_bytes(z.read(name))
            b=p.read_bytes();info=z.getinfo(name);assert zlib.crc32(b)==info.CRC and len(b)==info.file_size
            receipt.append({'source_url':entry['links']['self'],'member':name,'path':str(p),'bytes':len(b),
                'sha256':hashlib.sha256(b).hexdigest(),'zip_crc32_verified':True})
            print(name,len(b),flush=True)
            (BASE/'coronary-reference-manifest.json').write_text(json.dumps(receipt,indent=2)+'\n')

def weights():
    entry=next(e for e in record()['files'] if e['key']=='pretrained_weights.zip')
    member='pretrained_weights/cas_net.pt';p=OUT/'cas_net.pt'
    expected='f3e280b74e2f3c32ac122996100694fb7d1357f3aa2e582e5e6bb7461f90d6c1'
    if p.exists():
        assert hashlib.sha256(p.read_bytes()).hexdigest()==expected
        print('Pinned CAS-Net checkpoint already present');return
    with zipfile.ZipFile(RemoteFile(entry['links']['self'],entry['size'])) as z:
        raw=z.read(member);info=z.getinfo(member)
        assert len(raw)==info.file_size and zlib.crc32(raw)==info.CRC
    assert hashlib.sha256(raw).hexdigest()==expected
    p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
    receipt={'source_url':entry['links']['self'],'member':member,'path':str(p),'bytes':len(raw),'sha256':expected,'zip_crc32_verified':True}
    (BASE/'coronary-weight-manifest.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(member,len(raw))

def original():
    # Kaggle wraps an individual dataset file in a ZIP. The first spanned
    # ImageCAS volume starts with complete per-scan NIfTI ZIP members.
    # Read only a bounded prefix, then verify each extracted inner ZIP CRC.
    url='https://www.kaggle.com/api/v1/datasets/download/xiaoweixumedicalai/imagecas/1-200.z01'
    req=urllib.request.Request(url,headers={'Range':'bytes=0-157286399'})
    dest=OUT/'original';dest.mkdir(parents=True,exist_ok=True)
    assert not (dest/'scan-manifest.json').exists(),'Do not overwrite retained acquisition'
    with urllib.request.urlopen(req,timeout=120) as response:
        assert response.status==206
        head=response.read(30);s=struct.unpack('<4s5H3L2H',head);assert s[0]==b'PK\x03\x04'
        name=response.read(s[-2]);extra=response.read(s[-1]);print('Outer ZIP',name,s[3],flush=True)
        assert s[3] in (0,8)
        dec=zlib.decompressobj(-15) if s[3]==8 else None
        inner=bytearray();received=30+len(name)+len(extra);pos=0;records=[]
        while received<157286400:
            b=response.read(2*1024*1024)
            if not b:break
            received+=len(b);inner.extend(dec.decompress(b) if dec else b)
            if pos==0 and inner[:4]==b'PK\x07\x08':pos=4
            while len(inner)>=pos+30:
                h=struct.unpack('<4s5H3L2H',inner[pos:pos+30])
                assert h[0]==b'PK\x03\x04',(pos,bytes(inner[pos:pos+4]))
                sig,ver,flags,method,mtime,mdate,crc,cs,us,fn,ex=h
                assert not flags&8,'Unexpected descriptor-based inner ZIP member'
                end=pos+30+fn+ex+cs
                if len(inner)<end:break
                n=bytes(inner[pos+30:pos+30+fn]).decode('utf8');packed=bytes(inner[pos+30+fn+ex:end])
                raw=zlib.decompress(packed,-15) if method==8 else packed
                assert len(raw)==us and zlib.crc32(raw)==crc,(n,us,len(raw))
                print('Inner member',n,len(raw),flush=True)
                if not n.endswith('/'):
                    p=dest/Path(n).name;p.write_bytes(raw)
                    records.append({'source_url':url,'outer_member':name.decode(),'inner_member':n,'path':str(p),
                        'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'inner_zip_crc32_verified':True})
                pos=end
                if any(x['inner_member'].endswith('1.img.nii.gz') for x in records) and any(x['inner_member'].endswith('1.label.nii.gz') for x in records):
                    (dest/'scan-manifest.json').write_text(json.dumps({'downloaded_prefix_bytes':received,'files':records},indent=2)+'\n');return
        raise RuntimeError('First matched scan was not completely present in the bounded prefix')

if __name__=='__main__':
    import sys
    {'refs':refs,'original':original,'weights':weights}[sys.argv[1]]()
