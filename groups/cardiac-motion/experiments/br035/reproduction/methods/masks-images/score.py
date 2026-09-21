"""Recompute mesh fit and mechanics, using reference probes for arbitrary topology."""
import json
from pathlib import Path
import numpy as np
from geometry import voxelize,locate,fields

LIMITS=dict(mask_dice=.90,volume_error_pct=5.,field_abs_error=1e-4,coverage=.95,motion_rmse_mm=2.,strain_mae_pp=5.,peak_mae_pp=5.,timing_frames=2.)

def score(path,data,truth=None):
    try:return evaluate(path,data,truth)
    except Exception as e:return dict(reward=0,error=type(e).__name__+': '+str(e)[:300])

def evaluate(path,data,truth=None):
    path=Path(path);data=Path(data)
    with np.load(path,allow_pickle=False) as z:pred={k:z[k] for k in z.files}
    P=np.asarray(pred['points'],float);tet=np.asarray(pred['tetra']);T,N,_=P.shape
    masks=np.load(data/'masks.npz')['masks'];g=json.loads((data/'geometry.json').read_text())
    assert P.ndim==3 and P.shape[-1]==3 and T==len(masks) and N>=4 and np.isfinite(P).all()
    assert tet.ndim==2 and tet.shape[1]==4 and len(tet)>0 and np.issubdtype(tet.dtype,np.integer) and tet.min()>=0 and tet.max()<N
    assert len(np.unique(np.sort(tet,axis=1),axis=0))==len(tet),'Duplicate tetrahedra'
    X=P[0];e0=X[tet[:,1:]]-X[tet[:,:1]];v0=abs(np.linalg.det(e0))/6
    assert v0.min()>1e-10,'Degenerate initial element'
    face=np.concatenate([tet[:,j] for j in [[0,1,2],[0,1,3],[0,2,3],[1,2,3]]]);_,counts=np.unique(np.sort(face,axis=1),axis=0,return_counts=True)
    assert counts.max()<=2,'Nonmanifold tetrahedral faces'
    F,E,J=fields(X,P,tet);field_error={}
    for key,ref in [('F',F),('E',E),('J',J)]:
        a=pred[key];assert a.shape==ref.shape and np.isfinite(a).all(),key+' wrong shape/nonfinite'
        field_error[key]=float(np.max(abs(a-ref)))
    dice=[]
    for p,m in zip(P,masks):
        got=voxelize(p,tet,np.array(g['origin_xyz_mm']),np.array(g['spacing_xyz_mm']),m.shape)
        dice.append(float(2*np.count_nonzero(got&m)/(got.sum()+m.sum())))
    volume=np.einsum('tm,m->t',abs(J),v0)/1000
    mv=masks.sum((1,2,3))*np.prod(g['spacing_xyz_mm'])/1000
    verr=float(100*np.mean(abs(volume/mv-1)))
    metrics=dict(vertices=N,tetrahedra=len(tet),mean_mask_dice=float(np.mean(dice)),min_frame_mask_dice=float(min(dice)),per_frame_mask_dice=dice,volume_ml=volume.tolist(),mask_volume_ml=mv.tolist(),mean_volume_error_pct=verr,inverted_elements=int((J<=0).sum()),J_min=float(J.min()),J_max=float(J.max()),J_percentiles=np.percentile(J,[1,5,50,95,99]).tolist(),field_max_abs_error=field_error)
    gates=dict(mask_fit=metrics['mean_mask_dice']>=LIMITS['mask_dice'],volume=verr<=LIMITS['volume_error_pct'],positive_elements=not metrics['inverted_elements'],field_calculation=max(field_error.values())<=LIMITS['field_abs_error'])
    out=dict(reward=int(all(gates.values())),construction_gates=gates,geometry=metrics,limits=LIMITS,mask_semantics=g['mask_semantics'])
    if g['mask_semantics']=='lv_cavity':
        ef=float(100*(1-volume.min()/volume.max()));refef=float(100*(1-mv.min()/mv.max()))
        out['cavity_function']=dict(ef_pct=ef,mask_ef_pct=refef,ef_error_pp=abs(ef-refef),ef_geometry_check_pass=abs(ef-refef)<=3,myocardial_strain_validated=False)
    if truth is not None:
        q=dict(np.load(truth));rt=q['tetra'];Q=q['points'];probes=Q[0][rt].mean(1);ids,bary=locate(X,tet,probes);covered=ids>=0;w=q['weights'];coverage=float(w[covered].sum()/w.sum())
        if not covered.any():out['material']=dict(coverage=coverage,pass_=False);return out
        labels=q['cell_labels'];valid=(labels>0)&np.all(np.linalg.norm(q['directions'],axis=-1)>.99,axis=0);lvcoverage=float(w[covered&valid].sum()/w[valid].sum())
        predmotion=np.einsum('tnki,nk->tni',P[:,tet[ids[covered]]],bary[covered]);refmotion=Q[:,rt[covered]].mean(2)
        err=np.sum((predmotion-refmotion)**2,-1);rmse=float(np.sqrt(np.average(err,axis=1,weights=w[covered]).mean()))
        local_labels=labels[covered];localw=w[covered];lv=local_labels>0
        lvrmse=float(np.sqrt(np.average(err[:,lv],axis=1,weights=localw[lv]).mean())) if lv.any() else None
        rf,_,_=fields(Q[0],Q,rt);take=covered&valid;axes=q['directions'][:,take]
        pe=np.linalg.norm(np.einsum('tnij,dnj->tndi',F[:,ids[take]],axes),axis=-1)-1
        re=np.linalg.norm(np.einsum('tnij,dnj->tndi',rf[:,take],axes),axis=-1)-1
        mae=100*np.average(abs(pe-re),axis=1,weights=w[take]).mean(0)
        regions=[];pc=[];rc=[];regioncoverage={}
        for label in range(1,18):
            region=(labels==label)&valid;regioncoverage[str(label)]=float(w[region&covered].sum()/w[region].sum())
            subset=labels[take]==label
            if not subset.any():continue
            regions.append(label);pc.append(100*np.average(pe[:,subset],axis=1,weights=w[take][subset]));rc.append(100*np.average(re[:,subset],axis=1,weights=w[take][subset]))
        pc=np.array(pc).transpose(1,0,2);rc=np.array(rc).transpose(1,0,2)
        peak=lambda c:np.stack([c[:,:,0].min(0),c[:,:,1].min(0),c[:,:,2].max(0)],1)
        peakmae=abs(peak(pc)-peak(rc)).mean(0);timing=[]
        for d in range(3):
            diffs=[]
            for r in range(len(regions)):
                ref=rc[:,r,d];p=pc[:,r,d];idx=int(p.argmin() if d<2 else p.argmax());val=ref.min() if d<2 else ref.max();near=np.where(abs(ref-val)<=.5)[0];diffs.append(float(abs(near-idx).min()))
            timing.append(float(np.mean(diffs)))
        passes=dict(coverage=coverage>=.95 and lvcoverage>=.95,motion=rmse<=2,strain=bool(np.all(mae<=5)),regional_peak=bool(np.all(peakmae<=5)),regional_timing=bool(np.all(np.array(timing)<=2)))
        out['material']=dict(coverage=coverage,lv_coverage=lvcoverage,covered_cells=int(covered.sum()),total_cells=len(rt),motion_rmse_mm=rmse,lv_motion_rmse_mm=lvrmse,strain_mae_pp=mae.tolist(),regional_peak_mae_pp=peakmae.tolist(),regional_timing_frames=timing,region_coverage=regioncoverage,regions=regions,predicted_regional_engineering_pct=pc.tolist(),reference_regional_engineering_pct=rc.tolist(),gates=passes,pass_=all(passes.values()),interpretation='Similarity to simulator material motion, not proof that this material map is identifiable from supplied masks.')
    return out

if __name__=='__main__':
    root=Path('/verifier');r=score('/app/answer/prediction.npz',root/'data',root/'truth.npz');p=Path('/logs/verifier');p.mkdir(parents=True,exist_ok=True);(p/'metrics.json').write_text(json.dumps(r,indent=2)+'\n');(p/'reward.txt').write_text(str(r['reward'])+'\n');print(json.dumps({k:v for k,v in r.items() if k!='material'}))
