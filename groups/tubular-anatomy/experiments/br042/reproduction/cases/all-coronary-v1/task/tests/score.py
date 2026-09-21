"""Arc-weighted labeled coronary centerline agreement; no clinical adjudication."""
import json
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree

def samples(obj):
    points=[];labels=[];weights=[]
    curves=obj['centerlines'];assert isinstance(curves,list) and 0<len(curves)<=200
    for curve in curves:
        p=np.asarray(curve['points_ras_mm'],dtype=float);l=np.asarray(curve['labels'])
        assert p.ndim==2 and p.shape[1]==3 and 2<=len(p)<=20000 and np.isfinite(p).all()
        assert l.shape==(len(p),) and np.isin(l,np.arange(1,15)).all()
        d=np.linalg.norm(np.diff(p,axis=0),axis=1);assert (d>1e-6).all() and (d<=1.5).all()
        for a,b,la,lb,length in zip(p[:-1],p[1:],l[:-1],l[1:],d):
            n=int(np.ceil(length/.25));t=(np.arange(n)+.5)/n
            points.extend(a[None,:]+t[:,None]*(b-a));labels.extend(np.where(t<.5,la,lb));weights.extend([length/n]*n)
    assert len(points)<=500000
    return np.asarray(points),np.asarray(labels),np.asarray(weights)

def evaluate(obj,ref):
    r,rl,rw=samples(ref)
    try:p,pl,pw=samples(obj)
    except Exception as e:return {'reward':0,'format_valid':False,'error':type(e).__name__+': '+str(e)}
    d=cKDTree(r).query(p)[0];back=cKDTree(p).query(r)[0]
    mean=lambda a,w:float(np.average(a,weights=w))
    rows={}
    for k in sorted(set(rl)|set(pl)):
        rm=rl==k;pm=pl==k
        sd=cKDTree(r[rm]).query(p[pm])[0] if rm.any() and pm.any() else np.full(pm.sum(),np.inf)
        sb=cKDTree(p[pm]).query(r[rm])[0] if pm.any() and rm.any() else np.full(rm.sum(),np.inf)
        rows[str(int(k))]={'reference_length_mm':float(rw[rm].sum()),'submitted_length_mm':float(pw[pm].sum()),'recall_1mm':mean(sb<=1,rw[rm]) if rm.any() else None,'precision_1mm':mean(sd<=1,pw[pm]) if pm.any() else 0.,'recall_2mm':mean(sb<=2,rw[rm]) if rm.any() else None}
    present=[v for v in rows.values() if v['reference_length_mm']>0]
    macro=float(np.mean([v['recall_1mm'] for v in present]))
    # Label-specific distances make geometry and identity jointly necessary.
    good=np.zeros(len(p),bool)
    for k in set(pl):
        if np.any(rl==k):good[pl==k]=cKDTree(r[rl==k]).query(p[pl==k])[0]<=1
    precision=mean(good,pw)
    return {'format_valid':True,'reward':int(macro>=.90 and precision>=.90 and all(v['recall_1mm']>=.80 for v in present)), 'macro_labeled_recall_1mm':macro,'labeled_precision_1mm':precision,'unlabeled_recall_1mm':mean(back<=1,rw),'unlabeled_precision_1mm':mean(d<=1,pw),'unlabeled_recall_2mm':mean(back<=2,rw),'per_label':rows,'submitted_length_mm':float(pw.sum()),'reference_length_mm':float(rw.sum()),'centerlines':len(obj['centerlines'])}

def score(answer,reference):
    try:obj=json.loads((Path(answer)/'centerlines.json').read_text())
    except Exception as e:return {'reward':0,'format_valid':False,'error':type(e).__name__}
    return evaluate(obj,json.loads(Path(reference).read_text()))

if __name__=='__main__':
    out=score('/app/answer','/verifier/reference.json');p=Path('/logs/verifier');p.mkdir(parents=True,exist_ok=True)
    (p/'metrics.json').write_text(json.dumps(out,indent=2)+'\n');(p/'reward.txt').write_text(str(out['reward'])+'\n')
