"""Close a completed paired pilot while preserving frozen sources and raw runs."""
import json
from pathlib import Path
from run import verify,sha
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent;B=ROOT/'runs/br035-segmentation-mechanics'
def read(p):return json.loads(p.read_text())
def main():
    f=read(B/'freeze.json');verify(f);trials=[];replays={}
    for c in ['masks','masks-images']:
        rows=[read(B/f'{c}-{p}-receipt.json') for p in ['oracle','nop','sol-xhigh']];assert len({r['task_checksum'] for r in rows})==1
        assert rows[0]['grade']['reward']==1 and rows[1]['grade']['reward']==0
        for r in rows:
            assert r['execution']=='completed' and r['independent_replay_matches'];path=ROOT/r['result_path'];assert sha(path)==r['result_sha256']
            for p,h in r['artifacts'].items():assert sha(path.parent/'artifacts/app/answer'/p)==h
        assert rows[2]['runtime_matches_request'] and rows[2]['frozen_instruction_seen'];trials.extend(rows)
        replay=read(B/'replays'/c/'receipt.json');answer=(ROOT/rows[2]['result_path']).parent/'artifacts/app/answer'
        for p,h in replay['submitted_files_sha256'].items():assert sha(answer/p)==h
        for p,h in replay['input_files_sha256'].items():assert sha(B/'clinical'/c/p)==h
        for p,h in replay['output_files_sha256'].items():assert sha(B/'replays'/c/'output'/p)==h
        runtime=read(B/'replay-runtime-audit.json')[c]
        expected={k.removeprefix('environment/data/'):v for k,v in f['conditions'][c]['files'].items() if k.startswith('environment/data/')}
        assert runtime['files']==expected and not any(runtime['private_paths_present'].values())
        assert runtime['packages']=={'numpy':'2.2.6','scipy':'1.15.3','pillow':'11.3.0','opencv-python-headless':'4.12.0.88','meshio':'5.3.5','scikit-image':'0.25.2'}
        assert replay['exit_code']==0 and not replay['timeout']
        replays[c]=replay
    out=dict(round='BR-035',status='completed paired segmentation-to-mechanics pilot',freeze_sha256=sha(B/'freeze.json'),protocol_sha256=f['protocol_sha256'],preparation=f['preparation'],controls=f['controls'],analytic_validation=read(B/'analytic-validation.json'),trials=trials,replays=replays,image_audits={c:read(B/f'{c}-image-audit.json') for c in ['masks','masks-images']},author_review=read(B/'author-review.json'),posthoc_mesh_quality=read(B/'posthoc-mesh-quality.json'),replay_runtime_audit=read(B/'replay-runtime-audit.json'),replay_image_records={c:read(B/f'{c}-replay-image.json') for c in ['masks','masks-images']},replay_build_infrastructure=read(B/'replay-build-infrastructure.json'),authoring_sha256={str(p.relative_to(ROOT)):sha(p) for p in HERE.iterdir() if p.is_file()},limitations=['One fresh attempt per condition on one previously curated public synthetic case; no capability ceiling or causal effect of additional images is established.','Perfect masks do not uniquely identify material motion; material scores measure closeness to a particular simulator.','Material metrics are conditional on covered reference centroids, with volume-weighted and per-region coverage reported.','The primary construction reward does not require simulator strain agreement.','Clinical all-phase cavity masks encode EF; replay tests geometric preservation and executable transfer, not diagnostic discovery.','No clinical myocardial wall or independent tissue-motion measurements are available; cavity strain is not myocardial strain.','Public pretraining exposure is unknown.'])
    for p in [B/'results.json',ROOT/'docs/evidence/br035-segmentation-mechanics-results.json']:
        assert not p.exists(),'Retain final evidence append-only';p.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(status=out['status'],bytes=(B/'results.json').stat().st_size)))
if __name__=='__main__':main()
