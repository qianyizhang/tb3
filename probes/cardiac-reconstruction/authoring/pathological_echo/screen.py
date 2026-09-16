"""Compute pre-trial reference-function screen; do not expose it to the solver."""
import json,hashlib
from pathlib import Path
import numpy as np
import zarr
ROOT=Path(__file__).resolve().parents[4];B=ROOT/'runs/br034-pathological-echo/source'
def arr(p):return np.asarray(zarr.open_array(str(p),mode='r')[:])
def mesh(p):
    pts=arr(p/'point_values').astype(float)*1000;f=arr(p/'face_values');po=arr(p/'point_frame_offsets');fo=arr(p/'face_frame_offsets')
    ps=[pts[po[i]:po[i+1]] for i in range(len(po)-1)];fs=[f[fo[i]:fo[i+1]] for i in range(len(fo)-1)]
    return np.stack(ps),fs
def volume(p,f):
    t=p[f];return float(abs(np.einsum('ij,ij->i',t[:,0],np.cross(t[:,1],t[:,2])).sum()/6000))
def main():
    rows=[]
    for p in sorted(B.glob('exam_*/exams/*/*.zarr/data/3d_left_ventricle_mesh')):
        try:
            ps,fs=mesh(p);v=np.array([volume(pp,ff) for pp,ff in zip(ps,fs)]);assert min(v)>0
            attrs=json.loads((p.parent.parent/'.zattrs').read_text());man=attrs['recording_manifest']
            row=dict(exam=p.parts[-4],recording=p.parts[-3],frames=len(ps),vertices=ps.shape[1],reference_volume_ml=v.tolist(),reference_ef_pct=float(100*(1-min(v)/max(v))),
                     source_frames=attrs['frame_counts_by_content_type'],has_images=(p.parent/'3d_brightness_mode/.zarray').exists(),
                     points_sha256=hashlib.sha256(arr(p/'point_values').tobytes()).hexdigest(),same_faces=all(np.array_equal(fs[0],ff) for ff in fs))
            rows.append(row)
        except (FileNotFoundError,ValueError,KeyError) as e:print(type(e).__name__,p)
    (B/'function-screen.json').write_text(json.dumps(rows,indent=2)+'\n')
    print(json.dumps([{k:v for k,v in r.items() if k not in ['reference_volume_ml','points_sha256']} for r in rows],indent=2))
if __name__=='__main__':main()
