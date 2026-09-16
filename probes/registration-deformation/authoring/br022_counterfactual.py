"""Public-only, fixed counterfactual grid. Run in a no-network task container."""
import json
from pathlib import Path
import runpy
import shutil
import time
import numpy as np
from scipy.ndimage import map_coordinates,gaussian_filter
from scipy.optimize import differential_evolution
import SimpleITK as sitk


def rotation(a):
    th=np.linalg.norm(a)
    if th<1e-10:return np.eye(3)
    K=np.array([[0,-a[2],a[1]],[a[2],0,-a[0]],[-a[1],a[0],0]])/th
    return np.eye(3)+np.sin(th)*K+(1-np.cos(th))*K@K


def main():
    start=time.time();dest=Path('/output');dest.mkdir(exist_ok=True)
    d=np.load('/app/data/volume.npz');V=d['hu'];iv=np.linalg.inv(d['voxel_to_world'])
    S=np.load('/app/data/view.npy');j=json.loads(Path('/app/data/view.json').read_text());M=np.array(j['slice_to_world']);sx,sy=j['spacing_xy_mm']
    q=json.loads(Path('/app/data/queries.json').read_text());state=json.loads(Path('/state/stages.json').read_text())
    p=np.array(state['rigid_parameters']);cen=np.array(state['rigid_centre']);R=rotation(p[:3])
    aff=sitk.ReadTransform('/state/aff.tfm');bs=sitk.ReadTransform('/state/bs.tfm')
    # Secondary repair preserves the affine-then-residual construction, while
    # fitting the residual against the image to which it is actually applied.
    shutil.copy('/recovered/reg.py','/tmp/reg.py')
    text=Path('/recovered/reg2d.py').read_text().split('# patch matching')[0]
    old="bsout,R=reg(bs,[4,2,1],500)";assert text.count(old)==1
    Path('/tmp/residual.py').write_text(text.replace(old,"moving=movaff\n"+old))
    recovered=runpy.run_path('/tmp/residual.py');residual=recovered['bsout']
    sitk.WriteTransform(residual,str(dest/'residual-bs.tfm'))
    yy,xx=np.mgrid[-8:8+.01:.8,-8:8+.01:.8];normal=np.cross(R@M[:3,0],R@M[:3,1]);normal/=np.linalg.norm(normal)
    all_rows=[]
    for composition in ['original','direct_bspline','residual_on_affine']:
        def mapped(x):
            b=residual if composition=='residual_on_affine' else bs
            v=b.TransformPoint(tuple(x))
            if composition!='direct_bspline':v=aff.TransformPoint(v)
            W=(M@np.r_[v,0,1])[:3]
            return cen+R@(W-cen)+p[3:6]
        inputs=[]
        for name,(px,py) in zip(q['query_ids'],q['pixels_uv']):
            x=np.array([px*sx,py*sy]);centre=mapped(x)
            e1=mapped(x+[.5,0])-mapped(x-[.5,0]);e1/=np.linalg.norm(e1)
            e2=mapped(x+[0,.5])-mapped(x-[0,.5]);e2-=e1*e1.dot(e2);e2/=np.linalg.norm(e2)
            source=map_coordinates(S,np.vstack([(py+yy/sy).ravel(),(px+xx/sx).ravel()]),order=1,mode='nearest').reshape(xx.shape)
            high=source-gaussian_filter(source,1.6)
            inputs.append((name,centre,e1,e2,source,high))
        for bound in [9,30]:
            for seed in ([17] if composition=='residual_on_affine' else [17,41,73]):
                rows=[];answers=[]
                for name,centre,e1,e2,source,high in inputs:
                    def objective(z):
                        world=centre[:,None]+e1[:,None]*(xx.ravel()+z[0])+e2[:,None]*(yy.ravel()+z[1])+normal[:,None]*z[2]
                        ij=(iv@np.vstack([world,np.ones(world.shape[1])]))[:3]
                        target=map_coordinates(V,ij,order=1,cval=-1024).reshape(xx.shape)
                        c=np.corrcoef(source.ravel(),target.ravel())[0,1];ht=target-gaussian_filter(target,1.6)
                        ch=np.corrcoef(high.ravel(),ht.ravel())[0,1]
                        return -(.4*c+.6*ch)
                    fit=differential_evolution(objective,[(-bound,bound)]*3,popsize=12,maxiter=40,tol=.001,polish=True,seed=seed,workers=1)
                    point=centre+e1*fit.x[0]+e2*fit.x[1]+normal*fit.x[2];answers.append(point.tolist())
                    rows.append({'id':name,'centre':centre.tolist(),'axes':np.column_stack([e1,e2,normal]).tolist(),
                        'offset':fit.x.tolist(),'objective_score':float(-fit.fun),'nfev':fit.nfev})
                result={'composition':composition,'bound_mm':bound,'seed':seed,'query_ids':q['query_ids'],'points_world_mm':answers,'diagnostics':rows}
                filename=f'{composition}-b{bound}-s{seed}.json';(dest/filename).write_text(json.dumps(result,indent=2)+'\n')
                all_rows.append(filename);print('COUNTERFACTUAL',filename,flush=True)
    (dest/'index.json').write_text(json.dumps({'conditions':all_rows,'elapsed_s':time.time()-start},indent=2)+'\n')


if __name__=='__main__':main()
