"""Public CT reslicing and anonymous mask overlays in physical LPS millimetres."""
import argparse
import json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from inspect_scene import load_scene,PALETTE

PLANES={'axial':(0,1,2,1,'R','L','A','P'),
        'coronal':(0,2,1,-1,'R','L','S','I'),
        'sagittal':(1,2,0,-1,'A','P','S','I')}

def transform(p,a):
    return np.sum(p[...,None,:]*a[:3,:3],axis=-1)+a[:3,3]

def sample(array,a,q,background):
    ijk=np.rint(transform(q,np.linalg.inv(a))).astype('int32')
    valid=np.all((ijk>=0)&(ijk<np.array(array.shape)),axis=-1)
    out=np.full(q.shape[:-1],background,dtype=array.dtype)
    out[valid]=array[tuple(ijk[valid].T)]
    return out

def bounds(objects):
    p=np.concatenate([o['surface_lps'] for o in objects]);return p.min(0),p.max(0)

def render_slice(ct,affine,objects,plane,at,center=None,span=None,level=50,width=400,size=500,overlay=True):
    h,v,k,sign,left,right,top,bottom=PLANES[plane]
    lo,hi=bounds(objects)
    center=(lo+hi)/2 if center is None else np.asarray(center,dtype=float)
    span=float(max(hi[h]-lo[h],hi[v]-lo[v])+60 if span is None else span)
    q=np.zeros((size,size,3));q[:]=center;q[:,:,k]=at
    axis=np.linspace(-span/2,span/2,size)
    q[:,:,h]=center[h]+axis[None,:];q[:,:,v]=center[v]+sign*axis[:,None]
    hu=sample(ct,affine,q,-1024)
    gray=np.uint8(np.clip((hu-(level-width/2))/width,0,1)*255)
    rgb=np.repeat(gray[:,:,None],3,axis=2);labels=[]
    for o in objects:
        mask=sample(o['mask'],o['affine_lps'],q,False)
        if not mask.any():continue
        if overlay:
            edge=mask.copy();edge[1:-1,1:-1]&=~(mask[:-2,1:-1]&mask[2:,1:-1]&mask[1:-1,:-2]&mask[1:-1,2:])
            rgb[edge]=tuple(bytes.fromhex(PALETTE[o['color_index']%len(PALETTE)][1:]))
        labels.append(o['object_id'])
    im=Image.fromarray(rgb);d=ImageDraw.Draw(im);font=ImageFont.load_default(size=16)
    for xy,text in [((size/2-5,4),top),((size/2-5,size-22),bottom),((4,size/2),left),((size-20,size/2),right)]:
        box=d.textbbox(xy,text,font=font);d.rectangle(box,fill='black');d.text(xy,text,font=font,fill='white')
    return im,labels

def contact_sheet(ct,affine,objects,path,plane,positions,level=50,width=400,span=None,overlay=True,size=500):
    cols=min(3,len(positions));rows=(len(positions)+cols-1)//cols
    canvas=Image.new('RGB',(cols*size,rows*(size+52)),(18,23,30));d=ImageDraw.Draw(canvas);font=ImageFont.load_default(size=16)
    for j,at in enumerate(positions):
        im,labels=render_slice(ct,affine,objects,plane,at,span=span,level=level,width=width,size=size,overlay=overlay)
        x=(j%cols)*size;y=(j//cols)*(size+52);canvas.paste(im,(x,y+45))
        d.text((x+8,y+2),f'{plane} {at:.1f} mm | L {level:g} W {width:g}',font=font,fill='white')
        d.text((x+8,y+22),', '.join(labels) if overlay else 'CT only',font=font,fill='white')
    path.parent.mkdir(parents=True,exist_ok=True);canvas.save(path)

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--data',type=Path,default=Path('/app/data'))
    ap.add_argument('--objects',help='Comma-separated IDs; all objects if omitted');ap.add_argument('--plane',choices=PLANES,default='axial')
    ap.add_argument('--positions',help='Comma-separated physical LPS slice positions (mm); default five across selected objects')
    ap.add_argument('--level',type=float,default=50);ap.add_argument('--width',type=float,default=400)
    ap.add_argument('--span',type=float,help='Square field of view in mm; default object bounds plus 60 mm')
    ap.add_argument('--no-overlay',action='store_true');ap.add_argument('--out',type=Path,default=Path('/app/ct-focus.png'))
    a=ap.parse_args();objects=load_scene(a.data)
    if a.objects:
        wanted=set(a.objects.split(','));objects=[o for o in objects if o['object_id'] in wanted]
        assert len(objects)==len(wanted),'Unknown or repeated IDs'
    with np.load(a.data/'ct.npz',allow_pickle=False) as z:ct=z['hu'];affine=z['affine_lps']
    lo,hi=bounds(objects);axis=PLANES[a.plane][2]
    positions=[float(x) for x in a.positions.split(',')] if a.positions else np.linspace(lo[axis],hi[axis],7)[1:-1].tolist()
    assert a.width>0 and (a.span is None or a.span>0) and 0<len(positions)<=30
    contact_sheet(ct,affine,objects,a.out,a.plane,positions,a.level,a.width,a.span,not a.no_overlay)
    print(json.dumps({'output':str(a.out),'plane':a.plane,'positions_mm':positions,'objects':[o['object_id'] for o in objects]}))

if __name__=='__main__':main()
