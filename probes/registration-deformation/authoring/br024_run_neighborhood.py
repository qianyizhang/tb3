"""Execute final predeclared public-input patient-2 rescue and grade afterward."""
import hashlib
import json
from pathlib import Path
import subprocess
import time
from score import score

ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'runs/br024-harder-registration';HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    plan=json.loads((OUT/'neighborhood-plan.json').read_text())
    for p,h in plan['files'].items():assert sha(ROOT/p)==h
    screen=json.loads((OUT/'screen.json').read_text());rows=[]
    for case in screen['cases']:
        if case['case']!=2:continue
        for c in case['candidates']:
            folder=OUT/'candidates'/c['name']/'neighborhood';folder.mkdir(exist_ok=False)
            cmd=['docker','run','--rm','--network','none','--cpus','4','--memory','4g',
                 '-v',f'{ROOT/c["public_path"]}:/app/data:ro','-v',f'{folder}:/output',
                 '-v',f'{HERE/"baseline_patches.py"}:/baseline.py:ro','-v',f'{HERE/"br024_neighborhood.py"}:/runner.py:ro',
                 'sha256:dd4a6f96b30342bd15fedb795dc9371d0ddd15b03e7e2eadef843e41325a3014','python','/runner.py']
            start=time.time()
            with (folder/'execution.log').open('w') as log:p=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
            assert p.returncode==0,'Execution problem; preserve as infrastructure result'
            grade=score(json.loads((folder/'points.json').read_text()),json.loads((ROOT/c['truth_path']).read_text()))
            row={'name':c['name'],'case':2,'rank':c['rank'],'grade':grade,'elapsed_seconds':time.time()-start,
                 'command':cmd,'private_labels_mounted':False,'answer_path':str((folder/'points.json').relative_to(ROOT)),'answer_sha256':sha(folder/'points.json')}
            rows.append(row);(OUT/'neighborhood-feasibility.json').write_text(json.dumps({'round':'BR-024','plan_sha256':sha(OUT/'neighborhood-plan.json'),'rows':rows},indent=2)+'\n')
            print(json.dumps(row|{'command':'retained in receipt'}),flush=True)
            if grade['reward']==1:break

if __name__=='__main__':main()
