"""Fixed, label-wise physical-distance scorer for BR-036."""
import json, math
from pathlib import Path

def score(answer, truth):
    expected=truth['points_ras_mm']
    try:
        assert isinstance(answer,dict) and set(answer)==set(expected)
        distances={}
        for k,gt in expected.items():
            p=answer[k]
            assert isinstance(p,list) and len(p)==3
            assert all(type(v) in (int,float) and math.isfinite(v) for v in p)
            distances[k]=math.dist(p,gt)
        return {'reward':int(max(distances.values())<=truth['tolerance_mm']), 'errors_mm':distances,
                'mean_mm':sum(distances.values())/len(distances),'max_mm':max(distances.values()),
                'within_3mm':sum(v<=3 for v in distances.values()),'within_5mm':sum(v<=5 for v in distances.values())}
    except (AssertionError,TypeError,ValueError):
        return {'reward':0,'invalid':'Expected exactly the requested named finite RAS-mm triples'}

if __name__=='__main__':
    truth=json.loads(Path('/verifier/truth.json').read_text())
    try: answer=json.loads(Path('/app/answer/landmarks.json').read_text())
    except (OSError,ValueError): answer=None
    out=score(answer,truth);p=Path('/logs/verifier');p.mkdir(parents=True,exist_ok=True)
    (p/'details.json').write_text(json.dumps(out,indent=2));(p/'reward.txt').write_text(str(out['reward']))
