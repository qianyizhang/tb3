"""Posthoc mesh-quality diagnostics; these never change the frozen rewards."""
import json
from pathlib import Path
import numpy as np
from geometry import boundary,fields
ROOT=Path(__file__).resolve().parents[4];B=ROOT/'runs/br035-segmentation-mechanics'
def quality(P,tet):
    _,_,J=fields(P[0],P,tet);w=abs(np.linalg.det(P[0][tet[:,1:]]-P[0][tet[:,:1]]))/6;face=boundary(tet);edge=np.concatenate([face[:,[0,1]],face[:,[1,2]],face[:,[2,0]]]);_,counts=np.unique(np.sort(edge,axis=1),axis=0,return_counts=True)
    low=np.average(J<.2,axis=1,weights=w)*100;high=np.average(J>2,axis=1,weights=w)*100
    return dict(boundary_faces=len(face),boundary_edges_with_incidence_not_two=int((counts!=2).sum()),boundary_edge_incidence_histogram={str(k):int((counts==k).sum()) for k in np.unique(counts)},fraction_reference_volume_J_below_point2_pct=low.tolist(),fraction_reference_volume_J_above_2_pct=high.tolist(),max_frame_low_J_volume_pct=float(low.max()),max_frame_high_J_volume_pct=float(high.max()),scope='Posthoc engineering distortion indicators, not frozen gates or clinical cutoffs. Global self-intersections and active-force balance are not exhaustively checked.')
def main():
    out={};z=dict(np.load(B/'prepared/truth.npz'));out['source']=quality(z['points'],z['tetra'])
    for c in ['masks','masks-images']:
        receipt=json.loads((B/f'{c}-sol-xhigh-receipt.json').read_text());answer=(ROOT/receipt['result_path']).parent/'artifacts/app/answer';z=dict(np.load(answer/'prediction.npz'));out[c]=quality(z['points'],z['tetra'])
    (B/'posthoc-mesh-quality.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:{n:v for n,v in x.items() if not isinstance(v,list)} for k,x in out.items()},indent=2))
if __name__=='__main__':main()
