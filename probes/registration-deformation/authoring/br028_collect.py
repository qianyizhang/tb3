"""Independent BR-028 grading, frozen-input checks, and allowlisted receipts."""
import json
from pathlib import Path
from collect import read,sha,seconds
from br028_run_trials import verify
from score import score

ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'runs/br028-registration-3d-source'


def collect_trial(task,phase):
    paths=list((ROOT/'runs'/f'br028-{task["task"]}-{phase}-v1-20260916').glob('*/result.json'));assert len(paths)==1
    file=paths[0];result=read(file);assert result.get('finished_at')
    truth=read(ROOT/task['task_path']/'tests/truth.json');instruction=(ROOT/task['task_path']/'instruction.md').read_text().strip()
    metrics=file.parent/'verifier/metrics.json';answer=file.parent/'artifacts/app/answer/points.json'
    grade=read(metrics) if metrics.exists() else None;regrade=score(read(answer) if answer.exists() else {},truth)
    if grade:
        assert grade['reward']==regrade['reward']
        for k in ['rms_mm','max_mm']:
            if k in regrade:assert abs(grade[k]-regrade[k])<1e-6
    exception=result.get('exception_info') or {};usage=result.get('agent_result') or {}
    row={'task':task['task'],'phase':phase,'result_path':str(file.relative_to(ROOT)),'result_sha256':sha(file),
         'task_checksum':result['task_checksum'],'execution':'timeout' if exception.get('exception_type')=='AgentTimeoutError' else 'execution_error' if exception else 'completed',
         'exception_type':exception.get('exception_type'),'reward':(result.get('verifier_result') or {}).get('rewards',{}).get('reward'),
         'grade':grade,'independent_replay_matches':bool(grade),'started_at':result.get('started_at'),'finished_at':result.get('finished_at'),
         'agent_seconds':seconds(result.get('agent_execution')),'total_seconds':seconds(result),
         'input_tokens':usage.get('n_input_tokens'),'cached_input_tokens':usage.get('n_cache_tokens'),
         'output_tokens':usage.get('n_output_tokens'),'estimated_cost_usd':usage.get('cost_usd')}
    if answer.exists():row.update(answer_path=str(answer.relative_to(ROOT)),answer_sha256=sha(answer))
    if metrics.exists():row['grade_sha256']=sha(metrics)
    if phase=='sol-xhigh':
        contexts=[];sessions=[];seen=False
        for session in sorted((file.parent/'agent/sessions').rglob('*.jsonl')):
            sessions.append({'path':str(session.relative_to(ROOT)),'sha256':sha(session)})
            for line in session.read_text().splitlines():
                try:event=json.loads(line)
                except ValueError:continue
                p=event.get('payload') or {}
                if event.get('type')=='turn_context':
                    c={k:p[k] for k in ['model','effort','reasoning_effort'] if k in p}
                    if c and c not in contexts:contexts.append(c)
                if event.get('type')=='response_item' and p.get('role')=='user':
                    content=p.get('content',[])
                    if isinstance(content,list):seen|=any(instruction in x.get('text','') for x in content if isinstance(x,dict))
        config=result['config']['agent'];row.update(requested_model=config['model_name'],requested_effort=config['kwargs']['reasoning_effort'],
            runtime_contexts=contexts,session_files=sessions,frozen_instruction_seen=seen,
            runtime_matches_request=bool(contexts) and all(c.get('model','').removeprefix('openai/')=='gpt-5.6-sol' and c.get('effort',c.get('reasoning_effort'))=='xhigh' for c in contexts))
        if row['execution']=='completed':assert row['runtime_matches_request'] and seen
    return row


def main():
    plan=read(OUT/'plan.json');freeze=read(OUT/'freeze.json');task=freeze['task']
    assert sha(ROOT/plan['protocol_path'])==plan['protocol_sha256']
    assert (OUT/'plan.json').read_bytes()==(ROOT/'docs/evidence/br028-plan.json').read_bytes()
    assert freeze['plan_sha256']==sha(OUT/'plan.json')
    verify(task);verify(plan['parent_task'])
    for path,h in plan['prior_receipts'].items():assert sha(ROOT/path)==h
    for path,h in plan['code_sha256'].items():assert sha(ROOT/path)==h
    old=plan['parent_task'];base=ROOT/task['task_path']
    assert set(task['files'])-set(old['files'])=={'environment/data/reference_volume.npz'}
    assert not set(old['files'])-set(task['files'])
    changed=[p for p,h in old['files'].items() if task['files'][p]!=h]
    assert sorted(changed)==['instruction.md','task.toml']
    author=read(OUT/'author-audit.json');assert sha(OUT/'author-audit.json')==freeze['author_audit_sha256']
    truth=read(base/'tests/truth.json')
    for row in author['author_rows']:
        assert sha(ROOT/row['answer_path'])==row['answer_sha256']
        assert score(read(ROOT/row['answer_path']),truth)==row['grade']
    assert author['author_rows'][0]['grade']['reward']==1
    rows=[collect_trial(task,p) for p in ['oracle','nop','sol-xhigh']]
    assert len({r['task_checksum'] for r in rows})==1
    assert rows[0]['reward']==1 and rows[1]['reward']==0
    audit=read(OUT/'bench-audit.json');assert audit['status'].startswith('completed')
    assert audit['plan_sha256']==sha(OUT/'plan.json') and audit['freeze_sha256']==sha(OUT/'freeze.json')
    check=audit['replications']['sol-xhigh'];assert check['image_audit']['public_files_match_plan']
    assert check['result']['result_sha256']==rows[-1]['result_sha256']
    parent=next(r for r in read(ROOT/'docs/evidence/br024-results.json')['prospective_rows'] if r['phase']=='sol-xhigh')
    assert sha(ROOT/parent['answer_path'])==parent['answer_sha256'] and sha(ROOT/parent['result_path'])==parent['result_sha256']
    receipt={'round':'BR-028','plan_sha256':sha(OUT/'plan.json'),'freeze_sha256':sha(OUT/'freeze.json'),
             'contrast':'Added source3D; same 2D inputs, query locations, destination CT, private answers, tolerance and resources.',
             'matched_prior_inputs_and_evaluation':True,'prior_task_files_and_receipts_unchanged':True,
             'changed_existing_task_files':changed,'added_task_files':['environment/data/reference_volume.npz'],
             'author_audit':author,'sampling_check':read(OUT/'sampling-check.json'),'prior_2d_attempt':parent,
             'prospective_rows':rows,'bench_audit':audit,'bench_audit_sha256':sha(OUT/'bench-audit.json'),
             'limitations':['One fresh attempt per condition cannot isolate source-depth effects from strategy and model variability.',
                            'The source volume is genuinely new information; repeated copies of the original plane are not equivalent.',
                            'Public source annotations leave potential training contamination despite isolated inputs and trace audit.',
                            'Sparse engineering landmark tolerances do not establish dense-field or clinical validity.']}
    for p in [OUT/'results.json',ROOT/'docs/evidence/br028-results.json']:p.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps([{k:r.get(k) for k in ['phase','execution','reward','grade','agent_seconds']} for r in rows],indent=2))

if __name__=='__main__':main()
