import importlib.util,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).parents[1];sys.path.insert(0,str(ROOT/'authoring'))
from fixtures import cases,forward

def predict(family,p,commands):
    s=0.;out=[]
    for u in commands:
        if family=='static':s=max(abs(u)-p,0)*(1 if u>=0 else -1)
        elif family=='play':s=sorted([u-p,s,u+p])[1]
        else:s+=p*(u-s)
        out.append(s)
    return out

def main():
    spec=importlib.util.spec_from_file_location('service',ROOT/'environment/instrument/server.py');service=importlib.util.module_from_spec(spec);spec.loader.exec_module(service)
    controls={k:[] for k in ['independent_reference','service','static_fit','lag_fit','reset_each_command']}
    for c in cases():
        u=c['input']['commands'];y=c['expected']['outputs']
        candidates=dict(independent_reference=predict('play',.173,u),service=service.measure(u),static_fit=predict('static',.173,u),lag_fit=predict('lag',.827,u),reset_each_command=[forward([v])[0] for v in u])
        for name,out in candidates.items():
            if max(abs(a-b) for a,b in zip(out,y))<=1e-6:controls[name].append(c['name'])
    assert len(controls['service'])==len(controls['independent_reference'])==12
    assert all(len(v)<12 for k,v in controls.items() if k not in ['service','independent_reference'])
    # Check the predetermined identification sequence across each declared family.
    probe=[0,1,.8,.6,0,-1,-.6,-.8,0,0,0,.3,.3,.3];identifications=0
    for family,values in [('static',[.05,.12,.173,.25,.35]),('play',[.05,.12,.173,.25,.35]),('lag',[.1,.2,.5,.8,.9])]:
        for parameter in values:
            y=predict(family,parameter,probe);fits=[]
            for f,p in [('static',1-y[1]),('play',1-y[1]),('lag',y[1])]:
                if max(abs(a-b) for a,b in zip(predict(f,p,probe),y))<1e-10:fits.append((f,p))
            assert len(fits)==1 and fits[0][0]==family and abs(fits[0][1]-parameter)<1e-10
            identifications+=1
    print(json.dumps(dict(case_count=12,controls=controls,identification_checks=identifications,identifiability='At reset step [0,1], static/play expose r=1-y while lag exposes alpha=y; reversal/dwell distinguish the families throughout the declared bounds.'),indent=2))

if __name__=='__main__':main()
