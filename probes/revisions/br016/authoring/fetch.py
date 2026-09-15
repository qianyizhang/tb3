"""Fetch a fixed source-order pilot; verify annex MD5 and retain SHA256 receipts."""
import hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=ROOT/'runs/br016-aneurysm/source'
TREE=json.loads((OUT/'tree.json').read_text());REV=TREE['sha']
def get(url,path):
    if not path.exists():
        subprocess.run(['curl','-L','--fail','--retry','2','-sS',url,'-o',str(path)],check=True)
    return path.read_bytes()
receipts=[]
for name in ['README','participants.tsv','participants.json','dataset_description.json']:
    get(f'https://raw.githubusercontent.com/OpenNeuroDatasets/ds003949/{REV}/{name}',OUT/name)
for subject in ['sub-000','sub-013','sub-022','sub-062']:
    paths=[x['path'] for x in TREE['tree'] if x['path'].startswith('derivatives/manual_masks/'+subject+'/') and x['path'].endswith('.nii.gz')]
    # First session only. No repeated patient scans.
    session=min(p.split('/')[3] for p in paths)
    for path in paths:
        if '/'+session+'/' not in path:continue
        dest=OUT/Path(path).name
        pointer=get(f'https://raw.githubusercontent.com/OpenNeuroDatasets/ds003949/{REV}/{path}',OUT/(dest.name+'.annex')).decode()
        m=re.search(r'MD5E-s(\d+)--([0-9a-f]+)',pointer);assert m
        data=get('https://s3.amazonaws.com/openneuro.org/ds003949/'+path,dest)
        assert len(data)==int(m[1]) and hashlib.md5(data).hexdigest()==m[2]
        receipt={'path':path,'file':dest.name,'bytes':len(data),'md5':m[2],'sha256':hashlib.sha256(data).hexdigest()}
        receipts.append(receipt);print(json.dumps(receipt),flush=True)
(OUT/'receipt.json').write_text(json.dumps({'dataset':'ds003949','git_tree':REV,'selection':'first two positive subjects, first control, first multi-lesion subject; first session each','files':receipts},indent=2)+'\n')
