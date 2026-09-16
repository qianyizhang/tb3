"""Geometry-only verifier; does not execute submitted code or render CT."""
import json
from pathlib import Path
import numpy as np


def score(answer, truth):
    try:
        t = np.asarray(answer['slice_to_lps'], dtype=float)
        assert t.shape == (4, 4) and np.isfinite(t).all(), 'finite 4x4 required'
        assert np.allclose(t[3], [0, 0, 0, 1], atol=1e-6, rtol=0), 'homogeneous row'
        r = t[:3, :3]
        assert np.allclose(r.T @ r, np.eye(3), atol=1e-3, rtol=0), 'rigid axes'
        assert abs(np.linalg.det(r) - 1) <= 1e-3, 'right handed frame'
        gt = np.asarray(truth['slice_to_lps'])
        h, w = truth['shape']
        sx, sy = truth['spacing_xy_mm']
        # Independent scalar construction, including all four observed corners.
        errors = []
        for v in np.linspace(0, h-1, 7):
            for u in np.linspace(0, w-1, 7):
                actual = t[:3, 3] + u*sx*t[:3, 0] + v*sy*t[:3, 1]
                expected = gt[:3, 3] + u*sx*gt[:3, 0] + v*sy*gt[:3, 1]
                errors.append(float(np.linalg.norm(actual-expected)))
        centre = np.array([(w-1)*sx/2, (h-1)*sy/2, 0, 1])
        rms = float(np.sqrt(np.mean(np.square(errors))))
        maximum = max(errors)
        return dict(reward=int(rms <= 3.0 and maximum <= 5.0), rms_mm=rms,
                    max_mm=maximum, centre_mm=float(np.linalg.norm((t@centre-gt@centre)[:3])),
                    normal_deg=float(np.degrees(np.arccos(np.clip(np.dot(t[:3, 2], gt[:3, 2]), -1, 1)))))
    except (KeyError, TypeError, ValueError, AssertionError) as exc:
        return dict(reward=0, reason=str(exc))


if __name__ == '__main__':
    truth = json.loads(Path('/verifier/truth.json').read_text())
    try:
        answer = json.loads(Path('/app/answer/pose.json').read_text())
    except (OSError, ValueError):
        answer = {}
    result = score(answer, truth)
    dest = Path('/logs/verifier'); dest.mkdir(parents=True, exist_ok=True)
    (dest/'metrics.json').write_text(json.dumps(result, indent=2)+'\n')
    (dest/'reward.txt').write_text(str(result['reward'])+'\n')
    print(json.dumps(result))
