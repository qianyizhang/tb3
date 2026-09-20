"""Freeze V3 without touching V1/V2 or exposing private reference context."""
from pathlib import Path
import copy, hashlib, json, shutil, tomllib
import numpy as np
from score import evaluate
ROOT = Path(__file__).resolve().parents[4]
H = Path(__file__).resolve().parent
B = ROOT/'runs/br042-all-vessels-v3'
T = B/'tasks/all-vessels'
OLD = ROOT/'runs/br042-all-vessels-v2/tasks/all-vessels'
MODELS = [('sol-xhigh','openai/gpt-5.6-sol','xhigh'), ('astra-medium','openai/gpt-6-astra','medium'), ('astra-xhigh','openai/gpt-6-astra','xhigh')]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
if __name__ == '__main__':
    assert not T.exists(), 'Never overwrite a freeze'
    shutil.copytree(OLD,T)
    shutil.copy2(H/'instruction.md',T/'instruction.md')
    shutil.copy2(H/'score.py',T/'tests/score.py')
    toml=(T/'task.toml').read_text().replace('all-vessels-image-only-v2','all-vessels-image-only-v3')
    (T/'task.toml').write_text(toml)
    assert tomllib.loads(toml)['agent']['timeout_sec']==3600
    ref=json.loads((T/'tests/reference.json').read_text())
    # Only oracle gets these names; no case-specific inventory in agent image.
    names={1:'LM',2:'LAD',3:'LCx',4:'D1',5:'D2',6:'OM1',7:'OM2',8:'IM',9:'RCA',10:'R-PDA',11:'R-PLA',12:'L-PDA',13:'L-PLA',14:'Other'}
    oracle=copy.deepcopy(ref)
    for c in oracle['centerlines']:c['vessel_name']=' / '.join(names[k] for k in sorted(set(c['labels'])))
    (T/'solution/centerlines.json').write_text(json.dumps(oracle)+'\n')
    controls={'oracle':evaluate(oracle,ref)}
    for name in ['swapped_labels','all_zero_labels','missing_left','missing_small_branch','shifted','extension','extra_unscored','duplicate_alternative']:
        obj=copy.deepcopy(oracle)
        if name=='missing_left':obj['centerlines']=[c for c in obj['centerlines'] if c['id'].startswith('right')]
        elif name=='missing_small_branch':obj['centerlines']=[c for c in obj['centerlines'] if 6 not in c['labels']]
        elif name=='extension':
            c=obj['centerlines'][-1];p=np.array(c['points_ras_mm']);v=p[-1]-p[-2];v/=np.linalg.norm(v)
            for i in range(1,31):c['points_ras_mm'].append((p[-1]+i*.5*v).tolist());c['labels'].append(c['labels'][-1])
        elif name=='extra_unscored':obj['centerlines'].append({'id':'synthetic-extra','vessel_name':'Synthetic distant test course','points_ras_mm':[[1000,0,0],[1000.5,0,0]],'labels':[0,0]})
        elif name=='duplicate_alternative':
            c=copy.deepcopy(obj['centerlines'][0]);c['id']='duplicate';c['labels']=[0]*len(c['labels']);obj['centerlines'].append(c)
        else:
            for c in obj['centerlines']:
                if name=='swapped_labels':c['labels']=[9 if k==2 else 2 if k==9 else k for k in c['labels']]
                elif name=='all_zero_labels':c['labels']=[0]*len(c['labels'])
                else:c['points_ras_mm']=(np.array(c['points_ras_mm'])+20).tolist()
        controls[name]=evaluate(obj,ref)
    expected={'oracle':(True,True),'swapped_labels':(True,False),'all_zero_labels':(True,False),'missing_left':(False,False),'missing_small_branch':(False,False),'shifted':(False,False),'extension':(True,True),'extra_unscored':(True,True),'duplicate_alternative':(False,False)}
    for name,(g,l) in expected.items():
        assert (controls[name]['geometry_pass'],controls[name]['labeled_pass'])==(g,l),(name,controls[name])
    # Public surface allowlist excludes all private references, controls and trial history.
    public={str(p.relative_to(T/'environment')):sha(p) for p in sorted((T/'environment').rglob('*')) if p.is_file()}
    assert set(public)=={'Dockerfile','DATA-LICENSE.txt','SOURCE_NOTICE.md','data/image.nii.gz'}
    assert sha(T/'environment/data/image.nii.gz')==sha(OLD/'environment/data/image.nii.gz')
    prompt=(T/'instruction.md').read_text()
    forbidden=['BR-042','BR-041','case 1','27 polylines','51.6','87.0','25.9','88.9','Astra','Sol','previous attempt','reference OM2']
    assert not any(s in prompt for s in forbidden)
    audit={'purpose':'Disambiguation only; no case-specific target inventory, coordinates, previous outputs, scoring feedback, extraction code or anatomical conclusions in public inputs.', 'public_files':public,'instruction_sha256':sha(T/'instruction.md'),'same_full_CTA':True,'one_hour_agent_timeout':True,'generic_taxonomy_and_review_instructions':True,'private_reference_sha256':sha(T/'tests/reference.json'),'reference_bytes_unchanged_from_v2':sha(T/'tests/reference.json')==sha(OLD/'tests/reference.json'),'history_exposure':False,'revision_caveat':'Authored after prior outcomes; prospective same-byte comparisons here are controlled, but refinement is not an independent held-out result.'}
    (B/'validation.json').write_text(json.dumps(controls,indent=2)+'\n')
    (ROOT/'docs/evidence/br042-v3-input-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    freeze={'round':'BR-042','version':3,'attempts_per_model':1,'retries':0,'timeout_seconds':3600,'execution':'sequential isolated jobs, same task bytes','models':[{'phase':p,'model':m,'effort':e} for p,m,e in MODELS], 'tasks':[{'task_path':str(T.relative_to(ROOT)),'files':{str(p.relative_to(T)):sha(p) for p in sorted(T.rglob('*')) if p.is_file()}}]}
    for p in [B/'freeze.json',ROOT/'docs/evidence/br042-v3-freeze.json']:p.write_text(json.dumps(freeze,indent=2)+'\n')
    print(json.dumps({'frozen_task':str(T),'controls':{k:{'geometry':v['geometry_pass'],'labeled':v['labeled_pass']} for k,v in controls.items()},'public_audit':audit},indent=2))
