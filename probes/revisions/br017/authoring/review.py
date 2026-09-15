"""Review all completed trials and localize answers against source-derived deltas."""
import itertools
import json
from pathlib import Path
import re
import sys

import nibabel as nib
import numpy as np
from common import ROOT, OUT, sha, write
from audit import full_mask


def main():
    result = json.loads((OUT / 'results.json').read_text())
    task_count = len(list((OUT / 'freezes').glob('*.json')))
    assert len(result['rows']) == task_count * 3 and result['task_files_unchanged']
    models = [r for r in result['rows'] if r['phase'] == 'sol-xhigh']
    assert len(models) == task_count
    for row in result['rows']:
        assert row['execution'] == 'completed' and row['exception_type'] is None
        assert row['replay_matches']
        if row['phase'] in ['oracle', 'nop']:
            assert row['reward'] == (1 if row['phase'] == 'oracle' else 0)
    original = nib.load(ROOT / 'runs/br004-v1/source/s1233/segmentations/duodenum.nii.gz')
    baseline = np.asarray(original.dataobj, dtype=bool)
    affine = np.diag([-1., -1., 1., 1.]) @ original.affine
    reviews = []
    for row in models:
        assert row['runtime_matches_request'] and row['session_file_count'] == 1
        assert row['frozen_instruction_seen_in_user_message']
        task = row['task']; data = OUT / 'build' / task
        scene = json.loads((data / 'scene.json').read_text())
        host = next(o for o in scene['objects'] if o['proposed_label'] == 'duodenum')
        current = full_mask(data / host['file'], original.shape, affine)
        delta = current & ~baseline
        expected = {(host['object_id'], 'pancreas')} if delta.any() else set()
        pred = row['answer']['findings']
        actual = {(x['object_id'], x['included_label']) for x in pred}
        identities = expected == actual and len(pred) == len(expected)
        witnesses = []
        if identities:
            for finding in pred:
                point = np.array(finding['point_lps_mm'], dtype=float)
                voxel = np.linalg.solve(affine[:3, :3], point - affine[:3, 3])
                # Search a local source-grid neighbourhood, independently of the grader's full point list.
                offsets = np.array(list(itertools.product(range(-3, 4), repeat=3)))
                index = np.rint(voxel).astype(int) + offsets
                valid = np.all((index >= 0) & (index < baseline.shape), axis=1)
                index = index[valid]
                index = index[delta[tuple(index.T)]]
                differences = np.sum((index - voxel)[:, None, :] * affine[None, :3, :3], axis=2)
                distances = np.linalg.norm(differences, axis=1)
                nearest = float(distances.min()) if len(distances) else None
                witnesses.append({'point_lps_mm': finding['point_lps_mm'],
                                  'source_delta_nearest_mm': nearest,
                                  'accepted': nearest is not None and nearest <= 3.0 + 1e-9})
        independent = identities and all(w['accepted'] for w in witnesses)
        assert independent == row['grade']['passed']
        root = (ROOT / row['result_path']).parent
        trajectory = json.loads((root / 'agent/trajectory.json').read_text())
        calls = [c for s in trajectory['steps'] for c in s.get('tool_calls', [])]
        images = []
        for c in calls:
            if 'view_image' in json.dumps(c):
                images += re.findall(r'''['"](/app/[^'"\n]+\.png)['"]''', c['arguments'].get('input', ''))
                if c.get('function_name', '').endswith('view_image') and c['arguments'].get('path'):
                    images.append(c['arguments']['path'])
        returned_images = sum(
            x.get('content', '').count("'type': 'input_image'") +
            x.get('content', '').count('"type": "input_image"')
            for s in trajectory['steps'] if any('view_image' in json.dumps(c) for c in s.get('tool_calls', []))
            for x in s.get('observation', {}).get('results', []))
        commands, messages = [], []
        for line in (root / 'agent/codex.txt').read_text().splitlines():
            try:
                event = json.loads(line)
            except ValueError:
                continue
            item = event.get('item', {})
            if event.get('type') != 'item.completed':
                continue
            if item.get('type') == 'command_execution':
                commands.append(item)
            elif item.get('type') == 'agent_message':
                messages.append(item.get('text', ''))
        reviews.append({'task': task, 'result_sha256': row['result_sha256'],
                        'classification': 'valid_synthetic_task_pass' if independent else 'reviewed_synthetic_task_miss',
                        'independent_host_class_check': identities,
                        'independent_source_delta_witnesses': witnesses,
                        'independent_grade_matches': True,
                        'expected_inclusions': len(expected), 'reported_inclusions': len(pred),
                        'literal_image_paths_count': len(images), 'literal_image_paths': images,
                        'images_returned_as_input_image': returned_images,
                        'command_count': len(commands),
                        'nonzero_command_exit_codes': [c['exit_code'] for c in commands if c['exit_code'] != 0],
                        'delegation_calls': sum(any(k in json.dumps(c) for k in ['spawn_agent', 'create_thread', 'send_message_to_thread']) for c in calls),
                        'final_public_message': messages[-1] if messages else None,
                        'clinical_adjudication': 'Not established; source lineage is not independent clinician success.'})
    audit = json.loads((OUT / 'author/audit.json').read_text())
    record = {'round': 'BR-017', 'basis': 'Completed observable tool/answer records, frozen oracle/nop controls and independent localization on added source-grid voxels.',
              'tasks': reviews, 'controls': task_count * 2, 'author_scoring_controls': audit['author_scoring_controls'],
              'independent_source_audit_sha256': sha(OUT / 'author/audit.json'),
              'results_sha256': sha(OUT / 'results.json'),
              'intensity_review': json.loads((OUT / 'author/intensity-review.json').read_text()),
              'clinical_review': 'No independent specialist review was completed. Any observed failure is a synthetic-source task result, not a demonstrated clinician/model gap.',
              'interpretation_limit': 'Single trial per frozen condition; no population failure rate, causal mechanism, or general model weakness is established.'}
    write(OUT / 'author/reviews.json', record)
    write(ROOT / 'docs/evidence/br017-reviews.json', record)
    print(json.dumps([{k: r[k] for k in ['task', 'classification', 'images_returned_as_input_image', 'independent_grade_matches']} for r in reviews], indent=2))


if __name__ == '__main__':
    main()
