"""Post-outcome discrepancy review; never changes tasks, grades or thresholds."""
import json
from pathlib import Path
import re
import nibabel as nib
import numpy as np
from scipy import ndimage as ndi
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'runs/br026-vessel-repair'

def main():
    results=json.loads((BASE/'results.json').read_text())
    row=next(x for x in results['rows'] if x['task']=='vessel-v02' and x['phase']=='terra-high')
    task=BASE/'tasks/vessel-v02'
    ni=nib.load(task/'environment/data/image.nii.gz');im=ni.get_fdata()
    m=nib.load(task/'environment/data/proposed_mask.nii.gz').get_fdata()>0
    out=nib.load(ROOT/row['answer_path']).get_fdata()>0
    add=out&~m;pts=np.argwhere(add);spacing=np.linalg.norm(ni.affine[:3,:3],axis=0)
    src=ROOT/'runs/br025-vessel-curation/TopCoW2024_Data_Release'
    nums=list(map(int,re.findall(r'\d+',(src/'roi_loc_labelsTr/topcow_mr_012.txt').read_text())))
    lo=np.maximum(0,np.array(nums[3:])-10)
    full=np.asarray(nib.load(src/'cow_seg_labelsTr/topcow_mr_012.nii.gz').dataobj)
    labels=full[tuple(slice(int(a),int(a+n)) for a,n in zip(lo,m.shape))]
    assert np.array_equal(labels>0,m)
    contacts=ndi.binary_dilation(add,np.ones((3,3,3)))&m
    values,counts=np.unique(labels[contacts],return_counts=True)
    neighborhoods=ndi.binary_dilation(add,iterations=5)&~out
    d=ndi.distance_transform_edt(~m,sampling=spacing)
    receipt={'round':'BR-026','task':'vessel-v02','review_kind':'post_outcome_engineering_discrepancy_review',
        'answer_sha256':row['answer_sha256'],'added_voxels':int(add.sum()),
        'bbox_crop_ijk_inclusive':[pts.min(0).tolist(),pts.max(0).tolist()],
        'reference_labels_contact_voxels':dict(zip(map(str,values),map(int,counts))),
        'reference_contact_label_names':{'12':'L-ACA (left anterior cerebral artery)'},
        'label_name_source':'runs/br025-vessel-curation/TopCoW2024_Data_Release/README.txt',
        'addition_intensity_percentiles_10_50_90':np.percentile(im[add],[10,50,90]).tolist(),
        'nearby_unmasked_intensity_percentiles_10_50_90':np.percentile(im[neighborhoods],[10,50,90]).tolist(),
        'maximum_distance_to_reference_mm':float(d[add].max()),
        'clinical_adjudication':'Not performed. Image signal and reference disagreement alone do not establish that the added structure is anatomically false.',
        'interpretation':'Frozen preservation failure; absent-right-Pcom check passes. Do not describe this as invented Pcom anatomy or a clinically confirmed false bridge.'}
    (ROOT/'docs/evidence/br026-discrepancy-review.json').write_text(json.dumps(receipt,indent=2)+'\n')
    center=np.rint(np.median(pts,axis=0)).astype(int)
    bounds=[(max(0,int(pts[:,k].min())-12),min(m.shape[k],int(pts[:,k].max())+13)) for k in range(3)]
    canvas=Image.new('RGB',(1260,790),(18,22,29));draw=ImageDraw.Draw(canvas)
    draw.text((20,16),'UNCHANGED CASE: 244 voxels added outside the reference',fill='white')
    for axis in range(3):
        sl=[slice(a,b) for a,b in bounds];sl[axis]=int(center[axis]);sl=tuple(sl)
        a=im[sl].T;b=m[sl].T;c=add[sl].T
        g=np.clip((a-70)/430*255,0,255).astype('uint8');rgb=np.repeat(g[...,None],3,2)
        for col in range(3):
            q=rgb.copy()
            if col>0:q[b]=q[b]*.4+np.array([0,210,240])*.6
            if col==2:q[c]=q[c]*.25+np.array([255,90,50])*.75
            tile=Image.fromarray(q).resize((396,206),Image.Resampling.NEAREST)
            x=20+col*415;y=75+axis*230;canvas.paste(tile,(x,y))
            draw.text((x,y-17),f'{["Image","Original = reference","Terra (orange additions)"][col]} | axis {axis} = {center[axis]}',fill='white')
    draw.text((20,770),'Engineering disagreement review; no independent clinical adjudication.',fill='white')
    canvas.save(BASE/'terra-unchanged-result.png')
    print(json.dumps(receipt,indent=2))

if __name__=='__main__':main()
