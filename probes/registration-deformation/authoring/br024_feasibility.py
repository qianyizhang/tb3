"""Fixed public-input baseline screening; private labels used only after execution."""
import hashlib
import json
from pathlib import Path
import subprocess
import time
from score import score

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'runs/br024-harder-registration'


def main():
    plan = json.loads((OUT/'plan.json').read_text())
    baseline = ROOT / plan['baseline_path']
    assert hashlib.sha256(baseline.read_bytes()).hexdigest() == plan['baseline_sha256']
    screen = json.loads((OUT/'screen.json').read_text())
    rows = []
    for case in screen['cases']:
        for c in case['candidates']:
            folder = OUT / 'candidates' / c['name'] / 'baseline'
            folder.mkdir(exist_ok=False)
            command = ['docker','run','--rm','--network','none','--cpus','4','--memory','4g',
                       '-v',f'{ROOT/c["public_path"]}:/app/data:ro',
                       '-v',f'{baseline}:/baseline.py:ro','-v',f'{folder}:/output',
                       'sha256:dd4a6f96b30342bd15fedb795dc9371d0ddd15b03e7e2eadef843e41325a3014',
                       'python','/baseline.py','--data','/app/data','--out','/output/points.json','--kind','2d']
            start = time.time()
            with (folder/'execution.log').open('w') as log:
                p = subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
            assert p.returncode == 0, 'Preserve infrastructure failures; do not classify as task difficulty'
            answer = json.loads((folder/'points.json').read_text())
            truth = json.loads((ROOT/c['truth_path']).read_text())
            grade = score(answer,truth)
            row = {'name':c['name'],'case':case['case'],'rank':c['rank'],'grade':grade,
                   'elapsed_seconds':time.time()-start,'command':command,'private_labels_mounted':False,
                   'answer_path':str((folder/'points.json').relative_to(ROOT)),
                   'answer_sha256':hashlib.sha256((folder/'points.json').read_bytes()).hexdigest()}
            rows.append(row)
            (OUT/'feasibility.json').write_text(json.dumps({'round':'BR-024','rows':rows},indent=2)+'\n')
            print(json.dumps(row | {'command':'retained in receipt'}),flush=True)
            if grade['reward'] == 1:
                break


if __name__ == '__main__':
    main()
