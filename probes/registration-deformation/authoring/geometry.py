"""Small geometric controls, independent of any image-registration method."""
import numpy as np

def errors(pred,truth):
    e=np.linalg.norm(np.asarray(pred)-np.asarray(truth),axis=1)
    return {'rms_mm':float(np.sqrt(np.mean(e*e))), 'mean_mm':float(e.mean()),
            'p90_mm':float(np.quantile(e,.9)), 'max_mm':float(e.max()),'per_point_mm':e.tolist()}

def rigid_fit(a,b):
    a=np.asarray(a);b=np.asarray(b);ca=a.mean(0);cb=b.mean(0)
    u,_,v=np.linalg.svd((a-ca).T@(b-cb))
    r=u@np.diag([1,1,np.linalg.det(u@v)])@v
    return np.einsum('ni,ij->nj',a-ca,r)+cb

def affine_fit(a,b):
    q=np.c_[a,np.ones(len(a))]
    return q@np.linalg.lstsq(q,b,rcond=None)[0]
