"""Publish user-requested reference reveal separately from frozen model inputs."""
import json,shutil
import numpy as np
from pathlib import Path
from common import OUT,write
root=OUT/'blind-review';mapping=json.loads((OUT/'author/review-map.json').read_text());curation=json.loads((OUT/'author/curation.json').read_text())
refs={public:[{'center':x['center'],'extent_mm':x['label_extent_mm']} for x in curation['admitted'] if x['case']==name] for public,name in mapping.items()}
for public,name in mapping.items():
 if refs[public]:
  a=np.load(OUT/'build'/name/'brain.npz')['volume'];high=float(np.percentile(a[a>0],99.5))
  for ref in refs[public]:ref['display_high']=high
write(root/'references.json',refs)
m=json.loads((root/'manifest.json').read_text())
for case in m['cases']:case['label']=mapping[case['id']].replace('aneurysm-n','N')+' ('+case['id']+')'
m['reference_reveal_available']=True;write(root/'manifest.json',m)
backup=OUT/'author/review-before-reference-reveal.html'
if not backup.exists():shutil.copy2(root/'index.html',backup)
shutil.copy2(Path(__file__).with_name('review.html'),root/'index.html')

shutil.copy2(Path(__file__).with_name('case-stories.json'),root/'case-stories.json')
