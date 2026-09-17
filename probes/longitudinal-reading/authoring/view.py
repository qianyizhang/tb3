"""Generic native-grid image renderer; no case-specific default slices or ROIs."""
import argparse,json
from pathlib import Path
import nibabel as nib
import numpy as np
from PIL import Image,ImageDraw
p=argparse.ArgumentParser();p.add_argument('volume');p.add_argument('--axis',type=int,default=2);p.add_argument('--phase',type=int,default=0);p.add_argument('--slices',default='all');p.add_argument('--subtract-phase',type=int);p.add_argument('--out',required=True);p.add_argument('--columns',type=int,default=5);p.add_argument('--tile',type=int,default=384);a=p.parse_args()
ni=nib.load(a.volume);arr=np.asarray(ni.dataobj,dtype=np.float32)
if arr.ndim==4:
 arr=arr[:,:,:,a.phase]-(arr[:,:,:,a.subtract_phase] if a.subtract_phase is not None else 0)
n=arr.shape[a.axis];ks=list(range(n)) if a.slices=='all' else [int(x) for x in a.slices.split(',')]
lo,hi=np.percentile(arr,[1,99.8]);hi=max(hi,lo+1)
canvas=Image.new('RGB',(a.columns*a.tile,((len(ks)+a.columns-1)//a.columns)*(a.tile+25)),(20,20,20));draw=ImageDraw.Draw(canvas)
for index,k in enumerate(ks):
 sl=np.take(arr,k,axis=a.axis).T;sl=np.flipud(sl)
 im=Image.fromarray(np.uint8(np.clip((sl-lo)/(hi-lo),0,1)*255));im.thumbnail((a.tile,a.tile))
 x=(index%a.columns)*a.tile;y=(index//a.columns)*(a.tile+25);canvas.paste(im,(x,y));draw.text((x+4,y+a.tile+3),f'axis {a.axis} index {k} phase {a.phase}',fill='white')
canvas.save(a.out)
print(json.dumps(dict(output=a.out,shape=list(ni.shape),axis=a.axis,slices=ks,phase=a.phase,display='Native voxel axes; transposed then vertically flipped. Use affine for anatomical laterality.')))
