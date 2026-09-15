"""Create local orthogonal CT contacts and source-mask inventories for author review."""
import argparse,json
from pathlib import Path
import numpy as np
import nibabel as nib
from PIL import Image,ImageDraw

FOCUS=['lung_upper_lobe_left','lung_lower_lobe_left','lung_upper_lobe_right','lung_middle_lobe_right','lung_lower_lobe_right','heart','spleen','kidney_left','kidney_right','liver','rib_right_7','rib_right_8']

def tile(arr, low,high):
    a=np.clip((arr.astype(float)-low)/(high-low)*255,0,255).astype('uint8')
    im=Image.fromarray(np.flipud(a.T)).convert('RGB'); im.thumbnail((400,430))
    return im

def screen(path,out):
    img=nib.as_closest_canonical(nib.load(path/'ct.nii.gz'))
    ct=np.asarray(img.dataobj); stats={}; masks={}
    for label in FOCUS:
        m=nib.as_closest_canonical(nib.load(path/'segmentations'/f'{label}.nii.gz'))
        mask=np.asarray(m.dataobj)>0; idx=np.argwhere(mask); masks[label]=mask
        stats[label]={'voxels':len(idx),'bbox':[[int(x) for x in idx.min(axis=0)],[int(x) for x in idx.max(axis=0)]] if len(idx) else None}
    out.mkdir(parents=True,exist_ok=True)
    (out/f'{path.name}-stats.json').write_text(json.dumps({'shape':ct.shape,'affine':img.affine.tolist(),'labels':stats},indent=2)+'\n')
    points=[(int(ct.shape[0]*q),int(ct.shape[1]*.5),int(ct.shape[2]*.5)) for q in [.35,.5,.65]]
    canvas=Image.new('RGB',(1200,960),'#111111');d=ImageDraw.Draw(canvas)
    for col,(x,y,z) in enumerate(points):
        for row,window in enumerate([(-180,250),(-1000,300)]):
            im=tile(ct[:,int(ct.shape[1]*[.35,.5,.65][col]),:],*window)
            canvas.paste(im,(col*400,row*470+30));d.text((col*400+8,row*470+8),f'{path.name} coronal y={int(ct.shape[1]*[.35,.5,.65][col])} {window}',fill='white')
    canvas.save(out/f'{path.name}-contact.png')
    print(path.name,json.dumps(stats),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('subjects',nargs='+');a=p.parse_args()
    for subject in a.subjects:screen(a.root/subject,a.output)
