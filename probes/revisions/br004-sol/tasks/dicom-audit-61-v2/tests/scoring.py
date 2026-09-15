"""Exact findings and spatial evidence after public label-specific exclusions."""
import math

import numpy as np

TOLERANCE_MM = 3.0


def finite_point(value):
    if not isinstance(value, list) or len(value) != 3:
        raise ValueError('point_lps_mm must be a finite numeric 3D point')
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in value):
        raise ValueError('point_lps_mm must be a finite numeric 3D point')
    return np.asarray(value, dtype=float)


def near_region(point, coordinates):
    p = finite_point(point)
    return bool(np.any(np.sum((coordinates - p[None, :]) ** 2, axis=1) <= TOLERANCE_MM ** 2 + 1e-8))


def score(prediction, truth, regions):
    if not isinstance(prediction, dict) or set(prediction) != {'cases'}:
        raise ValueError('root must contain cases')
    cases = prediction['cases']
    if not isinstance(cases, list):
        raise ValueError('cases must be a list')
    ids = [c.get('case_id') for c in cases if isinstance(c, dict)]
    expected = {c['case_id']: c for c in truth['cases']}
    if len(ids) != len(cases) or any(not isinstance(cid, str) for cid in ids) or len(set(ids)) != len(ids) or set(ids) != set(expected):
        raise ValueError('case IDs must occur exactly once')
    details = []
    for row in cases:
        case_id = row['case_id']
        wanted = expected[case_id]
        raw = row.get('findings')
        if not isinstance(raw, list):
            raise ValueError('findings must be lists')
        findings, ignored = [], []
        for finding in raw:
            if not isinstance(finding, dict) or not isinstance(finding.get('label'), str):
                raise ValueError('findings must have string labels')
            point = finite_point(finding.get('point_lps_mm'))
            excluded = any(finding['label'] == e['label'] and np.all(point >= e['min_lps_mm']) and np.all(point <= e['max_lps_mm'])
                           for e in wanted.get('review_exclusions', []))
            (ignored if excluded else findings).append(finding)
        labels = [f['label'] for f in findings]
        if len(set(labels)) != len(labels):
            raise ValueError('one finding per in-scope label')
        positive = {f['label']: f for f in wanted['findings']}
        got, need = set(labels), set(positive)
        located, bad_points = [], []
        for finding in findings:
            if finding['label'] in positive:
                (located if near_region(finding['point_lps_mm'], regions[positive[finding['label']]['region_key']]) else bad_points).append(finding['label'])
        details.append({'case_id': case_id, 'missing': sorted(need - got), 'extra': sorted(got - need),
                        'bad_points': sorted(bad_points), 'located': sorted(located),
                        'expected_positive_labels': len(need), 'focus_labels': len(wanted['focus_labels']),
                        'source_stratum': wanted['stratum'], 'passed': got == need and not bad_points,
                        'ignored_findings': ignored})
    return {'passed': all(d['passed'] for d in details), 'cases': sorted(details, key=lambda x: x['case_id']),
            'correctly_located_labels': sum(len(d['located']) for d in details),
            'expected_positive_labels': sum(d['expected_positive_labels'] for d in details),
            'false_positive_labels': sum(len(d['extra']) for d in details)}
