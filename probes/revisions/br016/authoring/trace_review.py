"""Review observable tool use and delivered outputs; retain source overlap evidence."""
import json,re,shlex
from pathlib import Path
from common import ROOT,OUT,write,sha
reviews=[]
for trial in sorted((ROOT/'runs').glob('br016-*-sol-xhigh-v1-20260915/*/result.json')):
 result=json.loads(trial.read_text())
 if not result.get('finished_at'):continue
 task=Path(result['config']['task']['path']) if isinstance(result['config'].get('task'),dict) else None
 name=trial.parent.parent.name.removeprefix('br016-').removesuffix('-sol-xhigh-v1-20260915');task=OUT/'tasks'/name
 cp=trial.parent/'agent/codex.txt';items=[]
 for line in cp.read_text().splitlines():
  try:e=json.loads(line)
  except ValueError:continue
  if e.get('type')=='item.completed':items.append(e['item'])
 commands=[x.get('command','') for x in items if x['type']=='command_execution'];publicmessages=[x['text'] for x in items if x['type']=='agent_message']
 tr=trial.parent/'agent/trajectory.json';trajectory=json.loads(tr.read_text());calls=[c for s in trajectory.get('steps',[]) for c in s.get('tool_calls',[])]
 view_calls=[c for c in calls if 'view_image' in json.dumps(c)]
 regions=json.loads((task/'tests/expected.json').read_text())['regions'];accepted=[set(r['accepted_voxels']) for r in regions];coverage=[]
 for cmd in commands:
  if 'inspect_mra.py' not in cmd:continue
  try:
   outer=shlex.split(cmd);argv=shlex.split(outer[-1]);axis='ijk'.index(argv[argv.index('--axis')+1]);start=argv.index('--bounds')+1;b=list(map(int,argv[start:start+6]));positions=[]
   if '--slices' in argv:
    j=argv.index('--slices')+1
    while j<len(argv) and not argv[j].startswith('--'):positions.append(int(argv[j]));j+=1
   out=argv[argv.index('--out')+1]
  except (ValueError,IndexError):continue
  hits=[]
  for idx,r in enumerate(regions):
   for v in r['accepted_voxels']:
    q=list(map(int,v.split(',')))
    if all(b[2*d]<=q[d]<b[2*d+1] for d in range(3)) and (not positions or q[axis] in positions):hits.append(idx);break
  coverage.append({'output':out,'axis':'ijk'[axis],'slice_indices':positions,'bounds_exclusive':b,'intersects_accepted_regions':hits})
 review={'task':name,'trajectory_sha256':sha(tr),'completed_commands':len(commands),'image_review_wrappers':len(view_calls),'public_messages':publicmessages,'rendered_region_coverage':coverage,
  'interpretation':'Observable rendering overlap is not proof of attention or correct perception. Review source evidence independently before promoting a miss.',
  'source_retrieval_command_candidates':[x for x in commands if re.search(r'curl|wget|requests\.|urllib|openneuro|github',x,re.I)]}
 review['public_source_match_observed']=any('np.array_equal' in x.get('command','') and 'diff 0.0 0.0 True' in x.get('aggregated_output','') for x in items)
 review['annotation_inventory_exposed']=any('manual_masks' in x.get('aggregated_output','') and 'Lesion' in x.get('aggregated_output','') and 'ds003949-tree.json' in x.get('command','') for x in items)
 review['capability_evidence']='source-assisted / reference-exposed; exclude from unaided interpretation' if review['public_source_match_observed'] and review['annotation_inventory_exposed'] else 'no source lookup observed; clinical review still pending'
 reviews.append(review)
write(OUT/'author/trace-reviews.json',{'reviews':reviews});write(ROOT/'docs/evidence/br016-trace-reviews.json',{'reviews':reviews});print([(x['task'],x['completed_commands'],x['image_review_wrappers']) for x in reviews])
