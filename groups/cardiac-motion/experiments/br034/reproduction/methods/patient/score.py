"""Independent pilot scoring against withheld clinical surface annotations."""
import json
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree

def volumes(p,f):
    t=p[:,f];return np.abs(np.einsum('tmi,tmi->tm',t[:,:,0],np.cross(t[:,:,1],t[:,:,2])).sum(1)/6000)
def samples(p,f):
    t=p[f];return np.concatenate([p,t.mean(1),(t[:,0]+t[:,1])/2,(t[:,1]+t[:,2])/2,(t[:,0]+t[:,2])/2])
def distances(a,af,b,bf):
    aa=samples(a,af);bb=samples(b,bf)
    d=np.r_[cKDTree(bb).query(aa)[0],cKDTree(aa).query(bb)[0]]
    return float(d.mean()),float(np.percentile(d,95))
def category(ef):
    return 'severely_reduced' if ef<30 else 'moderately_reduced' if ef<=40 else 'mildly_reduced_or_borderline' if ef<54 else 'preserved'
def score(answer,reference):
    try:
        a=np.load(answer/'prediction.npz',allow_pickle=False);g=np.load(reference,allow_pickle=False)
        p=a['points'].astype(float);f=a['faces'];gp=g['points'];gf=g['faces']
        assert p.ndim==3 and p.shape[0]==len(gp) and p.shape[2]==3 and p.shape[1]<=10000
        assert f.ndim==2 and f.shape[1]==3 and np.issubdtype(f.dtype,np.integer) and len(f)<=20000
        assert np.isfinite(p).all() and f.min()>=0 and f.max()<p.shape[1]
        edges=np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]);ue,counts=np.unique(np.sort(edges,axis=1),axis=0,return_counts=True)
        assert (counts==2).all(),'Surface must be closed with two faces per edge'
        assert len(np.unique(edges,axis=0))==len(edges),'Surface faces must have consistent orientation'
        v=volumes(p,f);gv=volumes(gp,gf);assert min(v)>1
        ef=float(100*(1-min(v)/max(v)));gef=float(100*(1-min(gv)/max(gv)))
        summary=json.loads((answer/'summary.json').read_text());assert np.allclose(summary['volume_ml'],v,atol=.01)
        assert abs(float(summary['ef_pct'])-ef)<.05
        assert (answer/'solve.py').is_file() and (answer/'method.md').is_file()
        ds=np.array([distances(pp,f,gg,gf) for pp,gg in zip(p,gp)])
        volerr=np.abs(v-gv)/gv*100
        declared=summary.get('diagnosis',{}).get('functional_class')
        metrics=dict(format_valid=True,surface_mean_mm=float(ds[:,0].mean()),surface_p95_mm=float(ds[:,1].max()),
            per_frame_surface_mean_mm=ds[:,0].tolist(),volume_ml=v.tolist(),reference_volume_ml=gv.tolist(),
            ef_pct=ef,reference_ef_pct=gef,ef_error_pp=abs(ef-gef),mean_volume_error_pct=float(volerr.mean()),
            edv_error_pct=float(abs(max(v)-max(gv))/max(gv)*100),esv_error_pct=float(abs(min(v)-min(gv))/min(gv)*100),
            declared_functional_class=declared,reference_functional_class=category(gef),
            diagnostic_class_matches=declared==category(gef),diagnosis_consistent_with_own_ef=declared==category(ef),
            per_frame_surface_p95_mm=ds[:,1].tolist())
        gates=dict(surface_mean=metrics['surface_mean_mm']<=3,surface_p95=metrics['surface_p95_mm']<=6,
                   ef=metrics['ef_error_pp']<=8,edv=metrics['edv_error_pct']<=15,esv=metrics['esv_error_pct']<=15)
        metrics.update(gates=gates,reward=int(all(gates.values()) and metrics['diagnostic_class_matches']))
        return metrics
    except Exception as e:return dict(format_valid=False,reward=0,error=f'{type(e).__name__}: {e}')
if __name__=='__main__':
    out=score(Path('/app/answer'),Path('/verifier/reference.npz'))
    Path('/logs/verifier').mkdir(parents=True,exist_ok=True)
    Path('/logs/verifier/metrics.json').write_text(json.dumps(out,indent=2)+'\n')
    Path('/logs/verifier/reward.txt').write_text(str(out['reward'])+'\n')
    print(json.dumps(out))
