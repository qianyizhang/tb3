"""Prepare one admitted case without changing any previous task snapshot."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import numpy as np
import nibabel as nib
from scipy.interpolate import RegularGridInterpolator
from score import score

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'runs/br024-harder-registration'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser();ap.add_argument('candidate');ap.add_argument('--method',choices=['baseline','translation','neighborhood'],required=True);args=ap.parse_args()
    c=OUT/'candidates'/args.candidate;prep=json.loads((c/'preparation.json').read_text());truth=json.loads((c/'truth.json').read_text())
    answer=json.loads((c/args.method/'points.json').read_text());grade=score(answer,truth);assert grade['reward']==1
    case=prep['case'];name=f'deform-harder-patient{case}';task=OUT/'tasks'/name
    assert not task.exists();shutil.copytree(ROOT/'runs/br021-deformable/tasks/deform-2d',task)
    for p in (task/'environment/data').iterdir():p.unlink()
    for p in (c/'public').iterdir():shutil.copy2(p,task/'environment/data'/p.name)
    (task/'tests/truth.json').write_text(json.dumps(truth,indent=2)+'\n')
    (task/'solution/points.json').write_text(json.dumps({k:truth[k] for k in ['query_ids','points_world_mm']},indent=2)+'\n')
    toml=(task/'task.toml').read_text().replace('terminal-bench/deform-2d','terminal-bench/'+name)
    (task/'task.toml').write_text(toml)
    img=nib.load(ROOT/f'runs/br021-deformable/source/LungCT/imagesTr/LungCT_{case:04d}_0000.nii.gz')
    volume=np.asarray(img.dataobj);view=np.load(c/'public/view.npy');g=json.loads((c/'public/view.json').read_text());M=np.array(g['slice_to_world'])
    rng=np.random.default_rng(24);uv=np.column_stack([rng.integers(0,view.shape[1],300),rng.integers(0,view.shape[0],300)])
    world=M[:3,3]+np.einsum('ij,nj->ni',M[:3,:2],uv*np.array(g['spacing_xy_mm']))
    vox=np.einsum('ij,nj->ni',np.linalg.inv(img.affine[:3,:3]),world-img.affine[:3,3])
    pred=RegularGridInterpolator(tuple(np.arange(s) for s in volume.shape),volume)(vox)
    delta=float(np.max(np.abs(pred-view[uv[:,1],uv[:,0]])));assert delta<.001
    y=np.array(truth['points_world_mm']);controls={}
    for name2,offset in [('oracle',0),('tolerated',2),('rms_boundary_fail',3.01),('large_shift',8)]:
        q=y.copy();q[:,0]+=offset;controls[name2]=score({'query_ids':truth['query_ids'],'points_world_mm':q.tolist()},truth)
    controls['nop']=score({},truth);controls['shuffled']=score({'query_ids':truth['query_ids'],'points_world_mm':y[::-1].tolist()},truth)
    q=y.copy();q[0,0]+=5.01;controls['single_outlier']=score({'query_ids':truth['query_ids'],'points_world_mm':q.tolist()},truth)
    assert [v['reward'] for v in controls.values()]==[1,1,0,0,0,0,0]
    record={'round':'BR-024','case':case,'candidate':args.candidate,'task':name,'task_path':str(task.relative_to(ROOT)),
            'baseline_method':args.method,'baseline_answer_path':str((c/args.method/'points.json').relative_to(ROOT)),
            'baseline_grade':grade,'interpolation_max_hu_difference':delta,'controls':controls,
            'preparation':prep,'author_visibility_review':'Actual source/manual-target panels inspected; all eight have visible vessel/airway structure. No expert clinical or unique-correspondence certification.'}
    (OUT/'prepared').mkdir(exist_ok=True);(OUT/f'prepared/patient{case}.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({'task':record['task'],'baseline_grade':grade,'interpolation_max_hu_difference':delta},indent=2))


if __name__=='__main__':main()
