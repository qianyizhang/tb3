"""Local visual review of the actual derived images, not generated anatomy."""
import base64
import json
from pathlib import Path
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'runs/br020-registration'
sys.path.insert(0,str(ROOT/'probes/registration/authoring'))
from reslice import render


def main():
    result=json.loads((OUT/'results.json').read_text())
    row=next(r for r in result['rows'] if r['phase']=='terra-high')
    assert row.get('answer_path'), 'No submitted pose to render'
    pose=json.loads((ROOT/row['answer_path']).read_text())['slice_to_lps']
    data=OUT/'tasks/recon-r03/environment/data'
    with np.load(data/'volume.npz') as z:hu=z['hu'];a=z['voxel_to_lps']
    target=np.load(data/'target.npy');proposed=render(hu,a,pose,target.shape,(.9,.9))
    review=OUT/'review';review.mkdir(exist_ok=True)
    Image.fromarray(target).save(review/'target.png');Image.fromarray(proposed).save(review/'recovered.png')
    reference=Image.open(OUT/'author/true-pose-B30f.png').copy();reference.save(review/'reference.png')
    font_path='/System/Library/Fonts/Helvetica.ttc'
    title=ImageFont.truetype(font_path,27);body=ImageFont.truetype(font_path,18)
    sheet=Image.new('RGB',(1260,572),'#0e1523');draw=ImageDraw.Draw(sheet)
    draw.text((30,23),'Different CT reconstruction kernels: one frozen registration trial',font=title,fill='#f0f3fa')
    grade=row['grade'];line=f"Terra/high: {'PASS' if row['reward']==1 else 'MISS'}  |  RMS {grade.get('rms_mm',float('nan')):.3f} mm  |  max {grade.get('max_mm',float('nan')):.3f} mm  |  {row['agent_seconds']:.0f} s"
    draw.text((30,65),line,font=body,fill='#91d9d2')
    for i,(label,im,caption) in enumerate([
        ('Target: B50f',Image.fromarray(target),'Hidden second reconstruction'),
        ('B30f at reference pose',reference,'Different pixels even at the correct pose'),
        ('B30f at agent pose',Image.fromarray(proposed),'Rendered from the submitted matrix')]):
        x=30+i*410;draw.text((x,112),label,font=body,fill='white')
        sheet.paste(im.convert('RGB').resize((380,380),Image.Resampling.NEAREST),(x,145))
        draw.text((x,539),caption,font=body,fill='#bcc8d8')
    sheet.save(review/'comparison.png')
    def uri(name):return 'data:image/png;base64,'+base64.b64encode((review/name).read_bytes()).decode()
    html='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>BR-020 registration review</title>
<style>body{background:#0e1523;color:#edf3fb;font:17px/1.6 system-ui;margin:32px auto;max-width:1120px;padding:0 20px}h1{font-size:30px;margin-bottom:8px}.muted{color:#b3c1d3}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}.grid img{width:100%;image-rendering:pixelated}.overlay{width:min(540px,100%);position:relative;line-height:0}.overlay img{width:100%;image-rendering:pixelated}.overlay .top{position:absolute;inset:0;opacity:.5}input{width:min(540px,100%)}@media(max-width:720px){.grid{grid-template-columns:1fr}}</style>
<h1>Registering across CT reconstruction kernels</h1><p>__RESULT__</p><p class="muted">One real NLST B30f/B50f pair. The target is a newly authored oblique cardiac-region section; its pose is withheld. Acceptance: RMS ≤3 mm and maximum ≤5 mm. This is an engineering pilot, not a clinically certified cardiac view.</p>
<div class="grid"><div><h3>Target · B50f</h3><img alt="Sharp-kernel target section" src="__TARGET__"></div><div><h3>Reference pose · B30f</h3><img alt="Soft-kernel image at reference pose" src="__REFERENCE__"></div><div><h3>Agent pose · B30f</h3><img alt="Soft-kernel image at submitted pose" src="__RECOVERED__"></div></div>
<h2>Compare target and recovered section</h2><p>Move the slider to blend between target and recovered rendering. Residual texture differences are expected across kernels.</p><div class="overlay"><img alt="Target image" src="__TARGET__"><img class="top" id="top" alt="Recovered overlay" src="__RECOVERED__"></div><label for="blend">Recovered image opacity: <output id="value">50%</output></label><br><input id="blend" type="range" min="0" max="100" value="50"><script>document.getElementById('blend').addEventListener('input',e=>{document.getElementById('top').style.opacity=e.target.value/100;document.getElementById('value').textContent=e.target.value+'%';});</script>
<p class="muted">Source: National Lung Screening Trial via <a href="https://www.cancerimagingarchive.net/collection/nlst/">TCIA</a>, CC BY 4.0. Geometry matches across 139 slices; acquisition times are removed. Source attribution and TCIA data-use terms must be retained downstream. One trial does not estimate success rate or clinical utility.</p></html>'''
    for key,value in {'__RESULT__':line,'__TARGET__':uri('target.png'),'__REFERENCE__':uri('reference.png'),'__RECOVERED__':uri('recovered.png')}.items():html=html.replace(key,value)
    (review/'index.html').write_text(html)
    print(review/'index.html')


if __name__=='__main__':main()
