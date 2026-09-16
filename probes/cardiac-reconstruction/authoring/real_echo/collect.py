"""Retain control/model receipts and independently verify the saved artifact."""
import hashlib,json
from pathlib import Path
import numpy as np
from run import verify
from score import score
ROOT=Path(__file__).resolve().parents[4];B=ROOT/'runs/br032-real-echo'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    freeze=json.loads((B/'freeze.json').read_text());verify(freeze);rows=[]
    for phase in ['oracle','nop','sol-xhigh']:
        paths=list((ROOT/'runs'/f'br032-real-echo-{phase}-v1-20260916').glob('*/result.json'))
        if not paths:continue
        assert len(paths)==1;file=paths[0];r=json.loads(file.read_text());folder=file.parent
        assert r.get('finished_at')
        grade=json.loads((folder/'verifier/metrics.json').read_text());replay=score(folder/'artifacts/app/answer')
        assert grade['reward']==replay['reward']
        if grade['reward']==1:assert np.allclose(grade['volume_ml'],replay['volume_ml'],atol=1e-6)
        from datetime import datetime
        a=r.get('agent_execution') or {};dur=(datetime.fromisoformat(a['finished_at'])-datetime.fromisoformat(a['started_at'])).total_seconds() if a.get('finished_at') else None
        row=dict(phase=phase,execution='completed' if not r.get('exception_info') else 'execution_error',
                 exception_type=(r.get('exception_info') or {}).get('exception_type'),result_path=str(file.relative_to(ROOT)),result_sha256=sha(file),
                 task_checksum=r['task_checksum'],agent_seconds=dur,grade=grade,independent_replay_matches=True,
                 outcome_scope='artifact validity only, no reconstruction ground truth',
                 artifacts={str(p.relative_to(folder/'artifacts/app/answer')):sha(p) for p in (folder/'artifacts/app/answer').rglob('*') if p.is_file()})
        if phase=='sol-xhigh':
            contexts=[];seen=False;candidates=[];sessions=[];instruction=(ROOT/freeze['task_path']/'instruction.md').read_text().strip()
            for session in (folder/'agent/sessions').rglob('*.jsonl'):
                sessions.append(dict(path=str(session.relative_to(ROOT)),sha256=sha(session)))
                for line in session.read_text().splitlines():
                    try:e=json.loads(line)
                    except ValueError:continue
                    p=e.get('payload') or {}
                    if e.get('type')=='turn_context':
                        c={k:p[k] for k in ['model','effort','reasoning_effort'] if k in p}
                        if c and c not in contexts:contexts.append(c)
                    if e.get('type')=='response_item' and p.get('role')=='user':
                        seen|=any(instruction in x.get('text','') for x in p.get('content',[]) if isinstance(x,dict))
                    if p.get('type')=='function_call':
                        args=p.get('arguments','')
                        if any(s in args for s in ['curl ','wget ','requests.','urllib.','http://','https://','spawn_agent','create_thread']):candidates.append(dict(tool=p.get('name'),arguments=args))
            matches=bool(contexts) and all(c.get('model','').removeprefix('openai/')=='gpt-5.6-sol' and c.get('effort',c.get('reasoning_effort'))=='xhigh' for c in contexts)
            assert matches and seen
            row.update(runtime_contexts=contexts,runtime_matches_request=matches,frozen_instruction_seen=seen,session_files=sessions,
                       external_or_delegation_command_candidates=len(candidates),usage={k:(r.get('agent_result') or {}).get(k) for k in ['n_input_tokens','n_cache_tokens','n_output_tokens','cost_usd']})
            (B/'source-review-local.json').write_text(json.dumps(candidates,indent=2)+'\n')
        out=B/f'{phase}-receipt.json'
        if out.exists():assert json.loads(out.read_text())==row
        else:out.write_text(json.dumps(row,indent=2)+'\n')
        rows.append(row)
    assert len({r['task_checksum'] for r in rows})==1
    print(json.dumps([dict(phase=r['phase'],execution=r['execution'],format_reward=r['grade']['reward'],agent_seconds=r['agent_seconds']) for r in rows],indent=2))
if __name__=='__main__':main()
