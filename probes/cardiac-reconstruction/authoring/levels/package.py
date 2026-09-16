"""Prepare immutable local task packages; no previous source artifacts are changed."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
B=ROOT/'runs/br031-cardiac-levels'
SOURCE=ROOT/'runs/br029-dynamic-heart'
PIP='numpy==2.2.6 scipy==1.15.3 pillow==11.3.0 opencv-python-headless==4.12.0.88 meshio==5.3.5 scikit-image==0.25.2'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def structure(name, timeout=1800):
    task=B/'tasks'/name
    task.mkdir(parents=True,exist_ok=False)
    for sub in ['environment/data','tests','solution']: (task/sub).mkdir(parents=True)
    (task/'environment/Dockerfile').write_text(f'FROM python:3.12-slim-bookworm\nRUN pip install --no-cache-dir {PIP}\nWORKDIR /app\nCOPY data /app/data\nCOPY SOURCE_NOTICE.md /app/SOURCE_NOTICE.md\nRUN mkdir -p /app/answer\n')
    (task/'environment/SOURCE_NOTICE.md').write_text('Source: Multimodality STRAUS, CREATIS/INRIA/Philips, https://humanheart-project.creatis.insa-lyon.fr/multimodalityStraus.html . Simulated ultrasound and myocardial material meshes. Local research only; no redistribution license is asserted. This task provides all permitted case information in /app/data. Do not retrieve source reference answers, other case files or previous workbench outputs; use ordinary libraries freely. The initial anatomical reference and calibration are supplied, not inferred.\n')
    (task/'tests/test.sh').write_text('#!/bin/sh\nset -eu\npython /verifier/score.py\n')
    (task/'tests/Dockerfile').write_text(f'FROM python:3.12-slim-bookworm\nRUN pip install --no-cache-dir {PIP}\nCOPY . /verifier/\nRUN mkdir -p /app/answer /tests && cp /verifier/test.sh /tests/test.sh && chmod 755 /tests/test.sh\nWORKDIR /app\nCMD ["/tests/test.sh"]\n')
    (task/'task.toml').write_text(f'''artifacts = ["/app/answer"]
[task]
name = "terminal-bench/{name}"
description = "Cardiac reconstruction capability diagnostic"
authors = [{{name = "Research pilot"}}]
[metadata]
author_name = "Research pilot"
author_email = "probe@example.invalid"
category = "Data Science"
tags = ["cardiac", "deformation", "mechanics"]
[verifier]
timeout_sec = 600.0
environment_mode = "separate"
[agent]
timeout_sec = {timeout}.0
[environment]
build_timeout_sec = 600.0
cpus = 4
memory_mb = 8192
storage_mb = 16384
gpus = 0
network_mode = "public"
''')
    return task

def freeze(task, checks):
    record=dict(round='BR-031',task=task.name,task_path=str(task.relative_to(ROOT)),
                files={str(p.relative_to(task)):sha(p) for p in sorted(task.rglob('*')) if p.is_file()},
                controls=checks,protocol_sha256=sha(ROOT/'docs/research-rounds/BR-031-cardiac-agent-levels.md'),
                status='frozen before model trials',source='STRAUS simulated healthy case from BR-029')
    target=B/f'{task.name}-freeze.json'; assert not target.exists()
    target.write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(dict(task=task.name,files=len(record['files']),freeze_sha256=sha(target),controls=checks)))

def l0():
    from kinematics import from_input,analytic_inputs
    from score_l0 import score, compare
    task=structure('cardiac-l0');z=dict(np.load(SOURCE/'analysis-v2/healthy_reference.npz'))
    input_=dict(reference_points=z['points'][0],points=z['points'],tetra=z['tetra'],
                directions=z['directions'],cell_labels=z['cell_labels'])
    np.savez_compressed(task/'environment/data/motion.npz',**input_)
    shutil.copy2(task/'environment/data/motion.npz',task/'tests/source.npz')
    (task/'instruction.md').write_text('''Compute finite myocardial strain from the supplied material motion.

/app/data/motion.npz contains reference_points (N,3), points (T,N,3), tetra (M,4), directions (3,M,3), cell_labels (M). Coordinates are mm. Vertex identities are persistent material points. Direction order is longitudinal, circumferential, radial in the REFERENCE frame. This is finite deformation, with full Green-Lagrange tensors and directional engineering strain, not infinitesimal or logarithmic strain. F maps reference column vectors to current column vectors. Use signed volume ratios J. No per-frame alignment.

Write /app/answer/solve.py, runnable as `python solve.py --input PATH --output PATH`, and run it on motion.npz to produce /app/answer/fields.npz. Output keys:
- F and E: (T,M,3,3) deformation gradients and full Green-Lagrange tensors.
- J: (T,M) local volume ratios.
- engineering: (T,M,3) directional engineering strain in fractional units, not percent.
- valid: (M,) boolean; true only if cell_labels > 0 AND every supplied direction has norm > 0.99. Some positive-label cells have missing directions. Set only engineering[:,~valid] to NaN. F/E/J must remain finite for every tetrahedron.

Your executable must handle other valid input shapes using the same schema, including rigid rotations/translations and finite affine strains. Values are checked to absolute tolerance 1e-5, including exact missingness/support. An initial frame is provided, but all deformation is relative to reference_points. Include a brief method.md explaining conventions and checks. Ordinary scientific libraries are installed. Do not retrieve source answers; all necessary input is supplied. This stage evaluates calculations, not recovery of the supplied motion.
''')
    for src,dst in [('kinematics.py','kinematics.py'),('score_l0.py','score.py')]:shutil.copy2(HERE/src,task/'tests'/dst)
    shutil.copy2(HERE/'oracle_l0.py',task/'solution/solve.py')
    (task/'solution/solve.sh').write_text('#!/bin/sh\nset -eu\ncp /solution/solve.py /app/answer/solve.py\npython /app/answer/solve.py --input /app/data/motion.npz --output /app/answer/fields.npz\n')
    oracle=B/'controls/l0-oracle';oracle.mkdir(parents=True)
    shutil.copy2(HERE/'oracle_l0.py',oracle/'solve.py')
    subprocess.run([sys.executable,str(oracle/'solve.py'),'--input',str(task/'tests/source.npz'),'--output',str(oracle/'fields.npz')],check=True)
    good=score(oracle,task/'tests/source.npz');assert good['reward']==1,good
    none=score(B/'absent',task/'tests/source.npz');assert none['reward']==0
    inp=analytic_inputs();expected=from_input(inp)
    assert np.max(abs(expected['engineering'][1,0]))<1e-12
    assert np.max(abs(expected['E'][2]-expected['E'][3]))<1e-12
    wrong={**expected,'E':.5*(expected['F']+expected['F'].swapaxes(-1,-2))-np.eye(3)}
    np.savez_compressed(B/'controls/infinitesimal.npz',**wrong)
    bad=compare(B/'controls/infinitesimal.npz',expected);assert not bad['pass_']
    freeze(task,dict(oracle=good,nop=none,infinitesimal=bad,analytic_objectivity=True))

def l1():
    from score_l1 import all_sections,geometry_score,score
    task=structure('cardiac-l1')
    public=SOURCE/'public-video'
    for name in ['initial_mesh.npz','geometry.json']:
        shutil.copy2(public/name,task/'environment/data'/name)
    for i in range(4):shutil.copytree(public/f'view_{i}',task/'environment/data'/f'view_{i}')
    geo=json.loads((public/'geometry.json').read_text())
    z=dict(np.load(SOURCE/'analysis-v2/healthy_reference.npz'))
    init=dict(np.load(public/'initial_mesh.npz'))
    truth={k:z[k] for k in ['points','tetra','directions','cell_labels']}
    truth['point_labels']=init['point_labels']
    assert np.max(abs(truth['points'][0]-init['points']))<1e-9
    np.savez_compressed(task/'tests/truth.npz',**truth)
    planes=list(geo['planes'])
    center=np.array(geo['initial_center'])
    for angle in [30,90,150]:
        theta=np.deg2rad(angle)
        planes.append(dict(name=f'Withheld long axis {angle}',origin=center.tolist(),
                           u=[float(np.cos(theta)),float(np.sin(theta)),0],v=[0,0,-1]))
    origin=center.copy();origin[2]=np.quantile(init['points'][init['point_labels']>0,2],.35)
    planes.append(dict(name='Withheld short axis',origin=origin.tolist(),u=[1,0,0],v=[0,1,0]))
    (task/'tests/planes.json').write_text(json.dumps(planes,indent=2)+'\n')
    masks=all_sections(truth['points'],truth['tetra'],planes)
    np.savez_compressed(task/'tests/sections.npz',masks=masks)
    for src,dst in [('kinematics.py','kinematics.py'),('score_l1.py','score.py')]:shutil.copy2(HERE/src,task/'tests'/dst)
    np.savez_compressed(task/'solution/prediction.npz',points=truth['points'])
    (task/'solution/solve.sh').write_text('#!/bin/sh\nset -eu\ncp /solution/prediction.npz /app/answer/prediction.npz\n')
    (task/'instruction.md').write_text('''Recover a deforming biventricular myocardial body from four calibrated ultrasound videos and a supplied initial tetrahedral mesh.

Inputs in /app/data:
- initial_mesh.npz: points (N,3) in mm; tetra (M,4); labels (M,), point_labels (N,), directions (3,M,3). Vertex identities must remain persistent material identities. Label 0 denotes RV/unassigned tissue and lacks directional axes; positive labels are LV AHA 1-17. Direction order is longitudinal, circumferential, radial in the reference frame. Three positive-label cells also lack a complete basis.
- view_0 through view_3 contain 30 grayscale PNG frames each. All views are synchronized slices of one synthetic 3D ultrasound cycle. Frame 1 matches the supplied mesh. They are not independent unsynchronized acquisitions.
- geometry.json supplies plane origins and u/v unit vectors, pixel_center, spacing_mm, and frame count. Pixel (column,row) corresponds to origin + spacing_mm*((column-pixel_center)*u + (row-pixel_center)*v), in the SAME coordinate system as points. No extra transform is needed for these PNGs; native coordinate metadata describe their source. The first three views are long-axis planes and the fourth is short-axis. Image changes include speckle evolution and out-of-plane motion.

Write /app/answer/prediction.npz with key points, shape (30,N,3), in mm and the exact original vertex order. Preserve frame 1 coordinates within 1e-4 mm and preserve tetrahedral connectivity. Also retain your reconstruction code as /app/answer/solve.py and describe assumptions, checks and uncertainty in /app/answer/method.md. The 30-frame prediction is scored; a video or painted strain map is insufficient.

Use all supplied observations and appropriate spatial/temporal assumptions. You may use ordinary scientific libraries, which are installed. No pretrained reconstruction, author solver, later mesh, target strain, source reference answer or scoring feedback is supplied. Do not retrieve those from the source website or other workbench files. No per-frame or post-hoc realignment is allowed. The whole biventricular body is evaluated, with LV and RV/unassigned results also reported separately. Four planes leave some motion weakly observed: report those limitations without inventing missing observations.

Independent evaluation includes observed and withheld cross-sectional myocardial masks, sampled surface distance, myocardial tissue volume, material-point motion and strain derived from your submitted deformation. Development acceptance for geometry/motion: mean observed slice Dice >=0.90; mean withheld slice Dice >=0.85; symmetric sampled surface mean <=2 mm and p95 <=5 mm; mean relative myocardial volume-curve error <=5%; whole-body material-point RMSE <=2 mm; zero inverted elements. No withheld plane images/contours are supplied. A separate mechanics score requires each longitudinal/circumferential/radial strain MAE <=5 percentage points, mean regional peak error <=5 points, and mean regional peak-timing distance <=2 frames; reference extrema within 0.5 points count as ties. These are engineering diagnostics, not clinical tolerances. Strain uses directional engineering stretch relative to frame 1. You need not submit strain arrays: the evaluator recomputes them from points and supplied anatomical axes.

Physical frame duration is unknown: use cycle phase, not invented seconds. Myocardial volume is not blood-pool volume. Do not claim EF, blood flow, active-force equilibrium or a diagnosis. Focus on recovering material deformation, and report what the sparse images can support.
''')
    controls={}
    candidate_paths=dict(oracle=task/'solution/prediction.npz',
                         affine=SOURCE/'video-fit-v1/prediction.npz',
                         tissue=SOURCE/'tissue-fit-v2/prediction.npz')
    for name,path in candidate_paths.items():
        print('scoring',name,flush=True)
        r=score(path,truth,masks,planes);r.pop('region_engineering_percent',None);controls[name]=r
    r=geometry_score(np.repeat(truth['points'][:1],30,axis=0),truth,masks,planes)
    r.pop('region_engineering_percent',None);controls['static']=r
    controls['nop']=score(B/'absent.npz',truth,masks,planes)
    assert controls['oracle']['complete_pass'] and controls['oracle']['reward']==1,controls['oracle']
    assert controls['nop']['reward']==0 and controls['static']['reward']==0
    freeze(task,controls)

def l1v():
    # Read only already-curated image volumes; parent task and reference stay frozen.
    import sys
    sys.path.insert(0,str(HERE.parent/'dynamic_heart'))
    from prepare_video import mhd
    parent=B/'tasks/cardiac-l1';task=B/'tasks/cardiac-l1v'
    assert not task.exists();shutil.copytree(parent,task)
    (task/'task.toml').write_text((task/'task.toml').read_text().replace('terminal-bench/cardiac-l1','terminal-bench/cardiac-l1v'))
    images=task/'environment/data/volume_frames';images.mkdir()
    source_files={}
    for t in range(30):
        src=SOURCE/'source/patient01_healthy/image'/f'usfrm{t:02d}.mhd'
        image,spacing=mhd(src)
        output=images/f'frame_{t+1:02d}.npz'
        np.savez_compressed(output,volume=image)
        assert np.array_equal(np.load(output)['volume'],image)
        source_files[str(src.relative_to(ROOT))]=sha(src)
        source_files[str(src.with_suffix('.raw').relative_to(ROOT))]=sha(src.with_suffix('.raw'))
    geo=json.loads((task/'environment/data/geometry.json').read_text())
    info=dict(array_key='volume',array_axes=['z','y','x'],array_shape=list(image.shape),array_dtype=str(image.dtype),
              spacing_xyz_mm=spacing.tolist(),native_origin_xyz_mm=[0,0,0],native_direction_matrix=np.eye(3).tolist(),
              canonical_to_native_row_matrix=geo['canonical_to_native_rotation_rows'],
              canonical_to_native_offset_mm=geo['canonical_to_native_offset'],
              mapping='For a canonical row vector p from the mesh: native_world_mm = p @ canonical_to_native_row_matrix + canonical_to_native_offset_mm; native voxel xyz index = native_world_mm / spacing_xyz_mm. Sample the stored volume array in z,y,x order.',
              frames=30,intensities='Unmodified signed int16 source samples; not normalized PNG intensities.',physical_frame_duration_seconds=None)
    (task/'environment/data/volume_geometry.json').write_text(json.dumps(info,indent=2)+'\n')
    text=(task/'instruction.md').read_text()
    text='''Additional observation condition: alongside the four original videos you now have the FULL native 3D ultrasound cycle in /app/data/volume_frames/frame_01.npz through frame_30.npz. Each file contains volume[z,y,x] with unmodified source int16 values. /app/data/volume_geometry.json gives exact array axes, spacing and mesh-to-native mapping; the mesh and PNG coordinates have not changed. You may exploit full-volume registration/tracking or extract any desired planes. These are image volumes, not ground-truth deformation or segmentation. All 30 phases match the video and requested output frames.

The four scoring planes previously withheld from the four-video input now lie within these volumes. Their Dice remains a diagnostic at different planes, not a claim of unseen-view generalization in this condition. No future meshes, target strain or reference contours are supplied. Other contract details and numerical thresholds are identical to the four-video task below.

'''+text
    (task/'instruction.md').write_text(text)
    parentfreeze=json.loads((B/'cardiac-l1-freeze.json').read_text())
    freeze(task,dict(parent_task_sha256=sha(B/'cardiac-l1-freeze.json'),same_verifier_bytes=True,
                     same_oracle_bytes=True,volume_roundtrip_exact=True,source_files=source_files,
                     contrast_protocol_sha256=sha(ROOT/'docs/research-rounds/BR-031-volume-contrast.md')))
    current=json.loads((B/'cardiac-l1v-freeze.json').read_text())
    assert all(current['files'][k]==v for k,v in parentfreeze['files'].items() if k.startswith(('tests/','solution/')))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['l0','l1','l1v']);a=p.parse_args()
    {'l0':l0,'l1':l1,'l1v':l1v}[a.stage]()
