import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
OUT=ROOT/'runs/br014-components'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,obj):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,indent=2)+'\n')
def freeze_task(task,metadata):
    name=task.name;dest=OUT/'freezes'/f'{name}.json'
    assert not dest.exists(),'Never overwrite a task freeze'
    receipt={'round':'BR-014','tasks':[{'task':name,'task_path':str(task.relative_to(ROOT)),**metadata,
             'files':{str(p.relative_to(task)):sha(p) for p in sorted(task.rglob('*')) if p.is_file()}}]}
    write(dest,receipt);write(ROOT/'docs/evidence'/f'br014-{name}-freeze.json',receipt)
    return receipt
