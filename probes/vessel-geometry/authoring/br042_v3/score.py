"""V3: label-independent correspondence with separate geometry and label coverage."""
import json
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree

MAX_SAMPLES = 500000

def samples(obj, require_names=False):
    curves = obj['centerlines']
    assert isinstance(curves, list) and 0 < len(curves) <= 200
    points, labels, weights, owners = [], [], [], []
    ids, geometries = set(), set()
    count = 0
    for ci, curve in enumerate(curves):
        if require_names:
            ident = curve['id']; name = curve['vessel_name']
            assert isinstance(ident, str) and ident.strip() and ident not in ids
            assert isinstance(name, str) and name.strip()
            ids.add(ident)
        p = np.asarray(curve['points_ras_mm'], dtype=float)
        lab = np.asarray(curve['labels'])
        assert p.ndim == 2 and p.shape[1] == 3 and 2 <= len(p) <= 20000
        assert np.isfinite(p).all()
        assert lab.shape == (len(p),) and lab.dtype.kind in 'iu' and np.isin(lab, np.arange(15)).all()
        if require_names:
            key = min(p.tobytes(), p[::-1].tobytes())
            assert key not in geometries, 'Exact duplicate polyline geometry'
            geometries.add(key)
        lengths = np.linalg.norm(np.diff(p, axis=0), axis=1)
        assert (lengths > 1e-6).all() and (lengths <= 1.5).all()
        for a, b, la, lb, length in zip(p[:-1], p[1:], lab[:-1], lab[1:], lengths):
            n = int(np.ceil(length/.25)); count += n
            assert count <= MAX_SAMPLES, 'Excessive total sampled length'
            t = (np.arange(n)+.5)/n
            points.append(a[None, :]+t[:, None]*(b-a))
            labels.append(np.where(t < .5, la, lb))
            weights.append(np.full(n, length/n)); owners.append(np.full(n, ci))
    return np.concatenate(points), np.concatenate(labels), np.concatenate(weights), np.concatenate(owners)

def nearest(source, target):
    """Nearest target sample, breaking numerical ties by submitted sample order."""
    tree = cKDTree(target)
    d, idx = tree.query(source)
    # Resolve only ties; selection never inspects anatomical labels.
    dd, _ = tree.query(source, k=2)
    for j in np.flatnonzero(np.isfinite(dd[:, 1]) & (np.abs(dd[:, 0]-dd[:, 1]) <= 1e-10)):
        candidates = np.asarray(tree.query_ball_point(source[j], d[j]+1e-10), dtype=int)
        ds = np.linalg.norm(target[candidates]-source[j], axis=1)
        idx[j] = int(candidates[ds <= ds.min()+1e-10].min())
        d[j] = np.linalg.norm(target[idx[j]]-source[j])
    return d, idx

def evaluate(obj, ref):
    r, rl, rw, _ = samples(ref)
    try:
        p, pl, pw, owner = samples(obj, require_names=True)
    except Exception as exc:
        return {'schema_version': 3, 'format_valid': False, 'geometry_pass': False,
                'labeled_pass': False, 'reward': 0, 'error': type(exc).__name__+': '+str(exc)}
    d, matched = nearest(r, p)
    pd, _ = nearest(p, r)
    same = pl[matched] == rl
    mean = lambda mask, w: float(np.average(mask, weights=w))
    per = {}
    for k in sorted(set(rl)):
        mask = rl == k
        row = {'reference_length_mm': float(rw[mask].sum())}
        for tol in (1, 2):
            geometric = d[mask] <= tol; correct = geometric & same[mask]
            row[f'geometry_recall_{tol}mm'] = mean(geometric, rw[mask])
            row[f'labeled_recall_{tol}mm'] = mean(correct, rw[mask])
            row[f'label_accuracy_given_geometry_{tol}mm'] = mean(same[mask][geometric], rw[mask][geometric]) if geometric.any() else None
        per[str(int(k))] = row
    out = {'schema_version': 3, 'format_valid': True, 'per_reference_category': per}
    for name in ('geometry', 'labeled'):
        metrics = {}
        for tol in (1, 2):
            hit = (d <= tol) & (same if name == 'labeled' else True)
            metrics[f'length_weighted_recall_{tol}mm'] = mean(hit, rw)
            metrics[f'macro_recall_{tol}mm'] = float(np.mean([v[f'{name}_recall_{tol}mm'] for v in per.values()]))
        out[name] = metrics
        out[name+'_pass'] = bool(metrics['macro_recall_1mm'] >= .9 and all(v[f'{name}_recall_1mm'] >= .8 for v in per.values()))
    out['identity'] = {f'accuracy_given_geometry_{tol}mm': mean(same[d <= tol], rw[d <= tol]) if np.any(d <= tol) else None for tol in (1, 2)}
    # Reference mass partitions into missed geometry, covered wrong label, covered correct.
    out['reference_length_partition_mm'] = {
        'missed_geometry': float(rw[d > 1].sum()),
        'covered_wrong_label': float(rw[(d <= 1) & ~same].sum()),
        'covered_correct_label': float(rw[(d <= 1) & same].sum())}
    confusion = {}
    for k in sorted(set(rl)):
        mask = (rl == k) & (d <= 1)
        confusion[str(int(k))] = {str(int(j)): float(rw[mask & (pl[matched] == j)].sum()) for j in sorted(set(pl[matched][mask]))}
    out['matched_label_confusion_length_mm'] = confusion
    out['output_review'] = [{'id': c['id'], 'vessel_name': c['vessel_name'],
        'benchmark_labels': sorted(set(c['labels'])),
        'length_mm': float(pw[owner == i].sum()),
        'within_1mm_reference_fraction': mean(pd[owner == i] <= 1, pw[owner == i]),
        'outside_1mm_reference_length_mm': float(pw[(owner == i) & (pd > 1)].sum())} for i, c in enumerate(obj['centerlines'])]
    out.update(reward=int(out['labeled_pass']), reference_length_mm=float(rw.sum()),
               submitted_length_mm=float(pw.sum()), polylines=len(obj['centerlines']),
               submitted_points=sum(len(c['points_ras_mm']) for c in obj['centerlines']),
               review_note='Unmatched output is unadjudicated, not automatically false anatomy. No precision or extent pass gate.')
    return out

def score(answer, reference):
    try:
        obj = json.loads((Path(answer)/'centerlines.json').read_text())
    except Exception as exc:
        return {'schema_version': 3, 'format_valid': False, 'geometry_pass': False,
                'labeled_pass': False, 'reward': 0, 'error': type(exc).__name__}
    return evaluate(obj, json.loads(Path(reference).read_text()))

if __name__ == '__main__':
    out = score('/app/answer', '/verifier/reference.json')
    logs = Path('/logs/verifier'); logs.mkdir(parents=True, exist_ok=True)
    (logs/'metrics.json').write_text(json.dumps(out, indent=2)+'\n')
    (logs/'reward.txt').write_text(str(out['reward'])+'\n')
