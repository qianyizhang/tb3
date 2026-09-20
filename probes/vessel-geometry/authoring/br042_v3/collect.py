"""Collect completed V3 trials without changing frozen outputs or metrics."""
from pathlib import Path
from datetime import datetime
import hashlib,json
import numpy as np
from scipy.spatial.distance import cdist
from score import score,samples
from run_trials import ROOT,B,PHASES,verify,job_name

def independent(obj, ref):
    p,pl,pw,_=samples(obj,True);r,rl,rw,_=samples(ref)
    dist=np.full(len(r),np.inf);ids=np.full(len(r),-1,int)
    for start in range(0,len(p),128):
        d=cdist(r,p[start:start+128]);ix=d.argmin(1);v=d[np.arange(len(r)),ix]
        improve=v<dist-1e-10
        dist[improve]=v[improve];ids[improve]=start+ix[improve]
    # Dense tie resolver in original submission order, independent of tree implementation.
    for start in range(0,len(r),128):
        d=cdist(r[start:start+128],p);best=d.min(1)
        ix=(d<=best[:,None]+1e-10).argmax(1)
        ids[start:start+len(ix)]=ix;dist[start:start+len(ix)]=d[np.arange(len(ix)),ix]
    same=pl[ids]==rl;out={}
    for name in ['geometry','labeled']:
        out[name]={}
        for tol in [1,2]:
            hit=(dist<=tol)&(same if name=='labeled' else True)
            out[name][f'length_weighted_recall_{tol}mm']=float(np.average(hit,weights=rw))
            out[name][f'macro_recall_{tol}mm']=float(np.mean([np.average(hit[rl==k],weights=rw[rl==k]) for k in np.unique(rl)]))
    return out

def collect():
    task=json.loads((B/'freeze.json').read_text())['tasks'][0];verify(task);tp=ROOT/task['task_path'];rows=[]
    ref=json.loads((tp/'tests/reference.json').read_text())
    entries=[(phase,job_name(phase)) for phase in PHASES]
    for phase in ['astra-medium','astra-xhigh']:
        recovery=job_name(phase)+'-setup-recovery1'
        if list((ROOT/'runs'/recovery).glob('*/result.json')):
            entries=[(p+'-setup-failed' if p==phase else p,j) for p,j in entries]
            entries.append((phase,recovery))
    for phase,job in entries:
        paths=list((ROOT/'runs'/job).glob('*/result.json'))
        if len(paths)!=1:continue
        path=paths[0];r=json.loads(path.read_text());trial=path.parent
        if phase in ['sol-xhigh','astra-medium','astra-xhigh'] and r.get('exception_info') and not r.get('agent_execution'):phase+='-setup-failed'
        row={'phase':phase,'result_path':str(path.relative_to(ROOT)),'task_checksum':r.get('task_checksum'),'exception':r.get('exception_info'),'agent_execution':r.get('agent_execution'),'agent_result':r.get('agent_result'),'reward':(r.get('verifier_result') or {}).get('rewards')}
        ex=row['agent_execution'] or {}
        if ex.get('started_at') and ex.get('finished_at'):row['agent_wall_seconds']=(datetime.fromisoformat(ex['finished_at'].replace('Z','+00:00'))-datetime.fromisoformat(ex['started_at'].replace('Z','+00:00'))).total_seconds()
        mp=trial/'verifier/metrics.json'
        if mp.exists():row['score']=json.loads(mp.read_text())
        ans=trial/'artifacts/app/answer'
        if (ans/'centerlines.json').exists():
            row['answer_path']=str(ans.relative_to(ROOT));row['answer_sha256']=hashlib.sha256((ans/'centerlines.json').read_bytes()).hexdigest()
            row['method_md_present']=(ans/'method.md').exists()
            row['extraction_code_present']=any(ans.glob('*.py'))
            replay=score(ans,tp/'tests/reference.json');row['replay']=replay
            if 'score' in row:assert replay==row['score'];row['replay_matches']=True
            if replay['format_valid']:
                check=independent(json.loads((ans/'centerlines.json').read_text()),ref)
                assert all(np.isclose(v,replay[name][key]) for name,vals in check.items() for key,v in vals.items())
                row['independent_dense_distances']=check
        if phase not in ['oracle','nop']:
            contexts=[];candidates=[];image_calls=0;transport=[]
            log=trial/'agent/codex.txt'
            if log.exists():
                for line in log.read_text().splitlines():
                    try:event=json.loads(line)
                    except ValueError:continue
                    message=event.get('message',event.get('item',{}).get('message',''))
                    if any(x in message for x in ['Reconnecting','Falling back','stream disconnected']):transport.append(message)
            for session in (trial/'agent/sessions').rglob('*.jsonl'):
                for line in session.read_text().splitlines():
                    try:event=json.loads(line)
                    except ValueError:continue
                    payload=event.get('payload',{})
                    if event.get('type')=='turn_context':contexts.append({k:payload.get(k) for k in ['model','effort']})
                    if payload.get('type') in ['custom_tool_call','function_call']:
                        s=payload.get('input',payload.get('arguments',''));image_calls+='view_image' in s
                        if any(x in s for x in ['curl ','wget ','requests.','httpx.','web__run']):candidates.append(s[:2000])
            row['trace_audit']={'contexts':contexts[:1],'image_view_call_candidates':image_calls,'external_access_call_candidates':candidates,'transport_messages':transport,'note':'Inspect candidates manually. Runtime configuration is not provider identity attestation.'}
        rows.append(row)
    hashes={r['task_checksum'] for r in rows if r['task_checksum']};assert len(hashes)<=1
    out={'round':'BR-042','version':3,'frozen_bytes_verified':True,'same_task_checksum':len(hashes)==1,'completed_phases':[r['phase'] for r in rows],'runs':rows}
    out['normal_model_completions']=[r['phase'] for r in rows if r['phase'] in ['sol-xhigh','astra-medium','astra-xhigh'] and r['agent_execution'] and not r['exception']]
    out['interrupted_model_attempts']=[r['phase'] for r in rows if r['agent_execution'] and r['exception']]
    out['setup_exclusions']=[r['phase'] for r in rows if r['phase'].endswith('-setup-failed')]
    for p in [B/'results.json',ROOT/'docs/evidence/br042-v3-results.json']:p.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'completed':out['completed_phases'],'models':[{'phase':r['phase'],'exception_type':(r['exception'] or {}).get('exception_type'),'seconds':r.get('agent_wall_seconds'),'geometry':r.get('score',{}).get('geometry'),'labeled':r.get('score',{}).get('labeled')} for r in rows if r['phase'] not in ['oracle','nop']]},indent=2))
    return out
if __name__=='__main__':collect()
