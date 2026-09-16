"""Safe result receipts, artifact replay and trace metadata; no credentials."""
from datetime import datetime
import hashlib
import json
from pathlib import Path
import nibabel as nib
import numpy as np
from score import score_file
from run_trials import verify

ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'runs/br026-vessel-repair'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def seconds(x):
    if not x or not x.get('started_at') or not x.get('finished_at'):return None
    return (datetime.fromisoformat(x['finished_at'])-datetime.fromisoformat(x['started_at'])).total_seconds()

def main():
    freeze=read(BASE/'freeze.json');rows=[]
    audit_path=ROOT/'docs/evidence/br026-trace-audit.json'
    audits=read(audit_path)['audits'] if audit_path.exists() else []
    for task in freeze['tasks']:
        verify(task);base=ROOT/task['task_path']
        with np.load(base/'tests/truth.npz',allow_pickle=False) as z:truth={k:z[k] for k in z.files}
        group=[]
        for phase in ['oracle','nop','terra-high']:
            files=list((ROOT/'runs'/f"br026-{task['task']}-{phase}-v1-20260916").glob('*/result.json'))
            assert len(files)<=1
            if not files:continue
            p=files[0];r=read(p)
            if not r.get('finished_at'):continue
            ex=r.get('exception_info') or {};usage=r.get('agent_result') or {}
            row={'task':task['task'],'phase':phase,'execution':'completed' if not ex else 'excluded_execution_error',
                 'exception_type':ex.get('exception_type'),'result_path':str(p.relative_to(ROOT)),
                 'result_sha256':sha(p),'task_checksum':r['task_checksum'],
                 'reward':(r.get('verifier_result') or {}).get('rewards',{}).get('reward'),
                 'started_at':r.get('started_at'),'finished_at':r.get('finished_at'),
                 'agent_seconds':seconds(r.get('agent_execution')),'total_seconds':seconds(r),
                 'output_tokens':usage.get('n_output_tokens'),'input_tokens':usage.get('n_input_tokens'),
                 'cached_input_tokens':usage.get('n_cache_tokens'),'estimated_cost_usd':usage.get('cost_usd'),
                 'agent_version':(r.get('agent_info') or {}).get('version')}
            metrics=p.parent/'verifier/metrics.json'
            if metrics.exists():row['grade']=read(metrics)
            answer=p.parent/'artifacts/app/answer/corrected_mask.nii.gz'
            replay=score_file(answer,truth)
            if metrics.exists():
                assert replay['reward']==row['grade']['reward']
                if 'checks' in replay:assert replay['checks']==row['grade']['checks']
                for key in ['local_dice','local_recall','collateral_added_mm3','collateral_deleted_mm3','whole_mask_dice_diagnostic']:
                    if key in replay:assert abs(replay[key]-row['grade'][key])<1e-6
                row['artifact_replay_matches']=True
            if answer.exists():
                pred=np.asarray(nib.load(answer).dataobj)>0;original=truth['original'].astype(bool);gt=truth['gt'].astype(bool)
                deleted=gt & ~original
                row.update(answer_path=str(answer.relative_to(ROOT)),answer_sha256=sha(answer),
                           changed_voxels=int(np.count_nonzero(pred!=original)),
                           added_voxels=int(np.count_nonzero(pred&~original)),
                           deleted_voxels=int(np.count_nonzero(original&~pred)),
                           recovered_synthetic_gap_voxels=int(np.count_nonzero(deleted&pred)),
                           synthetic_gap_voxels=int(deleted.sum()))
            if phase=='terra-high':
                cfg=r['config']['agent'];row['requested_model']=cfg['model_name'];row['requested_effort']=cfg['kwargs']['reasoning_effort']
                contexts=[];sessions=[];instruction_seen=False
                instruction=(base/'instruction.md').read_text().strip()
                for session in sorted((p.parent/'agent/sessions').rglob('*.jsonl')):
                    sessions.append({'path':str(session.relative_to(ROOT)),'sha256':sha(session)})
                    for line in session.read_text().splitlines():
                        try:e=json.loads(line)
                        except ValueError:continue
                        payload=e.get('payload') or {}
                        if e.get('type')=='turn_context':
                            c={k:payload[k] for k in ['model','effort','reasoning_effort'] if k in payload}
                            if c and c not in contexts:contexts.append(c)
                        if e.get('type')=='response_item' and payload.get('role')=='user':
                            content=payload.get('content',[])
                            if isinstance(content,list) and any(instruction in x.get('text','') for x in content if isinstance(x,dict)):instruction_seen=True
                row.update(runtime_contexts=contexts,session_files=sessions,frozen_instruction_seen=instruction_seen,
                    runtime_matches_request=bool(contexts) and all(c.get('model','').removeprefix('openai/')=='gpt-5.6-terra' and c.get('effort',c.get('reasoning_effort'))=='high' for c in contexts),
                    source_retrieval_audit='pending_manual_trajectory_review')
                if row['execution']=='completed':assert row['runtime_matches_request'] and instruction_seen
                matching=[a for a in audits if a['task']==task['task'] and a['session_files']==sessions
                          and a['manual_review_status']=='completed']
                if matching:
                    row['source_retrieval_audit']=matching[0]['manual_review']['source_retrieval_observation']
                    row['trace_audit_path']=str(audit_path.relative_to(ROOT))
            group.append(row);rows.append(row)
        assert len({r['task_checksum'] for r in group})<=1
    report={'round':'BR-026','freeze_sha256':sha(BASE/'freeze.json'),'frozen_task_files_unchanged':True,
            'author_baselines':freeze['author_baselines'],'rows':rows,
            'limitations':['Two source patients and one fresh agent attempt per condition.',
              'Synthetic local deletion plus unchanged reference; no natural segmentation model error tested.',
              'Public training-source images; source retrieval can confound image-reasoning claims.',
              'Engineering annotation and threshold calibration, not independent clinical adjudication.',
              'One task result cannot establish broad vessel-repair capability or failure rates.',
              'Trace model labels are runtime provenance, not provider-side attestation.',
              'Real false-bridge repair is not tested by these two agent tasks.']}
    for p in [BASE/'results.json',ROOT/'docs/evidence/br026-results.json']:p.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps([{k:r.get(k) for k in ['task','phase','execution','reward','agent_seconds','changed_voxels','recovered_synthetic_gap_voxels','grade']} for r in rows],indent=2))

if __name__=='__main__':main()
