"""Actual source/reference CT panels for author visibility review only."""
import json
from pathlib import Path
import numpy as np
from scipy.ndimage import map_coordinates
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'runs/br024-harder-registration'


def patch(values):
    im = Image.fromarray(np.rint(np.clip((values+1000)/1200,0,1)*255).astype('uint8')).convert('RGB').resize((170,170))
    d = ImageDraw.Draw(im); d.line((79,85,91,85),fill='#ffa666'); d.line((85,79,85,91),fill='#ffa666')
    return im


def main():
    screen = json.loads((OUT/'screen.json').read_text())
    for case in screen['cases']:
        for c in case['candidates']:
            public = ROOT/c['public_path'];g=json.loads((public/'view.json').read_text());q=json.loads((public/'queries.json').read_text())
            truth=json.loads((ROOT/c['truth_path']).read_text());view=np.load(public/'view.npy')
            with np.load(public/'volume.npz') as z:vol=z['hu'];a=z['voxel_to_world']
            yy,xx=np.mgrid[-32:33,-32:33];off=np.array([xx.ravel(),yy.ravel()])*.65
            basis=np.array(g['slice_to_world'])[:3,:2]
            canvas=Image.new('RGB',(760,830),'#15201e');draw=ImageDraw.Draw(canvas)
            draw.text((12,10),c['name']+' | source then manual target | same nominal orientation, 41.6 mm FoV',fill='white')
            for i,(pixel,target) in enumerate(zip(q['pixels_uv'],truth['points_world_mm'])):
                coords=np.array(pixel)[:,None]+off/np.array(g['spacing_xy_mm'])[:,None]
                src=map_coordinates(view,coords[::-1],order=1,mode='constant',cval=-1000).reshape(65,65)
                world=np.array(target)[:,None]+np.einsum('ij,jn->in',basis,off)
                vox=np.einsum('ij,jn->in',np.linalg.inv(a[:3,:3]),world-a[:3,3,None])
                tar=map_coordinates(vol,vox,order=1,mode='constant',cval=-1000).reshape(65,65)
                x=12+(i%2)*380;y=48+(i//2)*193
                draw.text((x,y-16),q['query_ids'][i],fill='#e4ba82')
                canvas.paste(patch(src),(x,y));canvas.paste(patch(tar),(x+180,y))
            canvas.save(public.parent/'source-target-review.png')
    print('Saved six visibility review panels')


if __name__ == '__main__':
    main()
