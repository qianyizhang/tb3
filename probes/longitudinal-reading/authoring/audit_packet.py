"""Read-only inventory of solver image; no references/solutions mounted."""
from pathlib import Path
import argparse,json,subprocess
ROOT=Path(__file__).resolve().parents[3];B=ROOT/'runs/br037-longitudinal-reading'
p=argparse.ArgumentParser();p.add_argument('name');p.add_argument('image');a=p.parse_args()
f=json.loads((B/f'{a.name}-freeze.json').read_text())
code="""from pathlib import Path
import hashlib,json
b=Path('/app/data')
print(json.dumps({'files':{str(p.relative_to(b)):hashlib.sha256(p.read_bytes()).hexdigest() for p in b.rglob('*') if p.is_file()},'private_paths':{p:Path(p).exists() for p in ['/verifier','/tests','/solution']}}))
"""
r=json.loads(subprocess.check_output(['docker','run','--rm','--network','none','--entrypoint','python',a.image,'-c',code],text=True))
expected={k.removeprefix('environment/data/'):v for k,v in f['files'].items() if k.startswith('environment/data/')}
assert expected==r['files'] and not any(r['private_paths'].values())
r['image']=a.image;r['matches_frozen_packet']=True
(B/f'{a.name}-image-audit.json').write_text(json.dumps(r,indent=2)+'\n')
print(a.name,'isolated packet verified',len(expected),'files')
