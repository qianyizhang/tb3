"""Side-by-side Sol/xhigh and Terra/high, with native three-plane overlays."""
from pathlib import Path
import json,html
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from run_trials import ROOT,B,CASES,task
O=B/'review';O.mkdir(exist_ok=True)
r=json.loads((B/'results.json').read_text());summaries=[];sections=[];md=['# BR-040 — Sol/xhigh landmark comparison','','Same frozen 3D arrays, instructions, coordinate conventions and verifiers as the completed Terra/high runs. Both model and reasoning setting differ. One new Sol/xhigh attempt per condition; no retries.','', '| Input | Model / effort | Localization | Mean error, mm | False outside / absent detections |','|---|---|---|---:|---|']
for case in CASES:
 rows={x['model_setting']:x for x in r['trials'] if x['case']==case};t=ROOT/task(case)['task_path'];truth=json.loads((t/'tests/truth.json').read_text());g=json.loads((t/'environment/geometry.json').read_text());defs=json.loads((t/'environment/landmarks.json').read_text());mri=case.startswith('mri');thresholds=[3,5,10] if mri else [5,10,20]
 refs={k:{'status':'observed','ijk':v} for k,v in truth['points_ijk'].items()} if mri else truth['targets'];visible=sum(v['status']=='observed' for v in refs.values());answers={}
 for model,x in rows.items():
  s=x.get('score',{});valid=s.get('contract_valid') and not x['exception'];counts=x.get('success_counts_mm',{});loc=' / '.join(f'{counts.get(str(q),"—")}/{visible}' for q in thresholds);mean=s.get('mean_mm') if mri else s.get('mean_localized_error_mm');meantext='—' if mean is None else f'{mean:.2f}'
  if not valid:loc='Excluded / invalid';meantext='—'
  if mri:false='Not tested'
  elif valid:false=f"{s['hallucinated']['out_of_fov']}/{s['counts']['out_of_fov']} outside; {s['hallucinated']['absent']}/{s['counts']['absent']} absent"
  else:false='Invalid / infrastructure exclusion'
  summaries.append(f'<tr><td>{case}</td><td>{model}</td><td>{loc} at {thresholds} mm</td><td>{meantext}</td><td>{false}</td></tr>');md.append(f'| {case} | {model} | {loc} at {thresholds} mm | {meantext} | {false} |')
  if valid and x.get('answer_path'):
   a=json.loads((ROOT/x['answer_path']).read_text())['landmarks'];answers[model]={k:{'status':'observed','ijk':v} for k,v in a.items()} if mri else a
 if not answers:continue
 a=np.load(t/'environment/volume.npy',mmap_mode='r');spacing=np.array(g['spacing_ijk_mm']);window=g['display_window'];options=[];table=[]
 for key,gt in refs.items():
  preds={m:v[key] for m,v in answers.items()};centre=gt['ijk'] if gt['status']=='observed' else next((v['ijk'] for v in preds.values() if v['status']=='observed'),None)
  if centre is not None:
   centre=np.array(centre);fig,axs=plt.subplots(1,3,figsize=(13,4),constrained_layout=True)
   for axis,ax in enumerate(axs):
    u,v=[z for z in range(3) if z!=axis];idx=int(round(centre[axis]));sel=[slice(None)]*3;sel[axis]=idx
    ax.imshow(a[tuple(sel)].T,cmap='gray',vmin=window[0],vmax=window[1],origin='lower',extent=[-.5,a.shape[u]-.5,-.5,a.shape[v]-.5],aspect=spacing[v]/spacing[u],interpolation='nearest')
    rad=30 if mri else 50;ax.set_xlim(max(-.5,centre[u]-rad/spacing[u]),min(a.shape[u]-.5,centre[u]+rad/spacing[u]));ax.set_ylim(max(-.5,centre[v]-rad/spacing[v]),min(a.shape[v]-.5,centre[v]+rad/spacing[v]));ax.set_xlabel('ijk'[u]+' voxel');ax.set_ylabel('ijk'[v]+' voxel');ax.set_title(f"{'ijk'[axis]}={idx}")
    if gt['status']=='observed':ax.plot(gt['ijk'][u],gt['ijk'][v],'+',color='lime',ms=13,mew=2)
    for j,(model,color) in enumerate([('terra-high','orange'),('sol-xhigh','#ec6bff')]):
     p=preds.get(model,{}).get('ijk')
     if p is not None:
      ax.plot(p[u],p[v],'x' if j==0 else 'o',color=color,ms=7,mew=1.7,fillstyle='none');ax.text(.01,.99-j*.07,f'{model}: off-plane {(p[axis]-idx)*spacing[axis]:+.1f} mm',transform=ax.transAxes,va='top',color=color,fontsize=8)
   fig.suptitle(f'{case} / {key}: green GT, orange Terra/high, purple Sol/xhigh (projected markers)');fn=f'{case}-{key}.png';fig.savefig(O/fn,dpi=105);plt.close(fig);options.append(f'<option value="{fn}">{html.escape(str(key))}</option>')
  cells=[html.escape(str(key)),html.escape(str(defs.get(key,''))),gt['status']]
  for model in ['terra-high','sol-xhigh']:
   pred=preds.get(model);s=rows.get(model,{}).get('score',{});err=s.get('errors_mm',{}).get(key)
   cells.extend([pred['status'] if pred else 'unavailable','—' if err is None else f'{err:.2f}',html.escape(str(pred.get('ijk'))) if pred else '—'])
  table.append('<tr>'+''.join('<td>'+c+'</td>' for c in cells)+'</tr>')
 first=options[0].split('"')[1] if options else ''
 sections.append(f'''<section><h2>{case}</h2><p>{visible} visible targets; {len(refs)-visible} unavailable requests. Native array shape {g['shape_ijk']}. Positive axes {g['positive_array_axes_patient_directions']}.</p><label>Landmark <select onchange="this.parentElement.nextElementSibling.src=this.value">{''.join(options)}</select></label><img src="{first}"><div class="scroll"><table><tr><th>Key</th><th>Definition</th><th>Reference</th><th>Terra status</th><th>mm</th><th>ijk</th><th>Sol status</th><th>mm</th><th>ijk</th></tr>{''.join(table)}</table></div></section>''')
method_note='<p><b>Interpretation:</b> Sol partial CT missed one visible target (T5) and marked T13 uncertain. Its zero false detections are not perfect coverage. Sol MRI used AFIDs protocol illustrations and a labelled generic MNI template with affine registration, followed by manual review. Its attempted B-spline refinement did not produce proposals. No target-subject annotation retrieval was found in the preserved command/archive audit. MRI image-input counts include reference illustrations.</p>'
page='''<!doctype html><html><meta charset="utf-8"><title>Sol/xhigh CT and MRI landmarks</title><style>body{font:16px system-ui;max-width:1400px;margin:40px auto;padding:0 24px;background:#f6f8fb;color:#172437}section{background:white;border-radius:12px;padding:22px;margin-top:25px}table{border-collapse:collapse;width:100%;font-size:14px}td,th{text-align:left;padding:8px;border-bottom:1px solid #ddd}th{background:#e7edf4}img{display:block;width:100%;margin-top:15px}select{padding:8px}.scroll{overflow:auto}h1{font-size:32px}</style><h1>Sol/xhigh versus Terra/high: CT and MRI landmarks</h1><p>BR-040 · Frozen full-volume inputs → native 3D voxel coordinates · One fresh Sol attempt per condition · Identical earlier oracle/nop controls verified by task hashes.</p><p>This compares both model and effort. Localization denominators include every visible reference point. Mean error covers returned visible points. CT false detections are separated into out-of-FOV and absent-level targets; MRI has no unavailable requests. A 0/0 entry means no such targets, not a population rate.</p><table><tr><th>Input</th><th>Model / effort</th><th>Localization success</th><th>Mean mm</th><th>False detections</th></tr>'''+''.join(summaries)+'''</table><p>Green reference; orange Terra; purple Sol. Markers are projected onto each reference slice: off-plane offsets are printed on the panels. Scores use full 3D physical distances, never screenshot pixels. One CT subject with paired views and one MRI subject; the partial CT lacks a cranial enumeration anchor. These are pilot outcomes.</p>'''+method_note+''.join(sections)+'</html>'
(O/'index.html').write_text(page)
md+=['','CT false detections distinguish outside centres from genuinely absent T13/L6 under the source numbering convention. MRI has all 32 reference targets inside the scan; MRI hallucination was not tested. Each localization denominator includes all visible targets. The 0/0 full-CT outside entry means no such requests.','', '## Verification','', 'Frozen file hashes were checked before and after each run. Sol task checksums must equal completed same-byte oracle, nop and Terra controls. The host scorer replays the frozen verifier; physical distances are independently recomputed in world coordinates. Trace audits retain actual image input counts and candidate network commands.','', '## Limits','', 'One CT subject with two correlated views, one MRI subject, one attempt per condition and model. Sol/xhigh versus Terra/high changes both model and effort. CT labels follow the source convention; partial coverage can make enumeration uncertain. Exact reward alone is not a clinical or population capability claim.','', '## Evidence','', '- [Plan](BR-040-sol-landmarks.md)','- [Comparison data and trace audit](../evidence/br040-results.json)','- [Frozen inputs and control checksums](../evidence/br040-plan.json)','- Local comparison with per-landmark overlays: `runs/br040-sol-landmarks/review/index.html`.','']
md+=['## Interpretation and methods','','Sol partial CT missed the visible T5 centre and marked T13 uncertain. It made no observed claims for unavailable targets; this does not equal perfect coverage. The mean 7.44 mm covers its 12 returned visible points, while localization success uses all 13 reference points.','','Full CT improved substantially at 10/20 mm and in mean error, but its 5 mm count was 1/24 versus Terra 2/24. These endpoints should not be collapsed into a claim that Sol won every metric.','','Sol MRI used AFIDs protocol illustrations and a labelled generic MNI152NLin2009cAsym template with affine registration, followed by manual review. B-spline refinement first failed, then was terminated without reported proposal files. The agent completed normally afterward. This is allowed atlas-assisted agent performance, not unaided visual localization. No target-subject annotation retrieval was found in the preserved commands or copied archive audit; the AFIDs index exposed dataset URLs but contained no subject FCSV files.','','[Source assistance audit](../evidence/br040-source-audit.json) · [Configuration difference audit](../evidence/br040-config-audit.json) · [CT mask diagnostic](../evidence/br040-ct-diagnostic.json). The mask diagnostic does not alter the frozen score.','']
(ROOT/'docs/research-rounds/BR-040-results.md').write_text('\n'.join(md));print(O/'index.html')
