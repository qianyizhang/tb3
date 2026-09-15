"""Grade an explicitly supplied review export; preserve uncertainty and self-described experience."""
import argparse,json
from pathlib import Path
from common import OUT,write,sha
from scoring import score,read_json
ap=argparse.ArgumentParser();ap.add_argument('review',type=Path);ap.add_argument('--out',required=True,type=Path);args=ap.parse_args()
assert not args.out.exists(),'Preserve earlier reviewer receipts';d=read_json(args.review);assert d['packet']=='BR-016-blind-v1';mapping=read_json(OUT/'author/review-map.json');rows=[]
for public,r in d['reviews'].items():
 assert public in mapping
 if r.get('decision')=='unreviewed':continue
 row={'review_id':public,'task':mapping[public]+'-v2','decision':r.get('decision'),'confidence':r.get('confidence'),'reason':r.get('reason'),'reference_revealed_at':r.get('reference_revealed_at'),'review_mode':'guided' if r.get('reference_revealed_at') else 'exposure_not_determined'}
 if r.get('decision')=='uncertain':row['grade']=None;row['status']='reviewer_uncertain'
 else:
  assert r.get('decision') in ['none','findings']
  assert (r['decision']=='none')==(len(r['aneurysms'])==0),'Decision and markings disagree'
  key=read_json(OUT/'tasks'/(mapping[public]+'-v2')/'tests/expected.json');row['grade']=score({'aneurysms':r['aneurysms']},key);row['status']='answered'
 rows.append(row)
write(args.out,{'packet':d['packet'],'review_file_sha256':sha(args.review),'reviewed_at':d.get('reviewed_at'),'self_described_experience':d.get('experience'),'prior_exposure':d.get('prior_exposure','unspecified'),'credential_verification':'not performed','rows':rows,'interpretation':'Sampled reviewer performance against released references; not automatically whole-task professional validation.'})
print(json.dumps(rows,indent=2))
