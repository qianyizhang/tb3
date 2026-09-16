"""Fetch selected image ZIP members, validating decompression and archive CRC."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import hashlib,json,struct,sys,zlib
from ranges import read_range
ROOT=Path(__file__).resolve().parents[3];B=ROOT/'runs/br033-brain-routing'

if __name__=='__main__':
    f=json.loads((B/'topbrain-new-data.json').read_text())['files'][0]
    url='https://zenodo.org/records/21972006/files/'+f['key']
    rows=json.loads((B/'data-inventory.json').read_text());manifest=json.loads((B/'data-members.json').read_text())
    for case in sys.argv[1:]:
        e=next(x for x in rows if 'imagesTr_' in x['name'] and x['name'].endswith(f'topcow_{case}_0000.nii.gz'))
        dest=B/'sources'/e['name']
        if dest.exists():continue
        header=read_range(url,e['header_offset'],1024,f['size'],B/'image-range-cache')
        fields=struct.unpack('<4s5H3I2H',header[:30]);assert fields[0]==b'PK\x03\x04'
        offset=e['header_offset']+30+fields[-2]+fields[-1];size=e['compressed_bytes'];chunk=4*1024*1024
        parts=list(range(0,size,chunk))
        with ThreadPoolExecutor(4) as pool:
            fs=[pool.submit(read_range,url,offset+i,min(chunk,size-i),f['size'],B/'image-range-cache') for i in parts]
            compressed=b''.join(fu.result() for fu in fs)
        raw=zlib.decompress(compressed,-15) if fields[3]==8 else compressed
        assert len(raw)==e['bytes'] and zlib.crc32(raw)==e['crc32']
        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
        manifest.append({'member':e['name'],'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'crc32':e['crc32']})
        (B/'data-members.json').write_text(json.dumps(manifest,indent=2)+'\n');print(case,'verified',len(raw),flush=True)
