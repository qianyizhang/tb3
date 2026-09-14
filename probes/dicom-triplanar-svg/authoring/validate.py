"""Original NIfTI geometry supplies truth; actual returned SVG supplies the prediction."""
import argparse
import importlib.util
import json
from pathlib import Path
import sys
import time
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'tests'),str(ROOT/'solution')]
from compare import check_svg
from renderer import render,to_svg

PALETTE={'heart':'#e63946','lung_upper_lobe_left':'#2a9d8f',
         'lung_lower_lobe_left':'#90be6d','lung_upper_lobe_right':'#457b9d',
         'lung_middle_lobe_right':'#f4a261','lung_lower_lobe_right':'#f9c74f'}

def reference(original,affine,request,view,taxonomy):
    # Direct homogeneous transform from the independent source NIfTI volume;
    # no DICOM decoder, CT ordering or reference-renderer sampler is used here.
    n=request['size'];scale=request['pixel_size_mm'];cx,cy,cz=request['center_lps_mm']
    centers=np.arange(n,dtype=float)+.5-n/2
    U,V=np.meshgrid(centers*scale,centers*scale)
    plane=np.ones((4,n*n));plane[:3]=np.array([[cx],[cy],[cz]])
    if view=='axial':plane[0]+=U.ravel();plane[1]+=V.ravel()
    elif view=='coronal':plane[0]+=U.ravel();plane[2]-=V.ravel()
    else:plane[1]+=U.ravel();plane[2]-=V.ravel()
    # Explicit contraction also avoids Accelerate's spurious floating-point
    # status warnings for this tiny-by-wide multiply on the authoring Mac.
    transformed=np.einsum('ij,jk->ik',np.linalg.inv(affine),plane)
    assert np.isfinite(transformed).all()
    loc=np.floor(transformed[:3]+.5).astype(int)
    inside=np.all((loc>=0)&(loc<np.array(original.shape)[:,None]),axis=0)
    labels=np.zeros(n*n,dtype=np.uint8);labels[inside]=original[tuple(loc[:,inside])]
    result=np.zeros_like(labels)
    for index,name in enumerate(request['labels'],1):result[labels==taxonomy[name]]=index
    return result.reshape(n,n)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--scratch',type=Path,required=True);a=ap.parse_args()
    truth=np.load(a.scratch/'svg-truth.npz');volume=truth['labels'];affine=truth['affine']
    taxonomy={v:int(k) for k,v in json.loads((a.scratch/'svg-data/label-list.json').read_text()).items()}
    requests=[]
    for index,target in enumerate(['heart','lung_upper_lobe_left','lung_lower_lobe_right','lung_middle_lobe_right'],1):
        center_idx=np.argwhere(volume==taxonomy[target]).mean(axis=0)
        center=(affine@np.r_[center_idx,1])[:3]
        requests.append(dict(id=f'point-{index}',center_lps_mm=center.tolist(),size=128,
                             pixel_size_mm=3.,labels=PALETTE))
    (ROOT/'environment/requests.json').write_text(json.dumps(requests,indent=2)+'\n')
    (ROOT/'tests/requests.json').write_text(json.dumps(requests,indent=2)+'\n')
    expected={};metrics={};wrong={};started=time.monotonic()
    renders=a.scratch/'svg-renders';renders.mkdir(exist_ok=True)
    for request in requests:
        predicted=render(str(a.scratch/'svg-data/ct'),str(a.scratch/'svg-data/labels.dcm'),request)
        for view in ['axial','coronal','sagittal']:
            key=request['id']+'__'+view
            gt=reference(volume,affine,request,view,taxonomy);expected[key]=gt
            metrics[key]=check_svg(predicted[view],gt,request)
            (renders/(key+'.svg')).write_text(predicted[view])
            for name,bad in [('horizontal_mirror',gt[:,::-1]),('vertical_mirror',gt[::-1]),
                             ('transpose',gt.T),('empty',np.zeros_like(gt))]:
                try:check_svg(to_svg(bad,list(PALETTE.values())),gt,request)
                except AssertionError:wrong.setdefault(name,[]).append(key)
            # An organ's rectangular envelope cannot stand in for its section.
            bad=np.zeros_like(gt)
            for v in np.unique(gt):
                if not v:continue
                yy,xx=np.where(gt==v);bad[yy.min():yy.max()+1,xx.min():xx.max()+1]=v
            try:check_svg(to_svg(bad,list(PALETTE.values())),gt,request)
            except AssertionError:wrong.setdefault('bounding_boxes',[]).append(key)
    np.savez_compressed(ROOT/'tests/expected.npz',**expected)
    assert all(wrong.get(k) for k in ['horizontal_mirror','vertical_mirror','transpose','empty','bounding_boxes'])
    receipt={'views':len(expected),'per_label_metrics':metrics,'rejected_controls':wrong,
             'elapsed_seconds':time.monotonic()-started,
             'truth':'original transformed source NIfTI voxel masks and affine',
             'prediction':'DICOM decoded reference rendered through CairoSVG',
             'model_trials':0}
    print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
