"""Regrade saved submissions and retain allowlisted model/provenance evidence."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from run_trial import verify

ROOT=Path(__file__).resolve().parents[4];B=ROOT/'runs/br031-cardiac-levels'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def duration(r):
    from datetime import datetime
    if not r or not r.get('started_at') or not r.get('finished_at'):return None
    return (datetime.fromisoformat(r['finished_at'])-datetime.fromisoformat(r['started_at'])).total_seconds()

def collect(stage,phase):
    freeze=read(B/f'cardiac-{stage}-freeze.json');verify(freeze)
    paths=list((ROOT/'runs'/f'br031-cardiac-{stage}-{phase}-v1-20260916').glob('*/result.json'))
    assert len(paths)==1,'Missing/ambiguous completed trial'
    file=paths[0];r=read(file);assert r.get('finished_at')
    folder=file.parent;task=ROOT/freeze['task_path'];answer=folder/'artifacts/app/answer'
    metrics=folder/'verifier/metrics.json';exception=r.get('exception_info') or {}
    grade=read(metrics) if metrics.exists() else None
    out=dict(stage=stage,phase=phase,result_path=str(file.relative_to(ROOT)),result_sha256=sha(file),
             task_checksum=r['task_checksum'],freeze_sha256=sha(B/f'cardiac-{stage}-freeze.json'),
             execution='timeout' if exception.get('exception_type')=='AgentTimeoutError' else 'execution_error' if exception else 'completed',
             exception_type=exception.get('exception_type'),reward=(r.get('verifier_result') or {}).get('rewards',{}).get('reward'),
             total_seconds=duration(r),agent_seconds=duration(r.get('agent_execution')),
             grade=grade,artifacts={str(p.relative_to(answer)):sha(p) for p in sorted(answer.rglob('*')) if p.is_file()})
    usage=r.get('agent_result') or {}
    out['usage']={k:usage.get(k) for k in ['n_input_tokens','n_cache_tokens','n_output_tokens','cost_usd']}
    if grade and phase!='nop':
        if stage=='l0':
            from score_l0 import score
            replay=score(answer,task/'tests/source.npz')
        else:
            from score_l1 import score
            replay=score(answer/'prediction.npz',dict(np.load(task/'tests/truth.npz')),
                         np.load(task/'tests/sections.npz')['masks'],read(task/'tests/planes.json'))
        assert replay['reward']==grade['reward'],(replay,grade)
        if stage in ['l1','l1v'] and 'metrics' in replay:
            for key in replay['metrics']:
                assert np.allclose(replay['metrics'][key],grade['metrics'][key],atol=1e-6,rtol=0),key
        if stage=='l0':
            assert replay['source']['pass_']==grade['source']['pass_']
            assert replay['analytic']['pass_']==grade['analytic']['pass_']
        out['independent_replay_matches']=True
    contexts=[];seen=False;sessions=[];toolnames={};remote_commands=[]
    instruction=(task/'instruction.md').read_text().strip()
    for session in sorted((folder/'agent/sessions').rglob('*.jsonl')):
        sessions.append(dict(path=str(session.relative_to(ROOT)),sha256=sha(session)))
        for line in session.read_text().splitlines():
            try:e=json.loads(line)
            except ValueError:continue
            p=e.get('payload') or {}
            if e.get('type')=='turn_context':
                c={k:p[k] for k in ['model','effort','reasoning_effort'] if k in p}
                if c and c not in contexts:contexts.append(c)
            if e.get('type')=='response_item' and p.get('role')=='user':
                content=p.get('content',[])
                if isinstance(content,list):seen|=any(instruction in x.get('text','') for x in content if isinstance(x,dict))
            if p.get('type')=='function_call':
                name=p.get('name','');toolnames[name]=toolnames.get(name,0)+1
                args=p.get('arguments','')
                if any(s in args for s in ['curl ','wget ','requests.','urllib.','http://','https://','spawn_agent','create_thread']):
                    # Keep raw commands local for review; no secret-bearing command text in authored receipt.
                    remote_commands.append(dict(tool=name,arguments=args))
    if phase not in ['oracle','nop']:
        model,effort=phase.split('-')
        out.update(requested_model=f'gpt-5.6-{model}',requested_effort=effort,runtime_contexts=contexts,
                   frozen_instruction_seen=seen,session_files=sessions,tool_call_counts=toolnames,
                   external_or_delegation_command_candidates=len(remote_commands),
                   runtime_matches_request=bool(contexts) and all(c.get('model','').removeprefix('openai/')==f'gpt-5.6-{model}' and c.get('effort',c.get('reasoning_effort'))==effort for c in contexts))
        if out['execution']=='completed':assert out['runtime_matches_request'] and seen,out
        (B/f'{stage}-{phase}-source-review-local.json').write_text(json.dumps(remote_commands,indent=2)+'\n')
    return out

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage');p.add_argument('phase');a=p.parse_args()
    row=collect(a.stage,a.phase)
    path=B/f'{a.stage}-{a.phase}-receipt.json';assert not path.exists(),'Preserve existing receipts'
    path.write_text(json.dumps(row,indent=2)+'\n')
    shown={k:row[k] for k in ['stage','phase','execution','reward','agent_seconds','grade']}
    if shown['grade']:shown['grade']={k:v for k,v in shown['grade'].items() if k!='region_engineering_percent'}
    print(json.dumps(shown,indent=2))
