"""Public, label-free loader and orthographic renderer for abdominal objects."""
import argparse
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

PALETTE=['#eb8873','#67c2e5','#8ace92','#e8cf72','#b397df','#df83b2','#68cfcb',
         '#e4aa71','#b5ce72','#a6ace8','#e26971','#6d9be0','#cbbca0']

def load_scene(directory):
    directory=Path(directory)
    scene=json.loads((directory/'scene.json').read_text())
    out=[]
    for o in scene['objects']:
        with np.load(directory/o['file'],allow_pickle=False) as z:
            out.append({**o,'mask':z['mask'],'affine_lps':z['affine_lps'],
                        'surface_lps':z['surface_lps']})
    return out

def stats(objects):
    result=[]
    for o in objects:
        a=o['affine_lps'];p=np.argwhere(o['mask'])
        q=sum(p[:,k,None]*a[:3,k] for k in range(3))+a[:3,3]
        result.append({'object_id':o['object_id'],'voxel_count':len(p),
                       'volume_ml':round(float(len(p)*abs(np.linalg.det(a[:3,:3]))/1000),3),
                       'centroid_lps_mm':np.round(q.mean(0),3).tolist(),
                       'min_lps_mm':q.min(0).tolist(),'max_lps_mm':q.max(0).tolist(),
                       'extent_mm':(q.max(0)-q.min(0)+np.linalg.norm(a[:3,:3],axis=0)).tolist()})
    return result

def render(objects,path,yaw=35,pitch=20):
    font=ImageFont.load_default(size=18)
    small=ImageFont.load_default(size=15)
    canvas=Image.new('RGB',(1400,1210),(20,26,33));d=ImageDraw.Draw(canvas)
    d.text((20,10),'Anonymous anatomy | shared LPS coordinates in mm | L=left, P=posterior, S=superior',font=font,fill='white')
    points=[];colors=[]; centers=[]
    for i,o in enumerate(objects):
        p=o['surface_lps'];step=max(1,len(p)//12000);p=p[::step]
        points.append(p);colors.extend([PALETTE[o['color_index']%len(PALETTE)]]*len(p));centers.append(p.mean(0))
    p=np.concatenate(points);mid=(p.min(0)+p.max(0))/2;p=p-mid
    centers=np.array(centers)-mid
    # Columns are screen-right, screen-up, then viewing depth.
    ry=np.array([[np.cos(np.deg2rad(yaw)),0,np.sin(np.deg2rad(yaw))],[0,1,0],[-np.sin(np.deg2rad(yaw)),0,np.cos(np.deg2rad(yaw))]])
    rx=np.array([[1,0,0],[0,np.cos(np.deg2rad(pitch)),-np.sin(np.deg2rad(pitch))],[0,np.sin(np.deg2rad(pitch)),np.cos(np.deg2rad(pitch))]])
    bases=[np.eye(3)[:,[0,2,1]],np.eye(3)[:,[1,2,0]],np.eye(3)[:,[0,1,2]],ry@rx]
    titles=['Coronal: right +L, up +S','Sagittal: right +P, up +S','Axial: right +L, up +P',f'Oblique yaw={yaw}, pitch={pitch}']
    for j,(basis,title) in enumerate(zip(bases,titles)):
        q=p@basis;c=centers@basis
        lo=q[:,:2].min(0);hi=q[:,:2].max(0);middle=(hi+lo)/2
        scale=min(630/max(hi[0]-lo[0],1),470/max(hi[1]-lo[1],1))
        x=20+(j%2)*700;y=65+(j//2)*530
        d.text((x,y-25),title,font=font,fill='white')
        xy=(q[:,:2]-middle)*[scale,-scale]+[x+330,y+240]
        for k in np.argsort(q[:,2]):
            xx,yy=xy[k];d.rectangle((int(xx),int(yy),int(xx)+1,int(yy)+1),fill=colors[k])
        for o,cc in zip(objects,c):
            xx,yy=(cc[:2]-middle)*[scale,-scale]+[x+330,y+240]
            box=d.textbbox((int(xx),int(yy)),o['object_id'],font=small)
            d.rectangle(box,fill=(15,20,26));d.text((int(xx),int(yy)),o['object_id'],font=small,fill='white')
    for i,o in enumerate(objects):
        d.text((20+(i%7)*195,1130+(i//7)*30),o['object_id'],fill=PALETTE[o['color_index']%len(PALETTE)],font=font)
    canvas.save(path)

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--data',type=Path,default=Path('/app/data'))
    ap.add_argument('--objects',help='Comma-separated object IDs; omit to show all')
    ap.add_argument('--out',type=Path,help='Render PNG to this path; omitted means print statistics')
    ap.add_argument('--yaw',type=float,default=35);ap.add_argument('--pitch',type=float,default=20)
    args=ap.parse_args();objects=load_scene(args.data)
    if args.objects:
        wanted=set(args.objects.split(','));objects=[o for o in objects if o['object_id'] in wanted]
        assert len(objects)==len(wanted),'Unknown or repeated selection'
    if args.out: render(objects,args.out,args.yaw,args.pitch)
    else: print(json.dumps(stats(objects),indent=2))
