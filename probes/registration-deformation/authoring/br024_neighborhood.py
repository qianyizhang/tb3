"""Fixed public-only dense-neighborhood rescue; entrypoint /app/data -> /output."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
import numpy as np
from scipy.ndimage import gaussian_filter, map_coordinates
from scipy.optimize import minimize


def main():
    start=time.time();data=Path('/app/data');out=Path('/output');out.mkdir(exist_ok=True)
    q=json.loads((data/'queries.json').read_text());uv=np.array(q['pixels_uv'])
    view=np.clip(np.load(data/'view.npy'),-1000,200).astype(np.float32)
    grid=[]
    for v in np.arange(8,view.shape[0]-8,10):
        for u in np.arange(8,view.shape[1]-8,10):
            if np.min(np.linalg.norm(uv-[u,v],axis=1))>36:continue
            if np.std(view[v-8:v+9,u-8:u+9])<20:continue
            grid.append([int(u),int(v)])
    alluv=np.vstack([uv,np.array(grid)])
    work=Path('/tmp/neighborhood-public');work.mkdir(exist_ok=False)
    for p in data.iterdir():
        if p.name!='queries.json':(work/p.name).symlink_to(p)
    ids=q['query_ids']+[f'node{i:04d}' for i in range(len(grid))]
    (work/'queries.json').write_text(json.dumps({'query_ids':ids,'pixels_uv':alluv.tolist()}))
    subprocess.run([sys.executable,'/baseline.py','--data',str(work),'--out',str(out/'dense.json'),'--kind','2d'],check=True)
    dense=np.array(json.loads((out/'dense.json').read_text())['points_world_mm'])
    logs=json.loads((out/'dense.log.json').read_text())['queries']
    losses=np.array([r['stages'][-1]['loss'] for r in logs])
    geometry=json.loads((data/'view.json').read_text());pose=np.array(geometry['slice_to_world'])
    spacing=np.array(geometry['spacing_xy_mm']);basis=pose[:3,:2]
    nominal=pose[:3,3]+(alluv*spacing)@basis.T;displacements=dense-nominal
    with np.load(data/'volume.npz') as z:
        volume=np.clip(z['hu'],-1000,200).astype(np.float32);a=z['voxel_to_world']
    inv=np.linalg.inv(a[:3,:3]);origin=a[:3,3]
    smoothed=[gaussian_filter(volume,b) for b in [.4,.7,1.2]]
    views=[gaussian_filter(view,b) for b in [.4,.7,1.2]]
    results=[];records=[]
    for i,pixel in enumerate(uv):
        delta=alluv[len(uv):]-pixel;dist=np.linalg.norm(delta,axis=1);sel=dist<=36
        x=np.column_stack([np.ones(sel.sum()),delta[sel]*spacing/25])
        y=displacements[len(uv):][sel]
        weights=np.exp(-.5*(dist[sel]/20)**2)*np.clip(1-losses[len(uv):][sel],.05,1)**2
        robust=np.ones(len(y));coef=np.zeros((3,3))
        if len(y)<6:
            results.append(dense[i]);records.append({'query_id':ids[i],'action':'insufficient_neighborhood','nodes':len(y)});continue
        for _ in range(8):
            w=weights*robust
            coef=np.linalg.solve(x.T@(x*w[:,None])+np.diag([1e-4,.1,.1]),x.T@(y*w[:,None]))
            residual=np.linalg.norm(y-x@coef,axis=1);robust=1/np.sqrt(1+(residual/3)**2)
        prediction=nominal[i]+coef[0];difference=float(np.linalg.norm(prediction-dense[i]))
        record={'query_id':ids[i],'nodes':len(y),'baseline':dense[i].tolist(),'prediction':prediction.tolist(),'baseline_prediction_distance_mm':difference}
        if difference<=5:
            point=dense[i];record['action']='keep_consistent_baseline'
        else:
            local_basis=basis+coef[1:].T/25
            patches=[]
            for k,(half,step,weight) in enumerate([(10,1.5,.4),(16,2,.35),(25,3,.25)]):
                axis=np.arange(-half,half+.01,step);local=np.array(np.meshgrid(axis,axis,indexing='ij')).reshape(2,-1)
                coords=pixel[:,None]+local/spacing[:,None]
                inside=(coords[0]>=0)&(coords[0]<=view.shape[1]-1)&(coords[1]>=0)&(coords[1]<=view.shape[0]-1)
                local=local[:,inside];coords=coords[:,inside]
                target=map_coordinates(views[k],coords[::-1],order=1,prefilter=False);target-=target.mean()
                patches.append((local,target,np.linalg.norm(target),weight,smoothed[k]))
            def objective(offset):
                value=0.
                for local,target,norm,weight,vol in patches:
                    world=(prediction+offset)[:,None]+local_basis@local
                    coords=inv@(world-origin[:,None]);pred=map_coordinates(vol,coords,order=1,prefilter=False,mode='constant',cval=-1000);pred-=pred.mean()
                    value+=weight*(1-float(target@pred/(norm*np.linalg.norm(pred)+1e-8)))
                return value
            fit=minimize(objective,np.zeros(3),method='Powell',bounds=[(-3,3)]*3,options={'maxiter':65,'xtol':.02,'ftol':1e-5})
            point=prediction+fit.x;record.update(action='neighborhood_bounded_refinement',offset=fit.x.tolist(),loss=float(fit.fun))
        results.append(point);records.append(record)
    (out/'points.json').write_text(json.dumps({'query_ids':q['query_ids'],'points_world_mm':np.array(results).tolist()},indent=2)+'\n')
    (out/'neighborhood.log.json').write_text(json.dumps({'method':'fixed robust local displacement fit','grid_count':len(grid),'elapsed_seconds':time.time()-start,'queries':records},indent=2)+'\n')


if __name__=='__main__':main()
