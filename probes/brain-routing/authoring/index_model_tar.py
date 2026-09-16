"""Index the official uncompressed TA36 OCI export using HTTP range reads."""
from pathlib import Path
import hashlib,json,sys,tarfile
ROOT=Path(__file__).resolve().parents[3];B=ROOT/'runs/br033-brain-routing'
sys.path.insert(0,str(ROOT/'probes/vessel-geometry/authoring'))
from ranges import read_range

if __name__=='__main__':
    f=next(x for x in json.loads((B/'topbrain-models.json').read_text())['files'] if x['key'].endswith('.tar'))
    url='https://zenodo.org/records/21959166/files/'+f['key']
    inventory=B/'ta36-tar-inventory.json'
    rows=json.loads(inventory.read_text()) if inventory.exists() else []
    pos=((rows[-1]['offset']+rows[-1]['bytes']+511)//512)*512 if rows else 0
    out=B/'ta36-metadata';out.mkdir(exist_ok=True)
    while pos<f['size']-512:
        block=read_range(url,pos,min(65536,f['size']-pos),f['size'],B/'tar-range-cache')
        cursor=0
        while cursor+512<=len(block):
            header=block[cursor:cursor+512]
            if not any(header):print('Index complete',flush=True);sys.exit(0)
            e=tarfile.TarInfo.frombuf(header,'utf-8','strict')
            row={'name':e.name,'bytes':e.size,'offset':pos+cursor+512};rows.append(row)
            if e.isfile() and e.size<100000:
                raw=(block[cursor+512:cursor+512+e.size] if cursor+512+e.size<=len(block)
                     else read_range(url,row['offset'],e.size,f['size'],B/'tar-range-cache'))
                (out/Path(e.name).name).write_bytes(raw);row['sha256']=hashlib.sha256(raw).hexdigest()
            print(row,flush=True);inventory.write_text(json.dumps(rows,indent=2)+'\n')
            cursor+=512+((e.size+511)//512)*512
        pos+=cursor
