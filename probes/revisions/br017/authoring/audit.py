"""Independent source-to-public voxel comparisons for the frozen pilot."""
import json
from pathlib import Path
import sys
import tarfile

import nibabel as nib
import numpy as np
from common import ROOT, OUT, sha, write
sys.path.insert(0, str(ROOT / 'probes/revisions/br013/authoring'))
sys.path.insert(0, str(ROOT / 'probes/revisions/br014/authoring'))
from screen_fragments import components


def full_mask(path, shape, affine):
    with np.load(path, allow_pickle=False) as z:
        mask = z['mask']; a = z['affine_lps']
        assert mask.dtype == bool and np.array_equal(a[:3, :3], affine[:3, :3])
        origin = np.linalg.solve(affine[:3, :3], a[:3, 3] - affine[:3, 3])
        assert np.allclose(origin, np.rint(origin), atol=1e-9, rtol=0)
        start = np.rint(origin).astype(int); end = start + mask.shape
        assert np.all(start >= 0) and np.all(end <= shape)
        out = np.zeros(shape, dtype=bool)
        out[tuple(slice(x, y) for x, y in zip(start, end))] = mask
        assert out.sum() == mask.sum()
        return out


def count_components(mask):
    p = np.argwhere(mask)
    if not len(p):
        return []
    lo, hi = p.min(0), p.max(0) + 1
    return [len(c) for c in components(mask[tuple(slice(x, y) for x, y in zip(lo, hi))])]


def main():
    screen = json.loads((OUT / 'author/screen.json').read_text())
    source = ROOT / 'runs/br004-v1/source/s1233'
    im = nib.load(source / 'ct.nii.gz'); ct = np.asarray(im.dataobj)
    affine = np.diag([-1., -1., 1., 1.]) @ im.affine
    originals = {}
    for label, h in screen['source_mask_sha256'].items():
        path = source / 'segmentations' / f'{label}.nii.gz'
        assert sha(path) == h
        originals[label] = np.asarray(nib.load(path).dataobj, dtype=bool)
    assert sha(source / 'ct.nii.gz') == screen['source_ct_sha256']
    before_union = np.logical_or.reduce(list(originals.values()))
    source_components = {k: count_components(originals[k]) for k in ['pancreas', 'duodenum']}
    reviewed = []; controls = 0; unique_controls = 0; verifier_versions = set()
    for path in sorted((OUT / 'freezes').glob('*.json')):
        task = json.loads(path.read_text())['tasks'][0]; name = task['task']
        folder = ROOT / task['task_path']; data = OUT / 'build' / name
        assert all(sha(folder / p) == h for p, h in task['files'].items())
        with tarfile.open(folder / 'environment/data.tar.gz') as tar:
            members = tar.getmembers()
            assert {m.name for m in members} == {p.name for p in data.iterdir()}
            import hashlib
            for m in members:
                assert m.isfile() and hashlib.sha256(tar.extractfile(m).read()).hexdigest() == sha(data / m.name)
        scene = json.loads((data / 'scene.json').read_text())
        public = {o['proposed_label']: full_mask(data / o['file'], im.shape, affine)
                  for o in scene['objects']}
        assert len(public) == len(scene['objects'])
        union = np.logical_or.reduce(list(public.values()))
        assert np.array_equal(union, before_union)
        payload_path = folder / 'tests/region-0.npz'
        payload = full_mask(payload_path, im.shape, affine) if payload_path.exists() else np.zeros(im.shape, dtype=bool)
        assert not np.any(payload & ~originals['pancreas'])
        assert not np.any(payload & originals['duodenum'])
        assert np.array_equal(public['duodenum'], originals['duodenum'] | payload)
        assert np.array_equal(public['duodenum'] & ~originals['duodenum'], payload)
        if name == 'abdomen-m01':
            assert 'pancreas' not in public
            assert np.array_equal(payload, originals['pancreas'] & ~originals['duodenum'])
        else:
            assert np.array_equal(public['pancreas'], originals['pancreas'] & ~payload)
        unchanged = [k for k in originals if k not in ['pancreas', 'duodenum']]
        assert all(np.array_equal(public[k], originals[k]) for k in unchanged)
        with np.load(data / 'ct.npz') as z:
            assert np.array_equal(z['hu'], ct) and np.array_equal(z['affine_lps'], affine)
        absent = sorted(set(originals) - set(public))
        controls += len(task['controls'])
        verifier_version = tuple(sorted((p, h) for p, h in task['files'].items() if p.startswith('tests/')))
        if verifier_version not in verifier_versions:
            unique_controls += len(task['controls'])
            verifier_versions.add(verifier_version)
        assert all(c['grade']['passed'] == c['expected'] for c in task['controls'])
        reviewed.append({'task': name, 'all_public_members_match_frozen_archive': True,
                         'original_ct_samples_equal': int(ct.size), 'union_voxels_equal': int(union.sum()),
                         'unaltered_classes_equal': len(unchanged), 'host_added_voxels_equal_payload': int(payload.sum()),
                         'all_payload_voxels_original_pancreas': True,
                         'missing_proposed_labels': absent,
                         'label_absence_cue_identifies_foreign_class': bool(absent == ['pancreas']),
                         'public_components26': {k: count_components(public[k]) if k in public else []
                                                 for k in ['pancreas', 'duodenum']}})
    # Earlier trials remain immutable while this diagnostic changes the task type.
    history = []
    for pattern in ['br013-freeze.json', 'br014-*-freeze.json', 'br015-*-freeze.json']:
        for path in sorted((ROOT / 'docs/evidence').glob(pattern)):
            for task in json.loads(path.read_text())['tasks']:
                assert all(sha(ROOT / task['task_path'] / p) == h for p, h in task['files'].items())
                history.append(task['task'])
    record = {'round': 'BR-017', 'basis': 'Independent reconstruction from public crop affine plus original NIfTI source; no comparison only to a generator-produced key.',
              'tasks': reviewed, 'source_components26': source_components,
              'author_scoring_controls': unique_controls,
              'scoring_control_records_across_snapshots': controls,
              'historical_tasks_unchanged': history,
              'limitations': ['Voxel lineage proves the synthetic edit, not clinical realism or specialist solvability.',
                             'Missing-label and component counts are narrow shortcut screens, not a general anatomy baseline.']}
    write(OUT / 'author/audit.json', record)
    write(ROOT / 'docs/evidence/br017-audit.json', record)
    print(json.dumps(record, indent=2))


if __name__ == '__main__':
    main()
