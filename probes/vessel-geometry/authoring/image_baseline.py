"""Fixed public-input image/mediality baseline, designed after author source review.

No private mask or reference path is read during execution. This is a development
baseline, not a blinded discovery claim. Constants are fixed before its first score.
"""
from pathlib import Path
import hashlib,json,time,sys
import numpy as np
import nibabel as nib
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from skimage.graph import MCP_Geometric
from geometry import transform,resample_path
from build_geometry import generate_outputs

ROOT=Path(__file__).resolve().parents[3];B=ROOT/'runs/br030-vessel-geometry/geometry'

def main():
    mask_only='--mask-only' in sys.argv
    start=time.perf_counter();public=B/'input';out=B/('mask-only-baseline' if mask_only else 'image-baseline');assert not out.exists()
    ni=nib.load(public/'image.nii.gz');image=np.asarray(ni.dataobj);aff=ni.affine;sp=nib.affines.voxel_sizes(aff)
    mask=np.asarray(nib.load(public/'proposed_mask.nii.gz').dataobj)>0
    edit=np.asarray(nib.load(public/'editable_region.nii.gz').dataobj)>0
    req=json.loads((public/'request.json').read_text())
    # Matched contrast: remove intensity evidence only from repair/trace costs.
    # CPR still samples the real image, to isolate upstream geometry effects.
    signal=np.ones(mask.shape,bool) if mask_only else image>=120
    candidate=mask|(signal&edit)
    rad=ndi.distance_transform_edt(candidate,sampling=sp)
    cost=np.full(mask.shape,np.inf,dtype='float32');cost[candidate]=1/(.2+rad[candidate]);cost[candidate&~mask]*=4
    vox=np.argwhere(mask);tree=cKDTree(transform(vox,aff));ends=np.array([req['start_ras_mm'],req['end_ras_mm']]);idx=tree.query(ends)[1];a,z=vox[idx]
    solver=MCP_Geometric(cost,fully_connected=True,sampling=tuple(sp))
    costs,_=solver.find_costs([tuple(a)],[tuple(z)]);assert np.isfinite(costs[tuple(z)])
    path=np.array(solver.traceback(tuple(z)));world=transform(path,aff)
    seed=np.zeros(mask.shape,bool);seed[tuple(path.T)]=True
    near=ndi.distance_transform_edt(~seed,sampling=sp)<=.85
    repaired=mask|(signal&edit&near)
    # Trace the medial path again within the resulting segmentation.
    r=ndi.distance_transform_edt(repaired,sampling=sp);cost2=np.full(mask.shape,np.inf,dtype='float32');cost2[repaired]=1/(.2+r[repaired])
    solver2=MCP_Geometric(cost2,fully_connected=True,sampling=tuple(sp));dist,_=solver2.find_costs([tuple(a)],[tuple(z)])
    path2=transform(np.array(solver2.traceback(tuple(z))),aff)
    q,s=resample_path(path2,.5,.6)
    result=generate_outputs(out,repaired,aff,image,q)
    result.update(seconds=time.perf_counter()-start,added_voxels=int((repaired&~mask).sum()),
                  mask_only_repair_trace=mask_only,
                  parameters={'HU_threshold':120,'outside_mask_cost_multiplier':4,'repair_radius_mm':.85,'mediality_offset_mm':.2},
                  input_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(public.iterdir()) if p.is_file()},
                  provenance='Fixed algorithm, public inputs only at execution; designed after author reference review, no claim of blinded baseline development.')
    (out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
