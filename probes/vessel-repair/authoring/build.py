"""Author-only source audit and disclosed synthetic-gap fixture construction."""
import hashlib
import heapq
import itertools
import json
from pathlib import Path
import re
import shutil
import nibabel as nib
import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from score import score_array, LIMITS, CONN

ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'runs/br026-vessel-repair'
SOURCE=ROOT/'runs/br025-vessel-curation'
HERE=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2)+'\n')
def save(p,a,affine):
    img=nib.Nifti1Image(a,affine);img.set_qform(affine,code=1);img.set_sform(affine,code=1)
    nib.save(img,p)

def central_path(mask, spacing, endpoints):
    """Independent mediality-weighted path in the reference voxel annotation."""
    points=np.argwhere(mask); index={tuple(v):i for i,v in enumerate(points)}
    ends=[int(np.argmin(np.sum(((points-v)*spacing)**2,axis=1))) for v in endpoints]
    radii=ndi.distance_transform_edt(mask,sampling=spacing)
    offsets=[np.array(o) for o in itertools.product([-1,0,1],repeat=3) if any(o)]
    distances=np.full(len(points),np.inf); prev=np.full(len(points),-1,dtype=int)
    distances[ends[0]]=0; queue=[(0.,ends[0])]
    while queue:
        distance,i=heapq.heappop(queue)
        if distance!=distances[i]:continue
        if i==ends[1]:break
        v=points[i]
        for off in offsets:
            j=index.get(tuple(v+off))
            if j is None:continue
            cost=np.linalg.norm(off*spacing)/(.1+min(radii[tuple(v)],radii[tuple(points[j])]))
            new=distance+cost
            if new<distances[j]:distances[j]=new;prev[j]=i;heapq.heappush(queue,(new,j))
    assert np.isfinite(distances[ends[1]])
    ids=[ends[1]]
    while ids[-1]!=ends[0]:ids.append(int(prev[ids[-1]]))
    return points[ids[::-1]]

def main():
    assert not (BASE/'tasks').exists(), 'Never overwrite a prepared task'
    receipt=json.loads((SOURCE/'download-manifest.json').read_text())
    for e in receipt:assert sha(SOURCE/e['local_path'])==e['sha256']
    records=[]
    for name,pid,defect in [('vessel-v01','007',True),('vessel-v02','012',False)]:
        src=SOURCE/'TopCoW2024_Data_Release'
        image=nib.load(src/'imagesTr'/f'topcow_mr_{pid}_0000.nii.gz')
        label=nib.load(src/'cow_seg_labelsTr'/f'topcow_mr_{pid}.nii.gz')
        full=np.asarray(image.dataobj); full_labels=np.asarray(label.dataobj)
        assert image.shape==label.shape and np.array_equal(image.affine,label.affine)
        nums=list(map(int,re.findall(r'\d+',(src/'roi_loc_labelsTr'/f'topcow_mr_{pid}.txt').read_text())))
        dims,origin=np.array(nums[:3]),np.array(nums[3:])
        # Same broad CoW box plus native context halo, independent of defect.
        lo=np.maximum(0,origin-10);hi=np.minimum(full.shape,origin+dims+10)
        slices=tuple(slice(int(a),int(b)) for a,b in zip(lo,hi))
        data=full[slices].copy(); labels=full_labels[slices].copy();gt=labels>0
        aff=image.affine.copy();aff[:3,3]=np.einsum('ij,j->i',aff[:3,:3],lo)+aff[:3,3]
        spacing=np.array(image.header.get_zooms()[:3],dtype=float)
        editable=np.zeros(gt.shape,dtype=bool)
        editable[tuple(slice(int(o-l),int(o+n-l)) for o,l,n in zip(origin,lo,dims))]=True
        node=json.loads((SOURCE/'CoW_Centerline_Data/cow_nodes'/f'topcow_mr_{pid}.json').read_text())
        truth=dict(gt=gt,affine=aff,spacing=spacing,editable=editable)
        branches=[]
        for value in [8,9]:
            vessel=labels==value
            if not vessel.any():continue
            coords=np.array([node[str(value)][key][0]['coords'] for key in ['ICA boundary','PCA boundary']])
            inv=np.linalg.inv(aff); vox=np.einsum('ij,nj->ni',inv[:3,:3],coords)+inv[:3,3]
            path=central_path(vessel,spacing,vox)
            i=len(branches)
            truth.update({f'branch_{i}':vessel,f'path_{i}':path,f'anchors_{i}':path[[0,-1]],
                          f'corridor_{i}':ndi.distance_transform_edt(~vessel,sampling=spacing)<=1.2,
                          f'label_{i}':np.array(value)})
            branches.append({'label':value,'voxels':int(vessel.sum()),'path_voxels':len(path)})
        truth['branch_count']=np.array(len(branches))
        absent=0
        for value,parents in [(8,[4,2]),(9,[6,3])]:
            if np.any(labels==value):continue
            a=np.argwhere(labels==parents[0]);b=np.argwhere(labels==parents[1])
            distances,ix=cKDTree(a*spacing).query(b*spacing);closest=int(np.argmin(distances))
            ends=np.array([a[ix[closest]],b[closest]])
            length=float(distances[closest]);assert length>1.2
            line=np.unique(np.rint(np.linspace(ends[0],ends[1],int(length/.1)+2)).astype(int),axis=0)
            seed=np.zeros(gt.shape,dtype=bool);seed[tuple(line.T)]=True
            corridor=ndi.distance_transform_edt(~seed,sampling=spacing)<=2.
            truth.update({f'absent_corridor_{absent}':corridor,f'absent_anchors_{absent}':ends,
                          f'absent_label_{absent}':np.array(value),f'absent_line_{absent}':line})
            absent+=1
        truth['absent_count']=np.array(absent)
        original=gt.copy();repair=np.zeros(gt.shape,dtype=bool)
        generation={'kind':'unchanged_reference','source':pid}
        if defect:
            path=truth['path_0'];mid=path[len(path)//2]
            ijk=np.indices(gt.shape).transpose(1,2,3,0)
            distance=np.linalg.norm((ijk-mid)*spacing,axis=-1)
            deleted=(distance<=1.8)&(labels==8)
            assert deleted.any() and np.all(editable[deleted])
            original[deleted]=False;repair=(distance<=3.)&editable
            vessel_values=data[deleted].astype(float)
            ring=(distance>1.8)&(distance<3.)&~gt
            background=data[ring].astype(float)
            generation.update(kind='synthetic_spherical_gap',gap_radius_mm=1.8,
                repair_score_radius_mm=3.,center_ijk=mid.tolist(),
                deleted_voxels=int(deleted.sum()),deleted_mm3=float(deleted.sum()*np.prod(spacing)),
                source_signal={'vessel_median':float(np.median(vessel_values)),
                'background_median':float(np.median(background)),
                'vessel_p10':float(np.percentile(vessel_values,10)),
                'background_p90':float(np.percentile(background,90))})
        truth['original']=original;truth['repair_zone']=repair
        task=BASE/'tasks'/name
        for sub in ['environment/data','tests','solution']:(task/sub).mkdir(parents=True)
        dest=task/'environment/data'
        # Preserve the source's stored samples AND scale/intercept exactly.
        raw=np.asarray(image.dataobj.get_unscaled())[slices].copy()
        native=nib.Nifti1Image(raw,aff)
        native.set_qform(aff,code=1);native.set_sform(aff,code=1)
        native.header.set_slope_inter(image.dataobj.slope,image.dataobj.inter)
        nib.save(native,dest/'image.nii.gz')
        assert np.array_equal(np.asarray(nib.load(dest/'image.nii.gz').dataobj),data)
        save(dest/'proposed_mask.nii.gz',original.astype(np.uint8),aff)
        save(dest/'editable_region.nii.gz',editable.astype(np.uint8),aff)
        np.savez_compressed(task/'tests/truth.npz',**truth)
        save(task/'solution/reference.nii.gz',gt.astype(np.uint8),aff)
        shutil.copy(HERE/'score.py',task/'tests/score.py')
        shutil.copy(src/'License.txt',task/'environment/DATA-LICENSE.txt')
        notice='Image/reference source: TopCoW, Yang et al., https://zenodo.org/records/15692630 . Local research crop from a real MRA. The proposed mask may contain an authored connectivity defect or may be unchanged. Image intensities are unmodified. These are annotation-backed engineering examples, not independently adjudicated clinical diagnoses. Commercial use requires owner permission; see DATA-LICENSE.txt.\n'
        (task/'environment/SOURCE_NOTICE.md').write_text(notice)
        requirements='numpy==2.2.6 scipy==1.15.3 nibabel==5.3.2 pillow==11.3.0 scikit-image==0.25.2'
        (task/'environment/Dockerfile').write_text(f'FROM python:3.12-slim-bookworm\nRUN pip install --no-cache-dir {requirements}\nWORKDIR /app\nCOPY data /app/data\nCOPY SOURCE_NOTICE.md DATA-LICENSE.txt /app/\nRUN mkdir -p /app/answer\n')
        (task/'tests/Dockerfile').write_text(f'FROM python:3.12-slim-bookworm\nRUN pip install --no-cache-dir {requirements}\nCOPY . /verifier/\nRUN mkdir -p /app/answer /tests && cp /verifier/test.sh /tests/test.sh && chmod 755 /tests/test.sh\nWORKDIR /app\nCMD ["/tests/test.sh"]\n')
        (task/'tests/test.sh').write_text('#!/bin/sh\nset -eu\npython /verifier/score.py\n')
        (task/'solution/solve.sh').write_text('#!/bin/sh\nset -eu\nmkdir -p /app/answer\ncp /solution/reference.nii.gz /app/answer/corrected_mask.nii.gz\n')
        for f in ['tests/test.sh','solution/solve.sh']:(task/f).chmod(0o755)
        (task/'task.toml').write_text(f'''artifacts = ["/app/answer"]
[task]
name = "terminal-bench/{name}"
description = "Repair or preserve vessel connectivity using one MRA region."
authors = [{{name = "Research pilot"}}]
[metadata]
author_name = "Research pilot"
author_email = "probe@example.invalid"
category = "Data Science"
tags = ["mra", "segmentation", "topology"]
[verifier]
timeout_sec = 120.0
environment_mode = "separate"
[agent]
timeout_sec = 1800.0
[environment]
build_timeout_sec = 600.0
cpus = 2
memory_mb = 4096
storage_mb = 10240
gpus = 0
network_mode = "public"
''')
        shutil.copy(HERE/'instruction.md',task/'instruction.md')
        controls={'reference':score_array(gt,aff,truth),'unchanged_delivered':score_array(original,aff,truth)}
        bad=gt.copy();bad[editable]=False;controls['erase_review_region']=score_array(bad,aff,truth)
        bad=ndi.binary_closing(gt,structure=ndi.generate_binary_structure(3,1),iterations=6)
        bad[~editable]=gt[~editable];controls['broad_closing']=score_array(bad,aff,truth)
        bad=gt.copy();bad[np.isin(labels,[8,9])]=False;controls['remove_pcoms']=score_array(bad,aff,truth)
        if absent:
            bad=gt.copy()
            for i in range(absent):bad[tuple(truth[f'absent_line_{i}'].T)]=True
            controls['one_voxel_absent_bridge']=score_array(bad,aff,truth)
        if defect:
            bad=original.copy();bad[tuple(truth['path_0'].T)]=True
            controls['one_voxel_centerline_repair']=score_array(bad,aff,truth)
            bad=gt.copy();bad[(labels==9)&editable]=False
            controls['repair_plus_other_branch_deletion']=score_array(bad,aff,truth)
            # A non-identical acceptable repair: retain the medial bulk of the
            # true gap, but omit a small deterministic sample of boundary voxels.
            good=gt.copy();boundary=deleted & (ndi.distance_transform_edt(labels==8,sampling=spacing)<.4)
            vox=np.argwhere(boundary)[::6];good[tuple(vox.T)]=False
            controls['nonidentical_boundary_repair']=score_array(good,aff,truth)
            save(BASE/f'{name}-acceptable.nii.gz',good.astype(np.uint8),aff)
        expected={k:0 for k in controls};expected['reference']=1
        expected['unchanged_delivered']=int(not defect)
        if defect:expected['nonidentical_boundary_repair']=1
        for k,v in expected.items():assert controls[k]['reward']==v,(name,k,controls[k])
        r=dict(task=name,task_path=str(task.relative_to(ROOT)),shape=list(data.shape),spacing_mm=spacing.tolist(),
               source=pid,generation=generation,branches=branches,controls=controls,
               public_image_bytes=(dest/'image.nii.gz').stat().st_size,
               public_mask_bytes=(dest/'proposed_mask.nii.gz').stat().st_size)
        records.append(r);print(json.dumps({'task':name,'generation':generation,'controls':{k:v['reward'] for k,v in controls.items()}}),flush=True)
    write(BASE/'prepared.json',{'round':'BR-026','limits':LIMITS,'tasks':records})

if __name__=='__main__':main()
