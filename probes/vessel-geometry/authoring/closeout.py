"""Collect bounded evidence without changing frozen tasks or model artifacts."""
from pathlib import Path
import hashlib,json,shutil
from datetime import datetime
import numpy as np
from score_geometry import score

ROOT=Path(__file__).resolve().parents[3];B=ROOT/'runs/br030-vessel-geometry';E=ROOT/'docs/evidence'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def write(p,r):p.write_text(json.dumps(r,indent=2)+'\n')
def verify_freeze(base):
    freeze=read(base/'freeze.json')
    for task in freeze['tasks']:
        folder=ROOT/task['task_path'];actual={str(p.relative_to(folder)):sha(p) for p in folder.rglob('*') if p.is_file()}
        assert actual==task['files'],task['task_path']
    return sha(base/'freeze.json')

def main():
    freeze_sha=verify_freeze(B);old_sha=verify_freeze(ROOT/'runs/br026-vessel-repair')
    rows=[]
    for phase in ['oracle','nop','terra-high']:
        base=ROOT/'runs'/f'br030-coronary-cpr-{phase}-v1-20260916';paths=list(base.glob('*/result.json'));assert len(paths)==1
        result=read(paths[0]);assert not result.get('exception_info')
        detail=paths[0].parent;metrics=read(detail/'verifier/metrics.json')
        r={'phase':phase,'result_path':str(paths[0].relative_to(ROOT)),'task_checksum':result['task_checksum'],
           'reward':metrics['reward'],'exception':result.get('exception_info'),'started_at':result['started_at'],'finished_at':result['finished_at'],
           'metrics':metrics,'agent_result':result.get('agent_result')}
        times=result.get('agent_execution') or {}
        if times.get('started_at') and times.get('finished_at'):
            r['agent_seconds']=(datetime.fromisoformat(times['finished_at'])-datetime.fromisoformat(times['started_at'])).total_seconds()
        if phase=='terra-high':
            answer=detail/'artifacts/app/answer';replay=score(answer,B/'geometry/reference.npz')
            assert replay['reward']==metrics['reward'] and replay['checks']==metrics['checks']
            for k,v in replay['metrics'].items():
                if isinstance(v,(float,int)):assert np.isclose(v,metrics['metrics'][k],atol=1e-4),k
            r['artifact_replay_matches']=True
            r['artifact_sha256']={p.name:sha(p) for p in sorted(answer.iterdir()) if p.is_file()}
            sessions=list((detail/'agent/sessions').rglob('*.jsonl'));calls=[];contexts=[]
            for session in sessions:
                for line in session.read_text().splitlines():
                    event=json.loads(line);pay=event.get('payload',{})
                    if event.get('type')=='turn_context':contexts.append({'model':pay.get('model'),'effort':pay.get('effort')})
                    if event.get('type')=='response_item' and pay.get('type') in ['function_call','custom_tool_call']:
                        calls.append(str(pay.get('arguments',pay.get('input',''))))
            r['trace_audit']={'session_sha256':{str(p.relative_to(ROOT)):sha(p) for p in sessions},'contexts':contexts,
                'tool_batches':len(calls),'image_view_batches':sum('view_image' in a for a in calls),
                'external_source_retrieval_observed':False,
                'review':'Read native tool-call trajectory and final artifacts. Agent inspects CTA views and HU values, identifies a ridge between existing components, adds a 0.9-mm envelope above 100 HU around its selected ridge, skeleton-traces the named route, resamples, transports frames and meshes the mask. No source-answer retrieval or private reference access was observed. This is trace evidence, not provider-side identity attestation.',
                'failure_mechanism':'arc_mm retains the cumulative grid of the pre-resampling skeleton. Interpolation cuts polyline corners, so the final saved polyline is shorter; arc_mm is not recomputed after resampling.',
                'limits':'Image use was observed, but no matched image-removed model trial was run. The public source and training overlap were disclosed.'}
        rows.append(r)
    assert len({r['task_checksum'] for r in rows})==1
    report={'round':'BR-030','task':'coronary-cpr','freeze_sha256':freeze_sha,'previous_br026_freeze_sha256':old_sha,
       'frozen_bytes_unchanged':True,'model_trials':1,'docker_controls':2,'rows':rows,
       'author_geometry':read(B/'geometry/build-receipt.json'),
       'image_baseline':{'score':read(B/'geometry/image-baseline-score.json'),'receipt':read(B/'geometry/image-baseline/receipt.json')},
       'mask_only_baseline':{'score':read(B/'geometry/mask-only-baseline-score.json'),'receipt':read(B/'geometry/mask-only-baseline/receipt.json')},
       'post_outcome_arc_correction':{'intervention':read(B/'geometry/terra-arc-correction/intervention.json'),'score':read(B/'geometry/terra-arc-correction-score.json')},
       'conclusion':'A natural coronary segmentation error and a useful larger workflow are established. The single Terra trial passes anatomy repair, tracing and meshing and fails CPR distance-axis consistency only; one-field author correction passes. Both fixed author baselines pass, including geometry-only repair/trace. Do not claim a hard anatomical discrimination task, clinical failure or general model capability limit.',
       'clinical_qualification':'One training-split case; no independent expert adjudication of the old MRA disagreement and no lesion-specific diagnostic ground truth. Retain geometry workflow and narrow software-consistency miss; do not promote as an anatomical reasoning failure.'}
    write(E/'br030-results.json',report)
    for source,target in [('freeze.json','br030-freeze.json'),('geometry/validation.json','br030-validation.json'),('adjudication/review-packet.json','br030-adjudication.json')]:shutil.copy2(B/source,E/target)
    sources={'round':'BR-030','checked_date':'2026-09-16',
       'primary_sources':[
        {'url':'https://pmc.ncbi.nlm.nih.gov/articles/PMC13496301/','role':'TopCoW annotation scope, paired acquisition context, topology motivation'},
        {'url':'https://zenodo.org/records/15692630','role':'TopCoW paired CTA/MRA images and labels'},
        {'url':'https://github.com/claim-berlin/TopCoW_2024_MRA_winning_solution','role':'CLAIM implementation; one fold and ground-truth ROI crop used locally, not its full challenge ensemble'},
        {'url':'https://arxiv.org/abs/2608.30404','role':'ImageCAS-X preprint; annotation protocol, benchmark, source anonymisation statement'},
        {'url':'https://zenodo.org/records/21887809','role':'ImageCAS-X labels, named centerline graphs, meshes, split files, descriptors and CAS-Net weights; record declares CC BY 4.0'},
        {'url':'https://www.kaggle.com/datasets/xiaoweixumedicalai/imagecas','role':'Original CTA; listing declares Apache 2.0'},
        {'url':'https://github.com/kitbransby/ImageCAS-X','role':'Pinned full-volume CAS-Net inference and LPS centerline coordinate convention'}],
       'download_manifests':{name:read(B/name) for name in ['source-manifest.json','coronary-reference-manifest.json','coronary-weight-manifest.json','sources/coronary/original/scan-manifest.json']},
       'claim_prediction_receipt':read(B/'prediction-receipt.json'),'coronary_prediction_receipt':read(B/'coronary-prediction-receipt.json'),
       'mra_screen':read(B/'mra-screen.json'),'coronary_screen':read(B/'coronary-screen.json'),
       'source_case':{'id':'1','split':'train','image_quality':4,'image_quality_label':'excellent','dominance':'right','disease_descriptor':'yes (scan-level only)','CTA_and_mask_grid_match':True,'centerline_coordinate_source':'LPS mm; explicitly converted to NIfTI RAS mm'},
       'limitations':['Only one reference annotation set per patient was found in the downloaded ZIP inventory. A second-rater comparison is reported in the paper, but those separate masks were not located in the release.',
                      'Released centerlines are skeletonized and smoothed from corrected masks; surfaces are also mask-derived. They provide geometry checks, not independent anatomical votes.',
                      'Case 1 is a training-split development example. No held-out accuracy estimate.',
                      'Four MRA predictions had full skeleton coverage of the seven present communicating-artery labels inspected. No small-branch natural gap was admitted from that screen.',
                      'CAS-Net inference used native MPS with CPU fallback for adaptive_max_pool3d; full volume, weights, patching, mirroring and postprocessing retained. Batch size set to one.'],
       'infrastructure_events':['Initial CLAIM load required allowlisting NumPy scalar metadata under Torch safe loading; no model prediction was emitted before correction.',
                                'Initial coronary inference hit an unsupported MPS pooling operation; rerun used the documented CPU fallback and completed in 191.36 seconds.',
                                'Initial trial authorization review rejected possible medical-data disclosure. The public anonymized source and empty NIfTI text metadata were verified; review then approved the same trial command. No model trial began before approval.',
                                'Author image baseline initially passed a NumPy array where MCP expects tuple sampling; type correction preceded its first output/score and did not change algorithm parameters.']}
    write(E/'br030-sources.json',sources)
    print(json.dumps({'freeze_unchanged':True,'controls':[r['reward'] for r in rows[:2]],'Terra':rows[-1]['metrics']['stages'],'arc_only_correction':report['post_outcome_arc_correction']['score']['reward']},indent=2))

if __name__=='__main__':main()
