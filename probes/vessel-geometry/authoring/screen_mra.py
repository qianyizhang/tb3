"""Inspect untouched published-model predictions against branch references."""
from pathlib import Path
import json, sys
import nibabel as nib
import numpy as np
from scipy import ndimage as ndi
from skimage.morphology import skeletonize
from geometry import sample, transform

ROOT=Path(__file__).resolve().parents[3]; BASE=ROOT/'runs/br030-vessel-geometry'
SRC=ROOT/'runs/br025-vessel-curation/TopCoW2024_Data_Release'

def main():
    rows=[]
    for rec in json.loads((BASE/'prediction-receipt.json').read_text())['rows']:
        pid=rec['source']; img=nib.load(ROOT/rec['output']); p=np.asarray(img.dataobj)>0
        full=nib.load(SRC/'cow_seg_labelsTr'/f'topcow_mr_{pid}.nii.gz')
        lo=rec['roi_origin_ijk']; gt=np.asarray(full.dataobj)[tuple(slice(o,o+n) for o,n in zip(lo,p.shape))]
        sp=img.header.get_zooms()[:3]; d=ndi.distance_transform_edt(~p,sampling=sp)
        r={'case':pid,'binary_dice':float(2*np.count_nonzero(p&(gt>0))/(p.sum()+(gt>0).sum())),'branches':[]}
        for lab in [8,9,10]:
            v=gt==lab
            if not v.any():
                r['branches'].append({'label':lab,'reference_present':False}); continue
            sk=skeletonize(v).astype(bool)
            corridor=ndi.distance_transform_edt(~v,sampling=sp)<=1.
            c,n=ndi.label(p&corridor,np.ones((3,3,3)))
            hit=c[sk]; counts=np.bincount(hit); counts[0]=0
            r['branches'].append({'label':lab,'reference_present':True,'reference_voxels':int(v.sum()),
                'predicted_label_voxels':int((np.asarray(img.dataobj)==lab).sum()),
                'binary_recall':float(p[v].mean()),'skeleton_coverage_0p45mm':float((d[sk]<=.45).mean()),
                'max_skeleton_distance_mm':float(d[sk].max()),'skeleton_points':int(sk.sum()),
                'largest_local_component_skeleton_fraction':float(counts.max(initial=0)/sk.sum())})
        rows.append(r)
    out={'method':'single-fold cropped CLAIM development predictions; branch local binary checks','cases':rows}
    (BASE/'mra-screen.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))

if __name__=='__main__':main()
