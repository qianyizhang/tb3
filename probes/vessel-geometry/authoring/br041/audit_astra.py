"""Post-outcome trace/extent audit; never changes the frozen score or answer."""
from pathlib import Path
import json,numpy as np,nibabel as nib
from scipy.spatial import cKDTree
from scipy.ndimage import distance_transform_edt,map_coordinates
ROOT=Path(__file__).resolve().parents[4];B=ROOT/'runs/br041-image-only-centerline'
r=json.loads((B/'astra-results.json').read_text())['runs'][-1]
p=np.load(ROOT/r['answer_path']/'centerline.npy');ref=np.load(B/'tasks/named-rca/tests/reference.npy');z=np.load(ROOT/'runs/br030-vessel-geometry/geometry/reference.npz');aff=z['affine'];sp=nib.affines.voxel_sizes(aff);vox=nib.affines.apply_affine(np.linalg.inv(aff),p)
d=cKDTree(ref).query(p)[0];arc=np.r_[0,np.cumsum(np.linalg.norm(np.diff(p,axis=0),axis=1))];j=int(np.argmin(np.linalg.norm(p-ref[-1],axis=1)));trim=p[:j+1];fd=cKDTree(ref).query(trim)[0];back=cKDTree(trim).query(ref)[0];md=distance_transform_edt(~z['gt'],sampling=sp);maskdist=map_coordinates(md,vox.T,order=1);hu=map_coordinates(z['image'].astype(float),vox.T,order=1)
a={'closest_output_index_to_reference_end':j,'closest_distance_mm':float(np.linalg.norm(p[j]-ref[-1])),'additional_arc_after_reference_end_mm':float(arc[-1]-arc[j]),'full_output_outside_1mm_indices':np.flatnonzero(d>1).tolist(),'trimmed_diagnostic':{'p95_distance_mm':float(np.percentile(fd,95)),'coverage_within_1mm':float((back<=1).mean()),'length_mm':float(arc[j]),'endpoint_errors_mm':np.linalg.norm(trim[[0,-1]]-ref[[0,-1]],axis=1).tolist()},'extension':{'points':len(p)-j-1,'fraction_within_1mm_full_reference_mask':float((maskdist[j+1:]<=1).mean()),'HU_percentiles_0_25_50_75_100':np.percentile(hu[j+1:],[0,25,50,75,100]).tolist()},'note':'Post-outcome reference-assisted trimming is diagnostic only; not model success, no frozen scoring changes. Image brightness does not adjudicate vessel continuity or annotation scope.'}
session=next((ROOT/'runs/br041-named-rca-astra-xhigh-v1-20260919').glob('*/agent/sessions/**/*.jsonl'));calls=[];contexts=[]
for line in session.read_text().splitlines():
    row=json.loads(line);q=row.get('payload',{})
    if row['type']=='turn_context':contexts.append({k:q.get(k) for k in ['model','effort']})
    if q.get('type') in ['custom_tool_call','function_call']:calls.append(q.get('input',q.get('arguments','')))
a.update(context=contexts[0],session_path=str(session.relative_to(ROOT)),view_image_calls=sum('view_image' in s for s in calls),network_command_candidates=[s for s in calls if any(k in s for k in ['curl ','wget ','requests.','httpx.'])],export_native_affine_seen=any('nib.affines.apply_affine(A,p)' in s for s in calls),branch_diagnostic=json.loads((B/'astra-branch-diagnostic.json').read_text()))
(B/'astra-extent-diagnostic.json').write_text(json.dumps(a,indent=2)+'\n');(ROOT/'docs/evidence/br041-astra-audit.json').write_text(json.dumps(a,indent=2)+'\n');print(json.dumps(a,indent=2))
