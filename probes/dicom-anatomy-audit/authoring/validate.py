"""Validate source-to-SEG geometry, exact finding semantics and incorrect controls."""
import argparse,copy,importlib.util,json,sys
from pathlib import Path
import numpy as np

PROBE=Path(__file__).resolve().parents[1]

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def main():
    p=argparse.ArgumentParser();p.add_argument('--scratch',type=Path,required=True);a=p.parse_args()
    scoring=module('scoring',PROBE/'tests/scoring.py')
    reader=module('reader',PROBE/'environment/read_case.py')
    truth=json.loads((PROBE/'tests/expected.json').read_text())
    correct=json.loads((PROBE/'solution/findings.json').read_text())
    regions=np.load(PROBE/'tests/regions.npz',allow_pickle=False)
    good=scoring.score(correct,truth,regions);assert good['passed']
    wanted={c['case_id']:c for c in truth['cases']}
    def rejected(value):
        try:return not scoring.score(value,truth,regions)['passed']
        except (ValueError,TypeError,KeyError):return True
    controls={}
    no_findings=copy.deepcopy(correct)
    for row in no_findings['cases']:row['findings']=[]
    controls['no_findings']=scoring.score(no_findings,truth,regions)
    assert not controls['no_findings']['passed']
    all_labels={'cases':[{'case_id':c['case_id'],'findings':[{'label':label,'point_lps_mm':[0,0,0]} for label in c['focus_labels']]} for c in truth['cases']]}
    controls['flag_every_focus_label']=scoring.score(all_labels,truth,regions)
    assert not controls['flag_every_focus_label']['passed']
    bad_point=copy.deepcopy(correct)
    for row in bad_point['cases']:
        for f in row['findings']:f['point_lps_mm']=[99999,99999,99999]
    controls['correct_labels_wrong_points']=scoring.score(bad_point,truth,regions)
    assert not controls['correct_labels_wrong_points']['passed']
    cases=[c for c in correct['cases'] if c['findings']]
    for c in cases:
        for f in c['findings']:
            changed=copy.deepcopy(correct)
            target=next(x for x in changed['cases'] if x['case_id']==c['case_id'])
            target['findings']=[x for x in target['findings'] if x['label']!=f['label']]
            assert rejected(changed)
    duplicate=copy.deepcopy(correct);duplicate['cases'].append(copy.deepcopy(duplicate['cases'][0]));assert rejected(duplicate)
    nan=copy.deepcopy(correct)
    next(c for c in nan['cases'] if c['findings'])['findings'][0]['point_lps_mm']=[float('nan'),0,0]
    assert rejected(nan)
    coords=np.array([[0.,0.,0.]])
    assert scoring.near_region([3,0,0],coords)
    assert not scoring.near_region([3.001,0,0],coords)
    geometry=[];discrepancy=[]
    taxonomy=json.loads((a.scratch/'data/label-list.json').read_text());names={v:int(k) for k,v in taxonomy.items()}
    for c in truth['cases']:
        case_id=c['case_id'];raw=np.load(a.scratch/(case_id+'-private.npz'),allow_pickle=False)
        loaded=reader.load_case(a.scratch/'data'/case_id)
        assert np.array_equal(loaded['ct_hu'],raw['ct'].transpose(2,1,0)),case_id
        # Decode local IDs to the source vocabulary independently of sequence order.
        mapped=np.zeros_like(loaded['labels'],dtype=np.uint8)
        for local,label in loaded['label_names'].items():mapped[loaded['labels']==local]=names[label]
        assert np.array_equal(mapped,raw['submitted'].transpose(2,1,0)),case_id
        assert np.allclose(loaded['affine_lps'],raw['affine'],rtol=0,atol=1e-8),case_id
        geometry.append({'case_id':case_id,'ct_exact':True,'all_label_voxels_exact':True,'affine_exact':True})
        positive={f['label']:f for f in c['findings']}
        for label in c['focus_labels']:
            diff=(raw['original']==names[label])^(raw['submitted']==names[label])
            if label not in positive:
                assert not diff.any(),(case_id,label)
                continue
            # Separate scalar affine formulation of every private evidence point.
            rows=np.argwhere(diff)
            affine=raw['affine']
            pts=np.column_stack([affine[i,0]*rows[:,0]+affine[i,1]*rows[:,1]+affine[i,2]*rows[:,2]+affine[i,3] for i in range(3)])
            assert np.allclose(pts,regions[positive[label]['region_key']],rtol=0,atol=1e-4)
            discrepancy.append({'case_id':case_id,'label':label,'voxels':int(diff.sum()),'evidence_coordinates_match_source_difference':True})
    result={'round':'BR-004','task':'dicom-anatomy-audit','evidence_class':'author_controls','model_trials':0,'oracle':good,'incorrect_controls':controls,'geometry':geometry,'discrepancy_truth':discrepancy,'additional_checks':['each finding individually necessary','duplicate case rejected','nonfinite point rejected','3 mm inclusive spatial boundary'],'limits':'Reference report comes from reviewed source masks and authored edits. Oracle control checks solvability of the output/grader interface, not an independent general anatomical detector or expert clinical certification.'}
    (a.scratch/'author-controls.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'oracle_passed':good['passed'],'positive_labels':good['expected_positive_labels'],'cases':len(geometry),'controls':{k:v['passed'] for k,v in controls.items()}},indent=2))

if __name__=='__main__':main()
