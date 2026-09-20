"""BR-042: verify case-level GT, package a new all-coronary task, freeze controls."""
from pathlib import Path
import sys,json,hashlib,shutil,copy
import numpy as np
import nibabel as nib
ROOT=Path(__file__).resolve().parents[4];H=Path(__file__).resolve().parent
sys.path.insert(0,str(H.parent));from geometry import read_centerline,resample_path,transform,sample
from score import evaluate,samples
B=ROOT/'runs/br042-all-vessels-v2';T=B/'tasks/all-vessels';S=ROOT/'runs/br030-vessel-geometry/sources/coronary';D=S/'ImageCAS-X_dataset'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not T.exists(),'Do not overwrite frozen task'
image=nib.load(S/'original/1.img.nii.gz');mask=nib.load(D/'segmentations/1.coronary.nii.gz');assert image.shape==mask.shape and np.allclose(image.affine,mask.affine)
ref={'centerlines':[]};sources=[S/'original/1.img.nii.gz',D/'segmentations/1.coronary.nii.gz'];side_stats={}
for side in ['left','right']:
    source=D/f'centerlines/1.coronary_{side}_centerline.vtk';sources.append(source)
    x,f,lines=read_centerline(source);ijk=transform(x,np.linalg.inv(image.affine));assert np.isfinite(ijk).all() and ((ijk>=0)&(ijk<np.array(image.shape))).all()
    for i,line in enumerate(lines):
        p=x[line];labs=f['segment_label'][line];pout=[p[0]];lout=[int(labs[0])]
        for a,b,la,lb in zip(p[:-1],p[1:],labs[:-1],labs[1:]):
            length=np.linalg.norm(b-a)
            if length<=1e-6:continue
            n=int(np.ceil(length/.5))
            for j in range(1,n+1):
                t=j/n;pout.append(a+t*(b-a));lout.append(int(la if t<.5 else lb))
        ref['centerlines'].append({'id':f'{side}-{i}','points_ras_mm':np.asarray(pout).tolist(),'labels':lout})
    side_stats[side]={'points':len(x),'polylines':len(lines),'labels':np.unique(f['segment_label']).tolist(),'all_points_inside_native_CTA':True}
p,l,w=samples(ref)
for name in ['environment/data','tests','solution']:(T/name).mkdir(parents=True)
old=ROOT/'runs/br041-image-only-centerline/tasks/named-rca'
for name in ['Dockerfile','DATA-LICENSE.txt']:shutil.copy2(old/'environment'/name,T/'environment'/name)
shutil.copy2(S/'original/1.img.nii.gz',T/'environment/data/image.nii.gz')
(T/'environment/SOURCE_NOTICE.md').write_text('CTA: ImageCAS, Xiaowei Xu and collaborators, https://www.kaggle.com/datasets/xiaoweixumedicalai/imagecas (source listing Apache 2.0). Original field of view. Private evaluation: ImageCAS-X corrected coronary annotations and segmentation-derived centerlines, Bransby et al., https://github.com/kitbransby/ImageCAS-X and https://zenodo.org/records/21887809 (CC BY 4.0). Public development case, not held-out clinical validation. Do not retrieve case-specific annotations or previous solutions.\n')
shutil.copy2(H/'instruction.md',T/'instruction.md');shutil.copy2(H/'score.py',T/'tests/score.py');shutil.copy2(old/'tests/Dockerfile',T/'tests/Dockerfile')
(T/'tests/test.sh').write_text('#!/bin/sh\nset -eu\npython /verifier/score.py\n')
(T/'solution/solve.sh').write_text('#!/bin/sh\nset -eu\nmkdir -p /app/answer\ncp /solution/centerlines.json /app/answer/\n')
for path in [T/'tests/reference.json',T/'solution/centerlines.json']:path.write_text(json.dumps(ref)+'\n')
toml=(old/'task.toml').read_text().replace('named-rca-image-only','all-vessels-image-only-v2').replace('Repair a natural coronary segmentation gap, trace RCA to R-PDA, and produce rotated CPR and a world-space mesh.','Extract all visible clinically relevant vessels and labels; score coronary coverage and review other vessels.')
(T/'task.toml').write_text(toml)
controls={'oracle':evaluate(ref,ref)}
for name in ['swapped_labels','missing_left','shifted','missing_small_branch']:
    bad=copy.deepcopy(ref)
    if name=='missing_left':bad['centerlines']=[c for c in bad['centerlines'] if c['id'].startswith('right')]
    elif name=='missing_small_branch':bad['centerlines']=[c for c in bad['centerlines'] if 6 not in c['labels']]
    else:
        for c in bad['centerlines']:
            if name=='swapped_labels':c['labels']=[2 if k==9 else 9 if k==2 else k for k in c['labels']]
            else:c['points_ras_mm']=(np.asarray(c['points_ras_mm'])+20).tolist()
    controls[name]=evaluate(bad,ref)
assert controls['oracle']['reward']==1 and all(v['reward']==0 for k,v in controls.items() if k!='oracle')
(B/'validation.json').write_text(json.dumps(controls,indent=2)+'\n')
labels={1:'LM',2:'LAD',3:'LCx',4:'D1',5:'D2',6:'OM1',7:'OM2',8:'IM',9:'RCA',10:'R-PDA',11:'R-PLA',12:'L-PDA',13:'L-PLA',14:'Other'}
receipt={'round':'BR-042','source':'https://github.com/kitbransby/ImageCAS-X','source_record':'https://zenodo.org/records/21887809','case':1,'shape':list(image.shape),'affine':image.affine.tolist(),'mask_affine_matches':True,'trees':side_stats,'labeled_reference_lengths_mm':{labels[int(k)]:float(w[l==k].sum()) for k in np.unique(l)},'sources':{str(p.relative_to(ROOT)):sha(p) for p in sources},'scope':'Both coronary trees only. No complete thoracic vessel or clinical relevance GT. Segment labels and centerlines are dataset references, not independent expert adjudication. Full native CTA replaces prior author-selected crop.'}
(ROOT/'docs/evidence/br042-v2-gt-audit.json').write_text(json.dumps(receipt,indent=2)+'\n')
freeze={'round':'BR-042','model':'openai/gpt-6-astra','effort':'medium','attempts':1,'retries':0,'timeout_seconds':3600,'tasks':[{'task_path':str(T.relative_to(ROOT)),'files':{str(p.relative_to(T)):sha(p) for p in sorted(T.rglob('*')) if p.is_file()}}]}
for p in [B/'freeze.json',ROOT/'docs/evidence/br042-v2-freeze.json']:p.write_text(json.dumps(freeze,indent=2)+'\n')
print(json.dumps(receipt,indent=2));print('Frozen; oracle and four anatomical/label omission controls pass')
