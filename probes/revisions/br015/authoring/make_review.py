"""Answer-free review viewer built exclusively from frozen public V01 inputs."""
import base64
import json
import shutil
import sys
from pathlib import Path
import numpy as np
from PIL import Image
from common import ROOT,OUT,write,sha
sys.path.insert(0,str(ROOT/'probes/revisions/br013/authoring'))
from inspect_scene import load_scene
from inspect_ct import transform

def main():
    source=OUT/'build/abdomen-v01';out=OUT/'review/v01';out.mkdir(parents=True,exist_ok=True)
    for name in ['slices','outlines']:(out/name).mkdir(exist_ok=True)
    scene=load_scene(source);targets=json.loads((source/'targets.json').read_text())
    with np.load(source/'ct.npz') as z:ct=z['hu'];a=z['affine_lps']
    assert np.allclose(a[:3,:3],np.diag(np.diag(a[:3,:3]))) and np.all(np.diag(a)[:3]>0)
    contour=np.zeros(ct.shape,dtype='uint8');payload={'objects':[],'vocabulary':json.loads((source/'vocabulary.json').read_text()),'width':ct.shape[0],'height':ct.shape[1],'slices':ct.shape[2],'z0':a[2,3],'dz':a[2,2]}
    rng=np.random.default_rng(1504)
    for o in scene:
        p=o['surface_lps'];focus=o['object_id']!='context';count=min(len(p),3000 if focus else 9000)
        subset=p[rng.choice(len(p),count,replace=False)];quant=np.rint(subset*10);assert np.max(np.abs(quant/10-subset))<=.0501 and np.max(np.abs(quant))<32768
        q=transform(np.argwhere(o['mask']),o['affine_lps']);row={'id':o['object_id'],'center':q.mean(0).tolist(),'ml':float(len(q)*abs(np.linalg.det(o['affine_lps'][:3,:3]))/1000),'encoded':base64.b64encode(quant.astype('<i2').tobytes()).decode()}
        if focus:
            index=targets.index(o['object_id'])+1;row['index']=index
            m=o['mask'];edge=m.copy();edge[1:-1,1:-1,:]&=~(m[:-2,1:-1,:]&m[2:,1:-1,:]&m[1:-1,:-2,:]&m[1:-1,2:,:])
            xyz=transform(np.argwhere(edge),o['affine_lps']);ijk=np.rint(transform(xyz,np.linalg.inv(a))).astype(int)
            assert np.all((ijk>=0)&(ijk<ct.shape));np.bitwise_or.at(contour,tuple(ijk.T),1<<(index-1))
        payload['objects'].append(row)
    for k in range(ct.shape[2]):
        gray=np.uint8(np.clip((ct[:,:,k].astype(float)+150)/400,0,1)*255)
        Image.fromarray(gray.T).save(out/'slices'/f'{k}.png',compress_level=3)
        Image.fromarray(contour[:,:,k].T).save(out/'outlines'/f'{k}.png',compress_level=3)
    for p in source.glob('*.png'):shutil.copyfile(p,out/p.name)
    template=Path(__file__).with_name('review.template.html').read_text();assert template.count('__DATA__')==1
    (out/'index.html').write_text(template.replace('__DATA__',json.dumps(payload,separators=(',',':'))))
    # Separate answer form defaults are blank. No expected.json, source names or model outputs read.
    (out/'public-data.md').write_text(f'''# Input inventory

This packet contains eight anonymous target masks, the surrounding unlabelled
vasculature, and same-phase CT. Review asks for o307, o609 and o570; source keys
and model results are absent.

Authoritative local public arrays: {source}

The ready command-line tools are in {OUT/'tasks/abdomen-v01/environment'}.
Use inspect_ct.py with --data set to the public-array directory, for different
planes, positions and CT windows. The browser contains every native axial plane
in the CT crop, windowed at 50/400, with independently selectable target outlines.
The three-plane PNG previews and surface samples use the same physical frame.

Source: ColonVessels 2026, Hrubovcak et al., https://zenodo.org/records/17407158 .
CC BY 4.0. No additional surgical or disease history is provided.
''')
    write(OUT/'author/review-packet.json',{'path':str(out.relative_to(ROOT)),'targets_sampled':['o307','o609','o570'],'reference_key_embedded':False,'model_output_embedded':False,'native_axial_planes':ct.shape[2],'html_sha256':sha(out/'index.html'),'public_ct_sha256':sha(source/'ct.npz'),'public_scene_sha256':sha(source/'scene.json')})
    print(f'Prepared answer-free packet with {ct.shape[2]} native axial planes at {out}')

if __name__=='__main__':main()
