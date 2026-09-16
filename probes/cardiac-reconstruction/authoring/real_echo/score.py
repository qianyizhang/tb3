"""Artifact contract checks ONLY. No anatomy or reconstruction truth exists."""
import json
from pathlib import Path
import numpy as np

def volumes(points,faces):
    # Center first to limit cancellation; the mesh must be closed.
    p=points-points.mean(axis=1,keepdims=True);a=p[:,faces]
    return np.einsum('tfi,tfi->tf',a[:,:,0],np.cross(a[:,:,1],a[:,:,2])).sum(axis=1)/6000

def score(answer):
    answer=Path(answer)
    result=dict(reward=0,meaning='artifact contract only; never reconstruction accuracy',ground_truth_available=False)
    try:
        z=dict(np.load(answer/'prediction.npz',allow_pickle=False));p=z['points'];f=z['faces'];alt=z['alternative_points']
        assert p.ndim==3 and p.shape[0]==18 and p.shape[2]==3 and 4<=p.shape[1]<=10000,'points shape'
        assert f.ndim==2 and f.shape[1]==3 and 4<=len(f)<=20000 and np.issubdtype(f.dtype,np.integer),'faces shape/type'
        assert f.min()>=0 and f.max()<p.shape[1] and np.isfinite(p).all(),'indices/finite'
        assert alt.ndim==4 and alt.shape[1:]==p.shape and 2<=alt.shape[0]<=5 and np.isfinite(alt).all(),'alternative_points'
        edges=np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]);ordered=np.sort(edges,axis=1)
        keys,inverse,counts=np.unique(ordered,axis=0,return_inverse=True,return_counts=True)
        orient=np.bincount(inverse,weights=np.where(edges[:,0]<edges[:,1],1,-1),minlength=len(keys))
        assert np.all(counts==2) and np.all(orient==0),'closed oriented edges'
        tri=p[:,f];areas=np.linalg.norm(np.cross(tri[:,:,1]-tri[:,:,0],tri[:,:,2]-tri[:,:,0]),axis=2)/2
        assert areas.min()>1e-8,'degenerate faces'
        v=volumes(p,f);av=np.stack([volumes(a,f) for a in alt]);assert np.all(v>0) and np.all(av>0),'positive volumes'
        for fn in ['solve.py','method.md','summary.json']:assert (answer/fn).is_file(),fn
        summary=json.loads((answer/'summary.json').read_text());assert summary['frame_ids']==list(range(1,19)),'frame references'
        report_v=np.asarray(summary['volume_ml']);assert report_v.shape==(18,) and np.allclose(report_v,v,rtol=.001,atol=.01),'reported volumes'
        result.update(reward=1,vertices=p.shape[1],triangles=len(f),closed_oriented_edges=True,
            self_intersection_checked=False,volume_ml=v.tolist(),alternative_volume_ml=av.tolist(),
            displacement_from_first_rms_mm=float(np.sqrt(np.mean(np.sum((p-p[0])**2,axis=-1)))),
            temporal_step_rms_mm=float(np.sqrt(np.mean(np.sum(np.diff(p,axis=0)**2,axis=-1)))),
            first_last_point_gap_rms_mm=float(np.sqrt(np.mean(np.sum((p[-1]-p[0])**2,axis=-1)))),
            min_face_area_mm2=float(areas.min()))
    except Exception as e:result['error']=f'{type(e).__name__}: {e}'
    return result

if __name__=='__main__':
    import os
    r=score('/app/answer');p=Path('/logs/verifier');p.mkdir(parents=True,exist_ok=True)
    (p/'metrics.json').write_text(json.dumps(r,indent=2)+'\n');(p/'reward.txt').write_text(str(r['reward'])+'\n')
    print(json.dumps(r,indent=2))
