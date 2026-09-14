import json
from pathlib import Path

SEQUENCES=[
 [0,.2,.4,.6,.8,1], [0,-.2,-.4,-.6,-.8,-1],
 [0,1,.9,.8,.7,.5,0], [0,-1,-.9,-.8,-.7,-.5,0],
 [0,.7,.7,.7,.6,.6,.6,.7], [0,1,0,-1,0,1],
 [.31,-.28,.45,-.63,.9,-.5,.1], [0,0,0,0],
 [.1,.15,-.1,-.15,.12], [.8,.5,.6,.4,.55,.3],
 [-.5,-.3,-.4,-.1,.3,.1,-.2], [1]*6+[-1]*6+[0]*6]

def forward(commands,r=.173):
    q=0.;out=[]
    for u in commands:
        if u-q>r:q=u-r
        elif q-u>r:q=u+r
        out.append(q)
    return out

def cases():return [dict(name=f'history-{i:02}',input=dict(commands=c),expected=dict(outputs=forward(c))) for i,c in enumerate(SEQUENCES)]

if __name__=='__main__':
    p=Path(__file__).parents[1]
    (p/'tests/cases.json').write_text(json.dumps(cases(),indent=2)+'\n')
    public=[0,.1,.2,.35,.55,.8,1]
    (p/'environment/examples.json').write_text(json.dumps([dict(name='historical-increasing-sweep',input=dict(commands=public),expected=dict(outputs=forward(public)))],indent=2)+'\n')
