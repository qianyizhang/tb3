"""Engineering review packet, not expert clinical adjudication."""
from pathlib import Path
import json
import numpy as np
import nibabel as nib
from scipy import ndimage as ndi
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from geometry import sample, transform

ROOT=Path(__file__).resolve().parents[3]; B=ROOT/'runs/br030-vessel-geometry'

def main():
    mr=json.loads((ROOT/'runs/br025-vessel-curation/CoW_Centerline_Data/cow_nodes/topcow_mr_012.json').read_text())
    ct=json.loads((B/'sources/CoW_Centerline_Data/cow_nodes/topcow_ct_012.json').read_text())
    pairs=[]; seen=set()
    for lab,group in mr.items():
        for name,rows in group.items():
            match=ct.get(lab,{}).get(name,[])
            if len(rows)!=1 or len(match)!=1 or 'end' in name or 'start' in name:continue
            a=rows[0]['coords'];c=match[0]['coords'];key=tuple(a+c)
            if key in seen:continue
            seen.add(key);pairs.append((lab,name,a,c))
    x=np.array([r[2] for r in pairs]); y=np.array([r[3] for r in pairs])
    xc=x-x.mean(0);yc=y-y.mean(0);u,s,v=np.linalg.svd(xc.T@yc)
    fix=np.eye(3);fix[-1,-1]=np.linalg.det(v.T@u.T);rot=v.T@fix@u.T
    aff=np.eye(4);aff[:3,:3]=rot;aff[:3,3]=y.mean(0)-rot@x.mean(0)
    errors=np.linalg.norm(transform(x,aff)-y,axis=1)
    old=ROOT/'runs/br026-vessel-repair/tasks/vessel-v02'
    mrimg=nib.load(old/'environment/data/image.nii.gz');ref=nib.load(old/'solution/reference.nii.gz')
    answer=nib.load(ROOT/'runs/br026-vessel-v02-terra-high-v1-20260916/vessel-v02__86Naqao/artifacts/app/answer/corrected_mask.nii.gz')
    extra=(np.asarray(answer.dataobj)>0)&~(np.asarray(ref.dataobj)>0)
    assert int(extra.sum())==244
    points=transform(np.argwhere(extra),mrimg.affine);center=points.mean(0);target=transform(center,aff)
    ctimg=nib.load(B/'sources/TopCoW2024_Data_Release/imagesTr/topcow_ct_012_0000.nii.gz')
    ctref=nib.load(B/'sources/TopCoW2024_Data_Release/cow_seg_labelsTr/topcow_ct_012.nii.gz')
    extent=np.linspace(-6,6,121);a,b=np.meshgrid(extent,extent,indexing='xy')
    fig,axs=plt.subplots(2,3,figsize=(12,8),facecolor='#101923')
    for col,(i,j) in enumerate([(0,1),(0,2),(1,2)]):
        p=np.broadcast_to(center,a.shape+(3,)).copy();p[...,i]+=a;p[...,j]+=b
        cp=transform(p,aff)
        mv=sample(np.asarray(mrimg.dataobj),mrimg.affine,p)
        cv=sample(np.asarray(ctimg.dataobj),ctimg.affine,cp)
        ml=sample(np.asarray(ref.dataobj),ref.affine,p,0,0)>0
        cl=sample(np.asarray(ctref.dataobj),ctref.affine,cp,0,0)>0
        e=sample(extra,mrimg.affine,p,0,0)>0
        for row,values,mask,vmax in [(0,mv,ml,400),(1,cv,cl,650)]:
            ax=axs[row,col];ax.imshow(values,cmap='gray',origin='lower',extent=[-6,6,-6,6],vmin=0,vmax=vmax)
            if mask.any():ax.contour(a,b,mask,levels=[.5],colors=['#5bddd0'],linewidths=.8)
            if e.any():ax.contour(a,b,e,levels=[.5],colors=['#ff945c'],linewidths=1.1)
            ax.set_title(('MRA native plane' if row==0 else 'CTA at landmark-aligned plane')+f' {i}/{j}',color='white',fontsize=10)
            ax.tick_params(colors='white');ax.set_xlabel('mm from MRA addition centroid',color='white',fontsize=8)
    fig.suptitle('BR-026 disagreement: reference contour (cyan), prior addition (orange)\nCTA alignment is approximate; these planes cannot establish microscopic correspondence.',color='white',fontsize=12)
    fig.tight_layout();out=B/'adjudication';out.mkdir(exist_ok=True)
    fig.savefig(out/'paired-review.png',dpi=150,facecolor=fig.get_facecolor());plt.close(fig)
    r={'kind':'engineering paired-image review; no expert adjudication',
       'landmarks':len(pairs),'registration':'one rigid least-squares fit of unique one-to-one shared boundary/bifurcation landmarks; all used, no outlier rejection',
       'mra_to_ct_ras_matrix':aff.tolist(),'landmark_residual_mm':{'median':float(np.median(errors)),'p95':float(np.percentile(errors,95)),'max':float(errors.max())},
       'landmark_rows':[{'label':p[0],'name':p[1],'residual_mm':float(e)} for p,e in zip(pairs,errors)],
       'mra_addition_centroid_ras_mm':center.tolist(),'approximate_ct_centroid_ras_mm':target.tolist(),
       'added_voxels':244,'source_label_contact':'12 = L-ACA only',
       'frozen_score_disposition':'Preserve original mask-preservation failure; exclude from clinically confirmed topology failure claims.',
       'clinical_disposition':'Unresolved. A neuroradiologist must decide true unlabeled vessel, annotation scope mismatch, or false connection. Registration residual and differing modalities preclude automatic relabeling.',
       'review_question':'At the marked L-ACA-adjacent structure, is the 244-voxel addition true lumen within intended annotation scope, a real out-of-scope vessel, or a false connection? Review native CTA/MRA and source masks independently.',
       'source_annotation_scope':'TopCoW labels 13 CoW components within a specified ROI, not every visible intracranial artery. Source reports expert consensus for uncertain labels.',
       'source_url':'https://pmc.ncbi.nlm.nih.gov/articles/PMC13496301/',
       'supplement_retrieval':'PMC supplementary annotation appendix returned a browser verification page; no inaccessible protocol detail inferred.',
       'expert_contact':'No external messages sent.'}
    (out/'review-packet.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:r[k] for k in ['landmarks','landmark_residual_mm','clinical_disposition']},indent=2))

if __name__=='__main__':main()
