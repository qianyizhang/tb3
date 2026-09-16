"""Render source and manual corresponding patches for author visibility review."""
import json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import map_coordinates

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'runs/br021-deformable/author'


def main():
    q=json.loads((OUT/'public-2d/queries.json').read_text());g=json.loads((OUT/'public-2d/view.json').read_text())
    truth=json.loads((OUT/'truth.json').read_text());basis=np.array(g['slice_to_world'])[:3,:2]
    view=np.load(OUT/'public-2d/view.npy')
    with np.load(OUT/'public-2d/volume.npz') as z:hu=z['hu'];a=z['voxel_to_world']
    yy,xx=np.mgrid[-24:25,-24:25];offsets=np.array([xx.ravel(),yy.ravel()])*.75
    canvas=Image.new('RGB',(500,8*170+35),'#171c24');draw=ImageDraw.Draw(canvas)
    draw.text((35,10),'Exhale single-view query',fill='white');draw.text((280,10),'Inhale manual correspondence',fill='white')
    for i,(pixel,point) in enumerate(zip(q['pixels_uv'],truth['points_world_mm'])):
        coords=np.array(pixel)[:,None]+offsets/np.array(g['spacing_xy_mm'])[:,None]
        source=map_coordinates(view,coords[::-1],order=1,prefilter=False,mode='constant',cval=-1000)
        world=np.array(point)[:,None]+np.einsum('ij,jn->in',basis,offsets)
        vox=np.einsum('ij,jn->in',np.linalg.inv(a[:3,:3]),world-a[:3,3,None])
        destination=map_coordinates(hu,vox,order=1,prefilter=False)
        for j,patch in enumerate([source,destination]):
            im=Image.fromarray(np.rint(np.clip((patch.reshape(49,49)+1000)/1200,0,1)*255).astype('uint8')).convert('RGB').resize((147,147))
            d=ImageDraw.Draw(im);d.line((67,73,79,73),fill='#ff655c');d.line((73,67,73,79),fill='#ff655c')
            canvas.paste(im,(45+j*245,35+i*170))
        draw.text((4,105+i*170),q['query_ids'][i],fill='white')
    canvas.save(OUT/'manual-correspondence-review.png')


if __name__=='__main__':main()
