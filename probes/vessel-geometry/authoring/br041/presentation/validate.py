"""Validate viewer data integrity and its JS native-volume sampling kernel."""
from pathlib import Path
import json,re,subprocess,tempfile,hashlib
import numpy as np
from scipy.ndimage import map_coordinates
ROOT=Path(__file__).resolve().parents[5];B=ROOT/'runs/br041-image-only-centerline';P=B/'presentation';m=json.loads((P/'manifest.json').read_text());v=np.fromfile(P/m['volume'],dtype='<i2').reshape(m['shape']);rng=np.random.default_rng(4141)
pts=rng.random((300,3))*(np.array(v.shape)-1);pts=np.r_[pts,[[0,0,0],np.array(v.shape)-1,[-.1,0,0],[999,0,0]]];expected=map_coordinates(v.astype(float),pts.T,order=1,mode='constant',cval=-1024,prefilter=False)
html=(P/'index.html').read_text();kernel=html.split('function sample(p){',1)[1].split('\nasync function getRoute',1)[0];kernel='function sample(p){'+kernel
script="const fs=require('fs');const D="+json.dumps({'shape':m['shape']})+";const b=fs.readFileSync("+json.dumps(str(P/m['volume']))+");const V=new Int16Array(b.buffer,b.byteOffset,b.byteLength/2);"+kernel+"\nconsole.log(JSON.stringify("+json.dumps(pts.tolist())+".map(sample)));"
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'kernel.cjs';p.write_text(script);actual=np.array(json.loads(subprocess.check_output(['node',str(p)],text=True)))
error=float(np.max(np.abs(actual-expected)));assert error<1e-8,error
runs=json.loads((B/'astra-results.json').read_text())['runs'];digests={}
for k in ['terra','sol','astra']:
 row=next(r for r in runs if r['phase'].startswith(k));source=ROOT/row['answer_path']/'centerline.npy';copy=P/m['routes'][k]['lineDownload'];assert source.read_bytes()==copy.read_bytes();digests[k]=hashlib.sha256(copy.read_bytes()).hexdigest()
for k,r in m['routes'].items():
 n=len(r['path']);assert (P/r['cpr']).stat().st_size==8*n*65*4;assert (P/r['sections']).stat().st_size==n*65*65*4;assert np.allclose(r['arc'],np.r_[0,np.cumsum(np.linalg.norm(np.diff(r['path'],axis=0),axis=1))]);z=np.load(P/r['cprDownload']);assert np.allclose(z['source_ras_mm'][:,:,32],np.array(r['path'])[None,:,:])
receipt={'native_JS_sampler_points':len(pts),'native_JS_max_HU_error':error,'model_bytes_unchanged_sha256':digests,'all_five_route_binary_shapes_and_arc_axes':True,'CPR_center_source_mapping':True};(P/'numeric-validation.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
