"""Decode the public source's documented Philips private volume format.

Written from the authors' inspected utils_3d.py. Only image arrays and geometric
metadata are exported; the raw DICOM remains author-side.
"""
import json, struct, zlib
from pathlib import Path
import numpy as np
import pydicom

ROOT=Path(__file__).resolve().parents[4];B=ROOT/'runs/br032-real-echo'

def main():
    d=pydicom.dcmread(B/'source/selected.dcm')
    arr15=np.asarray(d[0x200d,0x3315].value,dtype=int)
    arr16=np.asarray(d[0x200d,0x3316].value,dtype=int)
    shape=tuple((arr15^arr15[-1])[2::-1]);stride=tuple((arr16^arr16[-1])[2::-1])
    f=d[0x200d,0x3cf5][1][0x200d,0x3cf1][0]
    assert f[0x200d,0x3cfa].value=='ZLib'
    raw=f[0x200d,0x3cf3].value;checks=f[0x200d,0x3cfb].value
    data_size,nframes=struct.unpack('<II',raw[:8]);starts=struct.unpack('<'+'I'*nframes,raw[8:8+4*nframes])
    frames=[]
    for i,s in enumerate(starts):
        assert checks[i*32:(i+1)*32]==raw[s:s+32]
        decoded=zlib.decompress(raw[s+32:])
        a=np.frombuffer(decoded,dtype=np.uint8)[:np.prod(stride)].reshape(stride)
        frames.append(a[:shape[0],:shape[1],:shape[2]].transpose(2,1,0).copy())
    frames=np.stack(frames)
    bounds=np.array([float(d[0x200d,k].value) for k in [0x3102,0x3103,0x3104,0x3105,0x3203,0x3204]]).reshape(3,2)
    timing={k:str(getattr(d,k,'')) for k in ['FrameTime','FrameTimeVector','CineRate','RecommendedDisplayFrameRate','NumberOfFrames']}
    np.savez_compressed(B/'native.npz',images=frames,bounds=bounds)
    info=dict(shape_T_rho_phi_theta=list(frames.shape),bounds_rho_mm_phi_rad_theta_rad=bounds.tolist(),
              decoded_dtype=str(frames.dtype),range=[int(frames.min()),int(frames.max())],
              stride_theta_phi_rho=list(map(int,stride)),tag_timing=timing,
              coordinate_definition='x=rho*cos(phi)*cos(theta), y=rho*sin(theta), z=rho*sin(phi)*cos(theta)',
              spatial_units='mm, following the inspected official view extractor',
              fragment_headers_match=True,zlib_decoding=True,dicom_identifiers_exported=False)
    (B/'decode.json').write_text(json.dumps(info,indent=2)+'\n');print(json.dumps(info,indent=2))

if __name__=='__main__':main()
