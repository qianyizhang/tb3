"""Audit a new public-only task image, replay its author solver, then freeze."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from score import score

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'runs/br024-harder-registration'
HERE=Path(__file__).resolve().parent


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())


def main():
    ap=argparse.ArgumentParser();ap.add_argument('case',type=int);args=ap.parse_args();case=args.case
    prep=read(OUT/f'prepared/patient{case}.json');task=ROOT/prep['task_path'];method=prep['baseline_method']
    folder=OUT/f'author/patient{case}';folder.mkdir(parents=True,exist_ok=False)
    tag=f'tb3-br024-patient{case}-author:20260916'
    image=subprocess.check_output(['docker','image','inspect','--format','{{.Id}}',tag],text=True).strip()
    audit_code='''import hashlib,json
from pathlib import Path
import numpy as np
paths=[p for p in Path('/app').rglob('*') if p.is_file()]
print(json.dumps({'files':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},'initial_answers':[p.name for p in Path('/app/answer').iterdir()],'private_paths':{p:Path(p).exists() for p in ['/tests','/solution','/app/truth.json','/app/baseline.py','/app/data/reference_volume.npz']},'numpy_version':np.__version__}))
'''
    audit=json.loads(subprocess.check_output(['docker','run','--rm','--network','none',image,'python','-c',audit_code],text=True))
    expected={'/app/SOURCE_NOTICE.md':sha(task/'environment/SOURCE_NOTICE.md')}
    expected.update({f'/app/data/{p.name}':sha(p) for p in (task/'environment/data').iterdir()})
    assert audit['files']==expected and not audit['initial_answers'] and not any(audit['private_paths'].values())
    command=['docker','run','--rm','--network','none','--cpus','4','--memory','4g',
             '-v',f'{folder}:/output','-v',f'{HERE/"baseline_patches.py"}:/baseline.py:ro']
    if method=='translation':
        command+=['-v',f'{HERE/"br022_baseline_ablation.py"}:/runner.py:ro',image,'python','/runner.py',
                  '--data','/app/data','--out','/output/points.json','--kind','2d','--model','translation','--context','multiscale']
    elif method=='baseline':
        command += [image,'python','/baseline.py','--data','/app/data','--out','/output/points.json','--kind','2d']
    else:
        command+=['-v',f'{HERE/"br024_neighborhood.py"}:/runner.py:ro',image,'python','/runner.py']
    with (folder/'execution.log').open('w') as log:
        subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True)
    grade=score(read(folder/'points.json'),read(task/'tests/truth.json'));assert grade['reward']==1
    author={'round':'BR-024','case':case,'image':image,'image_audit':audit,'public_files_match':True,
            'network':'none','private_labels_mounted':False,'command':command,'grade':grade,
            'answer_path':str((folder/'points.json').relative_to(ROOT)),'answer_sha256':sha(folder/'points.json'),
            'preparation':prep}
    for p in [folder/'audit.json',ROOT/f'docs/evidence/br024-patient{case}-author-audit.json']:
        p.write_text(json.dumps(author,indent=2)+'\n')
    freeze={'round':'BR-024','case':case,'plan_sha256':sha(OUT/'plan.json'),'author_audit_sha256':sha(folder/'audit.json'),
            'task':{'task':prep['task'],'task_path':prep['task_path'],
                    'files':{str(p.relative_to(task)):sha(p) for p in sorted(task.rglob('*')) if p.is_file()}}}
    (OUT/'freezes').mkdir(exist_ok=True)
    for p in [OUT/f'freezes/patient{case}.json',ROOT/f'docs/evidence/br024-patient{case}-freeze.json']:
        assert not p.exists();p.write_text(json.dumps(freeze,indent=2)+'\n')
    print(json.dumps({'case':case,'freeze_sha256':sha(OUT/f'freezes/patient{case}.json'),'grade':grade,'image':image},indent=2))


if __name__=='__main__':main()
