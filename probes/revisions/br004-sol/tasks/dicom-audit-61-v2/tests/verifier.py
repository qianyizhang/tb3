import json
from pathlib import Path
import numpy as np
from scoring import score

out=Path('/logs/verifier');out.mkdir(parents=True,exist_ok=True)
(out/'reward.txt').write_text('0\n')
try:
    path=Path('/app/answer/findings.json')
    if path.stat().st_size>200000:raise ValueError('answer exceeds 200 KB')
    def unique(pairs):
        result={}
        for key,value in pairs:
            if key in result:raise ValueError('duplicate JSON key')
            result[key]=value
        return result
    prediction=json.loads(path.read_text(),object_pairs_hook=unique)
    truth=json.loads(Path('/verifier/expected.json').read_text())
    regions=np.load('/verifier/regions.npz',allow_pickle=False)
    result=score(prediction,truth,regions)
except Exception as exc:
    result={'passed':False,'execution_error':str(exc)}
(out/'details.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
if result['passed']:(out/'reward.txt').write_text('1\n')
