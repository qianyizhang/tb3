"""Create concise condition-wise report from independently replayed results."""
from pathlib import Path
import json,datetime
ROOT=Path(__file__).resolve().parents[3];B=ROOT/'runs/br036-semantic-landmarks'
r=json.loads((B/'results.json').read_text());models=[x for x in r['trials'] if x['phase']=='terra-high']
lines=['# BR-036 — semantic landmark results','', 'Two source-order subjects, four frozen conditions, one fresh Terra/high attempt per condition. These are reference-agreement pilots, not clinical validation or a repeatability study.','', '[Candidate shortlist and protocol](BR-036-semantic-landmarks.md) · [Measured receipt](../evidence/br036-results.json) · [Local comparison panels](../../runs/br036-semantic-landmarks/review/index.html)','', '| Condition | Accepted targets | Mean / maximum point error | Outside-FOV handling | Agent duration |','| --- | ---: | --- | --- | ---: |']
for x in models:
 s=x.get('host_rescore',x.get('score',{}));e=x.get('agent_execution') or {};seconds=None
 if e.get('started_at') and e.get('finished_at'):seconds=(datetime.datetime.fromisoformat(e['finished_at'].replace('Z','+00:00'))-datetime.datetime.fromisoformat(e['started_at'].replace('Z','+00:00'))).total_seconds()
 if 'accepted_count' in s:
  accepted=f"{s['accepted_count']}/{s['total']}";outside=f"{s['outside_correct']}/{len(s['outside_gt'])}";inside={k:v for k,v in s['errors_mm'].items() if k not in s['outside_gt']};dist=f"{sum(inside.values())/len(inside):.2f} / {max(inside.values()):.2f} mm" if inside else 'No in-view coordinates'
 else:accepted=f"{s.get('within_5mm',0) if x['case'].startswith('ct') else s.get('within_3mm',0)}/{4 if x['case'].startswith('ct') else 8}";outside='Not tested';dist=f"{s['mean_mm']:.2f} / {s['max_mm']:.2f} mm" if 'mean_mm' in s else 'Invalid / unavailable'
 lines.append(f"| {x['case']} | {accepted} | {dist} | {outside} | {seconds:.0f} s |" if seconds else f"| {x['case']} | {accepted} | {dist} | {outside} | unavailable |")
lines+=['','Point errors above use submitted in-view coordinates; visibility failures and missing points are counted separately. An all-target pass requires every target to satisfy its fixed rule. See the receipt for per-point errors and output status.','']
for x in models:
 s=x.get('host_rescore',x.get('score',{}));lines += [f"## {x['case']}",'',f"Normal completion: {x['exception'] is None}. Fixed all-target reward: {x['reward']}.",'','| Landmark | Error (mm) | Output / accepted |','| --- | ---: | --- |']
 keys=list(s.get('accepted',s.get('errors_mm',{})))
 for k in keys:
  v=s.get('errors_mm',{}).get(k);error=f'{v:.3f}' if v is not None else '—';status=s.get('status',{}).get(k,'coordinate');accepted=s.get('accepted',{}).get(k)
  lines.append(f"| {k} | {error} | {status}"+(f" / {accepted}" if accepted is not None else '')+' |')
 lines+=['']
lines+=['## Interpretation limits','','CT slice spacing is 3 mm; MRI voxels are about 0.7 mm. Thresholds were fixed before results at 5/3 mm respectively. For cropped inputs, empty answers are valid only when the reference lies outside the FOV; an extrapolation must lie outside and be within 10 mm of the withheld point. MRI point 27 has one rater 3.138 mm from the consensus and requires caution near the threshold.','','The CT full/crop tasks share the same four queries. The MRI eight/full and 32/crop conditions differ in both query set and FOV; they cannot isolate a crop effect. Full and cropped data come from the same subjects, not four independent patients. No blind author solver, independent clinical adjudication, or population accuracy estimate is claimed. Public training exposure remains possible.','','Original freezes and first attempts remain unchanged. No retries or post-result threshold changes were used.']
(ROOT/'docs/research-rounds/BR-036-results.md').write_text('\n'.join(lines)+'\n')
print('Report generated for',len(models),'completed model attempts')
