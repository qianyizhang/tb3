"""Curator-only source-region views. These figures are never solver inputs."""
from pathlib import Path
import argparse,json
import numpy as np
import nibabel as nib
import pydicom
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[3];B=ROOT/'runs/br037-longitudinal-reading'
def scaled(a,lo=None,hi=None,size=400):
 if lo is None:lo,hi=np.percentile(a,[1,99.7])
 im=Image.fromarray(np.uint8(np.clip((a-lo)/max(hi-lo,1),0,1)*255)).convert('RGB');im=im.transpose(Image.Transpose.FLIP_TOP_BOTTOM);im.thumbnail((size,size));return im
def main(case):
 m=json.loads((B/'prepared'/case/'manifest.json').read_text());truth=next(x for x in json.loads((B/'grounding.json').read_text()) if x['case']==case)
 out=B/'review';out.mkdir(exist_ok=True);canvas=Image.new('RGB',(1600,900),(18,18,18));draw=ImageDraw.Draw(canvas);stats=[]
 for n,ref in enumerate(truth['references']):
  choices=[s for s in m['series'] if s['visit']==ref['visit'] and any(k in s['sequence'].lower() for k in ['vibrant','ethrive'])]
  d=pydicom.dcmread(B/ref['source'],stop_before_pixels=True);inds=list(map(int,d[(0x117,0x1035)].value))
  if len(choices)==1:
   s=choices[0];ni=nib.load(B/'prepared'/case/s['file']);raw=np.asarray(ni.dataobj);arrays=[raw[:,:,:,i] for i in inds]
  else:
   assert len(choices)==8,(case,len(choices));s=choices[inds[1]];ni=nib.load(B/'prepared'/case/s['file']);arrays=[np.asarray(nib.load(B/'prepared'/case/choices[i]['file']).dataobj) for i in inds]
  center=nib.affines.apply_affine(np.linalg.inv(ni.affine),ref['voi_center_ras_mm']);i,j,k=np.round(center).astype(int);rad=np.ceil(35/nib.affines.voxel_sizes(ni.affine)[:2]).astype(int)
  crops=[a[max(0,i-rad[0]):i+rad[0],max(0,j-rad[1]):j+rad[1],k].T for a in arrays]
  pre,early,late=arrays;sub=(early-pre)[:,:,k].T;lo,hi=np.percentile(np.stack(crops),[1,99.5]);views=[scaled(sub),*[scaled(x,lo,hi) for x in crops]]
  labels=['Full bilateral early minus pre','Reference region: pre','Reference region: early','Reference region: late']
  for col,(im,label) in enumerate(zip(views,labels)):
   x=col*400;y=n*450;canvas.paste(im,(x,y+35));draw.text((x+5,y+5),f'{case} {ref["visit"]} | {label}',fill='white')
  stats.append(dict(visit=ref['visit'],series=s['id'],native_center_voxel=center.tolist(),phases=inds,source_ftv_cc=ref['ftv_cc'],laterality=ref['laterality']))
 canvas.save(out/f'{case}-source-region.png');(out/f'{case}-source-region.json').write_text(json.dumps(stats,indent=2)+'\n')
 print(case,'review ready')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('case');a=p.parse_args();main(a.case)
