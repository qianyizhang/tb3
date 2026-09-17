"""Post-trial independent reproduction of P03's two reported measurement methods."""
from pathlib import Path
import json
import numpy as np
import nibabel as nib
from scipy.ndimage import gaussian_filter,label
ROOT=Path(__file__).resolve().parents[3];B=ROOT/'runs/br037-longitudinal-reading'
results={r['condition']:r for r in json.loads((B/'results.json').read_text())}
out=[]
for condition in ['p03-neutral','p03-cue']:
    if condition not in results:continue
    r=results[condition];a=r['assessment'];rows=[]
    for v,base,post,center in [('V1',54,57,[388,270,58]),('V2',115,116,[385,301,63])]:
        ni=nib.load(B/'prepared/P03'/f'{v}_S{base:02}.nii.gz')
        load=lambda n:np.asarray(nib.load(B/'prepared/P03'/f'{v}_S{n:02}.nii.gz').dataobj,dtype=np.float32)
        if condition=='p03-neutral':
            sub=gaussian_filter(load(base+1)-load(base),1)
            lo=np.array([330,200,40] if v=='V1' else [330,230,40]);hi=np.array([450,340,85] if v=='V1' else [450,370,90])
            crop=sub[tuple(slice(x,y) for x,y in zip(lo,hi))]
            lab,_=label(crop>=.30*crop.max());seed=np.unravel_index(crop.argmax(),crop.shape);idx=lab[seed];edge=1
            method={'post_phase':1,'threshold_fraction':.30,'gaussian_sigma_voxels':1,'bbox_convention':'voxel edges'}
        else:
            sub=load(post)-load(base);c=np.array(center);lo=c-[30,40,13];hi=c+[31,41,14]
            crop=sub[tuple(slice(x,y) for x,y in zip(lo,hi))]
            lab,_=label(crop>.50*crop.max());idx=lab[tuple(c-lo)];edge=0
            method={'post_phase':post-base,'threshold_fraction':.50,'gaussian_sigma_voxels':0,'bbox_convention':'voxel centers'}
        assert idx>0,'Seed must belong to an enhancing component'
        pts=np.argwhere(lab==idx);dims=(pts.max(0)-pts.min(0)+edge)*np.asarray(ni.header.get_zooms()[:3]);diam=float(dims.max())
        reported=next(m['longest_diameter_mm'] for m in a['comparison']['size_measurements_mm'] if m['visit']==v)
        assert abs(diam-reported)<.06,(condition,v,diam,reported)
        rows.append({'visit':v,'recomputed_mm':diam,'reported_mm':reported,'method':method})
    out.append({'condition':condition,'measurements':rows,'recomputed_percent_change':100*(rows[1]['recomputed_mm']/rows[0]['recomputed_mm']-1)})
(B/'measurement-audit.json').write_text(json.dumps({'posthoc':True,'meaning':'Reproduces model methods, not clinical measurement validation. Different phases, thresholds, smoothing and box conventions confound cue attribution.','conditions':out},indent=2)+'\n')
print(json.dumps(out,indent=2))
