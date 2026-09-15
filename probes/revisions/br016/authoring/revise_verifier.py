"""Preserve v1 fixtures; correct separate-verifier packaging before any model trial."""
import json,shutil
from common import ROOT,OUT,freeze_task
for name in ['aneurysm-n01','aneurysm-n02','aneurysm-n03']:
 src=OUT/'tasks'/name;dest=OUT/'tasks'/(name+'-v2');assert not dest.exists();shutil.copytree(src,dest)
 shutil.copy2(ROOT/'runs/br015-clinical/tasks/abdomen-c01/tests/Dockerfile',dest/'tests/Dockerfile')
 p=dest/'task.toml';p.write_text(p.read_text().replace('terminal-bench/'+name,'terminal-bench/'+name+'-v2'))
 old=json.loads((OUT/'freezes'/(name+'.json')).read_text())['tasks'][0]
 meta={k:v for k,v in old.items() if k not in ['task','task_path','files']};meta.update(revision=2,supersedes=name,revision_reason='Add missing separate verifier Dockerfile; no model trial on original fixture')
 freeze_task(dest,meta)
