"""Public-input-only multi-start intensity registration; no truth or labels read.

Coarse hypothesis search followed by local least-squares refinement. This is
an author feasibility baseline, not supplied to the benchmark agent.
"""
import argparse
import json
from pathlib import Path
import time
import numpy as np
from scipy.ndimage import gaussian_filter, map_coordinates
from scipy.optimize import minimize, least_squares
from scipy.spatial.transform import Rotation


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--data',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True);ap.add_argument('--starts',type=int,default=64)
    args=ap.parse_args(); started=time.monotonic()
    with np.load(args.data/'volume.npz') as z: hu=z['hu'].astype(np.float32); a=z['voxel_to_lps']
    target=np.load(args.data/'target.npy').astype(float)
    spec=json.loads((args.data/'image.json').read_text());sx,sy=spec['spacing_xy_mm'];h,w=target.shape
    inv=np.linalg.inv(a); centre=a[:3,:3]@((np.array(hu.shape)-1)/2)+a[:3,3]
    # Start only from the physical centre of the supplied volume. No anatomical
    # mask, target transform, generator seed or source subject ID is used.
    rng=np.random.default_rng(81173)
    frames=list(Rotation.create_group('O').as_matrix())
    frames+=list(Rotation.random(max(0,args.starts-len(frames)),random_state=rng).as_matrix())
    stages=[(gaussian_filter(hu,2.),gaussian_filter(target,3.3),6),
            (gaussian_filter(hu,.7),gaussian_filter(target,1.2),3),(hu,target,1)]

    def objective_factory(frame, stage, residual=False):
        vol,img,step=stages[stage]
        yy,xx=np.mgrid[0:h:step,0:w:step]
        coords=np.array([(xx.ravel()-(w-1)/2)*sx,(yy.ravel()-(h-1)/2)*sy,np.zeros(xx.size)])
        truth=img[yy,xx].ravel()/255.
        truth0=truth-truth.mean();truthnorm=np.linalg.norm(truth0)
        def f(p):
            r=Rotation.from_rotvec(p[3:]).as_matrix()@frame
            lps=np.einsum('ij,jn->in',r,coords)+(centre+p[:3])[:,None]
            vox=np.einsum('ij,jn->in',inv[:3,:3],lps)+inv[:3,3,None]
            samples=map_coordinates(vol,vox,order=1,mode='constant',cval=-1024.,prefilter=False)
            values=np.clip((samples+150)/500,0,1).astype(float)
            if residual:return values-truth
            v0=values-values.mean()
            return 1.-float(np.dot(v0,truth0)/(np.linalg.norm(v0)*truthnorm+1e-10))
        return f

    candidates=[]
    for i,frame in enumerate(frames[:args.starts]):
        f=objective_factory(frame,0)
        fit=minimize(f,np.zeros(6),method='Powell',bounds=[(-65,65)]*3+[(-.65,.65)]*3,
                     options={'maxiter':60,'ftol':.00015,'xtol':.001})
        candidates.append((float(fit.fun),frame,fit.x))
        if (i+1)%8==0:print(json.dumps({'stage':'coarse','starts':i+1,'best_ncc':1-min(c[0] for c in candidates),'seconds':time.monotonic()-started}),flush=True)
    candidates.sort(key=lambda x:x[0]);refined=[]
    for _,frame,p in candidates[:8]:
        f=objective_factory(frame,1)
        fit=minimize(f,p,method='Powell',options={'maxiter':120,'ftol':1e-7,'xtol':1e-5})
        refined.append((float(fit.fun),frame,fit.x))
    refined.sort(key=lambda x:x[0]);value,frame,p=refined[0]
    # Avoid finite-difference precision issues in float32 sampling: use explicit
    # physical/angular differences with stable 1e-3 parameter increments.
    f=objective_factory(frame,2,True)
    def jac(x):
        y=f(x);columns=[]
        for k in range(6):
            step=.005 if k<3 else .0001
            z=x.copy();z[k]+=step;columns.append((f(z)-y)/step)
        return np.array(columns).T
    final=least_squares(f,p,jac=jac,max_nfev=100,xtol=1e-9,ftol=1e-9,gtol=1e-9)
    p=final.x;r=Rotation.from_rotvec(p[3:]).as_matrix()@frame
    t=np.eye(4);t[:3,:3]=r;t[:3,3]=centre+p[:3]-r[:,0]*(w-1)*sx/2-r[:,1]*(h-1)*sy/2
    args.out.parent.mkdir(parents=True,exist_ok=True)
    answer={'slice_to_lps':t.tolist()};args.out.write_text(json.dumps(answer,indent=2)+'\n')
    evidence={'public_data':str(args.data),'starts':len(candidates),'seconds':time.monotonic()-started,
              'ncc':1-objective_factory(frame,2)(p),'pixel_rmse_255':float(np.sqrt(np.mean(f(p)**2))*255),
              'initialization':'volume physical centre, cube rotation group and independent random rotations',
              'coarse_best_ncc':1-candidates[0][0],'medium_best_ncc':1-value}
    args.out.with_suffix('.metrics.json').write_text(json.dumps(evidence,indent=2)+'\n');print(json.dumps(evidence),flush=True)


if __name__=='__main__':main()
