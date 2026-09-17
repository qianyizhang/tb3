"""Generate physical-aspect review panels, reference-centred with projected predictions."""
from pathlib import Path
import json,numpy as np,nibabel as nib
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[3];B=ROOT/'runs/br036-semantic-landmarks';out=B/'review';out.mkdir(exist_ok=True)
links=[]
for job in sorted((ROOT/'runs').glob('br036-*-terra-high-v1-20260917')):
 for p in job.glob('*/artifacts/app/answer/landmarks.json'):
  case=job.name.removeprefix('br036-').removesuffix('-terra-high-v1-20260917');task=B/'tasks'/case;ni=nib.load(task/'environment/volume.nii.gz');vol=np.asarray(ni.dataobj);aff=ni.affine;inv=np.linalg.inv(aff);spacing=np.linalg.norm(aff[:3,:3],axis=0)
  truth=json.loads((task/'tests/truth.json').read_text());pts=truth.get('points',truth.get('points_ras_mm'));ans=json.loads(p.read_text());images=[]
  low,high=(-200,1400) if case.startswith('ct') else np.percentile(vol[vol>0],[2,99])
  for name,gt in pts.items():
   point=ans.get(name);v=nib.affines.apply_affine(inv,gt)
   if np.any(v<0) or np.any(v>=vol.shape):continue
   pred=nib.affines.apply_affine(inv,point) if point is not None and len(point)==3 else None
   row=Image.new('RGB',(960,355),'#171b22');d=ImageDraw.Draw(row);err=f'{np.linalg.norm(np.array(point)-gt):.2f} mm' if pred is not None else 'empty';d.text((10,6),f'{name}: {err} | green reference; orange prediction projected onto reference slice',fill='white')
   for ax in range(3):
    axes=[j for j in range(3) if j!=ax];limits=[(max(0,int(v[j]-30/spacing[j])),min(vol.shape[j],int(v[j]+30/spacing[j])+1)) for j in axes]
    sl=np.take(vol,int(round(v[ax])),axis=ax)[limits[0][0]:limits[0][1],limits[1][0]:limits[1][1]]
    gray=np.uint8(np.clip((sl-low)/(high-low),0,1)*255);im=Image.fromarray(gray.T[::-1]).convert('RGB')
    size=(max(1,round(sl.shape[0]*spacing[axes[0]]*4)),max(1,round(sl.shape[1]*spacing[axes[1]]*4)));im=im.resize(size);dr=ImageDraw.Draw(im)
    def xy(q):return ((q[axes[0]]-limits[0][0])*size[0]/sl.shape[0],(limits[1][1]-1-q[axes[1]])*size[1]/sl.shape[1])
    for q,color in [(v,'#50fa7b'),(pred,'#ffad42')]:
     if q is None:continue
     x,y=xy(q);dr.line((x-5,y,x+5,y),fill=color,width=2);dr.line((x,y-5,x,y+5),fill=color,width=2)
    row.paste(im,(320*ax+10,45));off=f'; pred off-plane {(pred[ax]-v[ax])*spacing[ax]:+.1f} mm' if pred is not None else '';d.text((320*ax+10,28),f'voxel axis {ax}{off}',fill='white')
   images.append(row)
  panel=Image.new('RGB',(960,355*len(images)))
  for i,row in enumerate(images):panel.paste(row,(0,355*i))
  panel.save(out/f'{case}.png');links.append(f'<h2>{case}</h2><img src="{case}.png" style="max-width:100%">')
(out/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>BR-036 reference comparison</title><body style="background:#121720;color:#eee;font-family:system-ui;max-width:1000px;margin:auto"><h1>Semantic landmarks: reference comparison</h1><p>Native scan pixels. 60 mm reference-centred views at physical aspect ratio. Predictions are projected into each reference slice; off-plane distance is labelled. These are review panels, not model inputs or independent clinical adjudication. Cropped-out references omitted from images.</p>'+''.join(links))
print('Built review:',len(links),'completed submissions')
