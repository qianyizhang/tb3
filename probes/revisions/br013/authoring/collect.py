"""Collect completed pilot evidence; preserve unavailable usage and exclusions."""
import json
from datetime import datetime
from pathlib import Path
from screen import ROOT,OUT,sha,write
from scoring import score,read_json

def seconds(x):
    if not x or not x.get('started_at') or not x.get('finished_at'):return None
    return (datetime.fromisoformat(x['finished_at'])-datetime.fromisoformat(x['started_at'])).total_seconds()

def main():
    freeze=read_json(OUT/'freeze.json');rows=[]
    for task in freeze['tasks']:
        task_root=ROOT/task['task_path']
        assert all(sha(task_root/p)==digest for p,digest in task['files'].items())
        for phase in ['oracle','nop','sol-xhigh','terra-max']:
            paths=list((ROOT/'runs'/f"br013-{task['task']}-{phase}-v1-20260915").glob('*/result.json'))
            assert len(paths)<=1
            if not paths:continue
            path=paths[0];r=read_json(path)
            if not r.get('finished_at'):continue
            usage=r.get('agent_result') or {};exc=r.get('exception_info') or {}
            row={'task':task['task'],'phase':phase,'case':task['case'],'mode':task['mode'],
                 'result_path':str(path.relative_to(ROOT)),'result_sha256':sha(path),'task_checksum':r['task_checksum'],
                 'started_at':r.get('started_at'),'finished_at':r.get('finished_at'),
                 'execution':'timeout' if exc.get('exception_type')=='AgentTimeoutError' else 'execution_error' if exc else 'completed',
                 'exception_type':exc.get('exception_type'),'reward':(r.get('verifier_result') or {}).get('rewards',{}).get('reward'),
                 'agent_seconds':seconds(r.get('agent_execution')),'total_seconds':seconds(r),
                 'environment_setup_seconds':seconds(r.get('environment_setup')),'agent_setup_seconds':seconds(r.get('agent_setup')),
                 'verifier_seconds':seconds(r.get('verifier')),'input_tokens':usage.get('n_input_tokens'),
                 'cached_input_tokens':usage.get('n_cache_tokens'),'output_tokens':usage.get('n_output_tokens'),
                 'estimated_cost_usd':usage.get('cost_usd'),'agent_version':(r.get('agent_info') or {}).get('version')}
            details=path.parent/'verifier/details.json'
            if details.exists():row['grade']=read_json(details);row['grade_sha256']=sha(details)
            answer=path.parent/'artifacts/app/answer/answer.json'
            if answer.exists():
                row['answer_path']=str(answer.relative_to(ROOT));row['answer_sha256']=sha(answer)
                pred=read_json(answer);key=read_json(task_root/'tests/expected.json')
                row['answer']=pred;replayed=score(pred,key)
                reported={k:v for k,v in row.get('grade',{}).items() if k!='grading_seconds'}
                row['replay_matches']=replayed==reported
                assert row['replay_matches']
                field='corrections' if key['mode']=='audit' else 'assignments'
                wanted={(k,v) for k,v in key['truth'].items() if field=='assignments' or key['proposed'][k]!=v}
                try:
                    actual=[(x['object_id'],x['label']) for x in pred[field]]
                    independent=(set(pred)=={field} and len(actual)==len(wanted) and set(actual)==wanted
                                 and all(set(x)=={'object_id','label'} for x in pred[field]))
                except (TypeError,KeyError):independent=False
                row['independent_exact_set_check']=independent
                assert independent==replayed['passed']
            if phase in ['sol-xhigh','terra-max']:
                agent=r['config']['agent'];row['requested_model']=agent['model_name'];row['requested_effort']=agent['kwargs']['reasoning_effort']
                contexts=[];session_files=[];legacy=[];last_record=None;initial_prompt_seen=False
                instruction=(task_root/'instruction.md').read_text().strip()
                for session in sorted((path.parent/'agent/sessions').rglob('*.jsonl')):
                    session_files.append({'path':str(session.relative_to(ROOT)),'sha256':sha(session)})
                    for line in session.read_text().splitlines():
                        try:event=json.loads(line)
                        except ValueError:continue
                        p=event.get('payload') or {}
                        if event.get('type')=='turn_context':
                            ctx={k:p[k] for k in ['model','effort','reasoning_effort'] if k in p}
                            if ctx and ctx not in contexts:contexts.append(ctx)
                        if event.get('type')=='event_msg' and p.get('type')=='token_count':
                            u=(p.get('info') or {}).get('total_token_usage') or {}
                            if all(u.get(k)==row[k] for k in ['input_tokens','cached_input_tokens','output_tokens']):legacy.append(u)
                        if event.get('type')=='token_usage_record':last_record=p.get('thread_token_usage')
                        if event.get('type')=='response_item' and p.get('role')=='user':
                            content=p.get('content',[])
                            if isinstance(content,list) and any(instruction in x.get('text','') for x in content if isinstance(x,dict)):initial_prompt_seen=True
                row['runtime_contexts']=contexts;row['session_files']=session_files;row['session_file_count']=len(session_files)
                row['frozen_instruction_seen_in_user_message']=initial_prompt_seen
                row['runtime_matches_request']=bool(contexts) and all(c.get('model','').removeprefix('openai/')==row['requested_model'].removeprefix('openai/') and c.get('effort',c.get('reasoning_effort'))==row['requested_effort'] for c in contexts)
                row['reasoning_output_tokens']=legacy[-1].get('reasoning_output_tokens') if legacy else None
                row['last_record_stream_usage']=last_record
                row['token_basis']='Harbor counters; reasoning reported only from exactly matching legacy runtime counters. Record-stream totals retained separately.'
                trajectory=path.parent/'agent/trajectory.json'
                if trajectory.exists():
                    # Trajectories can exceed the answer size limit.
                    tr=json.loads(trajectory.read_text());calls=[c for s in tr.get('steps',[]) for c in s.get('tool_calls',[])]
                    row['trajectory_sha256']=sha(trajectory)
                    row['tool_wrappers']=len(calls);row['image_review_wrappers']=sum('view_image' in json.dumps(c) for c in calls)
                if row['execution']=='completed':assert row['runtime_matches_request']
            rows.append(row)
    for task in freeze['tasks']:
        observed=[r for r in rows if r['task']==task['task']]
        if len(observed)>1:assert len({r['task_checksum'] for r in observed})==1
    result={'round':'BR-013','freeze_sha256':sha(OUT/'freeze.json'),'task_files_unchanged':True,'rows':rows,
            'limitations':['One attempt per condition. A02/A03 reuse the same patient; three rows are not three independent patients.',
                           'A01 is calibration already solved by the author geometry baseline.',
                           'Source identity review is authored, not independent clinical certification. No diagnosis or subtle contour defect is graded.',
                           'Input tokens include cache; reasoning output is included in output. Cost is a harness estimate. CPU/RAM settings are limits, not measured peak usage.',
                           'Terra is conditional on valid Sol failure; no unconditional comparison of model success rates.']}
    write(OUT/'results.json',result);write(ROOT/'docs/evidence/br013-results.json',result)
    print(json.dumps([{k:r.get(k) for k in ['task','phase','execution','reward','agent_seconds','input_tokens','cached_input_tokens','output_tokens','runtime_matches_request','grade']} for r in rows],indent=2))

if __name__=='__main__':main()
