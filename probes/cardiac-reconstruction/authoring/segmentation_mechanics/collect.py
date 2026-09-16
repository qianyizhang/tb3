"""Independently regrade retained trials and inspect requested runtime identity."""
import argparse,json,hashlib
from pathlib import Path
from datetime import datetime
import numpy as np
from score import score
from run import verify
ROOT=Path(__file__).resolve().parents[4];B=ROOT/'runs/br035-segmentation-mechanics'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def compare(a,b):
    if isinstance(a,dict):
        assert a.keys()==b.keys()
        for k in a:
            if k=='error':assert a[k].split(':',1)[0]==b[k].split(':',1)[0]
            else:compare(a[k],b[k])
    elif isinstance(a,list):
        assert len(a)==len(b)
        for x,y in zip(a,b):compare(x,y)
    elif isinstance(a,(int,float)) and not isinstance(a,bool):assert np.isclose(a,b,atol=1e-5,rtol=1e-7)
    else:assert a==b

def main():
    p=argparse.ArgumentParser();p.add_argument('condition');a=p.parse_args();condition=a.condition;freeze=json.loads((B/'freeze.json').read_text());verify(freeze);rows=[]
    for phase in ['oracle','nop','sol-xhigh']:
        files=list((ROOT/'runs'/f'br035-{condition}-{phase}-v1-20260916').glob('*/result.json'))
        if not files:continue
        assert len(files)==1;file=files[0];r=json.loads(file.read_text());folder=file.parent
        if not r.get('finished_at'):continue
        out=B/f'{condition}-{phase}-receipt.json'
        if out.exists():rows.append(json.loads(out.read_text()));continue
        assert not r.get('exception_info'),r.get('exception_info')
        grade=json.loads((folder/'verifier/metrics.json').read_text());task=ROOT/freeze['conditions'][condition]['task_path'];regrade=score(folder/'artifacts/app/answer/prediction.npz',task/'tests/data',task/'tests/truth.npz');compare(grade,regrade)
        e=r.get('agent_execution') or {};duration=(datetime.fromisoformat(e['finished_at'])-datetime.fromisoformat(e['started_at'])).total_seconds() if e.get('finished_at') else None
        row=dict(condition=condition,phase=phase,execution='completed',result_path=str(file.relative_to(ROOT)),result_sha256=sha(file),task_checksum=r['task_checksum'],agent_seconds=duration,grade=grade,independent_replay_matches=True,artifacts={str(p.relative_to(folder/'artifacts/app/answer')):sha(p) for p in (folder/'artifacts/app/answer').rglob('*') if p.is_file()})
        if phase=='sol-xhigh':
            contexts=[];seen=False;candidates=[];instruction=(task/'instruction.md').read_text().strip();sessions=[]
            for session in (folder/'agent/sessions').rglob('*.jsonl'):
                sessions.append(dict(path=str(session.relative_to(ROOT)),sha256=sha(session)))
                for line in session.read_text().splitlines():
                    try:v=json.loads(line)
                    except ValueError:continue
                    d=v.get('payload') or {}
                    if v.get('type')=='turn_context':
                        c={k:d[k] for k in ['model','effort','reasoning_effort'] if k in d}
                        if c and c not in contexts:contexts.append(c)
                    if v.get('type')=='response_item' and d.get('role')=='user':seen|=any(instruction in x.get('text','') for x in d.get('content',[]) if isinstance(x,dict))
                    if d.get('type')=='function_call':
                        args=d.get('arguments','')
                        if any(s in args for s in ['curl ','wget ','requests.','urllib.','http://','https://','spawn_agent','create_thread']):candidates.append(dict(tool=d.get('name'),arguments=args))
            matched=bool(contexts) and all(c.get('model','').removeprefix('openai/')=='gpt-5.6-sol' and c.get('effort',c.get('reasoning_effort'))=='xhigh' for c in contexts);assert matched and seen
            row.update(runtime_contexts=contexts,runtime_matches_request=matched,frozen_instruction_seen=seen,session_files=sessions,external_or_delegation_command_candidates=len(candidates),usage={k:(r.get('agent_result') or {}).get(k) for k in ['n_input_tokens','n_cache_tokens','n_output_tokens','cost_usd']})
            (B/f'{condition}-source-review-local.json').write_text(json.dumps(candidates,indent=2)+'\n')
        out.write_text(json.dumps(row,indent=2)+'\n');rows.append(row)
    assert len({r['task_checksum'] for r in rows})<=1
    print(json.dumps([dict(condition=r['condition'],phase=r['phase'],seconds=r['agent_seconds'],reward=r['grade']['reward']) for r in rows]))
if __name__=='__main__':main()
