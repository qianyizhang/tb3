"""Author-only BR-020 construction; never available to the solving agent."""
import hashlib
import json
from pathlib import Path
import shutil
import sys
import numpy as np
from PIL import Image
from scipy.interpolate import RegularGridInterpolator
from scipy.spatial.transform import Rotation

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'runs/br020-registration'
LEGACY=ROOT/'probes/registration/authoring'
sys.path.insert(0,str(LEGACY))
from reslice import render
from score import score


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,obj):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,indent=2)+'\n')


def main():
    task=OUT/'tasks/recon-r03'
    assert not task.exists(), 'Never overwrite a prepared or frozen task'
    audit=json.loads((OUT/'author/source-audit.json').read_text())
    assert audit['slice_positions_equal']==139 and audit['blurred_hu_correlation']>.999
    with np.load(OUT/'source/B30f.npz') as z: soft=z['hu'];a=z['voxel_to_lps']
    with np.load(OUT/'source/B50f.npz') as z: sharp=z['hu'];assert np.array_equal(a,z['voxel_to_lps'])
    # Author visual landmark estimates, not expert annotations. Both lie in the
    # cardiac region: apex-side tip and superior medial/base-side heart.
    apex=a[:3,:3]@np.array([318,181,26])+a[:3,3]
    base=a[:3,:3]@np.array([244,234,56])+a[:3,3]
    long=base-apex;long/=np.linalg.norm(long)
    u=np.array([1.,0.,0.]);u-=long*np.dot(u,long);u/=np.linalg.norm(u)
    u=Rotation.from_rotvec(long*np.deg2rad(17)).apply(u);v=-long
    centre=(apex+base)/2+long*20
    pose=np.eye(4);pose[:3,:3]=np.column_stack([u,v,np.cross(u,v)])
    pose[:3,3]=centre-(u+v)*95.5*.9
    target=render(sharp,a,pose,(192,192),(.9,.9))
    matched=render(soft,a,pose,(192,192),(.9,.9))
    lo=np.array([64,64,0]);hi=np.array([448,416,128])
    hu=soft[64:448,64:416,:128].copy();affine=a.copy();affine[:3,3]=a[:3,:3]@lo+a[:3,3]
    # Full image-domain containment, and an independent interpolation check.
    yy,xx=np.indices(target.shape);uv=np.column_stack([xx.ravel(),yy.ravel()])
    points=pose[:3,3]+uv[:,0,None]*.9*u+uv[:,1,None]*.9*v
    indices=np.einsum('ij,nj->ni',np.linalg.inv(a[:3,:3]),points-a[:3,3])
    assert np.all(indices>=lo) and np.all(indices<=hi-1)
    ix=np.r_[np.random.default_rng(2001).choice(len(uv),200,replace=False),0,191,36672,36863]
    rg=RegularGridInterpolator(tuple(np.arange(s) for s in sharp.shape),sharp)
    samples=np.rint(np.clip((rg(indices[ix])+150)/500,0,1)*255).astype(np.uint8)
    assert np.max(np.abs(samples.astype(int)-target.ravel()[ix].astype(int)))<=1
    for sub in ['environment/data','tests','solution']:(task/sub).mkdir(parents=True)
    data=task/'environment/data'
    np.savez_compressed(data/'volume.npz',hu=hu,voxel_to_lps=affine)
    np.save(data/'target.npy',target,allow_pickle=False);Image.fromarray(target).save(data/'target.png')
    geometry={'shape':[192,192],'spacing_xy_mm':[.9,.9],
        'coordinates':'LPS millimetres; +x left, +y posterior, +z superior',
        'intensity':'8-bit round(255*clip((trilinear_HU+150)/500,0,1)); thin plane from a different reconstruction kernel',
        'volume_kernel':'B30f','target_kernel':'B50f'}
    write(data/'image.json',geometry)
    truth={'slice_to_lps':pose.tolist(),'shape':[192,192],'spacing_xy_mm':[.9,.9]}
    write(task/'tests/truth.json',truth);write(task/'solution/pose.json',{'slice_to_lps':pose.tolist()})
    shutil.copy(LEGACY/'reslice.py',task/'environment/reslice.py')
    shutil.copy(LEGACY/'score.py',task/'tests/score.py')
    shutil.copy(OUT/'source/B30f/LICENSE',task/'environment/DATA-LICENSE.txt')
    (task/'environment/SOURCE_NOTICE.md').write_text('CT source: National Lung Screening Trial (NLST), National Cancer Institute, via The Cancer Imaging Archive. Collection: https://www.cancerimagingarchive.net/collection/nlst/ . CC BY 4.0; see DATA-LICENSE.txt and https://www.cancerimagingarchive.net/data-usage-policies-and-restrictions/ . Derived native-grid thoracic crop (B30f) and newly authored windowed oblique section (B50f). No diagnostic certification. Downstream use must retain attribution and the TCIA data-use policy.\n')
    (task/'environment/Dockerfile').write_text('FROM python:3.12-slim-bookworm\nRUN pip install --no-cache-dir numpy==2.2.6 scipy==1.15.3 pillow==11.3.0\nWORKDIR /app\nCOPY data /app/data\nCOPY reslice.py SOURCE_NOTICE.md DATA-LICENSE.txt /app/\nRUN mkdir -p /app/answer\n')
    (task/'tests/Dockerfile').write_text('FROM python:3.12-slim-bookworm\nRUN pip install --no-cache-dir numpy==2.2.6\nCOPY . /verifier/\nRUN mkdir -p /app/answer /tests && cp /verifier/test.sh /tests/test.sh && chmod 755 /tests/test.sh\nWORKDIR /app\nCMD ["/tests/test.sh"]\n')
    (task/'tests/test.sh').write_text('#!/bin/sh\nset -eu\npython /verifier/score.py\n')
    (task/'solution/solve.sh').write_text('#!/bin/sh\nset -eu\nmkdir -p /app/answer\ncp /solution/pose.json /app/answer/pose.json\n')
    for p in [task/'tests/test.sh',task/'solution/solve.sh']:p.chmod(0o755)
    (task/'task.toml').write_text('''artifacts = ["/app/answer"]
[task]
name = "terminal-bench/recon-r03"
description = "Recover an oblique cardiac-region plane across CT reconstruction kernels."
authors = [{name = "Research pilot"}]
[metadata]
author_name = "Research pilot"
author_email = "probe@example.invalid"
category = "Data Science"
tags = ["registration", "ct", "geometry"]
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
    (task/'instruction.md').write_text('''# Recover an oblique cardiac-region CT slice pose

A thoracic CT crop and an oblique cardiac-region section are in /app/data.
They come from two reconstruction kernels of one CT examination, with matching
patient-space geometry: the volume is B30f and the target is B50f. Recover where
the target plane lies, including its in-plane position and orientation. It is
an oblique apex-side section, not an axial, coronal or sagittal source image.
Its exact pose has been lost.

Write /app/answer/pose.json as {"slice_to_lps": [[...],[...],[...],[...]]}.
The 4x4 rigid transform maps [u*sx, v*sy, 0, 1] to homogeneous patient LPS
millimetres, where u is image column, v is row, (0,0) is the top-left pixel
centre and (sx,sy) comes from image.json. Columns 1 and 2 are unit vectors for
increasing u and v; column 3 is their cross product. The last column is the
LPS position of pixel (0,0); the bottom row is [0,0,0,1].

Inputs:
- volume.npz: hu[i,j,k] (int16), voxel_to_lps (4x4), mapping voxel centres
  [i,j,k,1] to LPS. +x = patient left, +y = posterior, +z = superior.
- target.npy: uint8 [row,column], identical to target.png, no pose metadata.
- image.json: target dimensions, spacing, kernels and intensity convention.

The target was trilinearly sampled from the other reconstruction, then rounded
to uint8 using 255*clip((HU+150)/500,0,1). It is a thin plane, not a slab,
maximum-intensity projection or X-ray. All target points lie inside the
supplied volume's coverage. Reconstruction differences mean that rendering
the supplied CT at the correct pose will not exactly reproduce target pixels.
The volume's grid spacing is not the target pixel spacing.

/app/reslice.py renders the supplied B30f volume at a proposed pose:
python /app/reslice.py --pose /app/answer/pose.json --out /app/check.png
Python, NumPy, SciPy and Pillow are installed. You may use any suitable
registration method, other tools or public resources.

Acceptance is geometric: a finite rigid right-handed frame (orthonormality
and determinant tolerance 0.001), RMS point error <=3 mm and maximum <=5 mm
on a 7x7 grid spanning the supplied image, including its corners. Both limits
must pass. Intensity correlation alone is not the acceptance criterion.
Matrix values need not exactly equal the hidden reference.

You have 1800 seconds to complete the task.
''')
    controls={'oracle':score({'slice_to_lps':pose.tolist()},truth),'nop':score({},truth)}
    for name,shift in [('translate_2mm',2),('translate_8mm',8),('boundary_2.99',2.99),('boundary_3.01',3.01)]:
        t=pose.copy();t[0,3]+=shift;controls[name]=score({'slice_to_lps':t.tolist()},truth)
    for name,t in [('ras_lps',np.diag([-1.,-1.,1.,1.])@pose),('scale',pose@np.diag([1.1,1,1,1])),('reflection',pose@np.diag([1,1,-1,1]))]:
        controls[name]=score({'slice_to_lps':t.tolist()},truth)
    assert [c['reward'] for c in controls.values()]==[1,0,1,0,1,0,0,0,0]
    assert not Image.open(data/'target.png').info
    assert np.array_equal(np.asarray(Image.open(data/'target.png')),np.load(data/'target.npy'))
    with np.load(data/'volume.npz') as z:assert set(z.files)=={'hu','voxel_to_lps'}
    control=OUT/'author/matched-data';control.mkdir()
    shutil.copy(data/'volume.npz',control/'volume.npz');shutil.copy(data/'image.json',control/'image.json')
    np.save(control/'target.npy',matched,allow_pickle=False)
    Image.fromarray(matched).save(OUT/'author/true-pose-B30f.png')
    delta=target.astype(float)-matched.astype(float)
    record={'task':'recon-r03','task_path':str(task.relative_to(ROOT)),
        'public_geometry':geometry,'controls':controls,
        'files':{str(p.relative_to(task)):sha(p) for p in sorted(task.rglob('*')) if p.is_file()}}
    write(OUT/'author/generation.json',{'apex_estimate_lps':apex.tolist(),'base_estimate_lps':base.tolist(),
        'clinical_status':'Author visual estimates; not expert-certified cardiac plane',
        'crop_lo_ijk':lo.tolist(),'crop_hi_ijk':hi.tolist(),
        'independent_interpolation_samples':len(ix),'all_target_points_inside_volume':True,
        'true_pose_pixel_rmse':float(np.sqrt(np.mean(delta**2))),
        'true_pose_identical_pixel_fraction':float(np.mean(delta==0)),
        'true_pose_pixel_correlation':float(np.corrcoef(target.ravel(),matched.ravel())[0,1]),
        'true_pose_foreground_pixel_rmse':float(np.sqrt(np.mean(delta[(target>0)&(target<255)]**2)))})
    write(OUT/'prepared.json',{'round':'BR-020','tasks':[record]})
    print((OUT/'author/generation.json').read_text())


if __name__=='__main__':main()
