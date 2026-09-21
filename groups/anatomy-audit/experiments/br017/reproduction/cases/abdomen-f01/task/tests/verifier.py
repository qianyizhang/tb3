import json,time
from pathlib import Path
from scoring import score,read_json
start=time.monotonic();out=Path('/logs/verifier');out.mkdir(parents=True,exist_ok=True)
(out/'reward.txt').write_text('0\n')
try: result=score(read_json('/app/answer/answer.json'),read_json('/verifier/expected.json'),Path('/verifier'))
except Exception as e: result={'passed':False,'error':str(e)}
result['grading_seconds']=time.monotonic()-start
(out/'details.json').write_text(json.dumps(result,indent=2)+'\n')
(out/'reward.txt').write_text('1\n' if result['passed'] else '0\n')
print(json.dumps(result))
