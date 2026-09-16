"""Public-input component-gap baselines; no source IDs, labels, graph or truth."""
import argparse
import json
from pathlib import Path
import time
import nibabel as nib
import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree

def repair(data, original, editable, spacing, mode, detector='skeleton'):
    output=original.copy();components,n=ndi.label(original,structure=np.ones((3,3,3)))
    counts=np.bincount(components.ravel());ids=[i for i in range(1,n+1) if counts[i]>=50]
    surfaces={i:np.argwhere((components==i)&~ndi.binary_erosion(components==i)) for i in ids}
    pairs=[]
    for k,i in enumerate(ids):
        a=surfaces[i]; tree=cKDTree(a*spacing)
        for j in ids[k+1:]:
            b=surfaces[j];dist,ix=tree.query(b*spacing);m=int(np.argmin(dist))
            if dist[m]<=4.0:pairs.append((float(dist[m]),a[ix[m]],b[m]))
    endpoint_count=None
    if detector=='skeleton':
        from skimage.morphology import skeletonize
        sk=skeletonize(original,method='lee')
        degrees=ndi.convolve(sk.astype(np.int16),np.ones((3,3,3),dtype=np.int16))-sk
        ends=np.argwhere(sk & (degrees==1) & editable)
        endpoint_count=len(ends);pairs=[]
        for i,a in enumerate(ends):
            for b in ends[i+1:]:
                separation=float(np.linalg.norm((a-b)*spacing))
                if separation<=6.0:pairs.append((separation,a,b))
    notes=[]
    for separation,a,b in sorted(pairs,key=lambda x:x[0]):
        centre=(a+b)/2;radius=separation/2+1.0
        lo=np.maximum(0,np.floor(centre-(radius+1)/spacing).astype(int))
        hi=np.minimum(original.shape,np.ceil(centre+(radius+1)/spacing).astype(int)+1)
        slices=tuple(slice(int(x),int(y)) for x,y in zip(lo,hi))
        ijk=np.indices(tuple(hi-lo)).transpose(1,2,3,0)+lo
        dist=np.linalg.norm((ijk-centre)*spacing,axis=-1)
        zone=(dist<=radius)&editable[slices]
        old=output[slices].copy()
        if mode=='image':
            support=original[slices]&(dist<radius+1)
            threshold=float(np.percentile(data[slices][support],20)*.75)
            proposed=old | ((data[slices]>=threshold)&zone)
        else:
            ext=np.ceil(2./spacing).astype(int)
            grid=np.indices(tuple(ext*2+1)).transpose(1,2,3,0)-ext
            element=np.linalg.norm(grid*spacing,axis=-1)<=2.
            filled=ndi.binary_closing(old,structure=element)
            proposed=old | (filled&zone);threshold=None
        output[slices]=proposed
        notes.append({'separation_mm':separation,'centre_ijk':centre.tolist(),
                      'radius_mm':radius,'intensity_threshold':threshold,
                      'added_voxels':int(np.count_nonzero(proposed&~old))})
    return output,{'large_components':len(ids),'skeleton_endpoints':endpoint_count,'detector':detector,'candidate_pairs':notes}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('data',type=Path);p.add_argument('output',type=Path)
    p.add_argument('--mode',choices=['image','mask'],required=True)
    p.add_argument('--detector',choices=['component','skeleton'],default='skeleton');args=p.parse_args();t=time.monotonic()
    image=nib.load(args.data/'image.nii.gz');mask=nib.load(args.data/'proposed_mask.nii.gz')
    editable=np.asarray(nib.load(args.data/'editable_region.nii.gz').dataobj)>0
    output,details=repair(np.asarray(image.dataobj),np.asarray(mask.dataobj)>0,editable,np.array(image.header.get_zooms()[:3]),args.mode,args.detector)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    nib.save(nib.Nifti1Image(output.astype(np.uint8),mask.affine),args.output)
    details.update(mode=args.mode,seconds=time.monotonic()-t)
    args.output.with_suffix('.json').write_text(json.dumps(details,indent=2)+'\n')
    print(json.dumps(details))
