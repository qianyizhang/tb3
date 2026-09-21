"""Exact inclusion identity with tolerant physical-point localization."""
import json
import math
from pathlib import Path
import numpy as np


def read_json(path):
    path = Path(path)
    if path.stat().st_size > 200000:
        raise ValueError('Answer exceeds 200 KB')
    def unique(pairs):
        out = {}
        for k, v in pairs:
            if k in out:
                raise ValueError('Duplicate JSON key')
            out[k] = v
        return out
    return json.loads(path.read_text(), object_pairs_hook=unique)


def score(answer, key, region_dir):
    if not isinstance(answer, dict) or set(answer) != {'findings'} or not isinstance(answer['findings'], list):
        return {'passed': False, 'error': 'Expected exactly one list named findings'}
    seen = {}
    for finding in answer['findings']:
        if not isinstance(finding, dict) or set(finding) != {'object_id', 'included_label', 'point_lps_mm'}:
            return {'passed': False, 'error': 'Malformed finding'}
        oid, label, point = (finding[k] for k in ['object_id', 'included_label', 'point_lps_mm'])
        if not isinstance(oid, str) or not isinstance(label, str):
            return {'passed': False, 'error': 'Identity fields must be strings'}
        if (oid, label) in seen:
            return {'passed': False, 'error': 'Duplicate host/class pair'}
        if (not isinstance(point, list) or len(point) != 3 or
            not all(type(x) in (int, float) and math.isfinite(x) for x in point)):
            return {'passed': False, 'error': 'point_lps_mm must contain three finite numbers'}
        seen[(oid, label)] = point
    wanted = {(r['object_id'], r['included_label']): r for r in key['findings']}
    missing = sorted(wanted.keys() - seen.keys())
    extra = sorted(seen.keys() - wanted.keys())
    witnesses = []
    for pair in sorted(wanted.keys() & seen.keys()):
        with np.load(Path(region_dir) / wanted[pair]['region_file'], allow_pickle=False) as z:
            p = np.argwhere(z['mask']); a = z['affine_lps']
            assert len(p), 'Empty reference region'
            q = np.sum(p[:, None, :] * a[None, :3, :3], axis=2) + a[:3, 3]
            distance = float(np.linalg.norm(q - np.array(seen[pair]), axis=1).min())
        witnesses.append({'object_id': pair[0], 'included_label': pair[1],
                          'distance_to_included_voxel_mm': distance,
                          'accepted': distance <= key['point_tolerance_mm'] + 1e-9})
    detection = {k[0] for k in wanted} == {k[0] for k in seen}
    identity = not missing and not extra
    localization = identity and all(w['accepted'] for w in witnesses)
    return {'passed': bool(localization), 'detection_correct': detection,
            'identity_correct': identity, 'localization_correct': bool(localization),
            'expected_findings': len(wanted), 'reported_findings': len(seen),
            'missing_pairs': [list(p) for p in missing], 'extra_pairs': [list(p) for p in extra],
            'witnesses': witnesses}
