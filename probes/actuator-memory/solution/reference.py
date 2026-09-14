import json
from pathlib import Path

def predict(commands):
    p=json.loads((Path(__file__).parent/'calibration.json').read_text())
    family=p['family'];parameter=p['parameter'];state=0.;output=[]
    for u in commands:
        if family=='static':state=max(u-parameter,0) if u>=0 else min(u+parameter,0)
        elif family=='play':state=sorted([u-parameter,state,u+parameter])[1]
        else:state=(1-parameter)*state+parameter*u
        output.append(state)
    return output
