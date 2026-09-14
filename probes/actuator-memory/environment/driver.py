import sys,json
from pathlib import Path
if (Path(__file__).parent/'answer').is_dir():sys.path.insert(0,str(Path(__file__).parent/'answer'))
from solution import predict

def run(inputs):
    out=[]
    for c in inputs:
        try:out.append(dict(outputs=list(predict(c['commands']))))
        except Exception as e:out.append(dict(error=f'{type(e).__name__}: {e}'))
    return out

if __name__=='__main__':print(json.dumps(run(json.load(sys.stdin)),allow_nan=False))
