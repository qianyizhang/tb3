"""Read-only initial-image audit for the real case."""
import argparse,json,subprocess,hashlib
from pathlib import Path
from run import verify
ROOT=Path(__file__).resolve().parents[4];B=ROOT/'runs/br034-pathological-echo'
p=argparse.ArgumentParser();p.add_argument('image');a=p.parse_args()
f=json.loads((B/'freeze.json').read_text());verify(f)
code="""from pathlib import Path
import json,hashlib
b=Path('/app/data')
print(json.dumps(dict(files={str(p.relative_to(b)):hashlib.sha256(p.read_bytes()).hexdigest() for p in b.rglob('*') if p.is_file()},private_paths_present={str(p):p.exists() for p in [Path('/tests'),Path('/verifier'),Path('/solution')]})))
"""
r=json.loads(subprocess.check_output(['docker','run','--rm','--network','none','--entrypoint','python',a.image,'-c',code],text=True))
expected={k.removeprefix('environment/data/'):v for k,v in f['files'].items() if k.startswith('environment/data/')}
assert r['files']==expected and not any(r['private_paths_present'].values())
r.update(image=a.image,image_id=subprocess.check_output(['docker','image','inspect','--format','{{.Id}}',a.image],text=True).strip(),public_inventory_matches_freeze=True,
         excluded='Source identifiers, later reference surfaces, reference EF, hidden patient and author code are absent. Full cropped image volume and the initial reference surface are intentionally supplied, along with the old case solver.')
out=B/'image-audit.json';assert not out.exists();out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:r[k] for k in ['image','public_inventory_matches_freeze','private_paths_present']}))
