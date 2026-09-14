"""Author controls for five inspected, deliberately perturbed review packets."""
import argparse
import importlib.util
import json
from pathlib import Path
import tempfile
import time

ROOT=Path(__file__).resolve().parents[1]
def load(path):
    spec=importlib.util.spec_from_file_location('audit_control',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--scratch',type=Path,required=True);a=ap.parse_args()
    data=a.scratch/'audit-data';packets=json.loads((data/'packets.json').read_text())
    expected={p['id']:p['findings'] for p in json.loads((a.scratch/'audit-truth.json').read_text())['packets']}
    def pairs(rows):return sorted((r['label'],r['issue']) for r in rows)
    def evaluate(module):
        failed=[]
        for p in packets:
            result=module.audit(data/p['ct_dir'],data/p['segmentation'],p['focus_labels'])
            if pairs(result)!=pairs(expected[p['id']]):failed.append(p['id'])
        return failed
    started=time.monotonic();assert not evaluate(load(ROOT/'solution/auditor.py'))
    source=(ROOT/'solution/auditor.py').read_text()
    controls={'no_findings':evaluate(load(ROOT/'environment/auditor.py'))}
    mutations={
        'sequence_position_is_segment_number':(
            "names={int(s.SegmentNumber):str(s.SegmentLabel) for s in seg.SegmentSequence}",
            "names={i+1:str(s.SegmentLabel) for i,s in enumerate(seg.SegmentSequence)}"),
        'treat_patient_coordinates_as_RAS':(
            "accum[name][0]+=count;accum[name][1]+=total",
            "accum[name][0]+=count;accum[name][1]+=total*np.array([-1,-1,1])"),
        'require_heart_in_every_scan':(
            "if name=='heart' and all(data[n]['count']>100 for n in",
            "if name=='heart' or all(data[n]['count']>100 for n in"),
    }
    with tempfile.TemporaryDirectory() as tmp:
        for name,(old,new) in mutations.items():
            assert old in source;variant=source.replace(old,new);compile(variant,name,'exec')
            p=Path(tmp)/'auditor.py';p.write_text(variant);controls[name]=evaluate(load(p))
            assert controls[name],name
    print(json.dumps({'oracle_cases':5,'oracle_passed':5,'incorrect_controls':controls,
        'seconds':time.monotonic()-started,'model_trials':0,
        'scope':'one inspected source case, four focus labels, five correlated packets; not clinical validation'},indent=2))
if __name__=='__main__':main()
