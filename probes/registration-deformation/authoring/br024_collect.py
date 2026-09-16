"""Independent BR-024 grading, frozen-input checks, and allowlisted receipts."""
import json
from pathlib import Path
from collect import read,sha,seconds
from br024_run_trials import verify
from score import score

ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'runs/br024-harder-registration'


def collect_trial(task,phase):
    paths=list((ROOT/'runs'/f'br024-{task["task"]}-{phase}-v1-20260916').glob('*/result.json'));assert len(paths)==1
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
    plan=read(OUT/'plan.json');assert sha(ROOT/plan['protocol_path'])==plan['protocol_sha256']
    assert sha(ROOT/'runs/br021-deformable/source/source-receipt.json')==plan['source_receipt_sha256']
    assert (OUT/'plan.json').read_bytes()==(ROOT/'docs/evidence/br024-plan.json').read_bytes()
    assert sha(ROOT/plan['baseline_path'])==plan['baseline_sha256']
    rescue=read(OUT/'rescue-plan.json')
    assert (OUT/'rescue-plan.json').read_bytes()==(ROOT/'docs/evidence/br024-rescue-plan.json').read_bytes()
    for field in ['protocol','baseline','wrapper']:assert sha(ROOT/rescue[field+'_path'])==rescue[field+'_sha256']
    assert sha(Path(__file__).with_name('br024_translation.py'))==rescue['runner_sha256']
    assert rescue['parent_plan_sha256']==sha(OUT/'plan.json')
    neighborhood=read(OUT/'neighborhood-plan.json')
    assert (OUT/'neighborhood-plan.json').read_bytes()==(ROOT/'docs/evidence/br024-neighborhood-plan.json').read_bytes()
    for path,h in neighborhood['files'].items():assert sha(ROOT/path)==h
    for path,h in plan['prior_results_sha256'].items():assert sha(Path(path))==h
    for task in read(ROOT/'runs/br021-deformable/freeze.json')['tasks']:verify(task)
    cases=[];rows=[]
    for file in sorted((OUT/'freezes').glob('patient*.json')):
        freeze=read(file);case=freeze['case'];assert freeze['plan_sha256']==sha(OUT/'plan.json');task=freeze['task'];verify(task)
        author=read(OUT/f'author/patient{case}/audit.json');assert sha(OUT/f'author/patient{case}/audit.json')==freeze['author_audit_sha256']
        assert author['public_files_match'] and author['grade']['reward']==1
        batch=[collect_trial(task,p) for p in ['oracle','nop','sol-xhigh']]
        assert len({r['task_checksum'] for r in batch})==1
        assert batch[0]['reward']==1 and batch[1]['reward']==0
        audit=read(OUT/f'bench-audit-patient{case}.json');assert audit['status'].startswith('completed')
        assert audit['plan_sha256']==sha(OUT/'plan.json') and audit['freeze_sha256']==sha(file)
        check=audit['replications']['sol-xhigh'];assert check['image_audit']['public_files_match_plan']
        assert check['result']['result_sha256']==batch[-1]['result_sha256']
        cases.append({'case':case,'freeze_sha256':sha(file),'task':task,'author_audit':author,
                      'bench_audit_path':str((OUT/f'bench-audit-patient{case}.json').relative_to(ROOT)),
                      'bench_audit_sha256':sha(OUT/f'bench-audit-patient{case}.json'),'bench_audit':audit})
        rows.extend(batch)
    assert len(cases)<=2 and cases
    methods={'baseline':'feasibility.json','translation':'translation-feasibility.json','neighborhood':'neighborhood-feasibility.json'}
    curation=[]
    screen=read(OUT/'screen.json')
    for patient in screen['cases']:
        for candidate in patient['candidates']:
            methods_tested={}
            for method,path in methods.items():
                if not (OUT/path).exists():continue
                for record in read(OUT/path)['rows']:
                    if record['name']!=candidate['name']:continue
                    assert sha(ROOT/record['answer_path'])==record['answer_sha256']
                    regrade=score(read(ROOT/record['answer_path']),read(ROOT/candidate['truth_path']))
                    assert regrade==record['grade'];methods_tested[method]=record
            admitted=next((c for c in cases if c['author_audit']['preparation']['candidate']==candidate['name']),None)
            curation.append({'candidate':candidate,'methods':methods_tested,'admitted':bool(admitted)})
    receipt={'round':'BR-024','plan_sha256':sha(OUT/'plan.json'),'protocol_sha256':plan['protocol_sha256'],
             'screen_sha256':sha(OUT/'screen.json'),'prior_results_and_br021_task_files_unchanged':True,
             'translation_rescue_plan_sha256':sha(OUT/'rescue-plan.json'),'neighborhood_rescue_plan_sha256':sha(OUT/'neighborhood-plan.json'),
             'cases':cases,'prospective_rows':rows,'curation':curation,
             'limitations':['Cases deliberately selected using manual labels for nonuniform deformation; this is not unbiased held-out sampling.',
                            'One fresh attempt per admitted patient cannot establish reliable difficulty or model rankings.',
                            'Public annotations leave possible training contamination; runtime and trace audits cannot exclude it.',
                            'A failed author method on an unadmitted view is not evidence of a Sol failure.',
                            'Eight sparse landmarks and engineering tolerances do not certify dense or clinical registration validity.']}
    for p in [OUT/'results.json',ROOT/'docs/evidence/br024-results.json']:p.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps([{k:r.get(k) for k in ['task','phase','execution','reward','grade','agent_seconds']} for r in rows],indent=2))

if __name__=='__main__':main()
