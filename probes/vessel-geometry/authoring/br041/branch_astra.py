"""Post-outcome branch diagnosis; does not change the frozen task score."""
from pathlib import Path
import json,sys,numpy as np
from scipy.spatial import cKDTree
H=Path(__file__).resolve().parent;ROOT=H.parents[3];B=ROOT/'runs/br041-image-only-centerline'
sys.path.insert(0,str(H.parent));from geometry import read_centerline,named_route,resample_path
r=json.loads((B/'astra-results.json').read_text())['runs'][-1];p=np.load(ROOT/r['answer_path']/'centerline.npy')
x,f,ls=read_centerline(ROOT/'runs/br030-vessel-geometry/sources/coronary/ImageCAS-X_dataset/centerlines/1.coronary_right_centerline.vtk');out={}
for label,name in [(10,'R-PDA'),(11,'R-PLA')]:
    q,_=resample_path(named_route(x,f,ls,label)[0]);d=cKDTree(q).query(p)[0];b=cKDTree(p).query(q)[0]
    out[name]={'p95_distance_mm':float(np.percentile(d,95)),'coverage_within_1mm':float((b<=1).mean()),'output_fraction_within_1mm':float((d<=1).mean()),'endpoint_errors_mm':np.linalg.norm(p[[0,-1]]-q[[0,-1]],axis=1).tolist()}
    if label==11:np.save(B/'private-rpla-diagnostic.npy',q)
(B/'astra-branch-diagnostic.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
