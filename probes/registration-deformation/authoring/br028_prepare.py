"""Add exactly one source volume to the frozen BR-024 case; verify its origin."""
import datetime
import hashlib
import json
from pathlib import Path
import shutil
import nibabel as nib
import numpy as np
from scipy.interpolate import RegularGridInterpolator

ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'runs/br028-registration-3d-source';HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def write(p,v):p.parent.mkdir(exist_ok=True,parents=True);p.write_text(json.dumps(v,indent=2)+'\n')

def main():
    OUT.mkdir(exist_ok=False)
    old_freeze=ROOT/'runs/br024-harder-registration/freezes/patient3.json';old=read(old_freeze)['task'];oldtask=ROOT/old['task_path']
    assert {str(p.relative_to(oldtask)):sha(p) for p in oldtask.rglob('*') if p.is_file()}==old['files']
    source=ROOT/'runs/br021-deformable/source';source_path=source/'LungCT/imagesTr/LungCT_0003_0000.nii.gz'
    source_receipt=read(source/'source-receipt.json');record=next(r for r in source_receipt['files'] if r['member']==str(source_path.relative_to(source)))
    assert sha(source_path)==record['sha256']
    protocol=ROOT/'docs/research-rounds/BR-028-registration-3d-source.md'
    plan={'round':'BR-028','fixed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'protocol_path':str(protocol.relative_to(ROOT)),'protocol_sha256':sha(protocol),'parent_task':old,
          'prior_receipts':{str(p.relative_to(ROOT)):sha(p) for p in [old_freeze,ROOT/'docs/evidence/br024-results.json',ROOT/'docs/evidence/br024-stage-analysis.json',ROOT/'docs/evidence/br024-approach-analysis.json']},
          'source_file':record,'code_sha256':{str(p.relative_to(ROOT)):sha(p) for p in [HERE/'baseline_patches.py',HERE/'br022_baseline_ablation.py',HERE/'br028_baseline_3d.py',Path(__file__)]},
          'model':'openai/gpt-5.6-sol','reasoning_effort':'xhigh','agent_timeout_seconds':1800,'max_model_attempts':1,'max_retries':0,
          'contrast':'Add full source CT; keep existing 2D inputs, source query positions, target, answers, grader and limits.'}
    for p in [OUT/'plan.json',ROOT/'docs/evidence/br028-plan.json']:write(p,plan)
    task=OUT/'tasks/deform-patient3-source3d';shutil.copytree(oldtask,task)
    img=nib.load(source_path);hu=np.asarray(img.dataobj).astype(np.float32);a=img.affine
    public=task/'environment/data';np.savez_compressed(public/'reference_volume.npz',hu=hu,voxel_to_world=a)
    instruction=(task/'instruction.md').read_text()
    instruction=instruction.replace('- volume.npz: the inhale volume to search.','- volume.npz: the inhale volume to search.\n- reference_volume.npz: the full supplied exhale volume, including depth beyond the view.')
    oldtext='of anatomy into inhale. The full exhale volume is not supplied. Find where\nthe specified structures in this single view moved in the inhale volume.'
    newtext='of anatomy into inhale. The full exhale volume is supplied in reference_volume.npz.\nYou may use both 3D volumes and the view to find where the specified structures\nmoved in the inhale volume. Query locations and the required answer are unchanged.'
    assert oldtext in instruction;instruction=instruction.replace(oldtext,newtext)
    (task/'instruction.md').write_text(instruction)
    (task/'task.toml').write_text((task/'task.toml').read_text().replace('terminal-bench/deform-harder-patient3','terminal-bench/deform-patient3-source3d'))
    for name in old['files']:
        if name not in ['instruction.md','task.toml']:assert sha(task/name)==old['files'][name]
    q=read(public/'queries.json');g=read(public/'view.json');s=np.array(g['slice_to_world']);view=np.load(public/'view.npy')
    vv,uu=np.indices(view.shape);uv=np.column_stack([uu.ravel(),vv.ravel()]);world=s[:3,3]+(uv*np.array(g['spacing_xy_mm']))@s[:3,:2].T
    vox=(world-a[:3,3])@np.linalg.inv(a[:3,:3]).T
    sampled=RegularGridInterpolator(tuple(np.arange(n) for n in hu.shape),hu)(vox).reshape(view.shape)
    diff=float(np.max(np.abs(sampled-view)));assert diff<.001
    with np.load(public/'reference_volume.npz') as z:assert set(z.files)=={'hu','voxel_to_world'} and np.array_equal(z['hu'],hu) and np.array_equal(z['voxel_to_world'],a)
    prep={'round':'BR-028','task':'deform-patient3-source3d','task_path':str(task.relative_to(ROOT)),
          'plan_sha256':sha(OUT/'plan.json'),'old_public_files_and_private_evaluation_unchanged':True,
          'source_shape':list(hu.shape),'source_spacing_mm':np.diag(a)[:3].tolist(),
          'source_nifti_sha256':sha(source_path),'reference_volume_sha256':sha(public/'reference_volume.npz'),
          'independent_interpolation_samples':int(view.size),'max_hu_difference':diff,
          'query_world_mm':(s[:3,3]+(np.array(q['pixels_uv'])*np.array(g['spacing_xy_mm']))@s[:3,:2].T).tolist()}
    write(OUT/'prepared.json',prep);print(json.dumps(prep,indent=2))

if __name__=='__main__':main()
