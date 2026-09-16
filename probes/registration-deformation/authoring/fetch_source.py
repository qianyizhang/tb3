"""Fetch only the three manually annotated LungCT validation pairs."""
import hashlib
import json
from pathlib import Path
import re
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'runs/br021-deformable/source'
sys.path.insert(0,str(ROOT/'probes/dicom-anatomy-audit/authoring'))
import fetch_sources as remote_zip


def main():
    index=json.loads((OUT/'lungct-members.json').read_text())
    remote_zip.URL=index['url'];remote_zip.SIZE=index['size']
    remote=remote_zip.RemoteZip(OUT/'lungct-range-cache')
    records=[]
    with zipfile.ZipFile(remote) as archive:
        for name in archive.namelist():
            if name.endswith('/'):continue
            pair=re.search(r'LungCT_000[123]_000[01]\.(nii\.gz|csv)$',name)
            selected=pair and any('/'+part+'/' in name for part in ['imagesTr','landmarksTr','masksTr'])
            selected=selected or name.lower().endswith(('.json','.txt','.md'))
            if not selected:continue
            path=OUT/name;path.parent.mkdir(parents=True,exist_ok=True)
            if not path.exists():path.write_bytes(archive.read(name))
            records.append({'member':name,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
            print(name,path.stat().st_size,flush=True)
    receipt={'url':index['url'],'archive_bytes':index['size'],
             'source_page':'https://learn2reg.grand-challenge.org/Datasets/',
             'original_doi':'10.5281/zenodo.3835682','original_license':'CC BY 4.0',
             'selection':'All three manual-landmark validation cases, before task selection or baseline solving.',
             'files':records}
    (OUT/'source-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print('network_bytes',remote.transferred)


if __name__=='__main__':main()
