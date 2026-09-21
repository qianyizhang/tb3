"""Private, frozen semantic segmentation evaluation. No evaluator code runs in solver."""
import json,sys
from pathlib import Path
import numpy as np,nibabel as nib

def score(answer,reference,labels):
 ref=nib.load(reference);g=np.asanyarray(ref.dataobj).astype(np.int64);allowed=sorted(map(int,labels))
 p=Path(answer)
 if not p.is_file():return {'valid':False,'reason':'missing_output','macro_dice':0.0,'per_label':[]}
 try:
  im=nib.load(p);a=np.asanyarray(im.dataobj)
  if a.shape!=g.shape or not np.allclose(im.affine,ref.affine,atol=1e-5,rtol=0):raise ValueError('geometry mismatch')
  if not np.isfinite(a).all() or not np.equal(a,np.rint(a)).all():raise ValueError('noninteger or nonfinite labels')
  if not set(np.unique(a).astype(int)).issubset(allowed):raise ValueError('unknown label')
  a=a.astype(np.int64)
 except Exception as e:return {'valid':False,'reason':str(e),'macro_dice':0.0,'per_label':[]}
 n=max(allowed)+1;matrix=np.bincount((g*n+a).ravel(),minlength=n*n).reshape(n,n);gc=matrix.sum(axis=1);pc=matrix.sum(axis=0);rows=[]
 for k in allowed:
  if k==0:continue
  den=int(gc[k]+pc[k]);intersection=int(matrix[k,k]);d=2*intersection/den if den else None
  rows.append({'id':k,'gt_voxels':int(gc[k]),'prediction_voxels':int(pc[k]),'intersection':intersection,'dice':d})
 vals=[x['dice'] for x in rows if x['dice'] is not None]
 return {'valid':True,'macro_dice':float(np.mean(vals)) if vals else 0.0,'per_label':rows,'foreground_dice':float(2*(matrix[1:,1:].sum())/(gc[1:].sum()+pc[1:].sum())) if gc[1:].sum()+pc[1:].sum() else 1.0}
if __name__=='__main__':
 answer=Path(sys.argv[1]) if len(sys.argv)>1 else Path('/app/answer/segmentation.nii.gz')
 r=score(answer,'/tests/reference.nii.gz',json.loads(Path('/tests/labels.json').read_text()))
 out=Path('/logs/verifier');out.mkdir(parents=True,exist_ok=True);(out/'metrics.json').write_text(json.dumps(r,indent=2));(out/'reward.txt').write_text(str(r['macro_dice']));print(json.dumps({'valid':r['valid'],'macro_dice':r['macro_dice']}))
