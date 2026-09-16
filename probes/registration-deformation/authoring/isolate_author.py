"""Run the author method with only public data and no network or private mounts."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'runs/br021-deformable'


def main():
    code=ROOT/'probes/registration-deformation/authoring/baseline_patches.py'
    inventory="import pathlib,json,hashlib; p=pathlib.Path('/app'); print(json.dumps({'files':{str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in p.rglob('*') if f.is_file()},'private_exists':{str(q):q.exists() for q in map(pathlib.Path,['/tests','/solution','/verifier','/author','/baseline.py'])}}))"
    for kind in ['2d','3d']:
        dest=OUT/f'author/isolated/{kind}';assert not dest.exists();dest.mkdir()
        image=f'br021-deform-{kind}-author'
        image_id=subprocess.check_output(['docker','image','inspect',image,'--format','{{.Id}}'],text=True).strip()
        listing=json.loads(subprocess.check_output(['docker','run','--rm','--network','none',image,'python','-c',inventory],text=True))
        assert not any(listing['private_exists'].values())
        command=['docker','run','--rm','--network','none','--cpus','4','--memory','4g',
                 '-v',f'{code}:/baseline.py:ro','-v',f'{dest}:/output',image,
                 'python','/baseline.py','--kind',kind,'--data','/app/data','--out','/output/points.json']
        record={'image':image,'image_id':image_id,'command':command,'initial_image_inventory':listing,
                'code_sha256':hashlib.sha256(code.read_bytes()).hexdigest(),'started_at':datetime.now(timezone.utc).isoformat()}
        with (dest/'solver.log').open('w') as log:
            proc=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=600)
        record.update(returncode=proc.returncode,finished_at=datetime.now(timezone.utc).isoformat())
        (dest/'command.json').write_text(json.dumps(record,indent=2)+'\n');assert proc.returncode==0
        print(json.dumps({'condition':kind,'returncode':proc.returncode,'output':str(dest/'points.json')}),flush=True)


if __name__=='__main__':main()
