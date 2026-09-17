"""User-authorized extra landmark/FOV conditions, separately frozen."""
from run_trials import B,run
import json
if __name__=='__main__':
 for t in json.loads((B/'expanded-freeze.json').read_text())['tasks']:
  a=run(t,'oracle');b=run(t,'nop');assert a['task_checksum']==b['task_checksum']
  c=run(t,'terra-high');assert c['task_checksum']==a['task_checksum']
