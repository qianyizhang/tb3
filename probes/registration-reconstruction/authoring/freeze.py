"""Freeze only after public-input feasibility and source/geometry controls."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'runs/br020-registration'
sys.path.insert(0,str(ROOT/'probes/registration/authoring'))
from score import score

def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert not (OUT/'freeze.json').exists()
    record=read(OUT/'prepared.json')
    task=record['tasks'][0];base=ROOT/task['task_path'];truth=read(base/'tests/truth.json')
    files={str(p.relative_to(base)):sha(p) for p in sorted(base.rglob('*')) if p.is_file()}
    assert task['files']==files
    grades={}
    for name in ['cross-baseline','matched-baseline','cross-baseline-512','matched-baseline-512','isolated-baseline']:
        path=OUT/'author'/f'{name}.json'
        grades[name]={'grade':score(read(path),truth),**read(path.with_suffix('.metrics.json')),
                      'answer_sha256':sha(path)}
    assert all(grades[n]['grade']['reward']==1 for n in ['cross-baseline-512','matched-baseline-512','isolated-baseline'])
    container=read(OUT/'author/isolated-baseline-container.json')
    assert not container['mounts'] and container['network']=='none' and container['exit_code']==0
    allowed={'data/volume.npz','data/target.npy','data/target.png','data/image.json',
             'Dockerfile','reslice.py','SOURCE_NOTICE.md','DATA-LICENSE.txt'}
    assert {str(p.relative_to(base/'environment')) for p in (base/'environment').rglob('*') if p.is_file()}==allowed
    # Recheck containment using explicit einsum, avoiding macOS BLAS warnings.
    with np.load(base/'environment/data/volume.npz') as z:a=z['voxel_to_lps'];shape=z['hu'].shape
    t=np.array(truth['slice_to_lps']);y,x=np.indices(truth['shape'])
    q=np.array([x.ravel()*.9,y.ravel()*.9,np.zeros(x.size),np.ones(x.size)])
    index=np.einsum('ij,jn->in',np.linalg.inv(a)@t,q)[:3]
    assert np.isfinite(index).all() and np.all(index>=0) and np.all(index<=np.array(shape)[:,None]-1)
    audit={'round':'BR-020','baseline_results':grades,'isolated_baseline_container':container,
           'source_audit':read(OUT/'author/source-audit.json'),'generation':read(OUT/'author/generation.json'),
           'source_receipt_sha256':sha(OUT/'source/source-receipt.json'),
           'baseline_solver_sha256':sha(ROOT/'probes/registration/authoring/baseline.py'),
           'author_code_sha256':{p.name:sha(p) for p in sorted(Path(__file__).parent.glob('*.py'))},
           'agent_environment_files':sorted(allowed),'target_metadata_stripped':True,
           'all_pixels_inside_public_volume_rechecked':True,
           'baseline_limitation':'Author-selected method and adaptive start-count increase; public-input execution is not blind method discovery.',
           'clinical_limitation':'Engineering registration pilot with author visual landmark estimates, not certified diagnostic cardiac view.'}
    record.update(frozen_at=datetime.now(timezone.utc).isoformat(),author_audit_sha256=hashlib.sha256((json.dumps(audit,indent=2)+'\n').encode()).hexdigest())
    (OUT/'freeze.json').write_text(json.dumps(record,indent=2)+'\n')
    (ROOT/'docs/evidence/br020-author-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    shutil.copy(OUT/'freeze.json',ROOT/'docs/evidence/br020-freeze.json')
    print(json.dumps({'frozen':task['task'],'grades':{k:v['grade'] for k,v in grades.items()}}))


if __name__=='__main__':main()
