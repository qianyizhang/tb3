"""Build a local source-linked review of frozen BR-041 model centerlines."""
from pathlib import Path
import sys,json,hashlib,shutil,shlex
import numpy as np,nibabel as nib
from scipy.spatial import cKDTree
H=Path(__file__).resolve().parent;ROOT=H.parents[4];B=ROOT/'runs/br041-image-only-centerline';OUT=B/'presentation';G=ROOT/'runs/br030-vessel-geometry/geometry'
sys.path.insert(0,str(H.parents[1]));from geometry import frames,sample,section_coordinates,cpr_coordinates
from build_viewer import simplify
import trimesh

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 OUT.mkdir(exist_ok=True);assets=OUT/'data';assets.mkdir(exist_ok=True)
 freeze=json.loads((B/'freeze.json').read_text())['tasks'][0];tp=ROOT/freeze['task_path']
 assert {str(p.relative_to(tp)):sha(p) for p in tp.rglob('*') if p.is_file()}==freeze['files']
 im=nib.load(tp/'environment/data/image.nii.gz');v=np.asarray(im.dataobj,dtype='<i2');v.tofile(assets/'image.i16')
 ref=np.load(tp/'tests/reference.npy');other=np.load(B/'private-rpla-diagnostic.npy');results=json.loads((B/'astra-results.json').read_text())['runs']
 entries=[('reference','Reference · R-PDA',ref,'#55d8b4',None),('rpla','Reference · R-PLA',other,'#a49ef9',None)]
 for key,label,col in [('terra','Terra / high','#ed9a62'),('sol','Sol / xhigh','#71b8ff'),('astra','Astra / xhigh','#ffd36e')]:
  row=next(r for r in results if r['phase'].startswith(key));src=ROOT/row['answer_path']/'centerline.npy';entries.append((key,label,np.load(src),col,row))
 mesh=trimesh.load(G/'oracle/vessels.ply',process=False);verts,faces=simplify(mesh.vertices,mesh.faces)
 # mesh is reference-assisted context only; route evidence is unchanged.
 manifest={'shape':list(v.shape),'affine':im.affine.tolist(),'inverse':np.linalg.inv(im.affine).tolist(),'spacing':nib.affines.voxel_sizes(im.affine).tolist(),'volume':'data/image.i16','routes':{},'mesh':{'vertices':verts.round(3).tolist(),'faces':faces.tolist()},'center':((verts.max(0)+verts.min(0))/2).tolist(),'referenceEnd':ref[-1].tolist()}
 receipts=[];offsets=np.linspace(-8,8,65)
 for key,label,p,col,row in entries:
  p=p.astype(float);arc=np.r_[0,np.cumsum(np.linalg.norm(np.diff(p,axis=0),axis=1))];t,n,b=frames(p);xyz=cpr_coordinates(p,n,b,np.arange(0,360,45),offsets);hu=sample(v,im.affine,xyz);sec=sample(v,im.affine,section_coordinates(p,n,b,offsets))
  folder=assets/key;folder.mkdir(exist_ok=True);np.save(folder/'centerline.npy',p) if row is None else shutil.copy2(ROOT/row['answer_path']/'centerline.npy',folder/'centerline.npy')
  np.savez_compressed(folder/'review-cpr.npz',hu=hu,source_ras_mm=xyz,arc_mm=arc,offsets_mm=offsets,angles_deg=np.arange(0,360,45))
  hu.astype('<f4').tofile(folder/'cpr.f32');sec.astype('<f4').tofile(folder/'sections.f32')
  dist,nearest=cKDTree(ref).query(p);rarc=np.r_[0,np.cumsum(np.linalg.norm(np.diff(ref,axis=0),axis=1))]
  j=int(np.argmin(np.linalg.norm(p-ref[-1],axis=1)));split=np.flatnonzero(dist>2); late=split[split>len(p)*.4];focus=int(late[0]) if len(late) else j
  if key=='terra':focus=len(p)//2
  manifest['routes'][key]={'label':label,'color':col,'path':p.tolist(),'arc':arc.tolist(),'normal':n.tolist(),'binormal':b.tolist(),'referenceIndex':nearest.tolist(),'distance':dist.tolist(),'referenceEndIndex':j,'focusIndex':focus,'metrics':row['score']['metrics'] if row else None,'cpr':f'data/{key}/cpr.f32','sections':f'data/{key}/sections.f32','lineDownload':f'data/{key}/centerline.npy','cprDownload':f'data/{key}/review-cpr.npz'}
  if row:
   method=ROOT/row['answer_path']/'method.md';shutil.copy2(method,folder/'method.md');manifest['routes'][key]['method']=f'data/{key}/method.md'
  # Independent vectorized physical sampling checks on representative CPR pixels.
  from scipy.ndimage import map_coordinates
  rng=np.random.default_rng(41);ii=rng.integers(0,8,200);jj=rng.integers(0,len(p),200);kk=rng.integers(0,65,200);pts=xyz[ii,jj,kk];vox=nib.affines.apply_affine(np.linalg.inv(im.affine),pts);expected=map_coordinates(v.astype('float32'),vox.T,order=1,mode='constant',cval=-1024,prefilter=False);error=float(np.max(np.abs(expected-hu[ii,jj,kk])))
  assert error<.01;assert np.allclose(hu[:,:,32],sample(v,im.affine,p)[None,:],atol=.01);assert np.allclose(sec[:,32,32],hu[0,:,32],atol=.01)
  receipts.append({'route':key,'points':len(p),'source_line_sha256':sha(folder/'centerline.npy'),'max_independent_HU_error':error})
 (OUT/'manifest.json').write_text(json.dumps(manifest,separators=(',',':')));shutil.copy2(H/'viewer.html',OUT/'index.html')
 shutil.copy2(tp/'environment/data/image.nii.gz',assets/'image.nii.gz')
 (OUT/'validation.json').write_text(json.dumps({'frozen_task_unchanged':True,'routes':receipts,'mesh_faces':len(faces),'scope':'Author-generated review CPR from unchanged submitted paths; reference mesh is evaluator context.'},indent=2)+'\n')
 launcher=OUT/'Open review.command';launcher.write_text('#!/bin/zsh\ncd '+shlex.quote(str(ROOT))+'\nexec .venv-br030/bin/python probes/vessel-geometry/authoring/br041/presentation/launch.py\n');launcher.chmod(0o755)
 print(json.dumps({'viewer':str(OUT/'index.html'),'mesh_faces':len(faces),'routes':len(entries)}))
if __name__=='__main__':main()
