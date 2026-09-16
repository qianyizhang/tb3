"""Freeze only after both public-only isolated author checks have passed."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
from score import score
from run_trials import verify

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'runs/br021-deformable'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n')


def main():
    assert not (OUT/'freeze.json').exists(),'Never replace a freeze'
    prepared=read(OUT/'prepared.json');truth=read(OUT/'author/truth.json');isolated={}
    for kind in ['2d','3d']:
        d=OUT/f'author/isolated/{kind}';answer=d/'points.json';grade=score(read(answer),truth)
        assert grade['reward']==1
        isolated[kind]={'grade':grade,'answer_sha256':sha(answer),'solver':read(d/'points.log.json'),
             'command_receipt_sha256':sha(d/'command.json'),'command_receipt':read(d/'command.json')}
    baselines=[]
    for file in sorted((OUT/'author/baselines').glob('*.json')):
        if file.name.endswith('.log.json'):continue
        baselines.append({'name':file.stem,'grade':score(read(file),truth),'answer_sha256':sha(file),
                          'elapsed_s':read(file.with_suffix('.log.json')).get('elapsed_s')})
    audit={'round':'BR-021','source_audit':read(OUT/'author/source-audit.json'),
        'source_receipt_sha256':sha(OUT/'source/source-receipt.json'),
        'generation':read(OUT/'author/generation.json'),'baselines':baselines,'isolated_public_only_baselines':isolated,
        'visual_review':{'result':'All eight source/manual-destination positions have visible vessel or airway structure; author review, not clinician certification.',
                         'image_path':'runs/br021-deformable/author/manual-correspondence-review.png',
                         'sha256':sha(OUT/'author/manual-correspondence-review.png')},
        'baseline_code_sha256':sha(ROOT/'probes/registration-deformation/authoring/baseline_patches.py'),
        'limitations':['Case and plane deliberately selected for nonrigidity before baseline/model execution.',
            'Author algorithms developed on this case; no held-out accuracy claim.',
            'Public nominal source geometry in 2D deliberately isolates deformation; different from prior lost rigid pose tasks.',
            'Only eight correspondences, not full dense registration, are verified.',
            'Manual annotations are publicly available; image isolation and trace review cannot exclude all training contamination.',
            'Engineering tolerance has not been clinically validated.']}
    for task in prepared['tasks']:verify(task)
    freeze={**prepared,'frozen_at':datetime.now(timezone.utc).isoformat(),
        'protocol':{'model':'openai/gpt-5.6-terra','reasoning_effort':'high','attempts_per_condition':1,'automatic_retries':0,
                    'timeout_sec':1800,'separate_verifier':True,'conditions':'same eight manually annotated correspondences',
                    'rms_tolerance_mm':3,'max_tolerance_mm':5},
        'author_audit_path':'docs/evidence/br021-author-audit.json'}
    write(ROOT/'docs/evidence/br021-author-audit.json',audit)
    freeze['author_audit_sha256']=sha(ROOT/'docs/evidence/br021-author-audit.json')
    write(OUT/'freeze.json',freeze);write(ROOT/'docs/evidence/br021-freeze.json',freeze)
    print(json.dumps({'frozen':[t['task'] for t in freeze['tasks']],'freeze_sha256':sha(OUT/'freeze.json'),'isolated_grades':{k:v['grade'] for k,v in isolated.items()}},indent=2))


if __name__=='__main__':main()
