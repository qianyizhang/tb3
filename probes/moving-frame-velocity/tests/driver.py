import sys,json
from pathlib import Path
import numpy as np
if (Path(__file__).parent/'answer').is_dir():sys.path.insert(0,str(Path(__file__).parent/'answer'))
from solution import convert_track
from frame import Frame

def run(inputs):
    out=[]
    for c in inputs:
        try:
            t={k:np.asarray(v,float) for k,v in c['track'].items()}
            p,v=convert_track(t,Frame(c['frame']))
            out.append(dict(position=np.asarray(p).tolist(),velocity=np.asarray(v).tolist()))
        except Exception as e:out.append(dict(error=f'{type(e).__name__}: {e}'))
    return out

if __name__=='__main__':print(json.dumps(run(json.load(sys.stdin)),allow_nan=False))
