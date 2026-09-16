"""Pre-trial coordinate, topology, source digest, and visual alignment checks."""
import hashlib,json
from pathlib import Path
import numpy as np
import numcodecs,zarr
from PIL import Image,ImageDraw
from score import volumes
ROOT=Path(__file__).resolve().parents[4];B=ROOT/'runs/br034-pathological-echo'
def section(p,f,axis,value,origin,axes):
    tri=p[f];d=tri[:,:,axis]-value;keep=(d.min(1)<0)&(d.max(1)>0);tri=tri[keep];d=d[keep]
    out=np.zeros((len(tri),2,3));count=np.zeros(len(tri),int)
    for a,b in [(0,1),(1,2),(2,0)]:
        ids=np.flatnonzero((d[:,a]<0)!=(d[:,b]<0));alpha=d[ids,a]/(d[ids,a]-d[ids,b])
        out[ids,count[ids]]=tri[ids,a]+alpha[:,None]*(tri[ids,b]-tri[ids,a]);count[ids]+=1
    return (out[count==2]-origin)[:,:,axes]
def validate(base):
    prep=json.loads((base/'preparation.json').read_text());cal=json.loads((base/'input/geometry.json').read_text())
    gt=np.load(base/'reference.npz');p=gt['points'];f=gt['faces'];v=volumes(p,f)
    edges=np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]);counts=np.unique(np.sort(edges,axis=1),axis=0,return_counts=True)[1]
    assert (counts==2).all() and len(np.unique(edges,axis=0))==len(edges)
    assert np.allclose(v,prep['reference_volume_ml'],atol=1e-8)
    catalog=json.loads((B/'source/croissant.json').read_text());arrays=next(rs['data'] for rs in catalog['recordSet'] if rs['@id']=='arrays')
    row=next(x for x in arrays if x['arrays/recording_id']==prep['recording'] and x['arrays/array_path']=='data/3d_brightness_mode')
    source=B/'source'/prep['exam']/'exams'/prep['exam']/(prep['recording']+'.zarr')/'data/3d_brightness_mode'
    za=json.loads((source/'.zarray').read_text());assert za['shape']==za['chunks']
    decoded=numcodecs.get_codec(za['compressor']).decode((source/'0.0.0.0').read_bytes())
    direct=np.frombuffer(decoded,dtype=za['dtype']).reshape(za['shape'],order=za['order'])
    assert hashlib.sha256(direct.tobytes()).hexdigest()==prep['native_array_sha256']
    assert row['arrays/shape']==prep['native_shape']
    archive=json.loads((B/'source'/prep['exam']/'archive-receipt.json').read_text())
    assert archive['sha256']==prep['source_archive_sha256']==archive['source']['lfs']['oid']
    basis=np.array(prep['local_to_source_basis']);center=np.array(prep['local_to_source_center_mm']);native=np.einsum('tnj,ij->tni',p,basis)+center
    roundtrip=np.einsum('tni,ij->tnj',native-center,basis);error=float(np.max(abs(roundtrip-p)));assert error<1e-8
    # A geometric section with an independently recomputed raster intersection.
    lo=np.array(cal['origin_xyz_mm']);idx=np.rint(-lo).astype(int);planes=[(1,[0,2]),(0,[1,2]),(2,[0,1])]
    times=[0,int(v.argmin()),len(v)-1];sheet=Image.new('RGB',(960,3*340),'#101623');d=ImageDraw.Draw(sheet)
    for r,t in enumerate(times):
        for k,(axis,axes) in enumerate(planes):
            pic=Image.open(base/'input/previews'/f'plane{k+1}_{t:03d}.png').convert('RGB');draw=ImageDraw.Draw(pic)
            seg=section(p[t],f,axis,lo[axis]+idx[axis],lo,axes)
            for line in seg:draw.line(tuple(map(tuple,line)),fill='#5be6cb',width=1)
            scale=min(310/pic.width,310/pic.height);pic=pic.resize((round(pic.width*scale),round(pic.height*scale)))
            sheet.paste(pic,(k*320+(320-pic.width)//2,r*340+25));d.text((k*320+8,r*340+7),f'Reference / frame {t+1} / plane {k+1}',fill='white')
    sheet.save(base/'reference-alignment.png')
    out=dict(reference_mesh_closed_and_oriented=True,source_archive_hash_matches_publisher_lfs=True,direct_codec_decode_matches_zarr=True,
             publisher_array_digest=row['arrays/data_sha256'],decoded_c_order_digest=prep['native_array_sha256'],
             array_digest_note='Publisher data_sha256 is not reproduced by hashing raw C-order decoded bytes; its hash serialization is unspecified in inspected loader. Archive bytes match publisher LFS SHA-256; direct Blosc and Zarr decodes agree.',coordinate_roundtrip_max_mm=error,
             timestamp_max_error_s=prep['maximum_time_alignment_error_s'],reference_volume_matches_source_coordinates=True,
             source_reference_is_material_motion_truth=False,initial_mesh_only_is_public=True,
             reference_ef_pct=float(100*(1-v.min()/v.max())),reference_vertices=p.shape[1],reference_frames=len(p))
    (base/'validation.json').write_text(json.dumps(out,indent=2)+'\n');return out
if __name__=='__main__':
    print(json.dumps({'primary':validate(B),'held_out_patient':validate(B/'curation/ef48')},indent=2))
