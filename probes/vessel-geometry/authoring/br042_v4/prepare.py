"""Prepare a new local freeze and launch configs; never launches an experiment."""
from pathlib import Path
import hashlib,json,shutil,tomllib
ROOT=Path(__file__).resolve().parents[4]; H=Path(__file__).resolve().parent
B=ROOT/'runs/br042-all-vessels-v4'; T=B/'tasks/all-vessels'
OLD=ROOT/'runs/br042-all-vessels-v3/tasks/all-vessels'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    assert not B.exists(),'Never overwrite a prepared experiment'
    previous=json.loads((ROOT/'docs/evidence/br042-v3-freeze.json').read_text())['tasks'][0]
    assert {str(p.relative_to(OLD)):sha(p) for p in OLD.rglob('*') if p.is_file()}==previous['files']
    shutil.copytree(OLD,T)
    shutil.copy2(H/'instruction.md',T/'instruction.md')
    text=(T/'task.toml').read_text().replace('all-vessels-image-only-v3','all-vessels-image-only-v4')
    (T/'task.toml').write_text(text)
    assert tomllib.loads(text)['agent']['timeout_sec']==3600
    assert sha(T/'tests/score.py')==sha(OLD/'tests/score.py')
    assert sha(T/'tests/reference.json')==sha(OLD/'tests/reference.json')
    public={str(p.relative_to(T/'environment')):sha(p) for p in (T/'environment').rglob('*') if p.is_file()}
    assert set(public)=={'Dockerfile','DATA-LICENSE.txt','SOURCE_NOTICE.md','data/image.nii.gz'}
    assert public=={str(p.relative_to(OLD/'environment')):sha(p) for p in (OLD/'environment').rglob('*') if p.is_file()}
    prompt=(T/'instruction.md').read_text()
    assert not any(x in prompt for x in ['BR-042','Astra','Sol','case 1','right-2','right-3','316,314','reference OM2','previous attempt'])
    configs={};(B/'configs').mkdir()
    template=ROOT/'runs/br042-all-vessels-v2/configs/br042-all-vessels-astra-medium-v2-20260920.json'
    for phase in ['oracle','nop','astra-xhigh']:
        cfg=json.loads(template.read_text());job='br042-all-vessels-'+phase+'-v4-attempt1'
        cfg.update(job_name=job,n_attempts=1,n_concurrent_trials=1,timeout_multiplier=1.0,quiet=True)
        cfg['tasks'][0]['path']=str(T.relative_to(ROOT));cfg['retry']['max_retries']=0
        a=cfg['agents'][0];a.update(override_timeout_sec=None,max_timeout_sec=None)
        if phase=='astra-xhigh':a.update(name='codex',model_name='openai/gpt-6-astra',kwargs={'reasoning_effort':'xhigh'})
        else:a.update(name=phase,model_name=None,kwargs={},env={})
        assert cfg['environment']['mounts'] is None and not cfg['extra_instruction_paths'] and not cfg['plugins']
        assert not a['skills'] and not a['mcp_servers']
        path=B/'configs'/f'{phase}.json';path.write_text(json.dumps(cfg,indent=2)+'\n');path.chmod(0o600)
        configs[phase]={'path':str(path.relative_to(ROOT)),'sha256':sha(path),'job_name':job}
    freeze={'round':'BR-042','version':4,'status':'prepared_not_started','model':'openai/gpt-6-astra','effort':'xhigh','attempts':1,'retries':0,'timeout_seconds':3600,'configs':configs,'tasks':[{'task_path':str(T.relative_to(ROOT)),'files':{str(p.relative_to(T)):sha(p) for p in sorted(T.rglob('*')) if p.is_file()}}]}
    for p in [B/'freeze.json',ROOT/'docs/evidence/br042-v4-freeze.json']:p.write_text(json.dumps(freeze,indent=2)+'\n')
    audit={'public_environment_identical_to_v3':True,'reference_and_evaluator_identical_to_v3':True,'public_files':public,'instruction_sha256':sha(T/'instruction.md'),'case_specific_feedback_exposed':False,'scope':'Generic category cardinality, bounded peripheral workload, time-management and broader-review requirements. No extraction recipe, branch counts, coordinates, source courses or previous outputs supplied.','adjudication_limit':'No new label inheritance rule or retrospective GT relabeling. Ambiguous anatomy remains a separate review outcome.','comparison_limit':'Outcome-informed prompt refinement on the same public development case; not held-out capability estimation.','launch_config_policy':'Local configs retain required host routing/auth setup, not credential contents; configs are not committed.'}
    (ROOT/'docs/evidence/br042-v4-input-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    print('Prepared V4. No Docker jobs or model calls started.')
if __name__=='__main__':main()
