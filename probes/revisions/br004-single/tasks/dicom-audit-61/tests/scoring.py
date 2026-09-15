"""Pure deterministic finding and spatial-witness checks; no submitted code execution."""
import math
import numpy as np

TOLERANCE_MM=3.0

def near_region(point, coordinates):
    p=np.asarray(point,dtype=float)
    if p.shape!=(3,) or not np.isfinite(p).all():return False
    # Coordinates are private discrepancy-voxel centers in DICOM LPS mm.
    return bool(np.any(np.sum((coordinates-p[None,:])**2,axis=1) <= TOLERANCE_MM**2+1e-8))

def score(prediction, truth, regions):
    if not isinstance(prediction,dict) or set(prediction)!={'cases'}:raise ValueError('root must contain cases')
    cases=prediction['cases']
    if not isinstance(cases,list):raise ValueError('cases must be a list')
    ids=[c.get('case_id') for c in cases if isinstance(c,dict)]
    expected={c['case_id']:c for c in truth['cases']}
    if len(ids)!=len(cases) or len(set(ids))!=len(ids) or set(ids)!=set(expected):raise ValueError('case IDs must occur exactly once')
    details=[]
    for row in cases:
        case_id=row['case_id'];wanted=expected[case_id]
        findings=row.get('findings')
        if not isinstance(findings,list):raise ValueError('findings must be lists')
        labels=[f.get('label') for f in findings if isinstance(f,dict)]
        if len(labels)!=len(findings) or any(not isinstance(x,str) for x in labels) or len(set(labels))!=len(labels):raise ValueError('one finding per label')
        positive={f['label']:f for f in wanted['findings']}
        got=set(labels);need=set(positive)
        located=[];bad_points=[]
        for f in findings:
            if f['label'] in positive:
                if near_region(f.get('point_lps_mm',[]),regions[positive[f['label']]['region_key']]):located.append(f['label'])
                else:bad_points.append(f['label'])
        details.append({'case_id':case_id,'missing':sorted(need-got),'extra':sorted(got-need),'bad_points':sorted(bad_points),'located':sorted(located),'expected_positive_labels':len(need),'focus_labels':len(wanted['focus_labels']),'source_stratum':wanted['stratum'],'passed':got==need and not bad_points})
    return {'passed':all(d['passed'] for d in details),'cases':sorted(details,key=lambda x:x['case_id']),
            'correctly_located_labels':sum(len(d['located']) for d in details),
            'expected_positive_labels':sum(d['expected_positive_labels'] for d in details),
            'false_positive_labels':sum(len(d['extra']) for d in details)}
