"""Author-only construction of the two matched deformation diagnostics."""
import hashlib
import json
from pathlib import Path
import shutil
import numpy as np
import nibabel as nib
from scipy.interpolate import RegularGridInterpolator
from score import score

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'runs/br021-deformable'
HERE=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n')


def main():
    truth=json.loads((OUT/'author/truth.json').read_text());prep=json.loads((OUT/'author/preparation.json').read_text())
    baseline={}
    for kind,name in [('2d','2d-independent-v2'),('3d','3d-independent-v3')]:
        file=OUT/f'author/baselines/{name}.json';baseline[kind]=score(json.loads(file.read_text()),truth)
        assert baseline[kind]['reward']==1
    controls={'oracle':score({k:truth[k] for k in ['query_ids','points_world_mm']},truth),'nop':score({},truth)}
    y=np.array(truth['points_world_mm'])
    for name,delta in [('shift_2mm',2),('boundary_2_99',2.99),('boundary_3_01',3.01),('shift_8mm',8)]:
        x=y.copy();x[:,0]+=delta;controls[name]=score({'query_ids':truth['query_ids'],'points_world_mm':x.tolist()},truth)
    for name,x in [('shuffled_points',y[::-1]),('voxel_instead_of_mm',y/[1.75,1.25,1.75]),('nonfinite',y*np.nan)]:
        controls[name]=score({'query_ids':truth['query_ids'],'points_world_mm':x.tolist()},truth)
    controls['one_outlier_5_01']=score({'query_ids':truth['query_ids'],'points_world_mm':(y+np.array([[5.01,0,0]]+[[0,0,0]]*7)).tolist()},truth)
    assert [c['reward'] for c in controls.values()]==[1,0,1,1,0,0,0,0,0,0]
    # A different interpolation implementation validates physical sampling.
    img=nib.load(OUT/f"source/LungCT/imagesTr/LungCT_{prep['case']:04d}_0000.nii.gz")
    data=np.asarray(img.dataobj);view=np.load(OUT/'author/public-2d/view.npy');g=json.loads((OUT/'author/public-2d/view.json').read_text())
    uv=np.column_stack([np.random.default_rng(21).integers(0,view.shape[1],300),np.random.default_rng(22).integers(0,view.shape[0],300)])
    pose=np.array(g['slice_to_world']);points=pose[:3,3]+np.einsum('ij,nj->ni',pose[:3,:2],uv*np.array(g['spacing_xy_mm']))
    ijk=np.einsum('ij,nj->ni',np.linalg.inv(img.affine[:3,:3]),points-img.affine[:3,3])
    pred=RegularGridInterpolator(tuple(np.arange(s) for s in data.shape),data)(ijk)
    interpolation_max=float(np.max(np.abs(pred-view[uv[:,1],uv[:,0]])));assert interpolation_max<.001
    records=[]
    for kind in ['3d','2d']:
        task=OUT/f'tasks/deform-{kind}';assert not task.exists(),'Never overwrite a prepared task'
        for d in ['environment','tests','solution']:(task/d).mkdir(parents=True)
        shutil.copytree(OUT/f'author/public-{kind}',task/'environment/data')
        (task/'environment/SOURCE_NOTICE.md').write_text('Source: Learn2Reg LungCT release 1.11; Hering, Alessa, Murphy, Keelin, and van Ginneken, Bram (2020), Learn2Reg Challenge: CT Lung Registration - Training Data, https://doi.org/10.5281/zenodo.3835682 . CC BY 4.0, https://creativecommons.org/licenses/by/4.0/ . Source overview: https://learn2reg.grand-challenge.org/Datasets/ . Original clinical CT from Radboud University Medical Center, Nijmegen, The Netherlands. Challenge data are resampled, cropped and affine prealigned. This task converts a scan pair to HU arrays and derives an oblique view and query positions. World coordinates are dataset coordinates, not asserted native scanner LPS. Retain this attribution for reuse.\n')
        (task/'environment/Dockerfile').write_text('FROM python:3.12-slim-bookworm\nRUN pip install --no-cache-dir numpy==2.2.6 scipy==1.15.3 pillow==11.3.0 SimpleITK==2.5.2\nWORKDIR /app\nCOPY data /app/data\nCOPY SOURCE_NOTICE.md /app/\nRUN mkdir -p /app/answer\n')
        shutil.copy(HERE/'score.py',task/'tests/score.py');write(task/'tests/truth.json',truth)
        write(task/'solution/points.json',{k:truth[k] for k in ['query_ids','points_world_mm']})
        (task/'tests/Dockerfile').write_text('FROM python:3.12-slim-bookworm\nCOPY . /verifier/\nRUN mkdir -p /app/answer /tests && cp /verifier/test.sh /tests/test.sh && chmod 755 /tests/test.sh\nWORKDIR /app\nCMD ["/tests/test.sh"]\n')
        (task/'tests/test.sh').write_text('#!/bin/sh\nset -eu\npython /verifier/score.py\n')
        (task/'solution/solve.sh').write_text('#!/bin/sh\nset -eu\nmkdir -p /app/answer\ncp /solution/points.json /app/answer/points.json\n')
        for p in [task/'tests/test.sh',task/'solution/solve.sh']:p.chmod(0o755)
        (task/'task.toml').write_text(f'''artifacts = ["/app/answer"]
[task]
name = "terminal-bench/deform-{kind}"
description = "Transfer anatomical landmarks across respiratory deformation."
authors = [{{name = "Research pilot"}}]
[metadata]
author_name = "Research pilot"
author_email = "probe@example.invalid"
category = "Data Science"
tags = ["registration", "ct", "deformation"]
[verifier]
timeout_sec = 120.0
environment_mode = "separate"
[agent]
timeout_sec = 1800.0
[environment]
build_timeout_sec = 600.0
cpus = 4
memory_mb = 4096
storage_mb = 10240
gpus = 0
network_mode = "public"
''')
        common='''# Find corresponding anatomy across respiratory phases

The supplied images come from the same patient in exhale and inhale phases.
Breathing changes anatomical shape, so a global rigid or affine transform may
not adequately describe the correspondence. Locate the anatomical points
specified in queries.json in the inhale CT /app/data/volume.npz.

Write /app/answer/points.json as
{"query_ids": ["q01", "q02", ...], "points_world_mm": [[x,y,z], ...]}.
Use the exact query order and IDs from queries.json. Coordinates must be
finite numbers in the supplied dataset-world millimetres.

Each volume NPZ contains hu[i,j,k] (float32 HU) and voxel_to_world (4x4).
The latter maps zero-based voxel centres [i,j,k,1] to homogeneous dataset-world
millimetres. The challenge volumes were cropped, resampled and affine
prealigned; matching array indices are only a nominal spatial initialization.
Do not assume a scanner LPS or RAS convention from the array order. Expiration
coverage is incomplete. Every requested corresponding point is visible in
the supplied inhale volume.

'''
        if kind=='3d':
            special='''Inputs in /app/data:
- reference_volume.npz: the full supplied exhale volume.
- volume.npz: the inhale volume to search.
- queries.json: query_ids and reference_world_mm, specifying source landmarks
  in exhale dataset-world millimetres.

Find the same anatomical structures in inhale. A dense deformation field is
optional working material; the required deliverable is the eight positions.
'''
        else:
            special='''Inputs in /app/data:
- volume.npz: the inhale volume to search.
- view.npy: float32 HU [row,column] sampled from one thin oblique exhale plane.
- view.png: a preview, round(255*clip((HU+1000)/1200,0,1)).
- view.json: shape, spacing_xy_mm and slice_to_world (4x4).
- queries.json: query_ids and pixels_uv, specifying source landmarks by
  fractional pixel column u and row v in the exhale view.

The acquisition frame is supplied: slice_to_world maps [u*sx,v*sy,0,1] to
exhale dataset-world millimetres, where (sx,sy)=spacing_xy_mm and (0,0) is
the top-left pixel centre. This is a nominal source geometry, NOT the mapping
of anatomy into inhale. The full exhale volume is not supplied. Find where
the specified structures in this single view moved in the inhale volume.
The source landmarks are localized to this view within 0.35 mm through-plane.
The view is a trilinear thin section, not an X-ray projection or thick slab.
'''
        ending='''
Acceptance: root-mean-square Euclidean error <=3 mm AND maximum error <=5 mm
against independently supplied manual corresponding landmarks. The comparison
is in world millimetres, not voxels, and only the eight submitted positions are
graded. Pixel similarity alone is not acceptance. No dense-field accuracy is
claimed between the queried points.

Python, NumPy, SciPy, Pillow and SimpleITK are installed. You may use suitable
registration algorithms, other software and public method documentation.
Reference landmark annotation files and evaluation answer keys are not solver
inputs; recover correspondences from the supplied images.

You have 1800 seconds to complete the task.
'''
        (task/'instruction.md').write_text(common+special+ending)
        records.append({'task':f'deform-{kind}','task_path':str(task.relative_to(ROOT)),
            'files':{str(p.relative_to(task)):sha(p) for p in sorted(task.rglob('*')) if p.is_file()}})
    write(OUT/'prepared.json',{'round':'BR-021','tasks':records})
    write(OUT/'author/generation.json',{'controls':controls,'public_input_baselines':baseline,
        'independent_interpolation_samples':len(uv),'interpolation_max_hu_difference':interpolation_max,
        'tolerance_status':'3 mm RMS and 5 mm maximum engineering tolerances, not estimated interobserver or clinical equivalence bounds',
        'preparation':prep})
    print(json.dumps({'prepared':[r['task'] for r in records],'baselines':baseline,'interpolation_max_hu_difference':interpolation_max},indent=2))


if __name__=='__main__':main()
