"""Match independent physical patches using only the named public payload."""
import argparse
import json
import time
from pathlib import Path
import numpy as np
from scipy.ndimage import gaussian_filter,map_coordinates
from scipy.optimize import minimize


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--data',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True);ap.add_argument('--kind',choices=['2d','3d'],required=True)
    args=ap.parse_args();start=time.time();dim=2 if args.kind=='2d' else 3
    with np.load(args.data/'volume.npz') as z:hu=np.clip(z['hu'],-1000,200).astype(np.float32);a=z['voxel_to_world']
    inv=np.linalg.inv(a[:3,:3]);origin=a[:3,3]
    def mmul(A,B):return np.einsum('ij,jn->in',A,B)
    def sample(vol,points):return map_coordinates(vol,mmul(inv,points-origin[:,None]),order=1,prefilter=False,mode='constant',cval=-1000)
    def loss(target,pred):
        target=target-target.mean();pred=pred-pred.mean()
        return 1-float(np.dot(target,pred)/(np.linalg.norm(target)*np.linalg.norm(pred)+1e-8))
    q=json.loads((args.data/'queries.json').read_text())
    if dim==2:
        view=np.clip(np.load(args.data/'view.npy'),-1000,200).astype(np.float32)
        g=json.loads((args.data/'view.json').read_text());pose=np.array(g['slice_to_world']);spacing=np.array(g['spacing_xy_mm'])
        pixels=np.array(q['pixels_uv']);positions=pose[:3,3]+np.einsum('ij,nj->ni',pose[:3,:2],pixels*spacing)
        basis=pose[:3,:2]
    else:
        with np.load(args.data/'reference_volume.npz') as z:source=np.clip(z['hu'],-1000,200).astype(np.float32);source_a=z['voxel_to_world']
        assert np.array_equal(a,source_a)
        positions=np.array(q['reference_world_mm']);basis=np.eye(3)
    outputs=[];logs=[]
    for qi,position in enumerate(positions):
        point=position.copy();B=basis.copy();stages=[]
        for stage,(half,step,blur) in enumerate([(25,3,1.2),(16,2,.7),(10,1.5,.4)]):
            axes=[np.arange(-half,half+.01,step)]*dim
            local=np.array(np.meshgrid(*axes,indexing='ij')).reshape(dim,-1)
            if dim==2:
                coords=pixels[qi,:,None]+local/spacing[:,None]
                inside=(coords[0]>=0)&(coords[0]<=view.shape[1]-1)&(coords[1]>=0)&(coords[1]<=view.shape[0]-1)
                local=local[:,inside];coords=coords[:,inside]
                target=map_coordinates(gaussian_filter(view,blur),coords[::-1],order=1,prefilter=False)
            else:
                target=sample(gaussian_filter(source,blur),position[:,None]+local)
                # Expiration coverage is cropped: ignore uniform outside-air
                # padding instead of demanding a matching crop in inspiration.
                valid=sample(source,position[:,None]+local)>-999
                target=target[valid];local=local[:,valid]
            vol=gaussian_filter(hu,blur)
            def objective(params):
                P=point+params[:3];L=B+params[3:].reshape(3,dim)/50
                return loss(target,sample(vol,P[:,None]+mmul(L,local)))+.000015*np.sum(params[3:]**2)+.00001*np.sum(params[:3]**2)
            starts=[np.zeros(3+3*dim)]
            if stage==0:
                ranked=[]
                for dx in np.arange(-35,36,7):
                    for dy in np.arange(-35,36,7):
                        for dz in np.arange(-35,36,7):
                            p0=np.r_[[dx,dy,dz],np.zeros(3*dim)];ranked.append((objective(p0),p0))
                ranked.sort(key=lambda z:z[0]);starts=[]
                for _,p0 in ranked:
                    if all(np.linalg.norm(p0[:3]-s[:3])>=10 for s in starts):starts.append(p0)
                    if len(starts)>=6:break
            fits=[minimize(objective,p0,method='Powell',options={'maxiter':65,'xtol':.02,'ftol':1e-5}) for p0 in starts]
            fits.sort(key=lambda r:r.fun);r=fits[0];point+=r.x[:3];B+=r.x[3:].reshape(3,dim)/50
            stages.append({'half_width_mm':half,'loss':float(r.fun),'point':point.tolist(),'candidate_losses':[float(f.fun) for f in fits]})
        outputs.append(point.tolist());logs.append({'query_id':q['query_ids'][qi],'stages':stages})
        print(json.dumps({'query':qi+1,'elapsed_s':time.time()-start,'loss':float(r.fun)}),flush=True)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps({'query_ids':q['query_ids'],'points_world_mm':outputs},indent=2)+'\n')
    args.out.with_suffix('.log.json').write_text(json.dumps({'method':f'Independent {dim}D affine patches with translation multistart','queries':logs,'elapsed_s':time.time()-start},indent=2)+'\n')


if __name__=='__main__':main()
