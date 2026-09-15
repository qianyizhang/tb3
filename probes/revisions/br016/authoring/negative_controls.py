"""Empty output is a valid negative; explicitly test a false-positive rejection."""
import json,subprocess
from common import ROOT,OUT,write,sha
name='aneurysm-n03-v2';t=OUT/'tasks'/name;dest=OUT/'negative-controls';assert not dest.exists();dest.mkdir()
freeze=json.loads((OUT/'freezes'/(name+'.json')).read_text())['tasks'][0];assert all(sha(t/p)==h for p,h in freeze['files'].items())
tag='br016-negative-verifier-control'
subprocess.run(['docker','build','-q','-t',tag,str(t/'tests')],check=True)
rows=[]
for label,answer,want in [('empty',{'aneurysms':[]},True),('false_positive',{'aneurysms':[[175,224,80]]},False)]:
 d=dest/label;write(d/'answer/answer.json',answer);(d/'logs').mkdir()
 subprocess.run(['docker','run','--rm','-v',f'{d}/answer:/app/answer:ro','-v',f'{d}/logs:/logs/verifier',tag],check=True)
 result=json.loads((d/'logs/details.json').read_text());assert result['passed']==want
 rows.append({'name':label,'answer':answer,'grade':result})
write(ROOT/'docs/evidence/br016-negative-controls.json',{'task':name,'files_unchanged':all(sha(t/p)==h for p,h in freeze['files'].items()),'rows':rows})
