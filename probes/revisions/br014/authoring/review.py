"""Authored interpretation plus independent retained-voxel evidence checks."""
import json
import sys
from collections import defaultdict
import numpy as np
from common import ROOT, OUT, sha, write
sys.path.insert(0, str(ROOT/'probes/revisions/br013/authoring'))
from inspect_scene import load_scene


def points(o):
    p=np.argwhere(o['mask']);a=o['affine_lps']
    q=np.sum(p[:,None,:]*a[None,:3,:3],axis=2)+a[:3,3]
    return {tuple(x) for x in np.round(q,6)}


def main():
    result=json.loads((OUT/'results.json').read_text())
    assert len(result['rows'])==6 and result['task_files_unchanged']
    models=[r for r in result['rows'] if r['phase']=='sol-xhigh']
    assert len(models)==2
    for r in result['rows']:
        assert r['execution']=='completed' and r['exception_type'] is None
        assert r['reward']==(0 if r['phase']=='nop' else 1)
        assert r['replay_matches']
    for r in models:
        assert r['runtime_matches_request'] and r['session_file_count']==1
        assert r['frozen_instruction_seen_in_user_message'] and r['independent_exact_set_check']
    old=json.loads((ROOT/'docs/evidence/br013-freeze.json').read_text())
    for task in old['tasks']:
        assert all(sha(ROOT/task['task_path']/p)==s for p,s in task['files'].items())
    truth=json.loads((ROOT/'runs/br013-abdomen/tasks/abdomen-a01/tests/expected.json').read_text())['truth']
    originals={truth[o['object_id']]:points(o) for o in load_scene(ROOT/'runs/br013-abdomen/build/abdomen-a01')}
    screen=json.loads((OUT/'author/component-screen.json').read_text())
    checks=[]
    for v in screen['variants']:
        lineage={r['object_id']:r for r in v['lineage']};groups=defaultdict(list)
        for o in load_scene(ROOT/v['data_path']):
            label=lineage[o['object_id']]['label'];p=points(o)
            assert p<=originals[label]
            assert all(not (p&x) for x in groups[label])
            groups[label].append(p)
        for label,parts in groups.items():
            merged=set().union(*parts);missing=originals[label]-merged
            cut=next((c for c in v['cuts'] if c['label']==label),None)
            assert len(missing)==(cut['removed_voxels'] if cut else 0)
            checks.append({'gap_mm':v['gap_mm'],'label':label,'parts':len(parts),'retained_voxels':len(merged),'removed_voxels':len(missing)})
    reviews={
        'abdomen-i01':{
            'validity':'valid_model_pass', 'outcome':'11/11 exact identities; retire this tested condition as a hard Sol candidate.',
            'strategy':'Statistics and focused central-organ/vessel views; recognized the compact object inside the duodenal loop. One answer-file patch mismatch recovered. No private answer or external source matching observed.',
            'interpretation':'Same geometry as BR013-A02, exact present-label inventory. The historical 9/11 miss becomes 11/11 in one fresh trial, consistent with inventory uncertainty contributing. This is not a replicated causal estimate or proof that unaided mask-only recognition is always identifiable.',
            'terra_followup':'Skipped: no valid Sol failure.'},
        'abdomen-f01':{
            'validity':'valid_model_pass', 'outcome':'15/15 identities, including all four fragments; retire this synthetic split as a hard Sol candidate.',
            'strategy':'Focused shape/context views, surface-distance matrix and cross-mask overlap counts. Missing SciPy was replaced by NumPy. Both organ pairs correctly assigned; no external source matching or private key access observed.',
            'interpretation':'Substantial pieces and explicit repeated-label contract make grading clear. Artificial cut planes remain a shortcut. Compared with historical A01, IDs and contract also changed; the resource difference is descriptive, not an isolated fragmentation effect. Source overlap was used as a grouping heuristic, so success is not proof of pure anatomical reasoning.',
            'terra_followup':'Skipped: no valid Sol failure.'}}
    record={'round':'BR-014','review_basis':'Authored review of observable commands, images requested, public progress messages and answer artifacts; not independent clinical adjudication.',
            'tasks':reviews,'independent_lineage_checks':checks,
            'historical_br013_freezes_unchanged':True,'result_sha256':sha(OUT/'results.json'),
            'specialist_mask_only_adjudication':'Outstanding; not promoted into the interview submission.',
            'next_decision':'Keep fragmentation as a stress/control axis. Retain broad-inventory atypical identity recognition as the failure-backed research lead, subject to independent inferability review. Do not increase fragment count or remove more anatomy merely to force a miss.'}
    write(OUT/'author/reviews.json',record);write(ROOT/'docs/evidence/br014-reviews.json',record)
    print('Reviewed two normal passes; four Docker controls, 26 class/variant lineage checks and all historical freezes agree. No Terra trigger.')


if __name__=='__main__':main()
