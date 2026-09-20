"""Private post-run attribution of reference matches to submitted courses."""
import json
import numpy as np
from score import samples,nearest
from run_trials import ROOT,B

ref=json.loads((B/'tasks/all-vessels/tests/reference.json').read_text())
r,rl,rw,_=samples(ref)
out=[]
for row in json.loads((B/'results.json').read_text())['runs']:
    if row['phase'] in ['oracle','nop'] or not row.get('replay',{}).get('format_valid'):continue
    obj=json.loads((ROOT/row['answer_path']/'centerlines.json').read_text())
    p,pl,_,owners=samples(obj,True);d,idx=nearest(r,p);per={}
    for k in sorted(set(rl)):
        mask=(rl==k)&(d<=1);entries=[]
        for owner in sorted(set(owners[idx[mask]])):
            c=obj['centerlines'][owner];m=mask&(owners[idx]==owner)
            entries.append({'id':c['id'],'vessel_name':c['vessel_name'],
                            'matched_reference_mm':float(rw[m].sum()),
                            'correctly_labeled_mm':float(rw[m&(pl[idx]==rl)].sum()),
                            'submitted_labels':sorted(set(int(x) for x in pl[idx[m]]))})
        per[str(int(k))]=sorted(entries,key=lambda x:-x['matched_reference_mm'])
    out.append({'phase':row['phase'],'reference_category_to_submitted_courses':per})
(B/'match-attribution.json').write_text(json.dumps(out,indent=2)+'\n')
print(B/'match-attribution.json')
