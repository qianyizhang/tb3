"""Generate a local comparison draft for authored interpretation after collection."""
import json
from pathlib import Path
from run_trials import ROOT,B
NAMES={1:'LM',2:'LAD',3:'LCx',4:'D1',5:'D2',6:'OM1',7:'OM2',8:'IM',9:'RCA',10:'R-PDA',11:'R-PLA',12:'L-PDA',13:'L-PLA',14:'Other'}
r=json.loads((B/'results.json').read_text())
models=[x for phase in ['sol-xhigh','astra-medium','astra-xhigh'] for x in r['runs'] if x['phase']==phase and x.get('agent_execution')]
setup_failures=[x for x in r['runs'] if x['phase'].endswith('-setup-failed')]
lines=['# BR-042 V3 comparison — draft numerical readout','', '| Model / effort | Normal completion | Time | Geometry length coverage | Labeled length coverage | Geometry macro | Labeled macro | Label accuracy on matched length | Geometry / labeled pass |','| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |']
for row in models:
 s=row.get('score',{});g=s.get('geometry',{});l=s.get('labeled',{});ident=s.get('identity',{}).get('accuracy_given_geometry_1mm');secs=row.get('agent_wall_seconds',0)
 pct=lambda v:'—' if v is None else f'{v:.1%}'
 lines.append(f"| {row['phase']} | {not bool(row['exception'])} | {secs/60:.2f} min | {pct(g.get('length_weighted_recall_1mm'))} | {pct(l.get('length_weighted_recall_1mm'))} | {pct(g.get('macro_recall_1mm'))} | {pct(l.get('macro_recall_1mm'))} | {pct(ident)} | {s.get('geometry_pass')} / {s.get('labeled_pass')} |")
lines+=['','All coverage above uses 1 mm. Geometry and labeled columns share reference denominators. Geometry matches ignore submitted labels, including code 0. Passing requires macro ≥90% and each present category ≥80%.','', '| Category | '+' | '.join(x['phase']+' geometry / labeled' for x in models)+' |','| --- | '+' | '.join('---:' for _ in models)+' |']
for k,name in NAMES.items():
 vals=[]
 for row in models:
  p=row.get('score',{}).get('per_reference_category',{}).get(str(k))
  vals.append(f"{p['geometry_recall_1mm']:.1%} / {p['labeled_recall_1mm']:.1%}" if p else '—')
 if any(v!='—' for v in vals):lines.append('| '+name+' | '+' | '.join(vals)+' |')
lines+=['','| Model / effort | Geometry length at 2 mm | Labeled length at 2 mm | Geometry macro at 2 mm | Labeled macro at 2 mm |','| --- | ---: | ---: | ---: | ---: |']
for row in models:
 s=row.get('score',{})
 lines.append('| '+row['phase']+' | '+' | '.join(pct(s.get(name,{}).get(key)) for name,key in [('geometry','length_weighted_recall_2mm'),('labeled','length_weighted_recall_2mm'),('geometry','macro_recall_2mm'),('labeled','macro_recall_2mm')])+' |')
lines+=['','| Model / effort | Missed geometry, mm | Covered with wrong label, mm | Covered with correct label, mm |','| --- | ---: | ---: | ---: |']
for row in models:
 p=row.get('score',{}).get('reference_length_partition_mm',{})
 lines.append('| '+row['phase']+' | '+' | '.join(f'{p[k]:.1f}' if k in p else '—' for k in ['missed_geometry','covered_wrong_label','covered_correct_label'])+' |')
for row in models:
 lines+=['',f"## {row['phase']}",'']
 if row['exception']:lines.append('Exception: '+json.dumps(row['exception']))
 s=row.get('score',{});a=row.get('agent_result') or {}
 lines.append(f"Polylines: {s.get('polylines')}; points: {s.get('submitted_points')}; length: {s.get('submitted_length_mm')}. Input tokens: {a.get('n_input_tokens')}; cached: {a.get('n_cache_tokens')}; output: {a.get('n_output_tokens')}; monetary cost: {a.get('cost_usd')}.")
 lines.append('Reference length partition, mm: '+json.dumps(s.get('reference_length_partition_mm')))
 if row.get('answer_path'):lines.append('Output: `'+row['answer_path']+'`.')
 lines.append('Trace audit: '+json.dumps(row.get('trace_audit')))
if setup_failures:
 lines+=['','## Excluded setup failures','','These jobs failed before model execution and are retained separately from the completed model attempts.']
 for row in setup_failures:lines.append('- '+row['phase']+': `'+row['result_path']+'`.')
(B/'comparison-draft.md').write_text('\n'.join(lines)+'\n')
print(B/'comparison-draft.md')
