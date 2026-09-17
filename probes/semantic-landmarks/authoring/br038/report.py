"""Generate measured report; interpretive discussion remains separately authored."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[4];B=ROOT/'runs/br038-volume-landmarks'
x=json.loads((B/'results.json').read_text());trials=[r for r in x['trials'] if r['phase']=='terra-high']
lines=['# BR-038 — full-volume voxel-landmark retest','', '[Setup and coordinate audit](BR-038-volume-landmarks.md) · [Measured results](../evidence/br038-results.json) · [Interpretation](BR-038-traces.md) · [Voxel-axis overlays](../../runs/br038-volume-landmarks/review/index.html)','', 'Complete native volumes were supplied. Outputs are tagged zero-based [i,j,k] array indices; the verifier converts differences to millimetres. No crop or screenshot-coordinate output is involved.','', '| Task | Accepted | Mean / max error | Duration | Coordinate check / supplied viewer |','| --- | ---: | --- | ---: | --- |']
for r in trials:
 s=r.get('score',{});lines.append(f"| {r['case']} | {s.get('accepted_count','?')}/{s.get('total','?')} | {s.get('mean_mm',0):.3f} / {s.get('max_mm',0):.3f} mm | {r.get('agent_seconds',0):.0f} s | {r.get('coordinate_check_called')} / {r.get('provided_viewer_called')} |")
for r in trials:
 lines+=['',f"## {r['case']}",'',f"Normal completion: {r['exception'] is None}; reward: {r['reward']}; contract valid: {r.get('score',{}).get('contract_valid')}.",'','| Landmark | Error mm | Within tolerance |','| --- | ---: | --- |']
 for k,e in r.get('score',{}).get('errors_mm',{}).items():lines.append(f"| {k} | {e:.3f} | {r['score']['accepted'][k]} |")
lines+=['','The fixed limits are 5 mm for CT and 3 mm for MRI. These are reference-agreement thresholds, not clinical standards. An all-target reward requires every queried point to pass. Public reference use and coordinate-helper usage are audited in the receipt.','', 'These new runs change output representation and display scaffolding. The MRI also changes query set/FOV relative to earlier conditions. One attempt per condition cannot isolate causality or establish population accuracy.']
(ROOT/'docs/research-rounds/BR-038-results.md').write_text('\n'.join(lines)+'\n')
print('Reported',len(trials),'completed model attempts')
