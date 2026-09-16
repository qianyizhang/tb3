"""Close a bounded screen only when all conditionally required trials are collected."""
import hashlib
import json
from pathlib import Path
from run_trial import verify

ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent;B=ROOT/'runs/br031-cardiac-levels'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())

def main():
    rows=[]
    for p in sorted(B.glob('*-receipt.json')):rows.append(read(p))
    models=[r for r in rows if r['phase'] not in ['oracle','nop']]
    assert models and all(r['execution']=='completed' for r in models),'Handle infrastructure/timeout separately'
    stages=sorted({r['stage'] for r in rows})
    for stage in stages:
        freeze=read(B/f'cardiac-{stage}-freeze.json');verify(freeze)
        assert sha(ROOT/'docs/research-rounds/BR-031-cardiac-agent-levels.md')==freeze['protocol_sha256']
        same=[r for r in rows if r['stage']==stage]
        assert len({r['task_checksum'] for r in same})==1
        assert next(r for r in same if r['phase']=='oracle')['reward']==1
        assert next(r for r in same if r['phase']=='nop')['reward']==0
    one=next(r for r in models if r['stage']=='l1' and r['phase']=='terra-high')
    pending=False
    if not one['grade']['complete_pass']:
        two=next(r for r in models if r['stage']=='l1' and r['phase']=='sol-xhigh')
        if not two['grade']['complete_pass']:
            three=next((r for r in models if r['stage']=='l1v' and r['phase']=='sol-xhigh'),None)
            if three is None:
                assert (B/'approval-block.json').exists() and not (ROOT/'runs/br031-cardiac-l1v-sol-xhigh-v1-20260916').exists()
                pending=True
            else:assert three['execution']=='completed'
    for r in models:
        assert r['runtime_matches_request'] and r['frozen_instruction_seen'] and r['independent_replay_matches']
        assert sha(ROOT/r['result_path'])==r['result_sha256']
        answer=(ROOT/r['result_path']).parent/'artifacts/app/answer'
        for p,h in r['artifacts'].items():assert sha(answer/p)==h
    images=[]
    for p in sorted(B.glob('*-image-audit.json')):
        r=read(p);assert r['public_inventory_matches_freeze'] and not any(r['private_paths_present'].values())
        images.append(dict(path=str(p.relative_to(ROOT)),sha256=sha(p),stage=p.name.split('-')[0],image_id=r['image_id'],allowed_files=len(r['files'])))
    compact=[]
    for row in rows:
        row=dict(row)
        if row['grade']:row['grade']={k:v for k,v in row['grade'].items() if k!='region_engineering_percent'}
        compact.append(row)
    result=dict(round='BR-031',status='completed L0/L1; L1V awaiting explicit approval' if pending else 'completed bounded author-curated agent diagnostic',
                remaining_action=read(B/'approval-block.json') if pending else None,
                approval_resolution=read(B/'approval-resolution.json') if (B/'approval-resolution.json').exists() else None,
                source='One STRAUS simulated healthy cycle; prior author exposure; no independent clinical data',
                user_source_context='Hierarchy pasted by user from another chat. That chat was not identified or opened; no additional provenance is inferred.',
                wrappers=dict(controls_harbor='0.18.0',models_harbor='0.14.0',verifier='identical separate-container frozen task files within each condition'),
                trials=compact,image_audits=images,observation_coverage=read(B/'observation-coverage.json'),
                volume_input_check=read(B/'volume-registration-check.json'),section_checks=read(B/'section-validation.json'),
                original_author_baselines=read(B/'cardiac-l1-freeze.json')['controls'],
                small_surface_preserving_control=read(B/'controls/surface-preserving-score.json'),
                code_sha256={str(p.relative_to(ROOT)):sha(p) for p in sorted(HERE.glob('*')) if p.is_file()},
                frozen_tasks={s:sha(B/f'cardiac-{s}-freeze.json') for s in stages},
                protocols={str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'docs/research-rounds/BR-031-cardiac-agent-levels.md',ROOT/'docs/research-rounds/BR-031-volume-contrast.md']},
                limits=['One model attempt per condition; no success-rate estimate or general frontier claim.',
                        'L1 has sparse observation and unknown unobserved motion; oracle pass is not proof of identifiability.',
                        'In L1V the formerly withheld planes are inside the added volume, so their score is not unseen-view generalization.',
                        'Positive Jacobians and accurate total tissue volume do not establish valid local mechanics or force balance.',
                        'No stage 2-4 trial or cavity/EF, blood-flow or diagnostic claim.',
                        'Runtime trace model names do not independently establish provider-side identity or pretraining exposure.'])
    suffix='-pending-approval' if pending else ''
    for out in [B/f'results{suffix}.json',ROOT/f'docs/evidence/br031-cardiac-agent-results{suffix}.json']:
        assert not out.exists(),'Preserve a closed receipt'
        out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(model_trials=len(models),control_trials=len(rows)-len(models),pending_approval=pending,evidence_bytes=(B/f'results{suffix}.json').stat().st_size),indent=2))

if __name__=='__main__':main()
