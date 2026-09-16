"""Audit the actual public image, replay fixed baselines, then freeze task bytes."""
import json
from pathlib import Path
import subprocess
from br028_prepare import ROOT,OUT,HERE,read,write,sha
from score import score

def main():
    prep=read(OUT/'prepared.json');task=ROOT/prep['task_path'];plan=read(OUT/'plan.json')
    for path,h in plan['code_sha256'].items():assert sha(ROOT/path)==h
    image=subprocess.check_output(['docker','image','inspect','tb3-br028-source3d-author:20260916','--format','{{.Id}}'],text=True).strip()
    code="import pathlib,json,hashlib,numpy as np; p=pathlib.Path('/app'); print(json.dumps({'files':{str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in p.rglob('*') if f.is_file()},'answers':[f.name for f in (p/'answer').iterdir()],'private_exists':{s:pathlib.Path(s).exists() for s in ['/tests','/solution','/verifier','/author','/baseline.py','/app/truth.json']},'source_npz_members':np.load('/app/data/reference_volume.npz').files}))"
    listing=json.loads(subprocess.check_output(['docker','run','--rm','--network','none',image,'python','-c',code],text=True))
    expected={'/app/SOURCE_NOTICE.md':sha(task/'environment/SOURCE_NOTICE.md')}
    expected.update({f'/app/data/{p.name}':sha(p) for p in (task/'environment/data').iterdir()})
    assert listing['files']==expected and not listing['answers'] and not any(listing['private_exists'].values())
    assert set(listing['source_npz_members'])=={'hu','voxel_to_world'}
    rows=[]
    for kind in ['2d-translation','3d-affine']:
        folder=OUT/'author'/kind;folder.mkdir(parents=True,exist_ok=False)
        runner=HERE/('br022_baseline_ablation.py' if kind=='2d-translation' else 'br028_baseline_3d.py')
        command=['docker','run','--rm','--network','none','--cpus','4','--memory','4g','-v',f'{HERE/"baseline_patches.py"}:/baseline.py:ro',
                 '-v',f'{runner}:/runner.py:ro','-v',f'{folder}:/output',image,'python','/runner.py']
        if kind=='2d-translation':command+=['--data','/app/data','--out','/output/points.json','--kind','2d','--model','translation','--context','multiscale']
        with (folder/'execution.log').open('w') as log:subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=600)
        grade=score(read(folder/'points.json'),read(task/'tests/truth.json'))
        if kind=='2d-translation':assert grade['reward']==1
        row={'method':kind,'grade':grade,'command':command,'network':'none','private_labels_mounted':False,
             'answer_path':str((folder/'points.json').relative_to(ROOT)),'answer_sha256':sha(folder/'points.json')}
        rows.append(row);print(json.dumps(row|{'command':'retained in receipt'}),flush=True)
    audit={'round':'BR-028','image':image,'public_files_match':True,'image_audit':listing,'preparation':prep,'author_rows':rows}
    for p in [OUT/'author-audit.json',ROOT/'docs/evidence/br028-author-audit.json']:write(p,audit)
    freeze={'round':'BR-028','plan_sha256':sha(OUT/'plan.json'),'author_audit_sha256':sha(OUT/'author-audit.json'),
            'task':{'task':prep['task'],'task_path':prep['task_path'],'files':{str(p.relative_to(task)):sha(p) for p in sorted(task.rglob('*')) if p.is_file()}}}
    for p in [OUT/'freeze.json',ROOT/'docs/evidence/br028-freeze.json']:assert not p.exists();write(p,freeze)
    print(json.dumps({'freeze_sha256':sha(OUT/'freeze.json'),'image':image}),flush=True)

if __name__=='__main__':main()
