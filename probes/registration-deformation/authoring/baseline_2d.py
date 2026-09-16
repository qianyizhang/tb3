"""Public single-view baseline: affine image fit then local patch registration."""
import argparse
import json
import time
from pathlib import Path
import numpy as np
from scipy.ndimage import gaussian_filter,map_coordinates
from scipy.optimize import minimize


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--data',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args();start=time.time()
    with np.load(args.data/'volume.npz') as z:hu=np.clip(z['hu'],-1000,200).astype(np.float32);a=z['voxel_to_world']
    view=np.clip(np.load(args.data/'view.npy'),-1000,200).astype(np.float32)
    geometry=json.loads((args.data/'view.json').read_text());pose=np.array(geometry['slice_to_world'])
    spacing=np.array(geometry['spacing_xy_mm']);inv=np.linalg.inv(a[:3,:3]);origin=a[:3,3]
    q=json.loads((args.data/'queries.json').read_text());uv=np.array(q['pixels_uv'])
    centre=(np.array(view.shape[::-1])-1)/2
    base=pose[:3,3]+pose[:3,:2]@(centre*spacing);basis=pose[:3,:2].copy()

    def sample(vol,points):return map_coordinates(vol,inv@(points-origin[:,None]),order=1,prefilter=False,mode='constant',cval=-1000)
    def loss(target,pred):
        target=target-target.mean();pred=pred-pred.mean()
        return 1-float(np.dot(target,pred)/(np.linalg.norm(target)*np.linalg.norm(pred)+1e-8))
    def grid(stride):
        yy,xx=np.mgrid[0:view.shape[0]:stride,0:view.shape[1]:stride]
        return np.array([xx.ravel(),yy.ravel()]),(np.array([xx.ravel(),yy.ravel()])-centre[:,None])*spacing[:,None]

    xy,delta=grid(5);coarse=gaussian_filter(hu,2.);target=gaussian_filter(view,2.)[xy[1],xy[0]]
    choices=[]
    for dx in np.arange(-35,36,7):
        for dy in np.arange(-35,36,7):
            for dz in np.arange(-35,36,7):
                t=np.array([dx,dy,dz]);choices.append((loss(target,sample(coarse,(base+t)[:,None]+basis@delta)),t))
    choices.sort(key=lambda v:v[0]);candidates=[]
    # Basis changes are dimensionless; parameter scaling makes Powell steps comparable.
    def unpack(p):return base+p[:3],basis+p[3:].reshape(3,2)/100
    for _,shift in choices[:8]:
        p=np.r_[shift,np.zeros(6)]
        for blur,stride,maxiter in [(2.,4,70),(1.,2,50)]:
            vol=gaussian_filter(hu,blur);tv=gaussian_filter(view,blur);xy,d=grid(stride);target=tv[xy[1],xy[0]]
            def objective(p):
                b,B=unpack(p);return loss(target,sample(vol,b[:,None]+B@d))+.000002*np.sum(p[3:]**2)
            r=minimize(objective,p,method='Powell',options={'maxiter':maxiter,'xtol':.03,'ftol':1e-5});p=r.x
        candidates.append((float(r.fun),p))
    candidates.sort(key=lambda z:z[0]);objective,p=candidates[0];b,B=unpack(p)
    print(json.dumps({'global_loss':objective,'elapsed_s':time.time()-start}),flush=True)
    answers=[];logs=[]
    for index,pixel in enumerate(uv):
        initial=b+B@((pixel-centre)*spacing);point=initial.copy();local_basis=B.copy();stages=[]
        for half,blur in [(20,1.2),(13,.7),(8,.4)]:
            yy,xx=np.mgrid[-half:half+1:2,-half:half+1:2];local=np.array([xx.ravel(),yy.ravel()])*spacing[:,None]
            coords=pixel[:,None]+np.array([xx.ravel(),yy.ravel()])
            inside=(coords[0]>=0)&(coords[0]<=view.shape[1]-1)&(coords[1]>=0)&(coords[1]<=view.shape[0]-1)
            coords=coords[:,inside];local=local[:,inside]
            target=map_coordinates(gaussian_filter(view,blur),coords[::-1],order=1,prefilter=False)
            vol=gaussian_filter(hu,blur)
            def obj_local(params):
                P=point+params[:3];L=local_basis+params[3:].reshape(3,2)/50
                return loss(target,sample(vol,P[:,None]+L@local))+.00001*np.sum(params[3:]**2)+.00005*np.sum(params[:3]**2)
            starts=[np.zeros(9)]
            if half==20:
                ranked=[]
                for dx in [-8,0,8]:
                    for dy in [-8,0,8]:
                        for dz in [-8,0,8]:
                            p0=np.r_[[dx,dy,dz],np.zeros(6)];ranked.append((obj_local(p0),p0))
                starts=[z[1] for z in sorted(ranked,key=lambda z:z[0])[:3]]
            fits=[minimize(obj_local,p0,method='Powell',options={'maxiter':70,'xtol':.02,'ftol':1e-5}) for p0 in starts]
            r=min(fits,key=lambda z:z.fun);point+=r.x[:3];local_basis+=r.x[3:].reshape(3,2)/50
            stages.append({'half_width_pixels':half,'loss':float(r.fun),'point':point.tolist()})
        answers.append(point.tolist());logs.append({'id':q['query_ids'][index],'initial':initial.tolist(),'stages':stages})
        print(json.dumps({'query':index+1,'point':point.tolist(),'elapsed_s':time.time()-start}),flush=True)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps({'query_ids':q['query_ids'],'points_world_mm':answers},indent=2)+'\n')
    args.out.with_suffix('.log.json').write_text(json.dumps({'method':'Global affine image correlation + multiscale local affine patches','global_loss':objective,'global_centre':b.tolist(),'global_basis':B.tolist(),'queries':logs,'elapsed_s':time.time()-start},indent=2)+'\n')


if __name__=='__main__':main()
