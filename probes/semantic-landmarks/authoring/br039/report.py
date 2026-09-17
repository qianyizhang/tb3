"""Local review of all 26 requests and paired full/partial CT trials."""
from pathlib import Path
import json,html
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[4];B=ROOT/'runs/br039-ct-landmarks';OUT=B/'review';OUT.mkdir(exist_ok=True)
result=json.loads((B/'results.json').read_text());sections=[]
for r in result['trials']:
 if r['phase']!='terra-high':continue
 case=r['case'];s=r.get('score',{});task=B/'tasks'/case
 if not s.get('contract_valid'):sections.append(f'<h2>{case}</h2><pre>{html.escape(json.dumps(r,indent=2))}</pre>');continue
 a=np.load(task/'environment/volume.npy',mmap_mode='r');g=json.loads((task/'environment/geometry.json').read_text());truth=json.loads((task/'tests/truth.json').read_text());spacing=np.array(g['spacing_ijk_mm']);rows=[];options=[];figures=[]
 for key,row in s['rows'].items():
  gt=truth['targets'][key];pred=row['predicted_ijk'];err=row.get('error_mm');imagefile=None
  centre=gt['ijk'] if gt['status']=='observed' else pred if row['predicted_status']=='observed' else None
  if centre is not None:
   centre=np.array(centre);fig,axs=plt.subplots(1,3,figsize=(13,4),constrained_layout=True)
   for axis,ax in enumerate(axs):
    uv=[i for i in range(3) if i!=axis];u,v=uv;idx=int(round(centre[axis]));sel=[slice(None)]*3;sel[axis]=idx;sl=a[tuple(sel)].T
    ax.imshow(sl,cmap='gray',vmin=-200,vmax=1400,origin='lower',extent=[-.5,a.shape[u]-.5,-.5,a.shape[v]-.5],aspect=spacing[v]/spacing[u],interpolation='nearest')
    ax.set_xlim(centre[u]-45/spacing[u],centre[u]+45/spacing[u]);ax.set_ylim(centre[v]-45/spacing[v],centre[v]+45/spacing[v]);ax.set_xlabel('ijk'[u]+' voxel');ax.set_ylabel('ijk'[v]+' voxel');ax.set_title(f"{'ijk'[axis]}={idx}")
    if gt['status']=='observed':ax.plot(gt['ijk'][u],gt['ijk'][v],'+',color='lime',ms=12,mew=2)
    if pred is not None:
     ax.plot(pred[u],pred[v],'x',color='orange',ms=9,mew=2);ax.text(.01,.99,f'Prediction off-plane: {(pred[axis]-idx)*spacing[axis]:+.1f} mm',transform=ax.transAxes,va='top',color='orange',fontsize=8)
   fig.suptitle(f'{case} / {key}: green reference, orange prediction projection; {err:.2f} mm' if err is not None else f'{case} / {key}: unsupported observed detection')
   imagefile=f'{case}-{key}.png';fig.savefig(OUT/imagefile,dpi=105);plt.close(fig)
   options.append(f'<option value="{imagefile}">{key}</option>')
  rows.append(f'<tr><td>{key}</td><td>{gt["status"]}</td><td>{row["predicted_status"]}</td><td>{"—" if err is None else f"{err:.2f}"}</td><td>{html.escape(str(pred))}</td></tr>')
 c=s['counts'];h=s['hallucinated'];cr=s['correct_rejections']
 sections.append(f'''<section><h2>{case}</h2><p>{c['observed']} visible; {c['out_of_fov']} outside coverage; {c['absent']} absent additional levels.</p>
 <p><b>Invented detections:</b> outside {h['out_of_fov']}/{c['out_of_fov']}; absent {h['absent']}/{c['absent']}. Correct rejections: {cr}. Missed visible: {s['missed_visible']}.</p>
 <p><b>Localization:</b> ≤5 mm {s['success_counts_mm']['5']}/{c['observed']}; ≤10 mm {s['success_counts_mm']['10']}/{c['observed']}; ≤20 mm {s['success_counts_mm']['20']}/{c['observed']}. Mean among returned visible points: {s['mean_localized_error_mm']}. Agent {r.get('agent_seconds',0):.1f} s.</p>
 <p>Confusion matrix: {html.escape(str(s['confusion']))}</p>
 <label>Review landmark: <select onchange="this.parentElement.nextElementSibling.src=this.value">{''.join(options)}</select></label>
 {('<img src="'+options[0].split('"')[1]+'">') if options else '<p>No observed points to display.</p>'}
 <table><thead><tr><th>Target</th><th>Reference status</th><th>Terra status</th><th>Error mm</th><th>Predicted native ijk</th></tr></thead><tbody>{''.join(rows)}</tbody></table></section>''')
summary='<table><tr><th>CT input</th><th>Requested</th><th>Visible</th><th>False outside detections</th><th>Invented absent levels</th><th>Within 5 mm</th></tr>'+''.join(f"<tr><td>{r['case']}</td><td>26</td><td>{r['score']['counts']['observed']}</td><td>{r['score']['hallucinated']['out_of_fov']}/{r['score']['counts']['out_of_fov']}</td><td>{r['score']['hallucinated']['absent']}/2</td><td>{r['score']['success_counts_mm']['5']}/{r['score']['counts']['observed']}</td></tr>" for r in result['trials'] if r['phase']=='terra-high' and r.get('score',{}).get('contract_valid'))+'</table><p>The partial scan falsely labelled a point 2.14 mm from T5 as T4. Neither run invented T13 or L6. A 0/0 cell means no such targets were included.</p>'
page='''<!doctype html><html><meta charset="utf-8"><title>BR-039 — Expanded CT landmarks</title><style>body{font:16px system-ui;max-width:1200px;margin:40px auto;padding:0 24px;background:#f6f8fb;color:#182235}section{background:white;padding:24px;margin:24px 0;border-radius:12px}table{border-collapse:collapse;width:100%;font-size:14px}td,th{text-align:left;padding:7px;border-bottom:1px solid #ddd}img{display:block;width:100%;margin:12px 0}select{padding:8px}h1{font-size:32px}</style>
<h1>26 requested CT landmarks: localization and hallucination</h1><p>BR-039 · Fresh Terra/high · One VerSe subject, two field-of-view conditions · Full 3D intensity arrays → native 3D voxel coordinates.</p>
<p>Source: <a href="https://github.com/anjany/verse">VerSe</a>, subject 823. The source's 7 cervical / 12 thoracic / 5 lumbar convention makes T13 and L6 absent. Partial CT retains native k=0:920. Reference points and masks stayed private. Original intensities were converted losslessly from float64 to int16. Geometry checks and matched oracle/nop controls precede trials.</p>
<p>An explicit out-of-FOV estimate is not an invented observed detection. Uncertain abstentions, mistaken absence/FOV classifications, and missed visible targets are separate. Green/orange markers show projections: read the off-plane offset, rather than assuming both points lie on the displayed slice.</p>
<p>The four-point CT was a pilot. The richer MedPelvis candidate was excluded before trials because its documented coordinate mapping failed the anatomy overlay check. This report uses validated VerSe centres; it does not estimate performance across patients or all anatomical families.</p>'''+summary+''.join(sections)+'</html>'
(OUT/'index.html').write_text(page)
print(OUT/'index.html')
