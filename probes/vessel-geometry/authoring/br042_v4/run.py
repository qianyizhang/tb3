"""V4 readiness by default; --run launches controls then exactly one fresh model attempt."""
from pathlib import Path
import argparse,copy,hashlib,json,subprocess,time,types
ROOT=Path(__file__).resolve().parents[4]; B=ROOT/'runs/br042-all-vessels-v4'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def verify():
    manifest=ROOT/'docs/evidence/br042-v4-freeze.json'
    assert manifest.read_bytes()==(B/'freeze.json').read_bytes(),'Freeze manifests differ'
    f=json.loads(manifest.read_text());t=f['tasks'][0];p=ROOT/t['task_path']
    actual={str(x.relative_to(p)):sha(x) for x in p.rglob('*') if x.is_file()}
    assert actual==t['files'],'Frozen task changed'
    for phase,c in f['configs'].items():
        assert sha(ROOT/c['path'])==c['sha256'],'Launch config changed: '+phase
        cfg=json.loads((ROOT/c['path']).read_text())
        assert cfg['n_attempts']==1 and cfg['retry']['max_retries']==0
        assert cfg['environment']['mounts'] is None
        assert not (ROOT/'runs'/c['job_name']).exists(),'Existing run; no overwrite/retry: '+c['job_name']
    for rel in ['.venv/bin/harbor','.venv-validation/bin/harbor']:
        assert (ROOT/rel).is_file(),'Missing local runtime: '+rel
    assert not (B/'events.jsonl').exists(),'An attempt was already launched; do not rerun'
    return f,p

def control_checks(task):
    mod=types.ModuleType('v4_frozen_score')
    source=task/'tests/score.py'
    exec(compile(source.read_text(),str(source),'exec'),mod.__dict__)
    ref=json.loads((task/'tests/reference.json').read_text());oracle=json.loads((task/'solution/centerlines.json').read_text())
    cases={'oracle':oracle};zero=copy.deepcopy(oracle)
    for c in zero['centerlines']:c['labels']=[0]*len(c['labels'])
    cases['zero_labels']=zero
    split=copy.deepcopy(oracle);split['centerlines']=[]
    for c in oracle['centerlines']:
        mid=len(c['labels'])//2
        for suffix,a,b in [('a',0,mid+1),('b',mid,len(c['labels']))]:
            z=copy.deepcopy(c);z['id']+='-'+suffix;z['points_ras_mm']=c['points_ras_mm'][a:b];z['labels']=c['labels'][a:b];split['centerlines'].append(z)
    cases['split_same_categories']=split
    out={k:mod.evaluate(v,ref) for k,v in cases.items()}
    assert out['oracle']['geometry_pass'] and out['oracle']['labeled_pass']
    assert out['zero_labels']['geometry_pass'] and not out['zero_labels']['labeled_pass']
    assert out['split_same_categories']['geometry_pass'] and out['split_same_categories']['labeled_pass']
    return out

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--run',action='store_true',help='Start paid model execution after successful controls; requires user go-ahead.');args=ap.parse_args()
    freeze,task=verify();checks=control_checks(task)
    (B/'readiness.json').write_text(json.dumps({'checked_at_unix':time.time(),'status':'ready_not_started','controls':checks,'limits':'Offline readiness verifies bytes/configs/scoring, not provider or Docker availability.'},indent=2)+'\n')
    if not args.run:
        print('READY: frozen bytes/configs match; oracle, zero-label and split-category controls pass. No experiment started.');return
    # Exclusive creation makes simultaneous invocations and subsequent retries fail closed.
    with (B/'events.jsonl').open('x') as events:
        def emit(row):
            row['time']=time.time();events.write(json.dumps(row)+'\n');events.flush();print(json.dumps(row),flush=True)
        expected=None
        for phase in ['oracle','nop','astra-xhigh']:
            c=freeze['configs'][phase]
            # Recheck immutable inputs immediately before each process, including after controls.
            assert {str(x.relative_to(task)):sha(x) for x in task.rglob('*') if x.is_file()}==freeze['tasks'][0]['files']
            assert sha(ROOT/c['path'])==c['sha256']
            assert not (ROOT/'runs'/c['job_name']).exists()
            exe=ROOT/('.venv/bin/harbor' if phase=='astra-xhigh' else '.venv-validation/bin/harbor')
            emit({'event':'start','phase':phase,'job':c['job_name']})
            with (B/f'{phase}.log').open('x') as log:
                proc=subprocess.run([str(exe),'run','--config',str(ROOT/c['path'])],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
            paths=list((ROOT/'runs'/c['job_name']).glob('*/result.json'))
            r=json.loads(paths[0].read_text()) if len(paths)==1 else {}
            error=r.get('exception_info') or (None if proc.returncode==0 and r else 'Nonzero exit or missing result')
            reward=(r.get('verifier_result') or {}).get('rewards',{}).get('reward')
            assert {str(x.relative_to(task)):sha(x) for x in task.rglob('*') if x.is_file()}==freeze['tasks'][0]['files']
            if r:
                if expected is None:expected=r['task_checksum']
                assert expected==r['task_checksum'],'Control/model task checksum mismatch'
            emit({'event':'finish','phase':phase,'returncode':proc.returncode,'exception':error,'reward':reward,'result_path':str(paths[0].relative_to(ROOT)) if len(paths)==1 else None})
            if phase in ['oracle','nop']:
                assert not error and reward==int(phase=='oracle'),'Control failed; model not launched'
            else:
                emit({'event':'complete','status':'interrupted_or_failed' if error else 'completed','retry_performed':False})
                if error:raise SystemExit(1)
if __name__=='__main__':main()
