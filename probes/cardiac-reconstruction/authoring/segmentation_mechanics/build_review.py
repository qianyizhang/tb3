"""Render arbitrary submitted meshes, independently recomputed strain and mask fit."""
import json,shutil,os
from pathlib import Path
import numpy as np
from PIL import Image
from skimage.measure import find_contours
from geometry import fields,voxelize
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent;B=ROOT/'runs/br035-segmentation-mechanics';OUT=B/'review'
os.environ.setdefault('MPLCONFIGDIR',str(B/'matplotlib-cache'))
def read(p):return json.loads(p.read_text())
def boundary(tet):
    f=np.concatenate([tet[:,j] for j in [[0,1,2],[0,1,3],[0,2,3],[1,2,3]]]);owner=np.tile(np.arange(len(tet)),4);_,i,n=np.unique(np.sort(f,axis=1),axis=0,return_index=True,return_counts=True);i=i[n==1];return f[i],owner[i]
def export(P,tet=None,faces=None,clinical=False):
    strain=jac=None
    if tet is not None:
        faces,owner=boundary(tet);v=abs(np.linalg.det(P[:,tet[:,1:]]-P[:,tet[:,:1]])).sum(1)/6000
        if not clinical:
            _,E,J=fields(P[0],P,tet[owner]);strain=np.linalg.eigvalsh(E)[...,0]*100;jac=J
    else:v=abs(np.einsum('tfi,tfi->tf',P[:,faces[:,0]],np.cross(P[:,faces[:,1]],P[:,faces[:,2]])).sum(1))/6000
    ids=np.unique(faces);mapping=np.full(P.shape[1],-1);mapping[ids]=np.arange(len(ids));faces=mapping[faces]
    return dict(points=np.round(P[:,ids].astype(float),3).tolist(),faces=faces.tolist(),volume=v.tolist(),strain=np.round(strain.astype(float),3).tolist() if strain is not None else None,jacobian=np.round(jac.astype(float),4).tolist() if jac is not None else None)
def main():
    OUT.mkdir(exist_ok=True);shutil.copy2(HERE/'viewer.html',OUT/'index.html');cases=[];plotrows=[]
    for condition in ['masks','masks-images']:
        receipt=B/f'{condition}-sol-xhigh-receipt.json'
        if not receipt.exists():continue
        result=read(receipt);answer=ROOT/result['result_path'];answer=answer.parent/'artifacts/app/answer'
        for clinical in [False,True]:
            key=condition+('-clinical' if clinical else '-synthetic');d=OUT/key;d.mkdir(exist_ok=True);(d/'images').mkdir(exist_ok=True)
            source=B/'prepared';inp=B/'clinical'/condition if clinical else B/'tasks'/('cardiac-'+condition)/'environment/data';g=read(inp/'geometry.json');masks=np.load(inp/'masks.npz')['masks'];images=np.load(source/('clinical_images.npy' if clinical else 'synthetic_images.npy'),mmap_mode='r')
            rr=read(B/'replays'/condition/'receipt.json') if clinical and (B/'replays'/condition/'receipt.json').exists() else result if not clinical else {}
            output=B/'replays'/condition/'output' if clinical else answer;grade=rr.get('grade',{});ge=grade.get('geometry',{});mat=grade.get('material',{})
            pred=None;pmasks=[];predfile=output/'prediction.npz'
            if predfile.exists() and grade.get('geometry'):
                z=dict(np.load(predfile));P=z['points'];tet=z['tetra'];pred=export(P,tet,clinical=clinical)
                for p in P:pmasks.append(voxelize(p,tet,np.array(g['origin_xyz_mm']),np.array(g['spacing_xyz_mm']),masks.shape[1:]))
            if clinical:
                z=dict(np.load(ROOT/'runs/br034-pathological-echo/reference.npz'));ref=export(z['points'],faces=z['faces'],clinical=True)
            else:
                z=dict(np.load(source/'truth.npz'));ref=export(z['points'],z['tetra'])
            points=z['points'];center=(points[0].min(0)+points[0].max(0))/2;extent=(points-center).max()-min(0,(points-center).min());extent=extent/2
            sections=[[],[]];hi=max(float(np.percentile(images[0],99.8)),1)
            for axis in [0,1,2]:
                mid=masks.shape[axis+1]//2;pseq=[];rseq=[]
                for t in range(len(masks)):
                    sl=np.take(images[t],mid,axis=axis);Image.fromarray(np.clip(sl/hi*255,0,255).astype('uint8')).save(d/'images'/f'{axis}_{t}.png')
                    contour=lambda x:[np.round(c,2).tolist() for c in find_contours(x.astype(float),.5)]
                    rseq.append(contour(np.take(masks[t],mid,axis=axis)));pseq.append(contour(np.take(pmasks[t],mid,axis=axis)) if len(pmasks) else [])
                sections[0].append(pseq);sections[1].append(rseq)
            rows=[['Construction gates','Pass' if grade.get('reward')==1 else 'Not passed' if grade else 'No completed replay'],['Mean mask Dice',f"{ge.get('mean_mask_dice',float('nan')):.3f}"],['Volume error',f"{ge.get('mean_volume_error_pct',float('nan')):.2f}%"],['Inverted elements',str(ge.get('inverted_elements','—'))]]
            if not clinical and (B/'posthoc-mesh-quality.json').exists():
                quality=read(B/'posthoc-mesh-quality.json')[condition]
                rows += [['Nonmanifold boundary edges (posthoc)',str(quality['boundary_edges_with_incidence_not_two'])],['Minimum J',f"{ge.get('J_min',float('nan')):.3f}"]]
            if clinical:
                ef=grade.get('cavity_function',{});rows += [['Sol / reference EF',f"{ef.get('ef_pct',float('nan')):.2f} / {read(B/'preparation.json')['clinical_reference_ef_pct']:.2f}%"],['Myocardial strain','Not supported by cavity masks']]
            else:rows += [['Material probe coverage',f"{100*mat.get('coverage',0):.1f}%"],['Material motion RMSE',f"{mat.get('motion_rmse_mm',float('nan')):.2f} mm"],['Strain MAE: L / C / R',' / '.join(f'{x:.2f}' for x in mat.get('strain_mae_pp',[]))+' pp'],['Material diagnostic targets','Pass' if mat.get('pass_') else 'Not passed']]
            assessment=read(output/'assessment.json') if (output/'assessment.json').exists() else None
            for name in ['method.md','solve.py']:
                src=output/name if (output/name).exists() else answer/name
                if src.exists():shutil.copy2(src,d/name)
            rows=[[label,value if 'nan' not in value else '—'] for label,value in rows]
            out=dict(key=key,clinical=clinical,frames=len(masks),models=[pred,ref],center=center.tolist(),extent=float(extent),sections=sections,rows=rows,assessment=assessment,evidence=rr,note='Unchanged executable on clinical cavity masks.' if clinical else 'Fresh trial with independently generated mesh; source mesh identities withheld.',image_note=('Ultrasound shown here was supplied to the solver.' if condition=='masks-images' else 'Ultrasound is shown for review only; this solver received segmentation masks alone.')+' Gold outlines are the supplied segmentations. Teal outlines are independently rasterized mesh sections.')
            (d/'data.json').write_text(json.dumps(out,separators=(',',':')));cases.append(dict(key=key,name=('Clinical transfer · ' if clinical else 'Synthetic myocardium · ')+('masks + ultrasound' if condition=='masks-images' else 'masks alone')))
            plotrows.append((condition,clinical,grade))
    (OUT/'index.json').write_text(json.dumps(dict(headline='Both construction tests pass. Radial-strain error remains above 5 percentage points; clinical EF is preserved from the supplied masks. Mesh-quality qualifications are shown separately.',cases=cases),indent=2))
    report=ROOT/'docs/research-rounds/BR-035-results.md'
    if report.exists():shutil.copy2(report,OUT/'report.md')
    import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,3,figsize=(16,4.5))
    for condition,clinical,r in plotrows:
        if not r.get('geometry'):continue
        ge=r['geometry'];ax=axes[int(clinical)];v=np.array(ge['volume_ml']);x=np.linspace(0,100,len(v));ax.plot(x,v,label=condition)
        if not ax.lines[:-1]:ax.plot(x,ge['mask_volume_ml'],'k--',label='Supplied segmentation')
    for ax,title in zip(axes[:2],['Synthetic myocardial volume','Clinical LV cavity volume']):ax.set(title=title,xlabel='Acquired cycle (%)',ylabel='Volume (mL)');ax.grid(alpha=.2);ax.legend() if ax.lines else None
    for i,condition in enumerate(['masks','masks-images']):
        selected=[r for c,clinical,r in plotrows if c==condition and not clinical]
        if selected and selected[0].get('material',{}).get('strain_mae_pp'):
            axes[2].bar(np.arange(3)+(i-.5)*.35,selected[0]['material']['strain_mae_pp'],width=.35,label=condition)
    axes[2].axhline(5,color='black',linestyle='--',linewidth=1,label='Diagnostic target')
    axes[2].set(xticks=np.arange(3),xticklabels=['Longitudinal','Circumferential','Radial'],ylabel='Strain MAE (percentage points)',title='Similarity to simulator strain')
    axes[2].legend();axes[2].grid(axis='y',alpha=.2)
    fig.tight_layout();fig.savefig(OUT/'function-comparison.png',dpi=180);fig.savefig(OUT/'function-comparison.pdf');plt.close(fig);print(str(OUT))
if __name__=='__main__':main()
