import importlib.util,json,sys
from pathlib import Path
import numpy as np
import skrf as rf
sys.dont_write_bytecode=True
ROOT=Path(__file__).parents[1]
sys.path.insert(0,str(ROOT/'authoring'))
from fixtures import cases,physical_z,branches,encode


def load(path,name):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m


def decode(x):
    return dict(frequency_hz=np.array(x['frequency_hz']),s=np.array(x['s_real'])+1j*np.array(x['s_imag']),z0=np.array(x['z0_real'])+1j*np.array(x['z0_imag']),wave_definition=x['wave_definition'])


def main():
    baseline=load(ROOT/'solution/reference.py','baseline')
    controls={k:[] for k in ['library_baseline','ignore_all_metadata','ignore_wave_tag','metadata_relabel']}
    maxerr=0.;encode_error=0.;maxcond=0.
    for c in cases():
        a,b=[decode(c['input'][k]) for k in ['left','right']]
        expected=np.array(c['expected']['s_real'])+1j*np.array(c['expected']['s_imag'])
        got=baseline.compose(a,b);maxerr=max(maxerr,float(np.max(abs(got-expected))))
        for tag in controls:
            aa={**a};bb={**b}
            if tag in ['ignore_all_metadata','metadata_relabel']: aa.update(z0=50,wave_definition='power');bb.update(z0=50,wave_definition='power')
            if tag=='ignore_wave_tag':aa['wave_definition']=bb['wave_definition']='power'
            x=baseline.compose(aa,bb)
            if max(np.max(abs((x-expected).real)),np.max(abs((x-expected).imag)))<=1e-8:controls[tag].append(c['name'])
        for d in [a,b]:
            z=rf.network.s2z(d['s'],d['z0'],s_def=d['wave_definition'])
            for j in range(len(z)):
                encode_error=max(encode_error,float(np.max(abs(encode(z[j],d['z0'][j],d['wave_definition'])-d['s'][j]))))
                maxcond=max(maxcond,float(np.linalg.cond(z[j]+np.diag(d['z0'][j]))))
    assert len(controls['library_baseline'])==32 and maxerr<1e-10 and encode_error<1e-10
    assert all(len(v)<32 for k,v in controls.items() if k!='library_baseline')
    print(json.dumps(dict(case_count=32,physical_pair_count=8,frequency_count=16,max_library_vs_nodal_error=maxerr,max_encoding_residual=encode_error,max_encoding_condition=maxcond,controls=controls,versions=dict(numpy=np.__version__,scikit_rf=rf.__version__)),indent=2))


if __name__=='__main__':main()
