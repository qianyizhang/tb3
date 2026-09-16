"""Author-only construction. Never copy this directory into an agent image."""
import hashlib
import json
from pathlib import Path
import shutil
import numpy as np
import nibabel as nib
from PIL import Image
from scipy.interpolate import RegularGridInterpolator
from scipy.spatial.transform import Rotation
from reslice import render
from score import score

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT/'runs/br019-registration'
HERE = Path(__file__).resolve().parent

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, indent=2)+'\n')


def main():
    assert not (OUT/'tasks').exists(), 'Do not overwrite a prepared snapshot'
    src=ROOT/'runs/br004-v1/source/s0915'
    receipt=json.loads((src/'source-receipt.json').read_text())
    for filename in ['ct.nii.gz', 'segmentations/heart.nii.gz']:
        h=next(x['sha256'] for x in receipt['files'] if x['member']==f's0915/{filename}')
        assert sha(src/filename)==h
    image=nib.load(src/'ct.nii.gz'); full=np.asarray(image.dataobj)
    a=np.diag([-1.,-1.,1.,1.])@image.affine
    mask=np.asarray(nib.load(src/'segmentations/heart.nii.gz').dataobj)>0
    ijk=np.argwhere(mask); xyz=np.einsum('ij,nj->ni',a[:3,:3],ijk)+a[:3,3]
    centre=xyz.mean(axis=0)
    # Coarse apex-side surface candidate. This is not a clinical apex annotation.
    projection=np.einsum('ij,j->i',xyz,[1.,-.4,-.8])
    apex=xyz[projection>np.quantile(projection,.995)].mean(axis=0)
    long_axis=centre-apex; long_axis/=np.linalg.norm(long_axis)
    u=np.array([1.,0.,0.]);u-=long_axis*np.dot(u,long_axis);u/=np.linalg.norm(u)
    v=-long_axis; n=np.cross(u,v)
    # A private small angulation around the long axis prevents the source mask
    # and deterministic canonical convention from being a published answer.
    u=Rotation.from_rotvec(long_axis*np.deg2rad(17.)).apply(u);n=np.cross(u,v)
    frame=np.column_stack([u,v,n])
    centre_view=centre + u*5.3 + long_axis*4.7
    # Broad axis-aligned thoracic ROI; crop bounds encode no target orientation.
    lo=np.maximum(0,np.floor(ijk.mean(0)-90).astype(int))
    hi=np.minimum(full.shape,lo+180);lo=np.maximum(0,hi-180)
    hu=full[tuple(slice(int(x),int(y)) for x,y in zip(lo,hi))].copy()
    affine=a.copy();affine[:3,3]=a[:3,:3]@lo+a[:3,3]
    spacing=.9
    t=np.eye(4);t[:3,:3]=frame;t[:3,3]=centre_view-frame[:,0]*95.5*spacing-frame[:,1]*95.5*spacing
    full_target=render(hu,affine,t,(192,192),(spacing,spacing))
    # Independently check trilinear interpolation with RegularGridInterpolator.
    rng=np.random.default_rng(1901);uv=np.vstack([rng.integers(0,192,(200,2)),[[0,0],[0,191],[191,0],[191,191]]])
    points=t[:3,3]+np.outer(uv[:,0]*spacing,t[:3,0])+np.outer(uv[:,1]*spacing,t[:3,1])
    indices=np.einsum('ij,nj->ni',np.linalg.inv(affine)[:3,:3],points)+np.linalg.inv(affine)[:3,3]
    assert np.all(indices>=0) and np.all(indices<=np.array(hu.shape)-1), 'No border hints'
    rg=RegularGridInterpolator(tuple(np.arange(s) for s in hu.shape),hu.astype(float))
    independently=np.rint(np.clip((rg(indices)+150)/500,0,1)*255).astype(np.uint8)
    assert np.max(np.abs(independently.astype(int)-full_target[uv[:,1],uv[:,0]].astype(int)))<=1
    records=[]
    for name,box in [('cardiac-r01',(0,0,192,192)),('cardiac-r02',(42,26,170,154))]:
        x0,y0,x1,y1=box; target=full_target[y0:y1,x0:x1].copy()
        pose=t.copy();pose[:3,3]+=spacing*(x0*t[:3,0]+y0*t[:3,1])
        task=OUT/'tasks'/name
        for sub in ['environment/data','tests','solution']:(task/sub).mkdir(parents=True)
        data=task/'environment/data'; np.savez_compressed(data/'volume.npz',hu=hu,voxel_to_lps=affine)
        np.save(data/'target.npy',target,allow_pickle=False);Image.fromarray(target).save(data/'target.png')
        geometry={'shape':list(target.shape),'spacing_xy_mm':[spacing,spacing],
                  'coordinates':'LPS millimetres; +x left, +y posterior, +z superior',
                  'intensity':'8-bit, round(255*clip((trilinear_HU+150)/500,0,1)); no slab or projection'}
        write(data/'image.json',geometry)
        truth={'slice_to_lps':pose.tolist(),'shape':list(target.shape),'spacing_xy_mm':[spacing,spacing]}
        write(task/'tests/truth.json',truth);write(task/'solution/pose.json',{'slice_to_lps':pose.tolist()})
        shutil.copy(HERE/'reslice.py',task/'environment/reslice.py');shutil.copy(HERE/'score.py',task/'tests/score.py')
        shutil.copy(ROOT/'probes/dicom-anatomy-audit/environment/DATA-LICENSE.txt',task/'environment/DATA-LICENSE.txt')
        (task/'environment/SOURCE_NOTICE.md').write_text('CT: Jakob Wasserthal, TotalSegmentator small v2.0.1, CC BY 4.0. Source: https://zenodo.org/records/10047263 . Derived axis-aligned thoracic crop and newly authored oblique image. Source intensities are preserved; the derived image is windowed. This is a geometric research example, not a certified diagnostic view.\n')
        (task/'environment/Dockerfile').write_text('FROM python:3.12-slim-bookworm\nRUN pip install --no-cache-dir numpy==2.2.6 scipy==1.15.3 pillow==11.3.0\nWORKDIR /app\nCOPY data /app/data\nCOPY reslice.py SOURCE_NOTICE.md DATA-LICENSE.txt /app/\nRUN mkdir -p /app/answer\n')
        (task/'tests/Dockerfile').write_text('FROM python:3.12-slim-bookworm\nRUN pip install --no-cache-dir numpy==2.2.6\nCOPY . /verifier/\nRUN mkdir -p /app/answer /tests && cp /verifier/test.sh /tests/test.sh && chmod 755 /tests/test.sh\nWORKDIR /app\nCMD ["/tests/test.sh"]\n')
        (task/'tests/test.sh').write_text('#!/bin/sh\nset -eu\npython /verifier/score.py\n')
        (task/'solution/solve.sh').write_text('#!/bin/sh\nset -eu\nmkdir -p /app/answer\ncp /solution/pose.json /app/answer/pose.json\n')
        for p in [task/'tests/test.sh',task/'solution/solve.sh']:p.chmod(0o755)
        (task/'task.toml').write_text(f'''artifacts = ["/app/answer"]
[task]
name = "terminal-bench/{name}"
description = "Recover the patient-space pose of an oblique cardiac CT section."
authors = [{{name = "Research pilot"}}]
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
        (task/'instruction.md').write_text('''# Recover an oblique cardiac CT slice pose

A thoracic CT crop and an oblique section from the **same acquisition** are in
/app/data. Recover where that image lies in the volume, including its in-plane
position and orientation. The section is oriented along the cardiac apex
region; it is not an axial, coronal or sagittal source slice. It may show a
partial field. Its exact pose and any cropping offset have been lost.

Write /app/answer/pose.json as {"slice_to_lps": [[...],[...],[...],[...]]}.
The 4x4 rigid transform maps [u*sx, v*sy, 0, 1] to homogeneous patient LPS
millimetres, where u is image **column**, v is **row**, (0,0) is the top-left
pixel centre and (sx,sy) comes from image.json. The first two columns are unit
vectors for increasing u and v; the third is their cross product. Last column
is the LPS position of pixel (0,0); bottom row is [0,0,0,1].

Inputs:
- volume.npz: hu[i,j,k] (int16), voxel_to_lps (4x4), mapping voxel centres
  [i,j,k,1] to LPS. +x = patient left, +y = posterior, +z = superior.
- target.npy: uint8 [row,column], identical to target.png, no pose metadata.
- image.json: target dimensions, spacing and intensity convention.

The target is trilinearly interpolated from the supplied HU grid, then rounded
to uint8 using 255*clip((HU+150)/500,0,1). It is a thin plane, not a slab,
maximum-intensity projection or X-ray. The volume's grid spacing is not the
target pixel spacing. All target samples lie inside the volume.

/app/reslice.py is a forward renderer you can use to check any proposed pose:
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
        # Targeted independent acceptance controls before any model attempt.
        controls={'oracle':score({'slice_to_lps':pose.tolist()},truth),'nop':score({},truth)}
        for label,offset in [('translate_2mm',2.),('translate_8mm',8.)]:
            z=pose.copy();z[0,3]+=offset;controls[label]=score({'slice_to_lps':z.tolist()},truth)
        for label,z in [('ras_lps',np.diag([-1.,-1.,1.,1.])@pose),('scale',pose@np.diag([1.1,1,1,1]))]:
            controls[label]=score({'slice_to_lps':z.tolist()},truth)
        z=pose.copy();z[:3,0]*=-1;z[:3,2]*=-1
        z[:3,3]+=pose[:3,0]*(target.shape[1]-1)*spacing
        controls['mirrored_columns']=score({'slice_to_lps':z.tolist()},truth)
        assert [c['reward'] for c in controls.values()]==[1,0,1,0,0,0,0]
        assert not Image.open(data/'target.png').info
        with np.load(data/'volume.npz') as z: assert set(z.files)=={'hu','voxel_to_lps'}
        r={'task':name,'task_path':str(task.relative_to(ROOT)),'public_geometry':geometry,
           'source_ct_sha256':sha(src/'ct.nii.gz'),'controls':controls,
           'files':{str(p.relative_to(task)):sha(p) for p in sorted(task.rglob('*')) if p.is_file()}}
        records.append(r)
    write(OUT/'author/generation.json',{'source':'s0915','apex_candidate_lps':apex.tolist(),
          'whole_heart_center_lps':centre.tolist(),'crop_lo_ijk':lo.tolist(),
          'clinical_status':'apex-side heuristic, not expert adjudicated',
          'independent_interpolation_samples':204,'tasks':records})
    write(OUT/'prepared.json',{'round':'BR-019','tasks':records})
    print(json.dumps({'prepared':[r['task'] for r in records],'source':'s0915','hu_shape':hu.shape}))


if __name__=='__main__':main()
