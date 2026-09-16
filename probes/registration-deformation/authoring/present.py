"""Local interactive review of actual CT pixels and sparse correspondence errors."""
import base64
import io
import json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import map_coordinates
from score import score

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'runs/br021-deformable'
def read(p):return json.loads(p.read_text())
def png(values):
    im=Image.fromarray(np.rint(np.clip((values+1000)/1200,0,1)*255).astype('uint8')).convert('RGB')
    draw=ImageDraw.Draw(im);c=(np.array(im.size)-1)/2
    draw.line((c[0]-5,c[1],c[0]+5,c[1]),fill='#ffae6a');draw.line((c[0],c[1]-5,c[0],c[1]+5),fill='#ffae6a')
    buffer=io.BytesIO();im.save(buffer,format='PNG');return 'data:image/png;base64,'+base64.b64encode(buffer.getvalue()).decode()


def main():
    author=OUT/'author';truth=read(author/'truth.json');queries=read(author/'public-2d/queries.json');g=read(author/'public-2d/view.json')
    view=np.load(author/'public-2d/view.npy');basis=np.array(g['slice_to_world'])[:3,:2]
    with np.load(author/'public-2d/volume.npz') as z:hu=z['hu'];a=z['voxel_to_world']
    yy,xx=np.mgrid[-48:49,-48:49];offset=np.array([xx.ravel(),yy.ravel()])*.65
    def destination(point):
        world=np.array(point)[:,None]+np.einsum('ij,jn->in',basis,offset)
        ijk=np.einsum('ij,jn->in',np.linalg.inv(a[:3,:3]),world-a[:3,3,None])
        return png(map_coordinates(hu,ijk,order=1,prefilter=False,mode='constant',cval=-1000).reshape(97,97))
    data={'ids':truth['query_ids'],'source':[],'manual':[destination(p) for p in truth['points_world_mm']],'methods':{}}
    for pixel in queries['pixels_uv']:
        coords=np.array(pixel)[:,None]+offset/np.array(g['spacing_xy_mm'])[:,None]
        data['source'].append(png(map_coordinates(view,coords[::-1],order=1,prefilter=False,mode='constant',cval=-1000).reshape(97,97)))
    rows=read(OUT/'results.json')['rows'] if (OUT/'results.json').exists() else []
    for row in rows:
        if row['phase']!='terra-high' or not row.get('answer_path'):continue
        answer=read(ROOT/row['answer_path']);kind=row['task'].removeprefix('deform-')
        data['methods'][f'Terra / {kind.upper()}']={'grade':score(answer,truth),'seconds':row['agent_seconds'],
            'images':[destination(p) for p in answer['points_world_mm']], 'execution':row['execution']}
    for kind in ['2d','3d']:
        answer=read(author/f'isolated/{kind}/points.json');log=read(author/f'isolated/{kind}/points.log.json')
        data['methods'][f'Author baseline / {kind.upper()}']={'grade':score(answer,truth),'seconds':log['elapsed_s'],
            'images':[destination(p) for p in answer['points_world_mm']],'execution':'completed'}
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>BR-021 · Respiratory deformation</title>
<style>body{margin:0;background:#131922;color:#edf1f6;font:16px/1.55 system-ui,sans-serif}main{max-width:1120px;margin:auto;padding:42px 28px}h1{font-size:36px;line-height:1.15;margin:8px 0 18px}p{max-width:920px;color:#b7c4d4}.eyebrow{color:#69d1c5;font-size:13px;letter-spacing:.12em}.controls{display:flex;gap:18px;align-items:center;flex-wrap:wrap;margin:28px 0 16px}select,button{background:#223043;color:#edf1f6;border:1px solid #40536d;border-radius:8px;padding:10px;font:inherit}button{cursor:pointer}button.active{background:#236459;border-color:#69d1c5}#queries{display:flex;gap:8px;flex-wrap:wrap}.triplet{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin-top:26px}.triplet img{width:100%;aspect-ratio:1;border:1px solid #3b475b;background:black}.label{font-size:14px;color:#bdc9d8;margin-bottom:8px}#stats{padding:18px 0;font-size:19px}#error{font-weight:700;color:#ffbc84}.small{font-size:13px;color:#9eafc5}.barrow{display:flex;align-items:center;gap:12px;margin:8px 0}.track{height:13px;background:#29374b;flex:1;max-width:600px;position:relative;border-radius:4px}.bar{height:13px;background:#58b8a7;border-radius:4px}.mark{position:absolute;left:50%;top:-3px;height:19px;border-left:1px dashed #c7d0df}a{color:#85dacc}section{margin-top:36px;padding-top:24px;border-top:1px solid #334255}@media(max-width:700px){.triplet{grid-template-columns:1fr}h1{font-size:28px}}</style>
<main><div class="eyebrow">BR-021 · LOCAL RESEARCH REVIEW</div><h1>Same anatomy. A different breath.</h1>
<p>Eight manually matched landmarks from a real inhale/exhale CT pair. The 2D task receives one oblique exhale view and its nominal acquisition geometry; the 3D task receives both volumes. Both return the same eight corresponding inhale positions.</p>
<div class="controls"><label>Result <select id="method"></select></label><span id="status"></span></div><div id="stats"></div><div id="queries"></div>
<div class="triplet"><div><div class="label">Exhale query · supplied 2D anatomy</div><img id="source" alt="Exhale query patch"></div><div><div class="label">Inhale · manual reference position</div><img id="manual" alt="Inhale manual correspondence"></div><div><div class="label">Inhale · submitted position</div><img id="prediction" alt="Inhale submitted correspondence"></div></div>
<p id="error"></p><p class="small">Actual CT pixels, a 62.4 mm square field of view, identical display orientation and window. The cross marks each patch centre. Breathing changes local shape and orientation, so pixel identity is not expected. Black borders in source patches can reflect the supplied view boundary.</p>
<section><h2>Per-landmark distance</h2><div id="bars"></div><p class="small">Dashed line: 5 mm maximum-point limit. The complete answer must also have RMS error ≤3 mm.</p></section>
<section><h2>What this comparison establishes</h2><p>The best truth-assisted rigid fit leaves 5.42–5.46 mm RMS error on these queries; even a global affine fit exceeds the 3 mm RMS limit. Local deformation is required. Author baselines pass using image patch matching without correspondence annotations.</p>
<p>These are sparse correspondence diagnostics on one selected public case, not clinical validation or an estimate of general success rate. They do not verify deformation between landmarks. The source frame is supplied in 2D; recovering an unknown frame would be another condition.</p>
<p class="small">Source: <a href="https://learn2reg.grand-challenge.org/Datasets/">Learn2Reg LungCT 1.11</a>, Hering, Murphy and van Ginneken (2020), <a href="https://doi.org/10.5281/zenodo.3835682">Zenodo</a>, CC BY 4.0. Challenge reference: <a href="https://arxiv.org/abs/2112.04489">Hering et al., Learn2Reg</a>. Radboud University Medical Center. Preprocessed dataset-world coordinates. Original source annotations are public; leakage assessment relies on image and recorded-trace audits.</p></section></main>
<script>const data=__DATA__;let selected=0;const select=document.getElementById('method');Object.keys(data.methods).forEach(name=>select.add(new Option(name,name)));if(data.methods['Terra / 2D'])select.value='Terra / 2D';const queries=document.getElementById('queries');data.ids.forEach((id,i)=>{const b=document.createElement('button');b.textContent=id;b.onclick=()=>{selected=i;render()};queries.append(b)});function render(){const m=data.methods[select.value],g=m.grade;const span=Math.max(10,Math.ceil(g.max_mm/5)*5);document.getElementById('status').textContent=m.execution+' · '+(g.reward?'PASS':'FAIL');document.getElementById('stats').textContent=`RMS ${g.rms_mm.toFixed(2)} mm · Maximum ${g.max_mm.toFixed(2)} mm · ${m.seconds.toFixed(1)} s`;document.getElementById('source').src=data.source[selected];document.getElementById('manual').src=data.manual[selected];document.getElementById('prediction').src=m.images[selected];document.getElementById('error').textContent=`${data.ids[selected]}: ${g.per_point_mm[selected].toFixed(2)} mm from the manual reference`;[...queries.children].forEach((b,i)=>b.classList.toggle('active',i===selected));document.getElementById('bars').innerHTML=g.per_point_mm.map((e,i)=>`<div class="barrow"><span>${data.ids[i]}</span><div class="track"><div class="bar" style="width:${e/span*100}%;background:${e>5?'#e18972':'#58b8a7'}"></div><i class="mark" style="left:${5/span*100}%"></i></div><span>${e.toFixed(2)} mm</span></div>`).join('')+`<div class="small">Bar scale: 0–${span} mm</div>`}select.onchange=render;render();</script></html>'''
    dest=OUT/'review';dest.mkdir(exist_ok=True)
    (dest/'index.html').write_text(page.replace('__DATA__',json.dumps(data)))
    if 'Terra / 2D' in data['methods']:
        method=data['methods']['Terra / 2D']
        missed=[i for i,e in enumerate(method['grade']['per_point_mm']) if e>5]
        if missed:
            canvas=Image.new('RGB',(790,100+len(missed)*238),'#141c26');draw=ImageDraw.Draw(canvas)
            draw.text((15,15),f'2D agent: {len(missed)} missed correspondences',fill='white')
            for x,label in [(36,'Exhale query'),(290,'Inhale manual reference'),(545,'Inhale agent position')]:
                draw.text((x,58),label,fill='#cad7e8')
            for row,i in enumerate(missed):
                for col,uri in enumerate([data['source'][i],data['manual'][i],method['images'][i]]):
                    patch=Image.open(io.BytesIO(base64.b64decode(uri.split(',')[1]))).resize((210,210))
                    canvas.paste(patch,(30+col*255,85+row*238))
                draw.text((30,85+row*238+214),data['ids'][i],fill='white')
                draw.text((540,85+row*238+214),f"Error: {method['grade']['per_point_mm'][i]:.2f} mm",fill='#ffad7a')
            canvas.save(dest/'failures.png')
    print(dest/'index.html')


if __name__=='__main__':main()
