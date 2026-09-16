"""Allowlisted evidence extraction with independent regrading and context checks."""
from datetime import datetime
import hashlib
import json
from pathlib import Path
from run_trials import verify
from score import score

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'runs/br021-deformable'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def seconds(value):
    if not value or not value.get('started_at') or not value.get('finished_at'):return None
    return (datetime.fromisoformat(value['finished_at'])-datetime.fromisoformat(value['started_at'])).total_seconds()


def main():
    freeze=read(OUT/'freeze.json');rows=[]
    for task in freeze['tasks']:
        verify(task);base=ROOT/task['task_path'];truth=read(base/'tests/truth.json')
        instruction=(base/'instruction.md').read_text().strip();taskrows=[]
        for phase in ['oracle','nop','terra-high']:
            paths=list((ROOT/'runs'/f"br021-{task['task']}-{phase}-v1-20260916").glob('*/result.json'))
            assert len(paths)==1, f'Missing or ambiguous result for {task["task"]}/{phase}'
            file=paths[0];result=read(file);assert result.get('finished_at')
            exception=result.get('exception_info') or {};usage=result.get('agent_result') or {}
            metrics=file.parent/'verifier/metrics.json';answer=file.parent/'artifacts/app/answer/points.json'
            grade=read(metrics) if metrics.exists() else None
            replay=score(read(answer) if answer.exists() else {},truth)
            if grade:
                assert grade['reward']==replay['reward']
                for key in ['rms_mm','max_mm']:
                    if key in replay:assert abs(grade[key]-replay[key])<1e-6
            row={'task':task['task'],'phase':phase,'result_path':str(file.relative_to(ROOT)),
                'result_sha256':sha(file),'task_checksum':result['task_checksum'],
                'execution':'timeout' if exception.get('exception_type')=='AgentTimeoutError' else 'execution_error' if exception else 'completed',
                'exception_type':exception.get('exception_type'),
                'reward':(result.get('verifier_result') or {}).get('rewards',{}).get('reward'),
                'grade':grade,'independent_replay_matches':bool(grade),
                'started_at':result.get('started_at'),'finished_at':result.get('finished_at'),
                'agent_seconds':seconds(result.get('agent_execution')),'total_seconds':seconds(result),
                'input_tokens':usage.get('n_input_tokens'),'cached_input_tokens':usage.get('n_cache_tokens'),
                'output_tokens':usage.get('n_output_tokens'),'estimated_cost_usd':usage.get('cost_usd')}
            if answer.exists():row.update(answer_path=str(answer.relative_to(ROOT)),answer_sha256=sha(answer))
            if metrics.exists():row['grade_sha256']=sha(metrics)
            if phase=='terra-high':
                contexts=[];sessions=[];seen=False
                for session in sorted((file.parent/'agent/sessions').rglob('*.jsonl')):
                    sessions.append({'path':str(session.relative_to(ROOT)),'sha256':sha(session)})
                    for line in session.read_text().splitlines():
                        try:event=json.loads(line)
                        except ValueError:continue
                        p=event.get('payload') or {}
                        if event.get('type')=='turn_context':
                            context={k:p[k] for k in ['model','effort','reasoning_effort'] if k in p}
                            if context and context not in contexts:contexts.append(context)
                        if event.get('type')=='response_item' and p.get('role')=='user':
                            content=p.get('content',[])
                            if isinstance(content,list) and any(instruction in x.get('text','') for x in content if isinstance(x,dict)):seen=True
                config=result['config']['agent']
                row.update(requested_model=config['model_name'],requested_effort=config['kwargs']['reasoning_effort'],
                    runtime_contexts=contexts,session_files=sessions,frozen_instruction_seen=seen,
                    runtime_matches_request=bool(contexts) and all(c.get('model','').removeprefix('openai/')=='gpt-5.6-terra' and c.get('effort',c.get('reasoning_effort'))=='high' for c in contexts))
                if row['execution']=='completed':assert row['runtime_matches_request'] and seen
            taskrows.append(row)
        assert len({r['task_checksum'] for r in taskrows})==1
        assert taskrows[0]['reward']==1 and taskrows[1]['reward']==0
        rows.extend(taskrows)
    audit=read(OUT/'bench-audit.json')
    assert audit['status']=='completed' and audit['completed_at']
    assert audit['freeze_sha256']==sha(OUT/'freeze.json')
    assert audit['all_frozen_files_and_membership_unchanged']
    for task in freeze['tasks']:
        checked=audit['tasks'][task['task']]
        assert checked['task_checksums_match'] and checked['frozen_files_and_membership_unchanged']
        assert checked['image_audit']['public_files_match_frozen_environment']
    result={'round':'BR-021','freeze_sha256':sha(OUT/'freeze.json'),'frozen_files_unchanged':True,
        'author_audit_sha256':sha(ROOT/'docs/evidence/br021-author-audit.json'),'rows':rows,
        'bench_audit':audit,'bench_audit_sha256':sha(OUT/'bench-audit.json'),
        'limitations':['One deliberately selected patient and query set, one fresh model attempt per condition; no success-rate estimate.',
            'The 2D nominal source frame is supplied, so this isolates deformation rather than unknown-pose recovery.',
            'Eight sparse correspondences do not validate dense-field accuracy or topology.',
            'Public manual labels give an outside answer-retrieval/contamination possibility; trace/image audits are limited evidence.',
            '3 mm RMS / 5 mm maximum is an engineering criterion, not a clinical acceptance threshold.',
            'Author baselines were developed on the case; method runtime excludes development.',
            'These are lung respiratory landmarks, not expert-certified cardiac standard views.']}
    for path in [OUT/'results.json',ROOT/'docs/evidence/br021-results.json']:
        path.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps([{k:r.get(k) for k in ['task','phase','execution','reward','agent_seconds','grade']} for r in rows],indent=2))


if __name__=='__main__':main()
