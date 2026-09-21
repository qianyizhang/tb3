import json,time
from pathlib import Path
from scoring import score,read_json
s=time.monotonic();out=Path('/logs/verifier');out.mkdir(parents=True,exist_ok=True)
(out/'reward.txt').write_text('0\n')
try:r=score(read_json(Path('/app/answer/answer.json')),read_json(Path('/verifier/expected.json')))
except Exception as e:r={'passed':False,'error':str(e)}
r['grading_seconds']=time.monotonic()-s
(out/'details.json').write_text(json.dumps(r,indent=2)+'\n')
(out/'reward.txt').write_text('1\n' if r['passed'] else '0\n')
print(json.dumps(r))
