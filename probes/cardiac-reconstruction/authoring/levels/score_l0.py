"""Source-array checks plus fresh rigid/affine execution in the verifier container."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import numpy as np
from kinematics import from_input, analytic_inputs


def compare(path, expected):
    try:
        with np.load(path, allow_pickle=False) as z:
            errors = {}
            if not np.array_equal(z['valid'], expected['valid']):
                return dict(pass_=False, reason='incorrect directional-support mask')
            for key in ['F','E','J','engineering']:
                a, b = z[key], expected[key]
                if a.shape != b.shape or not np.array_equal(np.isnan(a), np.isnan(b)):
                    return dict(pass_=False, reason=f'{key}: shape or missingness')
                finite = np.isfinite(b)
                if not np.isfinite(a[finite]).all():
                    return dict(pass_=False, reason=f'{key}: nonfinite values')
                errors[key] = float(np.max(abs(a[finite]-b[finite])))
            return dict(pass_=max(errors.values()) <= 1e-5, max_absolute_errors=errors)
    except Exception as e:
        return dict(pass_=False, reason=type(e).__name__+': '+str(e)[:200])


def score(answer, source):
    result = dict(source=compare(answer/'fields.npz', from_input(dict(np.load(source)))))
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        sample = analytic_inputs()
        np.savez_compressed(tmp/'input.npz', **sample)
        try:
            p = subprocess.run([sys.executable, str(answer/'solve.py'), '--input', str(tmp/'input.npz'),
                                '--output', str(tmp/'fields.npz')], cwd=answer,
                               capture_output=True, timeout=120)
            result['analytic'] = compare(tmp/'fields.npz', from_input(sample))
            result['analytic']['exit_code'] = p.returncode
            if p.returncode:
                result['analytic']['pass_'] = False
        except Exception as e:
            result['analytic'] = dict(pass_=False, reason=type(e).__name__)
    result['reward'] = int(all(result[k]['pass_'] for k in ['source','analytic']))
    return result


if __name__ == '__main__':
    r=score(Path('/app/answer'), Path('/verifier/source.npz'))
    p=Path('/logs/verifier'); p.mkdir(parents=True,exist_ok=True)
    (p/'metrics.json').write_text(json.dumps(r,indent=2)+'\n')
    (p/'reward.txt').write_text(str(r['reward'])+'\n')
    print(json.dumps(r))
