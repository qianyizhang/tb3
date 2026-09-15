"""Fetch exactly one corresponding native venous CT, with bounded HTTP ranges."""
import json
import zipfile
from pathlib import Path
from common import ROOT,OUT,write,sha
from fetch_vessels import OptionalETagZip

def main():
    out=OUT/'source/colonvessels';index=json.loads((out/'index.json').read_text())
    name='data/pat_016/pat_016_Venous_Phase_CT.nrrd';entry=next(r for r in index['members'] if r['name']==name)
    dest=out/Path(name).name;assert not dest.exists(),'Do not silently overwrite a source'
    remote=OptionalETagZip(index['url'],out/'ranges')
    with zipfile.ZipFile(remote) as z,z.open(name) as f,dest.with_suffix('.partial').open('wb') as target:
        count=0
        while b:=f.read(8*1024*1024):
            target.write(b);count+=len(b)
            if count%(32*1024*1024)==0:print(f'{count}/{entry["bytes"]} source bytes',flush=True)
    assert count==entry['bytes'];dest.with_suffix('.partial').rename(dest)
    receipt={**entry,'url':index['url'],'sha256':sha(dest),'zip_crc_verified':True,'network_bytes':remote.transferred}
    write(out/'ct-receipt.json',receipt);print(json.dumps(receipt),flush=True)

if __name__=='__main__':main()
