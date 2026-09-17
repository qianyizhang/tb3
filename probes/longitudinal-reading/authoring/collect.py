"""Collect completed trials without exposing runtime credentials or hidden reasoning."""
from pathlib import Path
from collections import Counter
from datetime import datetime
import hashlib,json,re
import numpy as np
import nibabel as nib

ROOT=Path(__file__).resolve().parents[3];B=ROOT/'runs/br037-longitudinal-reading'
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
    grounding={c['case']:c for c in json.loads((B/'grounding.json').read_text())}
    out=[]
    for name in ['p01-neutral','p02-neutral','p03-neutral','p03-cue']:
        job=ROOT/'runs'/f'br037-{name}-terra-high-v1-20260917'
        rp=list(job.glob('*/result.json'))
        if not rp:continue
        p=rp[0];t=p.parent;d=json.loads(p.read_text());case=name[:3].upper()
        refs={r['visit']:r for r in grounding[case]['references']}
        freeze=json.loads((B/f'{name}-freeze.json').read_text());task=ROOT/freeze['task_path']
        assert {str(f.relative_to(task)):sha(f) for f in task.rglob('*') if f.is_file()}==freeze['files']
        manifest=json.loads((task/'environment/data/manifest.json').read_text())
        series={s['id']:s for s in manifest['series']}
        answers=list(t.glob('artifacts/**/assessment.json'))
        row={'condition':name,'trial':str(t.relative_to(ROOT)),'task_checksum':d['task_checksum'],
             'normal_completion':not bool(d.get('exception_info')),
             'exception_type':(d.get('exception_info') or {}).get('exception_type'),
             'contract_reward':(d.get('verifier_result') or {}).get('rewards',{}).get('reward'),
             'agent_result':d.get('agent_result'),'freeze_unchanged':True,'controls':[]}
        for phase in ['oracle','nop']:
            cp=next((ROOT/'runs'/f'br037-{name}-{phase}-v1-20260917').glob('*/result.json'))
            cd=json.loads(cp.read_text());assert cd['task_checksum']==d['task_checksum']
            row['controls'].append({'phase':phase,'contract_reward':cd['verifier_result']['rewards']['reward'],'exception_type':(cd.get('exception_info') or {}).get('exception_type')})
        if answers:
            assert len(answers)==1;ap=answers[0];a=json.loads(ap.read_text())
            row.update(answer=str(ap.relative_to(ROOT)),answer_sha256=sha(ap),assessment=a)
            points=[]
            for o in a.get('observations',[]):
                s=series.get(o.get('series_id'));ref=refs.get(o.get('visit'))
                if not s or not ref:continue
                ras=nib.affines.apply_affine(np.array(s['affine_ras_mm']),o['voxel'])
                lps_delta=(ras-np.array(ref['voi_center_ras_mm']))*[-1,-1,1]
                basis=np.array(ref['voi_half_vectors_lps_mm']).T
                unit=np.linalg.solve(basis,lps_delta)
                points.append({'visit':o['visit'],'series_id':o['series_id'],'voxel':o['voxel'],
                    'description':o['description'],'ras_mm':ras.tolist(),
                    'distance_to_source_voi_center_mm':float(np.linalg.norm(lps_delta)),
                    'within_source_voi':bool(np.max(np.abs(unit))<=1),
                    'voi_relative_coordinates':unit.tolist()})
            row['point_grounding']=points
            row['laterality_agrees_with_source']=a.get('primary_location',{}).get('laterality')=={'L':'left','R':'right'}[refs['V1']['laterality']]
            row['artifact_hashes']={str(f.relative_to(ap.parent)):sha(f) for f in ap.parent.rglob('*') if f.is_file()}
        # Only visible tool operations/messages, not reasoning items.
        events=[];counts=Counter();contexts=[];image_blocks=0
        for sp in sorted((t/'agent').glob('sessions/**/*.jsonl')):
            for ln,line in enumerate(sp.read_text().splitlines(),1):
                try:e=json.loads(line)
                except json.JSONDecodeError:continue
                q=e.get('payload',{})
                if e.get('type')=='turn_context':contexts.append({'model':q.get('model'),'effort':q.get('effort')})
                if e.get('type')!='response_item':continue
                typ=q.get('type');counts[typ]+=1
                if typ in ['custom_tool_call','function_call']:
                    events.append({'file':str(sp.relative_to(ROOT)),'line':ln,'type':typ,'name':q.get('name'),'input':q.get('input',q.get('arguments'))})
                elif typ in ['custom_tool_call_output','function_call_output']:
                    val=q.get('output',[])
                    if isinstance(val,list):image_blocks+=sum(x.get('type') in ['input_image','image'] for x in val if isinstance(x,dict))
                elif typ=='message' and q.get('role')=='assistant':
                    content=q.get('content',[])
                    events.append({'file':str(sp.relative_to(ROOT)),'line':ln,'type':'assistant_message','text':'\n'.join(x.get('text','') for x in content if isinstance(x,dict))})
        row['trace_summary']={'turn_contexts':contexts,'response_item_counts':dict(counts),'image_output_blocks':image_blocks,'visible_event_count':len(events)}
        execution=d.get('agent_execution') or {}
        row['agent_execution']=execution
        if execution.get('started_at') and execution.get('finished_at'):
            row['elapsed_seconds']=(datetime.fromisoformat(execution['finished_at'])-datetime.fromisoformat(execution['started_at'])).total_seconds()
        (B/f'{name}-visible-trace.json').write_text(json.dumps(events,indent=2)+'\n')
        out.append(row)
    (B/'results.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps([{'condition':r['condition'],'normal_completion':r['normal_completion'],'contract_reward':r['contract_reward'],'laterality_agrees':r.get('laterality_agrees_with_source'),'trace':r['trace_summary']} for r in out],indent=2))
if __name__=='__main__':main()
