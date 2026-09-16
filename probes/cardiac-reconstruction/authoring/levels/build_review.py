"""Local trial review. Default 3D playback is an agent submission when available."""
import html
import json
from pathlib import Path
import shutil
import sys
import numpy as np

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
B=ROOT/'runs/br031-cardiac-levels';OLD=ROOT/'runs/br029-dynamic-heart'
sys.path.insert(0,str(HERE.parent/'dynamic_heart'))
from analyze import analyze_model


def main():
    out=B/'review';out.mkdir(exist_ok=True)
    rows=[]
    for stage,phase in [('l0','terra-high'),('l1','terra-high'),('l1','sol-xhigh'),('l1v','sol-xhigh')]:
        p=B/f'{stage}-{phase}-receipt.json'
        if p.exists():rows.append(json.loads(p.read_text()))
    data=json.loads((OLD/'workbench/data.json').read_text())
    lab=out/'lab';lab.mkdir(exist_ok=True)
    for p in (OLD/'workbench').iterdir():
        if p.is_dir():shutil.copytree(p,lab/p.name,dirs_exist_ok=True)
        elif p.name!='index.html':shutil.copy2(p,lab/p.name)
    derived=B/'viewer-derived';derived.mkdir(exist_ok=True)
    geometry=dict(np.load(OLD/'analysis-v2/geometry.npz'))
    default=None
    for row in rows:
        if row['stage'] not in ['l1','l1v'] or row['execution']!='completed' or 'metrics' not in (row['grade'] or {}):continue
        result=ROOT/row['result_path'];p=result.parent/'artifacts/app/answer/prediction.npz'
        if not p.exists():continue
        name=row['stage']+'_'+row['phase'].replace('-','_')+'_trial'
        points=np.load(p)['points']
        if points.shape!=(30,11370,3) or not np.isfinite(points).all():continue
        stats,eng,weights=analyze_model(points,geometry['tetra'],geometry['cell_labels'],geometry['directions'],derived,name)
        z=dict(np.load(derived/f'{name}.npz'))
        valid=(geometry['cell_labels']>0)&np.all(np.linalg.norm(geometry['directions'],axis=-1)>.99,axis=0)
        stats['global_green_lagrange_percent']=(100*np.average(z['green_lagrange_directional'][:,valid],axis=1,weights=weights[valid])).tolist()
        angles=[]
        for ids in [range(1,7),range(13,17)]:
            mask=np.isin(geometry['point_labels'],list(ids));X=points[0,mask,:2];X=X-X.mean(0);seq=[]
            for current in points:
                Y=current[mask,:2];Y=Y-Y.mean(0)
                seq.append(np.arctan2(np.sum(X[:,0]*Y[:,1]-X[:,1]*Y[:,0]),np.sum(X*Y)))
            angles.append(np.unwrap(seq))
        stats['twist_degrees']=np.rad2deg(angles[1]-angles[0]).tolist()
        m=row['grade']['metrics']
        observations='four videos plus native 3D ultrasound' if row['stage']=='l1v' else 'four videos'
        stats.update(description=f"Fresh {row['requested_model']} / {row['requested_effort']} submission from {observations} and an initial mesh. Frozen independent evaluation; engineering research only.",
                     display_title=row['stage'].upper()+' · '+row['phase'].replace('-',' / ').title()+' · agent reconstruction',
                     comparison=dict(material_point_rmse_mm=m['material_rmse_mm'],directional_engineering_mae_pp=m['strain_mae_pp']),
                     pass_=row['grade']['complete_pass'],file=f'{name}.bin',frames=30)
        stats['pass']=stats.pop('pass_')
        np.concatenate([points,z['nodal_fields']],axis=-1).astype('<f4').tofile(lab/f'{name}.bin')
        data['models'][name]=stats
        default=name
        for fn in ['solve.py','method.md']:
            src=p.parent/fn
            if src.exists():shutil.copy2(src,out/f'{row["stage"]}-{row["phase"]}-{fn}')
    (lab/'data.json').write_text(json.dumps(data,separators=(',',':')))
    viewer=(OLD/'workbench/index.html').read_text()
    # Keep overlays anchored to the canvas even when the sidebar is taller.
    viewer=viewer.replace('</style>','.layout{align-items:start}</style>')
    for name,m in data['models'].items():
        if name.endswith('_trial'):
            viewer=viewer.replace('<select id="model">','<select id="model"><option value="'+name+'">'+html.escape(m['display_title'])+'</option>')
    viewer=viewer.replace("static:'A body without contraction'}[name]","static:'A body without contraction'}[name] || D.models[name].display_title")
    viewer=viewer.replace("'Healthy input case · cyan: selected mesh section · orange: reference'", "(model.startsWith('l1v_')?'Native 3D ultrasound also supplied · ':'Healthy input case · ')+'cyan: selected mesh section · orange: reference'")
    if default:viewer=viewer.replace("await choose('healthy_reference');requestAnimationFrame(tick)",f"$('model').value='{default}';await choose('healthy_reference');await choose('{default}');requestAnimationFrame(tick)")
    (lab/'index.html').write_text(viewer)
    table=[]
    for row in rows:
        grade=row['grade'] or {};m=grade.get('metrics',{})
        if row['stage']=='l0':
            outcome='Calculations PASS' if row['reward']==1 else row['execution']
            cells=['0 · supplied motion',row['phase'],outcome,'—','—','—','Numerical tensor checks']
        else:
            outcome=('Motion '+('PASS' if grade.get('deformation_pass') else 'MISS')+' · mechanics '+('PASS' if grade.get('mechanics_pass') else 'MISS')) if row['execution']=='completed' else row['execution']
            fmt=lambda k,unit='': f'{m[k]:.3f}{unit}' if k in m else '—'
            strain=' / '.join(f'{v:.2f}' for v in m.get('strain_mae_pp',[])) or '—'
            cells=['1V · full volume' if row['stage']=='l1v' else '1 · four videos',row['phase'],outcome,fmt('observed_dice_mean'),fmt('unseen_dice_mean'),fmt('material_rmse_mm',' mm'),strain+' pp']
        table.append('<tr>'+''.join('<td>'+html.escape(str(x))+'</td>' for x in cells)+'</tr>')
    pending=(B/'approval-block.json').exists() and not any(r['stage']=='l1v' for r in rows)
    status=('<div class="card"><strong>Three model trials complete; full-volume follow-up awaiting approval.</strong><p>The prepared L1V condition adds the native 3D ultrasound sequence with unchanged scoring. Its oracle and no-output controls pass. Automatic approval review blocked the model launch; no L1V model result exists.</p></div>' if pending else '')
    if any(r['stage']=='l1v' for r in rows):
        status='<div class="card"><strong>Full-volume follow-up complete.</strong><p>Adding native 3D ultrasound slightly improved image-plane overlap, but this fresh Sol attempt still missed material motion and mechanics. One attempt per condition cannot isolate information effects from strategy variability.</p></div>'
    if (ROOT/'runs/br032-real-echo/review/index.html').exists():
        status+='<p><a href="http://127.0.0.1:8770/index.html">Separate real-scan case study: no reference reconstruction</a></p>'
    figure=''
    if (B/'agent-comparison.png').exists():
        for suffix in ['png','pdf']:
            shutil.copy2(B/f'agent-comparison.{suffix}',out/f'agent-comparison.{suffix}')
        figure='<h2>Where recovery succeeded and failed</h2><p>Whole-body motion and radial strain still miss their fixed targets. Component scores remain separate.</p><a href="agent-comparison.pdf"><img src="agent-comparison.png" alt="Independent comparison of Terra and Sol reconstruction scores" style="width:100%;height:auto;border-radius:12px"></a>'
    content='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Cardiac agent experiments</title><style>
body{background:#101a23;color:#e2edf4;font:16px/1.6 system-ui;margin:0}main{max-width:1150px;margin:auto;padding:36px 24px}h1{font-size:36px;margin-bottom:8px}h2{font-size:23px;margin-top:35px}p{max-width:950px;color:#b8cbd8}a{color:#79d4e0}table{border-collapse:collapse;width:100%;font-size:14px}th,td{padding:13px 11px;text-align:left;border-bottom:1px solid #344653}th{color:#89b8cd}.overflow{overflow:auto}.card{background:#172732;border:1px solid #385260;padding:22px;border-radius:12px;margin:25px 0}.tag{letter-spacing:2px;text-transform:uppercase;color:#7bd9cf;font-size:12px}iframe{width:100%;height:1050px;border:1px solid #385260;border-radius:12px}strong{color:#fff}</style><main>
<div class="tag">BR-031 · frozen prospective agent trials</div><h1>Can the agent recover the beating tissue?</h1>
<p>Separate fresh model attempts, independent scoring, and no future mesh in the reconstruction input. The reference is one previously inspected <a href="https://humanheart-project.creatis.insa-lyon.fr/multimodalityStraus.html">STRAUS simulated healthy case</a>, not measured patient physiology.</p>
<div class="overflow"><table><thead><tr><th>Input stage</th><th>Agent</th><th>Independent gates</th><th>Observed Dice</th><th>Other-plane Dice*</th><th>Material RMSE</th><th>Strain L / C / R</th></tr></thead><tbody>'''+''.join(table)+'''</tbody></table></div><p>*The other four scoring planes are withheld in Stage 1. If Stage 1V is present, they lie inside the added native volume and are no longer unseen observations.</p>
<div class="card"><strong>What is supplied changes by stage.</strong><p>Stage 0 supplies the complete motion and tests calculations. Stage 1 supplies an initial mesh and four calibrated videos, and tests recovered motion. Regional strain is a separate score at Stage 1 already. The geometry gate uses observed Dice ≥0.90, withheld Dice ≥0.85, material RMSE ≤2 mm, surface and tissue-volume tolerances, and zero inversions. Mechanics additionally requires every directional strain and regional peak error ≤5 pp and mean timing error ≤2 frames.</p><p>Stages 2–4 remove geometry/calibration/views. Tracks 6–8 require cavity, Doppler/flow or diagnostic references that this package does not provide. Untested stages are not model failures. Sparse-plane misses do not prove uniquely recoverable information was available.</p></div>
'''+status+figure+'''<h2>Inspect the actual reconstruction</h2><p>This embedded workbench defaults to an agent submission when available. Switch the Motion model selector to compare it with the known simulator motion and author baselines. Colors are computed from material deformation. A plausible surface alone is not the acceptance test.</p>
<p><a href="lab/index.html">Open the full motion workbench</a> · <a href="results.json">Detailed trial receipts</a></p><iframe src="lab/index.html" title="Agent reconstruction and reference mechanics"></iframe>
<h2>Evidence boundary</h2><p>One fresh attempt per displayed condition, with a 30-minute allowance; no automatic retries. Oracle and no-output controls use matching frozen task checksums. Runtime traces are audited for model/effort and source exposure. The author had source access when preparing the task. This is a capability diagnostic on a development case, not a clinical validation, success-rate estimate or proof of provider-side model identity.</p></main></html>'''
    (out/'index.html').write_text(content)
    (out/'results.json').write_text(json.dumps(rows,indent=2)+'\n')
    print(out.resolve())

if __name__=='__main__':main()
