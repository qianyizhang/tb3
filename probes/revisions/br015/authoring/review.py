"""Audit completed BR-015 passes and compare public data to original source voxels.

This is an authored evidence review, not an independent clinical adjudication.
It reads existing local artifacts and never launches or rewrites a frozen task.
"""
import gzip
import hashlib
import json
import re
from pathlib import Path

import nibabel as nib
import numpy as np

from common import ROOT, OUT, sha, write


def digest_stream(stream):
    h = hashlib.sha256()
    while block := stream.read(1024 * 1024):
        h.update(block)
    return h.hexdigest()


def source_nrrd(path, dtype):
    """Parse independently of the builder; authenticate decoded backing bytes."""
    with path.open('rb') as f:
        header = []
        while True:
            line = f.readline()
            assert line, 'Truncated NRRD header'
            if not line.strip():
                break
            header.append(line.decode('ascii'))
        fields = dict(line.strip().split(':', 1) for line in header
                      if ':' in line and not line.startswith('#'))
        fields = {k: v.lstrip('= ') for k, v in fields.items()}
        assert fields['encoding'] == 'gzip'
        assert fields['space'] == 'left-posterior-superior'
        with gzip.GzipFile(fileobj=f) as decoded:
            decoded_sha = digest_stream(decoded)
    raw = path.with_suffix('.raw')
    with raw.open('rb') as f:
        assert digest_stream(f) == decoded_sha
    shape = tuple(map(int, fields['sizes'].split()))
    assert raw.stat().st_size == np.prod(shape) * np.dtype(dtype).itemsize
    array = np.memmap(raw, dtype=dtype, mode='r', shape=shape, order='F')
    a = np.eye(4)
    a[:3, :3] = np.array([list(map(float, x.split(',')))
                          for x in re.findall(r'\(([^)]+)\)', fields['space directions'])]).T
    a[:3, 3] = list(map(float, fields['space origin'].strip('()').split(',')))
    return array, a, fields, decoded_sha


def main():
    result = json.loads((OUT / 'results.json').read_text())
    assert len(result['rows']) == 6 and result['task_files_unchanged']
    for row in result['rows']:
        assert row['execution'] == 'completed' and row['exception_type'] is None
        assert row['reward'] == (0 if row['phase'] == 'nop' else 1)
        assert row['replay_matches']
        assert sha(ROOT / row['result_path']) == row['result_sha256']
        if row['phase'] == 'sol-xhigh':
            assert row['runtime_matches_request'] and row['session_file_count'] == 1
            assert row['frozen_instruction_seen_in_user_message']
            assert row['independent_exact_set_check']
    for name in ['abdomen-c01', 'abdomen-v01']:
        rows = [r for r in result['rows'] if r['task'] == name]
        assert len(rows) == 3 and len({r['task_checksum'] for r in rows}) == 1

    # Historical freezes remain evidence, even after their conditions are retired.
    checked = []
    for pattern in ['br013-freeze.json', 'br014-*-freeze.json', 'br015-*-freeze.json']:
        for path in sorted((ROOT / 'docs/evidence').glob(pattern)):
            for task in json.loads(path.read_text())['tasks']:
                for member, digest in task['files'].items():
                    assert sha(ROOT / task['task_path'] / member) == digest
                checked.append({'freeze': str(path.relative_to(ROOT)),
                                'task': task['task'], 'files': len(task['files'])})

    old = ROOT / 'runs/br013-abdomen/build/abdomen-a02'
    c01 = OUT / 'build/abdomen-c01'
    members = [p for p in old.iterdir() if p.is_file()]
    assert all(sha(p) == sha(c01 / p.name) for p in members)
    assert sha(OUT / 'tasks/abdomen-c01/tests/expected.json') == sha(
        ROOT / 'runs/br013-abdomen/tasks/abdomen-a02/tests/expected.json')
    original = nib.load(ROOT / 'runs/br004-v1/source/s0629/ct.nii.gz')
    with np.load(c01 / 'ct.npz', allow_pickle=False) as z:
        assert np.array_equal(z['hu'], np.asarray(original.dataobj))
        assert np.array_equal(z['affine_lps'], np.diag([-1., -1., 1., 1.]) @ original.affine)
        c01_ct_voxels = z['hu'].size

    frozen = json.loads((ROOT / 'docs/evidence/br015-abdomen-v01-freeze.json').read_text())['tasks'][0]
    source = OUT / 'source/colonvessels'
    segpath = source / 'pat_016_Venous_Phase_Veins.seg.nrrd'
    ctpath = source / 'pat_016_Venous_Phase_CT.nrrd'
    assert sha(segpath) == frozen['source_segmentation_sha256']
    assert sha(ctpath) == frozen['source_ct_sha256']
    raw, a, fields, decoded_mask_sha = source_nrrd(segpath, 'uint8')
    ct, ca, _, decoded_ct_sha = source_nrrd(ctpath, '<i2')
    # The source headers serialize the same grid with slightly different floats.
    assert np.allclose(a, ca, atol=1e-10, rtol=0) and raw.shape[1:] == ct.shape
    grid_error_bound = float(np.max(np.abs(a[:3, :3] - ca[:3, :3]) @
                                    (np.array(ct.shape) - 1) + np.abs(a[:3, 3] - ca[:3, 3])))
    assert grid_error_bound < 1e-9
    data = OUT / 'build/abdomen-v01'
    source_rows = [{'number': 0, 'object_id': 'context'}] + frozen['source_identities']
    voxel_checks = []
    for row in source_rows:
        n = row['number']
        layer = int(fields[f'Segment{n}_Layer'])
        value = int(fields[f'Segment{n}_LabelValue'])
        with np.load(data / f"{row['object_id']}.npz", allow_pickle=False) as z:
            mask, affine = z['mask'], z['affine_lps']
            assert np.array_equal(affine[:3, :3], a[:3, :3])
            origin = np.linalg.solve(a[:3, :3], affine[:3, 3] - a[:3, 3])
            assert np.allclose(origin, np.rint(origin), atol=1e-8, rtol=0)
            start = np.rint(origin).astype(int)
            end = start + mask.shape
            assert np.all(start >= 0) and np.all(end <= ct.shape)
            slices = tuple(slice(lo, hi) for lo, hi in zip(start, end))
            assert np.array_equal(mask, raw[(layer, *slices)] == value)
            # Whole-volume count rules out any omitted source voxels outside the crop.
            count = int(np.count_nonzero(raw[layer] == value))
            assert int(mask.sum()) == count
            if n:
                assert fields[f'Segment{n}_Name'] == row['name']
                assert count == row['voxels']
            voxel_checks.append({'object_id': row['object_id'], 'source_segment': n,
                                 'source_layer': layer, 'source_value': value,
                                 'voxels_identical': count, 'source_crop_exact': True})
    start = np.array(frozen['ct_crop_start']); end = np.array(frozen['ct_crop_stop'])
    with np.load(data / 'ct.npz', allow_pickle=False) as z:
        assert np.array_equal(z['hu'], ct[tuple(slice(x, y) for x, y in zip(start, end))])
        expected_affine = ca.copy(); expected_affine[:3, 3] += ca[:3, :3] @ start
        assert np.allclose(z['affine_lps'], expected_affine, atol=1e-10, rtol=0)
        v01_ct_voxels = z['hu'].size
    assert len(frozen['controls']) == 7
    assert all(c['expected'] == c['grade']['passed'] for c in frozen['controls'])

    packet = json.loads((OUT / 'author/review-packet.json').read_text())
    assert sha(ROOT / packet['path'] / 'index.html') == packet['html_sha256']
    record = {
        'round': 'BR-015',
        'review_basis': 'Authored review of observable commands, requested images, public messages and answer artifacts; independent source-array comparisons. No independent clinician adjudication.',
        'tasks': {
            'abdomen-c01': {
                'validity': 'valid_model_pass', 'outcome': '11/11 identities; retire this tested condition.',
                'strategy': 'Read scene statistics, inspected HU samples and focused central-object 3-D views plus axial CT slices. Replaced an unavailable SciPy dependency with NumPy. Correctly assigned compact pancreas and surrounding duodenum.',
                'tool_issue': 'One coronal reslice request failed because a negative comma-separated positions argument lacked an equals sign. Frozen helper remains unchanged; --positions=-195,-185 is the documented workaround.',
                'interpretation': 'The same broad-inventory geometry that produced the BR013-A02 miss is solved with source CT and ready tools. One trial does not isolate CT from its accompanying previews/examples or estimate a causal effect. Broad anatomical-prior weakness is not established.'},
            'abdomen-v01': {
                'validity': 'valid_model_pass', 'outcome': '8/8 identities; retire this tested condition.',
                'strategy': 'Read all eight target CT preview images, the two overview images, helper sources and object statistics. No new focused renderer, CT reslicing, endpoint-distance calculation or graph metric was executed. Recovered answer-patch mismatch and unavailable xxd command.',
                'interpretation': 'Intact specialist vessel masks with exact vocabulary and same-phase CT did not elicit a miss. A public example groups the collateral and its two neighboring routes; it contains no identity key but supplies a focus hint. This is a scaffolded diagnostic, not a demonstration of unaided clinical reasoning.',
                'source_caveats': ['Published surgeon annotations support the reference identities, not blind solvability of this packet.', 'Slicer in-progress status tags are retained and not resolved by the data paper.', 'Some small-vessel mask samples have low HU, consistent with a source/partial-volume concern that needs expert review; this audit does not certify contour accuracy.', 'No full learned geometric or graph baseline was measured.'],
                'clinical_diagnosis': 'None asserted; the descriptive connecting-vessel name is not a rare-disease diagnosis.'}},
        'observable_access_audit': 'No private reference-key access or external source/patient matching observed in either trial.',
        'historical_and_current_freeze_checks': checked,
        'c01_old_public_members_byte_identical': len(members),
        'c01_original_ct_voxels_equal': c01_ct_voxels,
        'v01_original_mask_checks': voxel_checks,
        'v01_ct_crop_voxels_equal': v01_ct_voxels,
        'v01_source_grid_max_error_bound_mm': grid_error_bound,
        'v01_decoded_source_mask_sha256': decoded_mask_sha,
        'v01_decoded_source_ct_sha256': decoded_ct_sha,
        'v01_author_scoring_controls': 7,
        'review_packet': packet,
        'human_review': {
            'status': 'not_completed', 'targets_requested': ['o307', 'o609', 'o570'],
            'answers_received': 0, 'human_accuracy': None,
            'reviewer_background': 'User reported some relevant experience, then declined to label the packet and deferred to author judgment.',
            'interpretation': 'Neither a scored human failure nor demonstrated clinician solvability. No clinician credentials inferred.',
            'model_outcome_disclosed_after_decline': True},
        'result_sha256': sha(OUT / 'results.json'),
        'decision': 'Two normal passes, no new Sol failure and no completed independent human review. Retire these conditions. Further trials require a documented, expert-supported error-versus-variant case; do not expand labels, trim evidence or inject smaller defects to force a miss.'}
    write(OUT / 'author/reviews.json', record)
    write(ROOT / 'docs/evidence/br015-reviews.json', record)
    print(json.dumps({'model_passes': 2, 'docker_controls': 4, 'author_scoring_controls': 7,
                      'source_mask_comparisons': len(voxel_checks), 'ct_voxels_equal': c01_ct_voxels + v01_ct_voxels,
                      'unchanged_frozen_tasks': len(checked), 'completed_human_reviews': 0}))


if __name__ == '__main__':
    main()
