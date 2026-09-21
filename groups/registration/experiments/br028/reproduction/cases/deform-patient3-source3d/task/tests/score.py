"""Independent geometry-only sparse correspondence grader."""
import json
import math
from pathlib import Path


def score(answer,truth):
    try:
        assert answer['query_ids']==truth['query_ids'],'query_ids must match the specified order'
        pts=answer['points_world_mm'];ref=truth['points_world_mm']
        assert isinstance(pts,list) and len(pts)==len(ref),'one position per query required'
        distances=[]
        for point,expected in zip(pts,ref):
            assert isinstance(point,list) and len(point)==3,'each position must have three coordinates'
            assert all(isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v) for v in point),'finite numeric coordinates required'
            distances.append(math.sqrt(sum((x-y)**2 for x,y in zip(point,expected))))
        rms=math.sqrt(sum(x*x for x in distances)/len(distances));maximum=max(distances)
        return {'reward':int(rms<=truth['rms_tolerance_mm'] and maximum<=truth['max_tolerance_mm']),
                'rms_mm':rms,'max_mm':maximum,'per_point_mm':distances}
    except (KeyError,TypeError,ValueError,AssertionError,OverflowError) as exc:
        return {'reward':0,'reason':str(exc)}


if __name__=='__main__':
    truth=json.loads(Path('/verifier/truth.json').read_text())
    try:answer=json.loads(Path('/app/answer/points.json').read_text())
    except (OSError,ValueError):answer={}
    result=score(answer,truth);dest=Path('/logs/verifier');dest.mkdir(parents=True,exist_ok=True)
    (dest/'metrics.json').write_text(json.dumps(result,indent=2)+'\n')
    (dest/'reward.txt').write_text(str(result['reward'])+'\n');print(json.dumps(result))
