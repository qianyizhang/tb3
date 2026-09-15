"""Add unstripped original angiograms without changing the initial source receipt."""
import hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];O=ROOT/'runs/br016-aneurysm/source';tree=json.loads((O/'tree.json').read_text());rev=tree['sha'];rows=[]
for sub in ['sub-000','sub-013','sub-022','sub-062']:
 paths=sorted(x['path'] for x in tree['tree'] if x['path'].startswith(sub+'/') and x['path'].endswith('_angio.nii.gz'))
 p=paths[0];dst=O/Path(p).name;ptr=O/(dst.name+'.annex')
 for url,target in [(f'https://raw.githubusercontent.com/OpenNeuroDatasets/ds003949/{rev}/{p}',ptr),('https://s3.amazonaws.com/openneuro.org/ds003949/'+p,dst)]:
  if not target.exists():subprocess.run(['curl','-L','--fail','--retry','2','-sS',url,'-o',str(target)],check=True)
 m=re.search(r'MD5E-s(\d+)--([0-9a-f]+)',ptr.read_text());data=dst.read_bytes();assert len(data)==int(m[1]) and hashlib.md5(data).hexdigest()==m[2]
 rows.append({'path':p,'file':dst.name,'bytes':len(data),'md5':m[2],'sha256':hashlib.sha256(data).hexdigest()});print(json.dumps(rows[-1]),flush=True)
(O/'raw-receipt.json').write_text(json.dumps(rows,indent=2)+'\n')
