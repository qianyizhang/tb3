"""Geometry, observed/private sections, material motion and mechanics score separately."""
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from scipy.spatial import cKDTree
from kinematics import fields

EDGES=np.array([[0,1],[0,2],[0,3],[1,2],[1,3],[2,3]])
LIMITS=dict(observed_dice=.90,unseen_dice=.85,surface_mean_mm=2.,surface_p95_mm=5.,
            tissue_volume_error_pct=5.,material_rmse_mm=2.,strain_mae_pp=5.,
            peak_mae_pp=5.,timing_mean_frames=2.)

def boundary(tet):
    faces=np.concatenate([tet[:,j] for j in [[0,1,2],[0,1,3],[0,2,3],[1,2,3]]])
    _,idx,count=np.unique(np.sort(faces,axis=1),axis=0,return_index=True,return_counts=True)
    return faces[idx[count==1]]

def section_mask(points,tetra,plane,size=192,spacing=.75):
    u,v,o=np.array(plane['u']),np.array(plane['v']),np.array(plane['origin'])
    normal=np.cross(u,v);dist=(points-o)@normal
    ds=dist[tetra];selected=tetra[(ds.min(1)<=0)&(ds.max(1)>=0)]
    if not len(selected):return np.zeros((size,size),bool)
    xyz=points[selected];s=dist[selected]
    left,right=s[:,EDGES[:,0]],s[:,EDGES[:,1]]
    crosses=(left*right<=0)&(abs(left-right)>1e-12)
    alpha=np.divide(left,left-right,out=np.zeros_like(left),where=abs(left-right)>1e-12)
    positions=xyz[:,EDGES[:,0]]+alpha[:,:,None]*(xyz[:,EDGES[:,1]]-xyz[:,EDGES[:,0]])
    projected=np.stack([(positions-o)@u,(positions-o)@v],axis=-1)/spacing+(size-1)/2
    im=Image.new('1',(size,size));draw=ImageDraw.Draw(im)
    for xy,keep in zip(projected,crosses):
        q=xy[keep]
        if len(q)<3:continue
        c=q.mean(0);q=q[np.argsort(np.arctan2(q[:,1]-c[1],q[:,0]-c[0]))]
        draw.polygon([tuple(p) for p in q],fill=1)
    return np.array(im,dtype=bool)

def all_sections(points,tetra,planes):
    return np.array([[section_mask(x,tetra,p) for x in points] for p in planes])

def regional_curves(eng,labels,weights,valid):
    return np.stack([np.average(eng[:,(labels==s)&valid],axis=1,weights=weights[(labels==s)&valid])
                     for s in range(1,18)],axis=1)*100

def geometry_score(points,truth,refmasks,planes):
    ref=truth['points'];tet=truth['tetra'];X=ref[0]
    if points.shape!=ref.shape or not np.isfinite(points).all():
        return dict(reward=0,reason='Expected finite points (30,11370,3), same vertex order')
    initial=float(np.max(np.linalg.norm(points[0]-X,axis=-1)))
    if initial>1e-4:return dict(reward=0,reason='Initial material coordinates changed',initial_max_mm=initial)
    f=fields(X,points,tet,truth['directions'],truth['cell_labels'])
    g=fields(X,ref,tet,truth['directions'],truth['cell_labels'])
    weights=abs(np.linalg.det(X[tet[:,1:]]-X[tet[:,:1]]))/6
    valid=g['valid'];labels=truth['cell_labels'];pointlabels=truth['point_labels']
    error=np.linalg.norm(points-ref,axis=-1)
    face=boundary(tet);verts=np.unique(face)
    surface=[]
    for a,b in zip(points,ref):
        sa=np.concatenate([a[verts],a[face].mean(1)])
        sb=np.concatenate([b[verts],b[face].mean(1)])
        surface.extend([cKDTree(sa).query(sb)[0],cKDTree(sb).query(sa)[0]])
    surface=np.concatenate(surface)
    predicted=all_sections(points,tet,planes)
    intersection=np.sum(predicted&refmasks,axis=(-1,-2))
    denominator=np.sum(predicted,axis=(-1,-2))+np.sum(refmasks,axis=(-1,-2))
    dice=np.divide(2*intersection,denominator,out=np.ones_like(intersection,dtype=float),where=denominator>0)
    strains=100*np.average(abs(f['engineering'][:,valid]-g['engineering'][:,valid]),axis=1,weights=weights[valid]).mean(0)
    curves=regional_curves(f['engineering'],labels,weights,valid)
    reference=regional_curves(g['engineering'],labels,weights,valid)
    peaks=lambda c:np.stack([c[:,:,0].min(0),c[:,:,1].min(0),c[:,:,2].max(0)],axis=1)
    peakerror=np.mean(abs(peaks(curves)-peaks(reference)),axis=0)
    timing=[]
    for d in range(3):
        vals=[]
        for s in range(17):
            r=reference[:,s,d];p=curves[:,s,d]
            idx=int(np.argmin(p) if d<2 else np.argmax(p))
            extremum=r.min() if d<2 else r.max()
            near=np.where(abs(r-extremum)<=.5)[0]
            vals.append(float(np.min(abs(near-idx))))
        timing.append(float(np.mean(vals)))
    volumes=(f['J']*weights).sum(1);refvolumes=(g['J']*weights).sum(1)
    metrics=dict(observed_dice_mean=float(dice[:4].mean()),unseen_dice_mean=float(dice[4:].mean()),
                 plane_dice_mean=dice.mean(1).tolist(),plane_dice_min=dice.min(1).tolist(),
                 surface_sample_mean_mm=float(surface.mean()),surface_sample_p95_mm=float(np.quantile(surface,.95)),
                 tissue_volume_error_pct=float(100*np.mean(abs(volumes/refvolumes-1))),
                 material_rmse_mm=float(np.sqrt(np.mean(error**2))),
                 lv_material_rmse_mm=float(np.sqrt(np.mean(error[:,pointlabels>0]**2))),
                 rv_unassigned_material_rmse_mm=float(np.sqrt(np.mean(error[:,pointlabels==0]**2))),
                 material_error_p95_mm=float(np.quantile(error,.95)),
                 strain_mae_pp=strains.tolist(),regional_peak_mae_pp=peakerror.tolist(),
                 regional_timing_mean_frames=timing,inverted_elements=int(np.sum(f['J']<=0)),
                 J_min=float(f['J'].min()),J_max=float(f['J'].max()),initial_max_mm=initial)
    gates=dict(observed=metrics['observed_dice_mean']>=LIMITS['observed_dice'],
               unseen=metrics['unseen_dice_mean']>=LIMITS['unseen_dice'],
               surface=metrics['surface_sample_mean_mm']<=LIMITS['surface_mean_mm'] and metrics['surface_sample_p95_mm']<=LIMITS['surface_p95_mm'],
               tissue_volume=metrics['tissue_volume_error_pct']<=LIMITS['tissue_volume_error_pct'],
               material_motion=metrics['material_rmse_mm']<=LIMITS['material_rmse_mm'],
               topology=metrics['inverted_elements']==0)
    mechanics=dict(strain=bool(np.all(strains<=LIMITS['strain_mae_pp'])),
                   regional_peak=bool(np.all(peakerror<=LIMITS['peak_mae_pp'])),
                   regional_timing=bool(np.all(np.array(timing)<=LIMITS['timing_mean_frames'])))
    return dict(reward=int(all(gates.values())),deformation_pass=all(gates.values()),
                mechanics_pass=all(mechanics.values()),complete_pass=all(gates.values()) and all(mechanics.values()),
                geometry_gates=gates,mechanics_gates=mechanics,metrics=metrics,
                region_engineering_percent=curves.tolist(),limits=LIMITS)

def score(path,truth,refmasks,planes):
    try:
        with np.load(path,allow_pickle=False) as z:points=z['points']
        return geometry_score(points,truth,refmasks,planes)
    except Exception as e:return dict(reward=0,reason=type(e).__name__+': '+str(e)[:200])

if __name__=='__main__':
    base=Path('/verifier')
    r=score(Path('/app/answer/prediction.npz'),dict(np.load(base/'truth.npz')),
            np.load(base/'sections.npz')['masks'],json.loads((base/'planes.json').read_text()))
    p=Path('/logs/verifier');p.mkdir(parents=True,exist_ok=True)
    (p/'metrics.json').write_text(json.dumps(r,indent=2)+'\n')
    (p/'reward.txt').write_text(str(r['reward'])+'\n')
    print(json.dumps({k:v for k,v in r.items() if k!='region_engineering_percent'}))
