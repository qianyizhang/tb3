"""Read-only task-image inventory, source references must be absent."""
import argparse,json,subprocess
from pathlib import Path
from run import verify,sha
ROOT=Path(__file__).resolve().parents[4];B=ROOT/'runs/br035-segmentation-mechanics'
p=argparse.ArgumentParser();p.add_argument('condition');p.add_argument('image');a=p.parse_args();f=json.loads((B/'freeze.json').read_text());verify(f)
code="""from pathlib import Path
import json,hashlib
b=Path('/app/data');print(json.dumps(dict(files={str(p.relative_to(b)):hashlib.sha256(p.read_bytes()).hexdigest() for p in b.rglob('*') if p.is_file()},private_paths_present={str(p):p.exists() for p in [Path('/tests'),Path('/verifier'),Path('/solution')]})))
"""
r=json.loads(subprocess.check_output(['docker','run','--rm','--network','none','--entrypoint','python',a.image,'-c',code],text=True));expected={k.removeprefix('environment/data/'):v for k,v in f['conditions'][a.condition]['files'].items() if k.startswith('environment/data/')};assert r['files']==expected and not any(r['private_paths_present'].values());r.update(image=a.image,image_id=subprocess.check_output(['docker','image','inspect','--format','{{.Id}}',a.image],text=True).strip(),public_inventory_matches_freeze=True)
out=B/f'{a.condition}-image-audit.json';assert not out.exists();out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(condition=a.condition,public_inventory_matches_freeze=True)))
