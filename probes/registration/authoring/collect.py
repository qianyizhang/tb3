"""Collect safe evidence, independently replay geometry, verify frozen bytes."""
from datetime import datetime
import hashlib
import json
from pathlib import Path
from score import score
from run_trials import verify

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'runs/br019-registration'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def seconds(obj):
    if not obj or not obj.get('started_at') or not obj.get('finished_at'):return None
    return (datetime.fromisoformat(obj['finished_at'])-datetime.fromisoformat(obj['started_at'])).total_seconds()


def main():
    frozen=read(OUT/'freeze.json'); rows=[];author={}
    for task in frozen['tasks']:
        verify(task);base=ROOT/task['task_path'];truth=read(base/'tests/truth.json')
        bp=OUT/'author'/f"{task['task'][-3:]}-baseline.json"
        author[task['task']]={'grade':score(read(bp),truth),**read(bp.with_suffix('.metrics.json')),
                              'answer_sha256':sha(bp),'solver_sha256':sha(Path(__file__).with_name('baseline.py'))}
        for phase in ['oracle','nop','terra-high']:
            files=list((ROOT/'runs'/f"br019-{task['task']}-{phase}-v1-20260916").glob('*/result.json'))
            assert len(files)<=1
            if not files:continue
            file=files[0];r=read(file)
            if not r.get('finished_at'):continue
            exception=r.get('exception_info') or {};usage=r.get('agent_result') or {}
            row={'task':task['task'],'phase':phase,'result_path':str(file.relative_to(ROOT)),
                 'result_sha256':sha(file),'task_checksum':r['task_checksum'],
                 'execution':'timeout' if exception.get('exception_type')=='AgentTimeoutError' else 'execution_error' if exception else 'completed',
                 'exception_type':exception.get('exception_type'),
                 'reward':(r.get('verifier_result') or {}).get('rewards',{}).get('reward'),
                 'started_at':r.get('started_at'),'finished_at':r.get('finished_at'),
                 'agent_seconds':seconds(r.get('agent_execution')),'total_seconds':seconds(r),
                 'agent_version':(r.get('agent_info') or {}).get('version'),
                 'input_tokens':usage.get('n_input_tokens'),'cached_input_tokens':usage.get('n_cache_tokens'),
                 'output_tokens':usage.get('n_output_tokens'),'estimated_cost_usd':usage.get('cost_usd')}
            mp=file.parent/'verifier/metrics.json'
            if mp.exists():row['grade']=read(mp);row['grade_sha256']=sha(mp)
            answer=file.parent/'artifacts/app/answer/pose.json'
            replay=score(read(answer) if answer.exists() else {},truth)
            if mp.exists():
                # Cross-platform float differences are not scientific differences.
                assert replay['reward']==row['grade']['reward']
                for key in ['rms_mm','max_mm','centre_mm','normal_deg']:
                    if key in replay:assert abs(replay[key]-row['grade'][key])<1e-5
                row['independent_replay_matches']=True
            if answer.exists():row.update(answer_path=str(answer.relative_to(ROOT)),answer_sha256=sha(answer))
            if phase=='terra-high':
                config=r['config']['agent']; row['requested_model']=config['model_name'];row['requested_effort']=config['kwargs']['reasoning_effort']
                contexts=[]; sessions=[];instruction_seen=False
                instruction=(base/'instruction.md').read_text().strip()
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
                            if isinstance(content,list) and any(instruction in x.get('text','') for x in content if isinstance(x,dict)):instruction_seen=True
                row.update(runtime_contexts=contexts,session_files=sessions,frozen_instruction_seen=instruction_seen,
                           runtime_matches_request=bool(contexts) and all(c.get('model','').removeprefix('openai/')=='gpt-5.6-terra' and c.get('effort',c.get('reasoning_effort'))=='high' for c in contexts))
                if row['execution']=='completed':assert row['runtime_matches_request'] and instruction_seen
            rows.append(row)
        group=[r for r in rows if r['task']==task['task']]
        assert len({r['task_checksum'] for r in group})<=1
    result={'round':'BR-019','freeze_sha256':sha(OUT/'freeze.json'),'frozen_task_files_unchanged':True,
            'author_public_input_baselines':author,'rows':rows,
            'limitations':['One source patient and two correlated views; one model attempt per condition.',
              'Synthetic same-acquisition sections preserve exact texture and interpolation structure.',
              'Apex-side heuristic is not expert clinical plane annotation; tolerances are engineering choices.',
              'Runtime/model labels are trace-consistent evidence, not provider-side attestation.',
              'No cross-acquisition, cross-modality or final-submission difficulty claim.']}
    (OUT/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    (ROOT/'docs/evidence/br019-results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps([{k:r.get(k) for k in ['task','phase','execution','reward','agent_seconds','grade']} for r in rows],indent=2))


if __name__=='__main__':main()
