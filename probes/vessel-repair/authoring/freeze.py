"""Freeze reviewed source-backed task bytes and pre-model controls."""
import hashlib
import json
from pathlib import Path
import shutil
import nibabel as nib
import numpy as np
from score import score_file,score_array,LIMITS

ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'runs/br026-vessel-repair';HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    assert not (BASE/'freeze.json').exists(),'Do not replace a freeze'
    record=json.loads((BASE/'prepared.json').read_text());baselines=[]
    for task in record['tasks']:
        path=ROOT/task['task_path'];shutil.copy(HERE/'instruction.md',path/'instruction.md')
        with np.load(path/'tests/truth.npz',allow_pickle=False) as z:truth={k:z[k] for k in z.files}
        assert score_file(path/'solution/reference.nii.gz',truth)['reward']==1
        task['format_controls']={}
        wrong=truth['affine'].copy();wrong[0,3]+=1
        task['format_controls']['wrong_affine']=score_array(truth['gt'],wrong,truth)
        task['format_controls']['nonbinary']=score_array(truth['gt'].astype(int)*2,truth['affine'],truth)
        task['format_controls']['missing_output']=score_file(BASE/'nonexistent-answer.nii.gz',truth)
        assert all(x['reward']==0 for x in task['format_controls'].values())
        v=task['task'].split('-')[-1]
        for mode in ['mask','image']:
            answer=BASE/'baselines'/f'{v}-skeleton-{mode}.nii.gz'
            metrics=score_file(answer,truth)
            baseline={'task':task['task'],'mode':mode,'grade':metrics,'answer_sha256':sha(answer),
                      'details':json.loads(answer.with_suffix('.json').read_text())}
            baselines.append(baseline)
            assert metrics['reward']==(1 if mode=='image' or v=='v02' else 0)
        task['files']={str(p.relative_to(path)):sha(p) for p in sorted(path.rglob('*')) if p.is_file()}
        task['public_input_files']=sorted(str(p.relative_to(path/'environment/data')) for p in (path/'environment/data').iterdir())
        assert task['public_input_files']==['editable_region.nii.gz','image.nii.gz','proposed_mask.nii.gz']
    record.update(limits=LIMITS,author_baselines=baselines,model_trials_before_freeze=0,
        authoring_files={str(p.relative_to(ROOT)):sha(p) for p in sorted(HERE.glob('*')) if p.is_file()},
        native_image_review='Native axial, coronal and sagittal gap sections inspected; source-scaled intensities preserved exactly.',
        source_status='Synthetic gap and unchanged reference; no natural segmentation model prediction.',
        clinical_status='Engineering annotation-backed pilot, not independent expert clinical adjudication.',
        threshold_status='Development-case calibration before model runs; not a held-out clinical tolerance study.')
    for p in [BASE/'freeze.json',ROOT/'docs/evidence/br026-freeze.json']:
        p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({'frozen_tasks':[t['task'] for t in record['tasks']],
          'freeze_sha256':sha(BASE/'freeze.json'),'baselines':[{k:r[k] for k in ['task','mode','grade']} for r in baselines]},indent=2))

if __name__=='__main__':main()
