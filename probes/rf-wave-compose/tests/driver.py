import json,sys
import numpy as np
from pathlib import Path
if (Path(__file__).parent/'answer').is_dir():sys.path.insert(0,str(Path(__file__).parent/'answer'))
from solution import compose


def decode(x):
    return dict(frequency_hz=np.asarray(x['frequency_hz'],float),
                s=np.asarray(x['s_real'])+1j*np.asarray(x['s_imag']),
                z0=np.asarray(x['z0_real'])+1j*np.asarray(x['z0_imag']),
                wave_definition=x['wave_definition'])


def run(inputs):
    results=[]
    for c in inputs:
        try:
            s=np.asarray(compose(decode(c['left']),decode(c['right'])),complex)
            results.append(dict(s_real=s.real.tolist(),s_imag=s.imag.tolist()))
        except Exception as e:results.append(dict(error=f'{type(e).__name__}: {e}'))
    return results


if __name__=='__main__':print(json.dumps(run(json.load(sys.stdin)),allow_nan=False))
