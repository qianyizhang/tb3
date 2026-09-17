"""Export compact safe receipts; never copy Harbor runtime configs or raw traces."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[3];B=ROOT/'runs/br037-longitudinal-reading';E=ROOT/'docs/evidence'
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def dump(name,value):(E/name).write_text(json.dumps(value,indent=2)+'\n')
r=json.loads((B/'results.json').read_text());assert len(r)==4
freezes={n:json.loads((B/f'{n}-freeze.json').read_text()) for n in [x['condition'] for x in r]}
for n,f in freezes.items():
    assert f['grounding_sha256']==sha(B/'grounding.json')
    audit=json.loads((B/f'{n}-image-audit.json').read_text());assert audit['matches_frozen_packet'] and not any(audit['private_paths'].values())
diff=[k for k,v in freezes['p03-neutral']['files'].items() if freezes['p03-cue']['files'].get(k)!=v]
assert sorted(diff)==['instruction.md','task.toml'],diff
dump('br037-freeze.json',{'round':'BR-037','model':'openai/gpt-5.6-terra','effort':'high',
    'grounding_sha256':sha(B/'grounding.json'),'selection_sha256':sha(B/'selected.json'),
    'qualitative_rubric_sha256':sha(B/'review-rubric.json'),
    'rubric_timing':'After launch, before reading final model answers. Source targets and packets frozen before launch.',
    'p03_pair_differing_files':diff,'p03_pair_data_identical':True,
    'conditions':[{'condition':x['condition'],'task_checksum':x['task_checksum'],
        'task_path':freezes[x['condition']]['task_path'],
        'freeze_receipt_sha256':sha(B/f"{x['condition']}-freeze.json"),
        'solver_image_audit_sha256':sha(B/f"{x['condition']}-image-audit.json"),
        'manifest_sha256':freezes[x['condition']]['files']['environment/data/manifest.json'],
        'controls':x['controls']} for x in r]})
safe=[]
for x in r:
    y={k:x[k] for k in ['condition','trial','task_checksum','normal_completion','exception_type','contract_reward','freeze_unchanged','answer','answer_sha256','assessment','point_grounding','laterality_agrees_with_source','trace_summary','elapsed_seconds']}
    y['visible_trace_path']=str((B/f"{x['condition']}-visible-trace.json").relative_to(ROOT))
    y['visible_trace_sha256']=sha(ROOT/y['visible_trace_path'])
    y['clinical_pass']=None;y['clinical_pass_reason']='No composite validated clinical oracle; source and authored review are separate.'
    safe.append(y)
dump('br037-results.json',{'round':'BR-037','collected_at':datetime.now(timezone.utc).isoformat(),
    'normal_completions':4,'mechanical_passes':4,'clinical_success_rate':None,
    'sol_trials':0,'brain_trials':0,'source_case_lookup_observed':False,
    'training_exposure':'Unknown for public data; no clean-room claim.',
    'results':safe,'measurement_audit':json.loads((B/'measurement-audit.json').read_text())})
g=json.loads((B/'grounding.json').read_text());cur=[]
for c in g:
    p=B/'prepared'/c['case']/'manifest.json';m=json.loads(p.read_text());visible=[s for s in m['series'] if s['visit'] in ['V1','V2']]
    cur.append({'case':c['case'],'source_id':c['source_id'],'stratum':c['source_stratum'],
        'clinical_context':{k:c['labels'][k] for k in ['Age_at_Screening','Arm','HR','HER2','pCR']},
        'ftv_cc':[c['labels'][f'VOLUME_TUM_BLU_V{i}0'] for i in range(1,5)],
        'source_diameter_values':[c['labels'][f'LD_T{i}'] for i in range(4)],
        'source_diameter_unit':'Not explicit in released workbook; cm is provisional, percentage comparisons are unit invariant.',
        'source_reference_regions':c['references'],
        'source_frame_count_all_visits':sum(s['source_frame_count'] for s in m['series']),
        'source_frame_count_visible':sum(s['source_frame_count'] for s in visible),
        'visible_volumes':len(visible),'visible_exam_days':sorted(set(s['day'] for s in visible)),
        'conversion_audit_sha256':sha(B/f"{c['case']}-conversion-audit.json")})
dump('br037-curation.json',{'round':'BR-037','collection_url':'https://www.cancerimagingarchive.net/collection/ispy2/',
    'collection_doi':'10.7937/TCIA.D8Z0-9T85','metadata_receipts':json.loads((B/'source/metadata-receipts.json').read_text()),
    'cases':cur,'brain_status':json.loads((B/'brain-triage.json').read_text()),
    'scope':'Three stratified breast treatment-monitoring cases. No multi-organ or rare-disease claim.'})
print('Exported BR-037 freeze, curation and results receipts; all four packet/grounding audits passed.')
