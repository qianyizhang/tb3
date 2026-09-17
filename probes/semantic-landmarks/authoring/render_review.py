"""Render author-only reference overlays; never copied into agent environment."""
from pathlib import Path
import json,numpy as np,nibabel as nib
from PIL import Image,ImageDraw
B=Path(__file__).resolve().parents[3]/'runs/br036-semantic-landmarks'
for c in json.loads((B/'curation.json').read_text())['cases']:
 ni=nib.load(B/'tasks'/c['case']/'environment/volume.nii.gz');a=np.asarray(ni.dataobj);panels=[]
 for name,v in c['points_voxel'].items():
  v=np.rint(v).astype(int);row=Image.new('RGB',(900,330));d=ImageDraw.Draw(row);d.text((10,5),name,fill='white')
  for axis in range(3):
   sl=np.take(a,v[axis],axis=axis);low,high=(-200,1200) if c['case'].startswith('ct') else np.percentile(a[a>0],[2,99])
   im=Image.fromarray(np.uint8(np.clip((sl-low)/(high-low),0,1)*255)).convert('RGB');axes=[k for k in range(3) if k!=axis]
   dr=ImageDraw.Draw(im);y,x=[v[k] for k in axes];dr.ellipse((x-3,y-3,x+3,y+3),outline='red',width=1)
   im.thumbnail((295,295));row.paste(im,(300*axis,25))
  panels.append(row)
 out=Image.new('RGB',(900,330*len(panels)))
 for i,p in enumerate(panels):out.paste(p,(0,i*330))
 out.save(B/f"{c['case']}-reference.png")
