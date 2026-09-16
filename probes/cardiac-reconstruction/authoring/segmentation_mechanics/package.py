"""Freeze both paired conditions and clinical transfer before either Sol attempt."""
import hashlib,json,shutil
from pathlib import Path
import numpy as np
from score import score
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent;B=ROOT/'runs/br035-segmentation-mechanics'
PIP='numpy==2.2.6 scipy==1.15.3 pillow==11.3.0 opencv-python-headless==4.12.0.88 meshio==5.3.5 scikit-image==0.25.2'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def hashes(p):return {str(f.relative_to(p)):sha(f) for f in sorted(p.rglob('*')) if f.is_file()}
def write_prediction(path,points,tet):
    # Privileged oracle uses inverse products, independent of scorer's edge-system solve.
    X=points[0];e0=X[tet[:,1:]]-X[tet[:,:1]];et=points[:,tet[:,1:]]-points[:,tet[:,:1]]
    F=np.einsum('mij,tmjk->tmik',np.linalg.inv(e0),et).swapaxes(-1,-2)
    E=(np.einsum('tmki,tmkj->tmij',F,F)-np.eye(3))/2;J=np.linalg.det(F)
    np.savez_compressed(path,points=points,tetra=tet,F=F,E=E,J=J)
def input_(dst,kind,images):
    dst.mkdir(parents=True,exist_ok=False);p=B/'prepared'
    shutil.copy2(p/f'{kind}_masks.npz',dst/'masks.npz');shutil.copy2(p/f'{kind}_geometry.json',dst/'geometry.json')
    if images:shutil.copy2(p/f'{kind}_images.npy',dst/'images.npy')
def main():
    assert not (B/'freeze.json').exists();z=dict(np.load(B/'prepared/truth.npz'))
    controls=B/'controls';controls.mkdir(exist_ok=False);write_prediction(controls/'oracle.npz',z['points'],z['tetra']);write_prediction(controls/'static.npz',np.repeat(z['points'][:1],len(z['points']),axis=0),z['tetra'])
    records={};metrics={}
    for condition,images in [('masks',False),('masks-images',True)]:
        task=B/'tasks'/('cardiac-'+condition);task.mkdir(parents=True,exist_ok=False)
        input_(task/'environment/data','synthetic',images);input_(B/'clinical'/condition,'clinical',images)
        for d in ['tests','solution']:(task/d).mkdir()
        (task/'environment/Dockerfile').write_text(f'FROM python:3.12-slim-bookworm\nRUN pip install --no-cache-dir {PIP}\nWORKDIR /app\nCOPY data /app/data\nRUN mkdir -p /app/answer\n')
        (task/'tests/Dockerfile').write_text(f'FROM python:3.12-slim-bookworm\nRUN pip install --no-cache-dir {PIP}\nCOPY . /verifier/\nRUN mkdir -p /app/answer /tests && cp /verifier/test.sh /tests/test.sh && chmod 755 /tests/test.sh\nWORKDIR /app\nCMD ["/tests/test.sh"]\n')
        (task/'tests/test.sh').write_text('#!/bin/sh\nset -eu\npython /verifier/score.py\n')
        for name in ['geometry.py','score.py']:shutil.copy2(HERE/name,task/'tests'/name)
        input_(task/'tests/data','synthetic',False);shutil.copy2(B/'prepared/truth.npz',task/'tests/truth.npz')
        shutil.copy2(controls/'oracle.npz',task/'solution/prediction.npz');(task/'solution/solve.sh').write_text('#!/bin/sh\nset -eu\ncp /solution/prediction.npz /app/answer/prediction.npz\n')
        toml=(ROOT/'runs/br034-pathological-echo/task/cardiac-adaptation/task.toml').read_text().replace('cardiac-adaptation','cardiac-'+condition).replace('Adapt a dynamic LV reconstruction to a clinical ultrasound and assess function','Construct a deforming mesh from supplied cardiac segmentations')
        (task/'task.toml').write_text(toml)
        conditiontext='Registered ultrasound images.npy is present and may be used together with the masks.' if images else 'No ultrasound image array is supplied; infer a plausible material map from the masks and stated modeling assumptions.'
        instruction='''Build a consistent deforming volumetric mesh from a complete cardiac segmentation sequence, and calculate its finite strain.

CONDITION

Inputs under /app/data:
- masks.npz key masks: boolean (T,Z,Y,X), sampled at voxel centers. The current case contains 30 phases of biventricular myocardial WALL, including inner and outer boundaries. They are binary per-phase segmentations, with no material identities, initial mesh, AHA labels or tracked points.
- geometry.json: origin_xyz_mm, spacing_xyz_mm, shape_tzyx, reference_frame=0, mask_semantics, phase and timestamps_s. World point=origin+spacing*[x,y,z]. All arrays are on this grid. Synthetic phase duration is unknown; do not invent strain rates in seconds.
- Where present, images.npy contains float32 ultrasound (T,Z,Y,X) on exactly this grid. It is image intensity, not blood velocity or reference deformation. Segmentation is already supplied for all frames.

Construct your OWN reference tetrahedral mesh from the first mask, then infer positions through the cycle on that fixed connectivity. Choose a usable resolution and explain it. Ordinary numpy/scipy/scikit-image/meshio/OpenCV/Pillow are installed; other ordinary meshing libraries are permitted. Your reference mesh need not match any hidden source mesh. Every vertex keeps a consistent hypothesized material identity, but consistent indices alone do not establish true tissue correspondence.

Write /app/answer/solve.py with CLI `python solve.py --input DIRECTORY --output DIRECTORY`, run it on the supplied case, and save prediction.npz containing:
- points: (T,N,3) world mm; points[0] is the reference configuration;
- tetra: integer (M,4), fixed connectivity, no duplicate or degenerate cells;
- F and E: (T,M,3,3), deformation gradients and full Green–Lagrange tensors;
- J: (T,M), signed current/reference volume ratios.
F maps reference COLUMN vectors to current column vectors; E=(F.T@F-I)/2. All numerical fields must be finite. Negative J is an inversion even if a renderer hides it. Use fractional strain, not percent. Arrays may use float32 if accurate enough. Include method.md describing geometry, motion assumptions, uncertainty, validations and the distinction between a plausible deformation and measured material motion. Also write assessment.json with mask_semantics, myocardial_strain_supported (boolean), limitations (list), and a short finding. For this synthetic wall, this boolean concerns whether the domain supports a myocardial strain model, not whether its recovered motion is validated.

The executable will be replayed on a second segmentation sequence with different dimensions/frame count and optional images. It may have mask_semantics=lv_cavity: then mesh/deform the cavity for geometric volume/EF checks, but explicitly set myocardial_strain_supported=false and do NOT interpret that mathematical deformation as myocardial strain. No epicardium or tissue tracking is supplied for a cavity. Do not hardcode the current patient's geometry or number of frames. Replay allowance: five minutes, 4 CPUs/8 GB.

The main construction checks are mean full-volume mask Dice>=0.90, mean relative domain-volume error<=5%, zero inverted cells, and F/E/J agreement with independent recomputation within absolute 1e-4. A static or independently remeshed sequence is insufficient. Cell topology must be shared through time. No per-frame realignment is performed by the evaluator.

Material motion and directional strain are separately assessed at independent reference locations using your piecewise affine map, NOT by matching your vertex IDs to the source. Coverage is reported. Research diagnostic targets are >=95% reference-volume coverage, material RMSE<=2 mm, each longitudinal/circumferential/radial strain and regional peak MAE<=5 percentage points, regional peak timing error<=2 frames. These are similarity targets to one simulator; especially without image texture, the input may not identify a unique material map. Material diagnostics do not enter the construction reward. Report unobservable motion and sensitivity rather than presenting smooth strain colors as verified physiology. No etiologic diagnosis or active-force equilibrium is requested.

Source: already curated public STRAUS simulation; the transfer case is clinical EchoXFlow. Public-source training exposure is unknown. All permitted observations are in /app/data. Do not retrieve original moving meshes, reference strain, prior solutions or other workbench outputs. There is no score feedback. Use your time to deliver and validate a runnable artifact; independent geometry and mechanics matter more than polished rendering.
'''.replace('CONDITION',conditiontext)
        (task/'instruction.md').write_text(instruction)
        if not metrics:
            for name in ['oracle','static']:
                print('score control',name,flush=True);metrics[name]=score(controls/f'{name}.npz',task/'environment/data',B/'prepared/truth.npz')
            metrics['nop']=score(B/'absent.npz',task/'environment/data',B/'prepared/truth.npz')
            assert metrics['oracle']['reward']==1 and metrics['oracle']['material']['pass_'],metrics['oracle']
            assert metrics['nop']['reward']==0 and metrics['static']['reward']==0
        records[condition]=dict(task_path=str(task.relative_to(ROOT)),files=hashes(task))
    out=dict(round='BR-035',status='frozen before either Sol attempt',conditions=records,controls=metrics,clinical_files=hashes(B/'clinical'),prepared_files=hashes(B/'prepared'),protocol_sha256=sha(ROOT/'docs/research-rounds/BR-035-segmentation-mechanics.md'),analytic_validation_sha256=sha(B/'analytic-validation.json'),parent_volume_freeze_sha256=sha(ROOT/'runs/br031-cardiac-levels/cardiac-l1v-freeze.json'),preparation= json.loads((B/'preparation.json').read_text()))
    (B/'freeze.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(conditions=list(records),oracle_reward=metrics['oracle']['reward'],static_reward=metrics['static']['reward'])))
if __name__=='__main__':main()
