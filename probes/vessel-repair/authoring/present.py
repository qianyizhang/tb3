"""Local native-slice author review; no source truth copied to solver inputs."""
import json
from pathlib import Path
import nibabel as nib
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'runs/br026-vessel-repair'
task=BASE/'tasks/vessel-v01'
record=json.loads((BASE/'prepared.json').read_text())['tasks'][0]
centre=np.array(record['generation']['center_ijk'])
image=nib.load(task/'environment/data/image.nii.gz');data=np.asarray(image.dataobj)
with np.load(task/'tests/truth.npz') as z:
    truth=z['gt'];original=z['original'];spacing=z['spacing']
canvas=Image.new('RGB',(1090,1060),'#111820');draw=ImageDraw.Draw(canvas)
font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',20)
small=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',15)
draw.text((18,14),'BR-026: native MRA sections through the authored gap',font=font,fill='white')
draw.text((18,43),'Left: image. Middle: proposed mask. Right: source reference. Orange marks the deleted voxels.',font=small,fill='#c7d1db')
low,high=0,float(np.percentile(data[truth],99))
for row,axis in enumerate([2,1,0]):
    dims=[k for k in range(3) if k!=axis]
    width=np.array([8,8,6])/spacing
    slices=[slice(max(0,int(c-r)),min(s,int(c+r)+1)) for c,r,s in zip(centre,width,data.shape)]
    slices[axis]=int(centre[axis]);key=tuple(slices)
    raw=data[key].T;gt=truth[key].T;pred=original[key].T
    gray=(np.clip((raw-low)/(high-low),0,1)*255).astype('uint8')
    rgb=np.repeat(gray[...,None],3,axis=2)
    for col,mask in enumerate([None,pred,gt]):
        arr=rgb.copy()
        if mask is not None:arr[mask]=(.45*arr[mask]+.55*np.array([42,206,214])).astype('uint8')
        if col==1:
            missed=gt&~pred;arr[missed]=(.3*arr[missed]+.7*np.array([255,156,39])).astype('uint8')
        tile=Image.fromarray(arr).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        aspect=spacing[dims[1]]/spacing[dims[0]]
        wanted=(tile.width,round(tile.height*aspect));scale=min(340/wanted[0],275/wanted[1])
        tile=tile.resize((round(wanted[0]*scale),round(wanted[1]*scale)),Image.Resampling.NEAREST)
        x=18+col*359+(340-tile.width)//2;y=105+row*310
        canvas.paste(tile,(x,y))
    draw.text((18,77+row*310),['Axial','Coronal','Sagittal'][row]+f' / source slice index {centre[axis]} in crop',font=small,fill='white')
draw.text((18,1023),'Engineering image review only; the reference is an annotation, not independent clinical adjudication.',font=small,fill='#c7d1db')
canvas.save(BASE/'native-gap-review.png')
print(BASE/'native-gap-review.png')
