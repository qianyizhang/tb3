"""Native-frame and source sampling diagnostics, separate from scoring."""
from pathlib import Path
import json
import numpy as np
import nibabel as nib
from scipy.ndimage import map_coordinates
from run_trials import ROOT,B
image=nib.load(B/'tasks/all-vessels/environment/data/image.nii.gz');vol=np.asarray(image.dataobj)
inv=np.linalg.inv(image.affine)
rows=json.loads((B/'results.json').read_text())['runs'];out=[]
for row in rows:
    if row['phase'] in ['oracle','nop'] or not row.get('replay',{}).get('format_valid'):continue
    obj=json.loads((ROOT/row['answer_path']/'centerlines.json').read_text());paths=[]
    for c in obj['centerlines']:
        p=np.asarray(c['points_ras_mm']);vox=np.einsum('ij,nj->ni',inv[:3,:3],p)+inv[:3,3]
        upper=np.array(image.shape)-1
        strict=((vox>=0)&(vox<=upper)).all(axis=1)
        inside=((vox>=-1e-5)&(vox<=upper+1e-5)).all(axis=1)
        sampled=vox.copy();sampled[inside]=np.clip(sampled[inside],0,upper)
        hu=map_coordinates(vol.astype('float32'),sampled.T,order=1,mode='constant',cval=-1024,prefilter=False)
        paths.append({'id':c['id'],'inside_native_image_fraction':float(inside.mean()),'strict_inside_fraction':float(strict.mean()),'boundary_tolerance_voxels':1e-5,'maximum_outside_voxels':float(np.maximum(np.maximum(-vox,vox-upper),0).max()),'median_HU':float(np.median(hu)),'p10_HU':float(np.percentile(hu,10)),'voxel_min':vox.min(0).tolist(),'voxel_max':vox.max(0).tolist()})
    out.append({'phase':row['phase'],'per_polyline':paths,'note':'Source support diagnostics only. Bright intensity is not proof of vessel identity; no new expert adjudication.'})
(B/'native-audit.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps([{'phase':r['phase'],'all_points_inside':all(x['inside_native_image_fraction']==1 for x in r['per_polyline'])} for r in out]))
