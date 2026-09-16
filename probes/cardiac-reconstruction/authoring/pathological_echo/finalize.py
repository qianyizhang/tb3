"""Close the completed experiment without rewriting frozen tasks or raw trials."""
import hashlib,json
from pathlib import Path
from run import verify
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent;B=ROOT/'runs/br034-pathological-echo'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    freeze=read(B/'freeze.json');verify(freeze)
    rows=[read(B/f'{k}-receipt.json') for k in ['oracle','nop','sol-xhigh']]
    assert all(r['execution']=='completed' for r in rows)
    assert len({r['task_checksum'] for r in rows})==1
    assert rows[0]['grade']['reward']==1 and rows[1]['grade']['reward']==0
    assert all(r['independent_replay_matches'] for r in rows)
    for r in rows:
        file=ROOT/r['result_path'];assert sha(file)==r['result_sha256']
        for p,h in r['artifacts'].items():assert sha(file.parent/'artifacts/app/answer'/p)==h
    assert rows[2]['runtime_matches_request'] and rows[2]['frozen_instruction_seen']
    for fn in ['evaluation-freeze.json','preserved-control-freeze.json','preserved-control-v2-freeze.json']:
        for p,h in read(B/fn)['files'].items():assert sha(B/p)==h
    replays={k:read(B/'replays'/('original-v2' if k=='original' else k)/'receipt.json') for k in ['original','patient','preserved','static','shift']}
    codehash=rows[2]['artifacts']['solve.py']
    assert all(r['submitted_files_sha256']['solve.py']==codehash for r in replays.values())
    for kind,r in replays.items():
        assert r['exit_code']==0 and not r['timeout']
        folder=B/'replays'/('original-v2' if kind=='original' else kind)
        inp=(B/'curation/ef48/input' if kind=='patient' else
             B/'curation/preserved-v2/input' if kind=='preserved' else
             folder/'input' if kind in ['static','shift'] else B/'input')
        for p,h in r['input_files_sha256'].items():assert sha(inp/p)==h
        for p,h in r['output_files_sha256'].items():assert sha(folder/'output'/p)==h
    out=dict(round='BR-034',status='completed selected clinical adaptation pilot',
        scope='Initialized dynamic LV cavity reconstruction, executable adaptation, and bounded functional assessment; no etiologic diagnosis truth',
        source_catalog_sha256=sha(B/'source/croissant.json'),source_code_commit=read(B/'source/repo-tree.json')['sha'],
        screened_cases=read(B/'source/function-screen.json'),screen_sector_coverage=read(B/'source/screen-sector-coverage.json'),
        primary_preparation=read(B/'preparation.json'),primary_validation=read(B/'validation.json'),
        hidden_patient_preparation=read(B/'curation/ef48/preparation.json'),hidden_patient_validation=read(B/'curation/ef48/validation.json'),
        preserved_patient_preparation=read(B/'curation/preserved-v2/preparation.json'),preserved_patient_validation=read(B/'curation/preserved-v2/validation.json'),
        freeze_sha256=sha(B/'freeze.json'),controls=freeze['controls'],
        evaluation_freeze_sha256=sha(B/'evaluation-freeze.json'),preserved_amendment_sha256=sha(ROOT/'docs/research-rounds/BR-034-preserved-control-amendment.md'),
        preserved_control_freezes={n:sha(B/n) for n in ['preserved-control-freeze.json','preserved-control-v2-freeze.json']},
        trials=rows,image_audit=read(B/'image-audit.json'),replays=replays,earlier_replay_infrastructure=read(B/'replays/original/receipt.json'),author_review=read(B/'author-review.json'),posthoc_geometry_diagnostic=read(B/'posthoc-geometry-diagnostic.json'),
        code_sha256={str(p.relative_to(ROOT)):sha(p) for p in HERE.iterdir() if p.is_file()},
        limitations=['One selected development patient and one model attempt do not establish a capability ceiling or clinical accuracy.',
                    'All scans are public and pretraining exposure is unknown.',
                    'Native archive bytes match publisher LFS hashes; publisher array-hash serialization was not reproduced by raw C-order hashing.',
                    'Reference surfaces are operator/software-derived and may contain errors; there is no independent cardiologist adjudication.',
                    'Initial reference surfaces are supplied; this is not raw segmentation from scratch.',
                    'LV endocardial surface indices do not establish myocardial material tracking or strain.',
                    'Functional-reference labels do not establish heart-failure syndrome, valve disease or disease etiology.',
                    'Image-only and post-model impressions from one session are descriptive, not a controlled diagnostic-benefit comparison.',
                    'The preserved-function control was added after dispatch and replaced on input-quality grounds before model completion.'])
    for p in [B/'results.json',ROOT/'docs/evidence/br034-clinical-adaptation-results.json']:
        assert not p.exists(),'Keep completed evidence append-only';p.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(status=out['status'],bytes=(B/'results.json').stat().st_size)))
if __name__=='__main__':main()
