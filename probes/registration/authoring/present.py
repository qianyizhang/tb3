"""Render a local source/recovery comparison from completed evidence."""
import html
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from reslice import render

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'runs/br019-registration'

def main():
    results=json.loads((OUT/'results.json').read_text())
    freeze=json.loads((OUT/'freeze.json').read_text())
    dest=OUT/'review';dest.mkdir(exist_ok=True)
    font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',20)
    small=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',16)
    canvas=Image.new('RGB',(1080,930),(14,20,30));d=ImageDraw.Draw(canvas)
    d.text((24,20),'BR-019  |  Oblique CT slice registration',font=font,fill='white')
    d.text((24,52),'One real CT. Reference image vs. independent numerical and agent recoveries.',font=small,fill='#becbda')
    cards=[]
    for index,task in enumerate(freeze['tasks']):
        name=task['task'];base=ROOT/task['task_path'];data=base/'environment/data'
        with np.load(data/'volume.npz') as z:hu=z['hu'];a=z['voxel_to_lps']
        geometry=json.loads((data/'image.json').read_text());target=np.load(data/'target.npy')
        baseline=json.loads((OUT/'author'/f'{name[-3:]}-baseline.json').read_text())
        im=render(hu,a,baseline['slice_to_lps'],geometry['shape'],geometry['spacing_xy_mm'])
        ar=results['author_public_input_baselines'][name]
        rows=[r for r in results['rows'] if r['task']==name and r['phase']=='terra-high']
        row=rows[0] if rows else None
        views=[('Target',target,f"{target.shape[1]} x {target.shape[0]} | 0.9 mm/pixel"),
               ('Author public-input solver',im,f"RMS {ar['grade']['rms_mm']:.6f} mm | {ar['seconds']:.2f} s execution")]
        if row and row.get('answer_path'):
            ans=json.loads((ROOT/row['answer_path']).read_text())
            recovered=render(hu,a,ans['slice_to_lps'],geometry['shape'],geometry['spacing_xy_mm'])
            grade=row['grade'];text=f"RMS {grade['rms_mm']:.4f} mm | {row['agent_seconds']:.1f} s agent"
            views.append(('Terra / high',recovered,text));Image.fromarray(recovered).save(dest/f'{name}-terra.png')
        else:views.append(('Terra / high',np.zeros_like(target),'Pending' if not row else row['execution']))
        y=100+index*380
        d.text((24,y),f"{name.upper()}  {'Full view' if index==0 else 'Partial view'}",font=font,fill='#70dfc4')
        for j,(label,array,caption) in enumerate(views):
            x=24+j*356; d.text((x,y+34),label,font=small,fill='white')
            pic=Image.fromarray(array).convert('RGB').resize((280,280),Image.Resampling.NEAREST)
            canvas.paste(pic,(x,y+60));d.text((x,y+346),caption,font=small,fill='#becbda')
        Image.fromarray(target).save(dest/f'{name}-target.png')
        cards.append({'task':name,'row':row,'baseline':ar})
    d.text((24,880),'Tolerance: RMS <= 3 mm and maximum <= 5 mm. Same-source texture is a strong matching cue.',font=small,fill='#becbda')
    d.text((24,906),'Apex-oriented feasibility view; not an expert-certified standard cardiac plane.',font=small,fill='#becbda')
    canvas.save(dest/'comparison.png')
    lines=[]
    for card in cards:
        row=card['row'];name=card['task']
        lines.append(f'<article><h2>{name}</h2>')
        if row and row.get('grade'):
            g=row['grade'];lines.append(f'<p><strong>{"PASS" if g["reward"] else "FAIL"}</strong> · RMS {g.get("rms_mm",float("nan")):.4f} mm · max {g.get("max_mm",float("nan")):.4f} mm · {row["agent_seconds"]:.1f} s</p>')
            if row.get('answer_path'):
                lines.append(f'<div class="blend"><img src="{name}-target.png"><img class="over" src="{name}-terra.png"></div><label>Target ↔ recovered <input type="range" min="0" max="1" value="0.5" step="0.01" oninput="this.parentNode.previousElementSibling.lastElementChild.style.opacity=this.value"></label>')
        else:lines.append('<p>Model result pending.</p>')
        lines.append('</article>')
    page='''<!doctype html><meta charset="utf-8"><title>BR-019 registration review</title>
<style>body{background:#0e141e;color:#edf4fc;font:17px/1.55 system-ui;max-width:1100px;margin:40px auto;padding:0 20px}h1{font-size:36px}a{color:#70dfc4}.wide{width:100%;border-radius:12px}.cards{display:flex;gap:32px}article{flex:1;padding:20px;background:#182331;border-radius:12px}.blend{position:relative;width:320px;height:320px;max-width:100%}.blend img{width:100%;height:100%;image-rendering:pixelated}.over{position:absolute;inset:0;opacity:.5}input{display:block;width:100%}.muted{color:#a9bbce}</style>
<h1>Recovering an oblique CT section</h1><p class="muted">BR-019 · real TotalSegmentator CT · same-acquisition full and partial views</p>
<p>The answer maps image pixel centres into patient LPS millimetres. The hidden verifier measures physical correspondence error across the visible field, independently of image correlation.</p>
<img class="wide" src="comparison.png"><div class="cards">'''+''.join(lines)+'''</div>
<p><strong>Interpretation:</strong> a match here can exploit identical image texture. It does not establish clinical landmark recognition, another-scan registration, or cross-modality performance. This apex-side view is geometrically defined and has no expert standard-plane adjudication.</p>
<p class="muted">Public payload: CT intensities and grid geometry, target pixels/spacing, forward renderer and attribution. Target pose, masks, generator, crop offset and verifier were withheld. One patient; the two conditions are correlated.</p>
<p>Source: <a href="https://zenodo.org/records/10047263">Jakob Wasserthal, TotalSegmentator small v2.0.1</a>, CC BY 4.0. Crop and derived sections created for this pilot.</p>'''
    (dest/'index.html').write_text(page)
    print(dest/'index.html')

if __name__=='__main__':main()
