"""Read-only inventory of the public task image, using an isolated temporary container."""
import argparse
import json
from pathlib import Path
import subprocess
from run_trial import verify,sha

ROOT=Path(__file__).resolve().parents[4];B=ROOT/'runs/br031-cardiac-levels'
p=argparse.ArgumentParser();p.add_argument('stage');p.add_argument('phase');p.add_argument('image');a=p.parse_args()
freeze=json.loads((B/f'cardiac-{a.stage}-freeze.json').read_text());verify(freeze)
code='''from pathlib import Path
import hashlib,json
b=Path('/app/data')
print(json.dumps(dict(files={str(p.relative_to(b)):hashlib.sha256(p.read_bytes()).hexdigest() for p in b.rglob('*') if p.is_file()},private_paths_present={str(p):p.exists() for p in [Path('/verifier'),Path('/solution'),Path('/tests')]})))
'''
proc=subprocess.run(['docker','run','--rm','--network','none','--entrypoint','python',a.image,'-c',code],capture_output=True,text=True,check=True)
r=json.loads(proc.stdout)
expected={k.removeprefix('environment/data/'):v for k,v in freeze['files'].items() if k.startswith('environment/data/')}
assert r['files']==expected and not any(r['private_paths_present'].values()),r
r.update(public_inventory_matches_freeze=True,image=a.image,
         image_id=subprocess.check_output(['docker','image','inspect','--format','{{.Id}}',a.image],text=True).strip(),
         freeze_sha256=sha(B/f'cardiac-{a.stage}-freeze.json'))
out=B/f'{a.stage}-{a.phase}-image-audit.json';assert not out.exists()
out.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({k:r[k] for k in ['public_inventory_matches_freeze','private_paths_present','image','image_id']}))
