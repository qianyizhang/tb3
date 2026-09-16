"""Close a completed descriptive case, preserving its evidence boundaries."""
import hashlib,json
from pathlib import Path
from run import verify
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent;B=ROOT/'runs/br032-real-echo'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    freeze=read(B/'freeze.json');verify(freeze)
    rows=[read(B/f'{phase}-receipt.json') for phase in ['oracle','nop','sol-xhigh']]
    assert all(r['execution']=='completed' for r in rows)
    assert len({r['task_checksum'] for r in rows})==1
    assert rows[0]['grade']['reward']==1 and rows[1]['grade']['reward']==0
    model=rows[2];assert model['runtime_matches_request'] and model['frozen_instruction_seen'] and model['independent_replay_matches']
    for r in rows:
        path=ROOT/r['result_path'];assert sha(path)==r['result_sha256']
        for file,h in r['artifacts'].items():assert sha(path.parent/'artifacts/app/answer'/file)==h
    audit=read(B/'image-audit.json');assert audit['public_inventory_matches_freeze'] and not any(audit['private_paths_present'].values())
    evidence=dict(round='BR-032',status='completed descriptive real-scan case; no accuracy oracle',
        source=read(B/'source/source-receipt.json'),source_decode=read(B/'decode.json'),
        freeze_sha256=sha(B/'freeze.json'),input_validation=read(B/'input-validation.json'),
        trial_receipts=rows,image_audit=audit,independent_image_review=read(B/'review-metrics.json'),
        author_adjudication=read(B/'author-review.json'),
        executable_input_response={kind:read(B/'replays'/f'{kind}-v2'/'receipt.json') for kind in ['pose','static']},
        earlier_replay_infrastructure={kind:read(B/'replays'/kind/'receipt.json') for kind in ['pose','static']},
        replay_assessment=read(B/'replay-assessment.json'),
        code_sha256={str(p.relative_to(ROOT)):sha(p) for p in HERE.iterdir() if p.is_file()},
        preserved_reference_experiment='docs/evidence/br031-cardiac-agent-results.json',
        limitations=['The public scan may have appeared in pretraining; source exposure is unknown.',
                    'Runtime traces show observed tool use, not provider-side training or hidden model processes.',
                    'Fresh tasks and rigid coordinate changes do not make public anatomy unseen.',
                    'Closed meshes, contrast proxies and overlays are not independent 3D or material truth.',
                    'Alternative shapes are sensitivity scenarios, not calibrated confidence bounds.',
                    'Input-response checks characterize the saved executable and do not diagnose memorization.',
                    'One low-frame-rate scan and one agent attempt do not estimate clinical accuracy or success rate.'])
    for p in [B/'results.json',ROOT/'docs/evidence/br032-real-echo-results.json']:
        assert not p.exists(),'Preserve closed receipts';p.write_text(json.dumps(evidence,indent=2)+'\n')
    print(json.dumps(dict(status=evidence['status'],bytes=(B/'results.json').stat().st_size)))

if __name__=='__main__':main()
