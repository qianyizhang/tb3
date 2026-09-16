"""Verify frozen task bytes and replay each retained submission independently."""
from datetime import datetime
import hashlib
import json
from pathlib import Path
import sys
from run_trials import verify

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'runs/br020-registration'
sys.path.insert(0,str(ROOT/'probes/registration/authoring'))
from score import score

def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def seconds(obj):
    if not obj or not obj.get('started_at') or not obj.get('finished_at'):return None
    return (datetime.fromisoformat(obj['finished_at'])-datetime.fromisoformat(obj['started_at'])).total_seconds()


def main():
    freeze=read(OUT/'freeze.json');task=freeze['tasks'][0];verify(task)
    base=ROOT/task['task_path'];truth=read(base/'tests/truth.json');rows=[]
    instruction=(base/'instruction.md').read_text().strip()
    for phase in ['oracle','nop','terra-high']:
        paths=list((ROOT/'runs'/f'br020-recon-r03-{phase}-v1-20260916').glob('*/result.json'))
        assert len(paths)==1, f'Missing or ambiguous result: {phase}'
        file=paths[0];r=read(file);assert r.get('finished_at')
        usage=r.get('agent_result') or {};exception=r.get('exception_info') or {}
        metrics=file.parent/'verifier/metrics.json';answer=file.parent/'artifacts/app/answer/pose.json'
        grade=read(metrics) if metrics.exists() else None
        replay=score(read(answer) if answer.exists() else {},truth)
        if grade:
            assert replay['reward']==grade['reward']
            for key in ['rms_mm','max_mm','centre_mm','normal_deg']:
                if key in replay:assert abs(replay[key]-grade[key])<1e-5
        row={'task':task['task'],'phase':phase,'result_path':str(file.relative_to(ROOT)),
             'result_sha256':sha(file),'task_checksum':r['task_checksum'],
             'execution':'timeout' if exception.get('exception_type')=='AgentTimeoutError' else 'execution_error' if exception else 'completed',
             'exception_type':exception.get('exception_type'),
             'reward':(r.get('verifier_result') or {}).get('rewards',{}).get('reward'),
             'grade':grade,'independent_replay_matches':bool(grade),
             'started_at':r.get('started_at'),'finished_at':r.get('finished_at'),
             'agent_seconds':seconds(r.get('agent_execution')),'total_seconds':seconds(r),
             'input_tokens':usage.get('n_input_tokens'),'cached_input_tokens':usage.get('n_cache_tokens'),
             'output_tokens':usage.get('n_output_tokens'),'estimated_cost_usd':usage.get('cost_usd')}
        if answer.exists():row.update(answer_path=str(answer.relative_to(ROOT)),answer_sha256=sha(answer))
        if metrics.exists():row['grade_sha256']=sha(metrics)
        if phase=='terra-high':
            contexts=[];sessions=[];seen=False
            for session in sorted((file.parent/'agent/sessions').rglob('*.jsonl')):
                sessions.append({'path':str(session.relative_to(ROOT)),'sha256':sha(session)})
                for line in session.read_text().splitlines():
                    try:e=json.loads(line)
                    except ValueError:continue
                    p=e.get('payload') or {}
                    if e.get('type')=='turn_context':
                        c={k:p[k] for k in ['model','effort','reasoning_effort'] if k in p}
                        if c and c not in contexts:contexts.append(c)
                    if e.get('type')=='response_item' and p.get('role')=='user':
                        content=p.get('content',[])
                        if isinstance(content,list) and any(instruction in x.get('text','') for x in content if isinstance(x,dict)):seen=True
            config=r['config']['agent']
            row.update(requested_model=config['model_name'],requested_effort=config['kwargs']['reasoning_effort'],
                runtime_contexts=contexts,session_files=sessions,frozen_instruction_seen=seen,
                runtime_matches_request=bool(contexts) and all(c.get('model','').removeprefix('openai/')=='gpt-5.6-terra' and c.get('effort',c.get('reasoning_effort'))=='high' for c in contexts))
            if row['execution']=='completed':assert row['runtime_matches_request'] and seen
        rows.append(row)
    assert len({r['task_checksum'] for r in rows})==1
    assert rows[0]['reward']==1 and rows[1]['reward']==0
    result={'round':'BR-020','freeze_sha256':sha(OUT/'freeze.json'),'frozen_files_unchanged':True,
            'author_audit_sha256':sha(ROOT/'docs/evidence/br020-author-audit.json'),'rows':rows,
            'limitations':['One patient, plane and model attempt; no success-rate estimate.',
              'Acquisition timestamps removed; shared acquisition supported by metadata and image agreement, not raw projections.',
              'Different patient/plane from BR019 prevents a causal difficulty comparison.',
              'Author landmark estimates and engineering tolerance are not expert clinical validation.',
              'Runtime labels and absence-of-leak trace review are not provider-side attestation.']}
    bench=read(OUT/'bench-audit.json')
    assert bench.get('completed_at') and bench.get('status')!='model_running', 'Execution/trace audit must be final'
    assert bench['task_checksums_match'] and bench['frozen_files_and_membership_unchanged']
    result['bench_audit']=bench
    result['bench_audit_sha256']=sha(OUT/'bench-audit.json')
    for p in [OUT/'results.json',ROOT/'docs/evidence/br020-results.json']:
        p.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps([{k:r.get(k) for k in ['phase','execution','reward','agent_seconds','grade']} for r in rows],indent=2))


if __name__=='__main__':main()
