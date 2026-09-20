"""Private post-hoc source/geometry audit. Never modifies trial inputs or scores."""
from pathlib import Path
import json,sys,hashlib
import numpy as np
import nibabel as nib
from scipy.ndimage import map_coordinates,distance_transform_edt
from scipy.spatial import cKDTree
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[4]; H=Path(__file__).resolve().parent
sys.path.insert(0,str(H.parent));from geometry import read_centerline,transform
sys.path.insert(0,str(H));from score import samples,nearest
B=ROOT/'runs/br042-all-vessels-v3';O=B/'review/branches';O.mkdir(exist_ok=True)
S=ROOT/'runs/br030-vessel-geometry/sources/coronary/ImageCAS-X_dataset'
im=nib.load(B/'tasks/all-vessels/environment/data/image.nii.gz');vol=im.get_fdata(dtype=np.float32);inv=np.linalg.inv(im.affine)
mask=nib.load(S/'segmentations/1.coronary.nii.gz').get_fdata(dtype=np.float32)
spacing=nib.affines.voxel_sizes(im.affine);edt=distance_transform_edt(mask>0,sampling=spacing).astype(np.float32)
trees={side:read_centerline(S/f'centerlines/1.coronary_{side}_centerline.vtk') for side in ['left','right']}
ref=json.loads((B/'tasks/all-vessels/tests/reference.json').read_text());rp,rl,rw,ro=samples(ref)
models={}
for row in json.loads((B/'results.json').read_text())['runs']:
 if row['phase'] in ['oracle','nop'] or not row.get('replay',{}).get('format_valid'):continue
 obj=json.loads((ROOT/row['answer_path']/'centerlines.json').read_text());p,l,w,owners=samples(obj,True)
 models[row['phase']]={'obj':obj,'p':p,'l':l,'owners':owners,'tree':cKDTree(p)}
print('models',list(models))
medium=next(v for k,v in models.items() if 'medium' in k)
names={1:'LM',2:'LAD',3:'LCx',4:'D1',5:'D2',6:'OM1',7:'OM2',9:'RCA',10:'R-PDA',11:'R-PLA',14:'Other'}
cases=[('D2','left',6,5),('OM1','left',10,6),('OM2','left',0,7),('R-PDA_A','right',2,10),('R-PDA_B','right',3,10)]
def sample(a,world,order=1):
 return map_coordinates(a,transform(np.asarray(world).reshape(-1,3),inv).T,order=order,mode='nearest').reshape(np.asarray(world).shape[:-1])
def path_resample(p):
 s=np.r_[0,np.cumsum(np.linalg.norm(np.diff(p,axis=0),axis=1))];s2=np.linspace(0,s[-1],int(s[-1]/.15)+1)
 return s2,np.stack([np.interp(s2,s,p[:,i]) for i in range(3)],axis=1)
stats=[]
for title,side,lineidx,label in cases:
 p,f,lines=trees[side];ids=lines[lineidx];q=p[ids].copy();labs=f['segment_label'][ids]
 # Orient away from parent, which carries the other label at one endpoint.
 if labs[-1]!=label:q=q[::-1];labs=labs[::-1]
 s,c=path_resample(q);t=np.gradient(c,axis=0);t/=np.linalg.norm(t,axis=1)[:,None]
 u=np.cross(t,np.tile([0,0,1.],(len(t),1)));u/=np.linalg.norm(u,axis=1)[:,None];v=np.cross(t,u)
 offsets=np.linspace(-4,4,161)
 grids=[c[:,None,:]+offsets[None,:,None]*axis[:,None,:] for axis in [u,v]]
 imgs=[sample(vol,g).T for g in grids];masks=[sample(mask,g,0).T for g in grids]
 ijk=transform(c,inv);d,ix=medium['tree'].query(c);owner=medium['owners'][ix];ml=medium['l'][ix]
 row={'branch':title,'source_line':f'{side}-{lineidx}','reference_label':label,'length_including_junction_mm':float(s[-1]),'origin_voxel_xyz':ijk[0].tolist(),'end_voxel_xyz':ijk[-1].tolist(),'center_HU_percentiles':np.percentile(sample(vol,c),[10,50,90]).tolist(),'mask_diameter_proxy_mm_percentiles':np.percentile(2*sample(edt,c),[10,50,90]).tolist(),'source_centerline_in_any_mask_fraction':float(np.mean(sample(mask,c,0)>0)),'source_centerline_in_same_label_mask_fraction':float(np.mean(sample(mask,c,0)==label))}
 stats.append(row)
 for overlay in [False,True]:
  fig=plt.figure(figsize=(15,10),facecolor='#101724');gs=fig.add_gridspec(3,4,height_ratios=[1.3,1,1],hspace=.47,wspace=.35)
  fig.suptitle(f'{title.replace("_"," ")} | source CTA + original reference | post-hoc localization',color='white',fontsize=18,y=.98)
  ax=fig.add_subplot(gs[0,:2]);ax.set_facecolor('#101724')
  # RAS x/y projection: topology context only, not a CT slice.
  for ln in lines:
   z=p[ln];k=int(np.bincount(f['segment_label'][ln].astype(int)).argmax());ax.plot(z[:,0],z[:,1],c='#778394',lw=1)
   if k in [2,3,4,5,6,7,9,10,11,14]:ax.text(*z[len(z)//2,:2],names[k],fontsize=8,color='#a8b3c5')
  ax.plot(c[:,0],c[:,1],c='#00e0d0',lw=3);ax.scatter(*c[0,:2],c='#fff066',s=35,zorder=5)
  for line in medium['obj']['centerlines']:
   z=np.array(line['points_ras_mm']);dist=cKDTree(c).query(z)[0]
   z=z[dist<4]
   if len(z)>1:ax.plot(z[:,0],z[:,1],c='#ff8c49',lw=1,alpha=.9)
  ax.set_aspect('equal');ax.set_title('Topology projection (not CTA): cyan reference, orange medium',color='white',fontsize=10);ax.set_xlabel('L ← RAS x (mm) → R',color='white');ax.set_ylabel('P ← RAS y (mm) → A',color='white')
  ax=fig.add_subplot(gs[0,2:]);ax.set_facecolor('#101724');ax.plot(s,d,c='#ff8c49');ax.axhline(1,c='#ffeb75',ls='--');ax.set_ylim(0,min(12,max(2,d.max()+.5)));ax.set_title('Distance to nearest Astra-medium submitted course',color='white',fontsize=10);ax.set_xlabel('Distance along reference from junction (mm)',color='white');ax.set_ylabel('Distance (mm)',color='white')
  for a in range(2):
   ax=fig.add_subplot(gs[1,a*2:a*2+2]);ax.imshow(imgs[a],cmap='gray',vmin=0,vmax=600,extent=[0,s[-1],4,-4],aspect='auto')
   if overlay:
    ax.axhline(0,c='#00e0d0',lw=.7)
    ax.contour(np.linspace(0,s[-1],len(s)),offsets,(masks[a]>0).astype(float),levels=[.5],colors=['#fff066'],linewidths=.6)
   ax.set_title(f'Curved plane {a+1}: consecutive cross-sections along GT',color='white',fontsize=10);ax.set_xlabel('Arc length (mm)',color='white');ax.set_ylabel('Offset (mm)',color='white')
  for a,fraction in enumerate([.15,.4,.65,.9]):
   i=int((len(c)-1)*fraction);grid=c[i]+offsets[:,None,None]*u[i]+offsets[None,:,None]*v[i];img=sample(vol,grid);seg=sample(mask,grid,0)
   ax=fig.add_subplot(gs[2,a]);ax.imshow(img,cmap='gray',vmin=0,vmax=600,extent=[-4,4,4,-4]);
   if overlay:
    ax.contour(offsets,offsets,(seg>0).astype(float),levels=[.5],colors=['#fff066'],linewidths=.7);ax.plot(0,0,'+',c='#00e0d0',ms=9)
   ax.set_title(f'{fraction*100:.0f}% | voxel {",".join(str(int(round(x))) for x in ijk[i])}',color='white',fontsize=10)
  for ax in fig.axes:
   ax.tick_params(colors='#bec9d9',labelsize=8)
   for spine in ax.spines.values():spine.set_color('#536075')
  fig.text(.02,.015,'Window 0–600 HU · 8 mm cross-section width · yellow = original coronary mask boundary · cyan = GT center · orange = model.\nGT-guided views establish local image appearance, not blind discoverability. Interpolated oblique views; diameter is a mask-derived proxy.',color='#c9d2e2',fontsize=10)
  fig.savefig(O/f'{title}-{"overlay" if overlay else "clean"}.png',dpi=140,facecolor=fig.get_facecolor());plt.close(fig)
 # Save precise course, nearest identities and source coordinates for interactive native inspection.
 row['samples']=[{'s_mm':float(s[i]),'voxel_xyz':ijk[i].tolist(),'medium_distance_mm':float(d[i]),'medium_label':int(ml[i]),'medium_id':medium['obj']['centerlines'][int(owner[i])]['id']} for i in range(0,len(s),max(1,len(s)//50))]
(O/'branch-evidence.json').write_text(json.dumps({'method':'Original VTK paths and original native segmentation; physical EDT diameter proxy, trilinear HU; GT-guided post-hoc inspection only. Frozen evaluation unchanged.','branches':stats},indent=2)+'\n')
print(json.dumps([{k:v for k,v in x.items() if k!='samples'} for x in stats],indent=2))
# Supplemental native orthogonal views. Pixel values come directly from native slices.
from PIL import Image,ImageDraw
from scipy.ndimage import binary_erosion
native=O/'native';native.mkdir(exist_ok=True)
basework=ROOT/'runs/br042-all-vessels-astra-medium-v3-20260920-setup-recovery1/all-vessels__tvkf3rA/artifacts/app/answer/work'
candidates=[]
for file in sorted(basework.glob('tree*.json')):
 for j,z in enumerate(json.loads(file.read_text())):
  z=np.asarray(z)
  if z.ndim==2 and z.shape[1]==3 and len(z)>1:
   _,dense=path_resample(nib.affines.apply_affine(im.affine,z));candidates.append(dense)
ctree=cKDTree(np.concatenate(candidates))
for row in stats:
 key=row['branch'];label=row['reference_label'];reference_idx=[i for i,c in enumerate(ref['centerlines']) if c['id']==row['source_line']][0]
 valid=(ro==reference_idx)&(rl==label);rr=rp[valid];ww=rw[valid]
 row['official_sample_diagnostics']={}
 for name,m in models.items():
  dd,ii=nearest(rr,m['p']);hit=dd<=1;correct=hit&(m['l'][ii]==label)
  row['official_sample_diagnostics'][name]={'geometry_1mm':float(np.average(hit,weights=ww)),'labeled_1mm':float(np.average(correct,weights=ww)),'matched_names':{m['obj']['centerlines'][int(o)]['id']:float(ww[hit&(m['owners'][ii]==o)].sum()) for o in set(m['owners'][ii[hit]])}}
 row['medium_all_saved_candidate_geometry_1mm']=float(np.average(ctree.query(rr)[0]<=1,weights=ww))
 frames=[]
 for fi,entry in enumerate(row['samples']):
  xyz=np.rint(entry['voxel_xyz']).astype(int);panel=Image.new('RGB',(768,280),'#101724');draw=ImageDraw.Draw(panel)
  # Each native plane is displayed without projection or slab averaging.
  for pi,(axes,fixed,title) in enumerate([((0,1),2,'Axial: x / y'),((0,2),1,'Coronal: x / z'),((1,2),0,'Sagittal: y / z')]):
   u0,v0=axes;xs=np.arange(xyz[u0]-32,xyz[u0]+32);ys=np.arange(xyz[v0]-32,xyz[v0]+32);xx,yy=np.meshgrid(xs,ys)
   pos=np.tile(xyz,(64,64,1));pos[:,:,u0]=xx;pos[:,:,v0]=yy;pos=np.clip(pos,0,np.array(vol.shape)-1)
   gray=np.clip(vol[tuple(pos.transpose(2,0,1))]/600*255,0,255).astype('uint8');rgb=np.repeat(gray[:,:,None],3,axis=2)
   raw=Image.fromarray(rgb).resize((256,256),Image.Resampling.NEAREST);panel.paste(raw,(pi*256,24));draw.text((pi*256+6,5),title+' | native voxels',fill='white')
  panel.save(native/f'{key}-{fi:02d}-clean.png')
  # Small reference and submitted-point markers; clean view remains independently available.
  draw=ImageDraw.Draw(panel)
  for pi,(axes,fixed) in enumerate([((0,1),2),((0,2),1),((1,2),0)]):
   def marks(vox,color):
    near=vox[np.abs(vox[:,fixed]-xyz[fixed])<=.5]
    for z in near:
     xp=(z[axes[0]]-xyz[axes[0]]+32)*4+pi*256;yp=(z[axes[1]]-xyz[axes[1]]+32)*4+24
     if pi*256<=xp<(pi+1)*256 and 24<=yp<280:draw.ellipse((xp-1,yp-1,xp+1,yp+1),fill=color)
   marks(transform(medium['p'],inv),'#ff8c49');marks(transform(rr,inv),'#00e0d0')
  panel.save(native/f'{key}-{fi:02d}-overlay.png');frames.append({'file':f'native/{key}-{fi:02d}','xyz':xyz.tolist(),'s':entry['s_mm']})
 row['frames']=frames
(O/'branch-evidence.json').write_text(json.dumps({'method':'Original VTK paths and original native segmentation; physical EDT diameter proxy, trilinear HU; GT-guided post-hoc inspection only. Frozen evaluation unchanged.','branches':stats},indent=2)+'\n')
# Compact retained evidence; generated image files stay local.
compact={'scope':'Post-hoc branch investigation; unchanged frozen scores; Astra xhigh partial timeout output.','sources':{},'branches':[{k:v for k,v in row.items() if k not in ['samples','frames']} for row in stats]}
for path in [B/'tasks/all-vessels/tests/reference.json',S/'segmentations/1.coronary.nii.gz',S/'centerlines/1.coronary_left_centerline.vtk',S/'centerlines/1.coronary_right_centerline.vtk']:
 compact['sources'][str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
(ROOT/'docs/evidence/br042-v3-branch-audit.json').write_text(json.dumps(compact,indent=2)+'\n')
(O/'index.html').write_text((H/'branch_review.html').read_text(encoding='utf-8'),encoding='utf-8')
print('Native review + evidence complete')
