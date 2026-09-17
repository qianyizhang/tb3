"""VerSe native full and partial CT -> 26 requested 3D landmarks, BR-039."""
from pathlib import Path
import json,hashlib,shutil,subprocess,copy
import numpy as np,nibabel as nib,SimpleITK as sitk
from score import score
from volume_tools import plane
ROOT=Path(__file__).resolve().parents[4];B=ROOT/'runs/br039-ct-landmarks';H=Path(__file__).resolve().parent
SRC=ROOT/'runs/br012-curation/source/files/20training/dataset-01training/derivatives/sub-verse823'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  while chunk:=f.read(8*1024*1024):h.update(chunk)
 return h.hexdigest()
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2)+'\n')
def name(label):return f'C{label}' if label<=7 else f'T{label-7}' if label<=19 else f'L{label-19}'
def main():
 assert not (B/'freeze.json').exists(),'Never overwrite freeze'
 ni=nib.load(B/'source/verse/ct.nii.gz');original=np.asarray(ni.dataobj)
 assert np.isfinite(original).all() and original.min()>=-32768 and original.max()<=32767
 arr=original.astype(np.int16);assert np.array_equal(arr,original), 'Only exact lossless dtype conversion permitted'
 del original
 mask=nib.load(SRC/'sub-verse823_dir-iso_seg-vert_msk.nii.gz')
 assert ni.shape==mask.shape and np.allclose(ni.affine,mask.affine)
 ctd=json.loads((SRC/'sub-verse823_dir-iso_seg-subreg_ctd.json').read_text());assert tuple(ctd[0]['direction'])==nib.aff2axcodes(ni.affine)==('L','A','S')
 points={name(r['label']):[r[x] for x in 'XYZ'] for r in ctd[1:]};assert len(points)==24
 ma=np.asarray(mask.dataobj)
 assert all(ma[tuple(np.rint(p).astype(int))]==(j+1) for j,p in enumerate(points.values()) if j>0)
 # C1 centre is between the atlas lateral masses, so no bone-mask membership expected.
 itk=sitk.ReadImage(str(B/'source/verse/ct.nii.gz'))
 for p in points.values():
  world=nib.affines.apply_affine(ni.affine,p);assert np.allclose(itk.TransformContinuousIndexToPhysicalPoint(p),world*[-1,-1,1])
 del itk,ma
 ramp=np.indices((7,11,13));ramp=10000*ramp[0]+100*ramp[1]+ramp[2]
 for axis in range(3):
  sl,axes=plane(ramp,axis,3)
  for row in range(sl.shape[0]):
   for col in range(sl.shape[1]):
    p=[0,0,0];p[axis]=3;p[axes[0]]=col;p[axes[1]]=row;assert sl[row,col]==ramp[tuple(p)]
 defs={name(i):f'Centre of vertebra {name(i)}: centre of the vertebral body, excluding posterior elements; for C1 use the atlas ring centre between its lateral masses.' for i in range(1,25)}
 defs['T13']='Centre of an additional thirteenth rib-bearing thoracic vertebral body, if present, between T12 and L1. Do not rename L1 to fill this request.'
 defs['L6']='Centre of an additional sixth lumbar vertebral body, if present, between L5 and the sacrum. Do not rename a sacral segment to fill this request.'
 checks=[];tasks=[]
 for case,upper in [('ct-full',arr.shape[2]),('ct-partial',920)]:
  task=B/'tasks'/case;base=ROOT/'runs/br038-volume-landmarks/tasks/ct-full';shutil.copytree(base,task)
  env=task/'environment';tests=task/'tests';sol=task/'solution';a=arr[:,:,:upper];aff=ni.affine.copy()
  nib.save(nib.Nifti1Image(a,aff),env/'volume.nii.gz')
  np.save(env/'volume.npy',a);write(env/'landmarks.json',defs);shutil.copy2(H/'volume_tools.py',env/'volume_tools.py')
  spacing=np.linalg.norm(aff[:3,:3],axis=0);examples=[]
  for v in [[17.,29.,11.],[a.shape[0]*.61,a.shape[1]*.37,a.shape[2]*.73]]:examples.append({'ijk':v,'ras_mm':nib.affines.apply_affine(aff,v).tolist()})
  g={'shape_ijk':list(a.shape),'array_access':'volume[i,j,k]','index_base':0,'voxel_to_ras_mm':aff.tolist(),'spacing_ijk_mm':spacing.tolist(),'positive_array_axes_patient_directions':list(nib.aff2axcodes(aff)),'nonanatomical_coordinate_examples':examples,'display_window':[-200,1400]};write(env/'geometry.json',g)
  targets={k:{'status':'observed' if -.5<=p[2]<=upper-.5 else 'out_of_fov','ijk':p} for k,p in points.items()}
  targets.update({k:{'status':'absent','ijk':None} for k in ['T13','L6']})
  truth={'targets':targets,'shape_ijk':list(a.shape),'linear_voxel_to_mm':aff[:3,:3].tolist(),'source_ijk':points,'source':'VerSe complete sub-verse823; source supplement 7/12/5/5, no T13 or L6','crop_native_k':[0,upper]};write(tests/'truth.json',truth);shutil.copy2(H/'score.py',tests/'score.py')
  answer={'space':'voxel_ijk_zero_based','landmarks':{k:{'status':v['status'],'ijk':v['ijk'] if v['status']=='observed' else None} for k,v in targets.items()}};write(sol/'landmarks.json',answer)
  control={'oracle':score(answer,truth),'nop':score({},truth)}
  allpresent=copy.deepcopy(answer)
  for k,v in allpresent['landmarks'].items():
   if v['status']!='observed':v.update(status='observed',ijk=[256.,200.,upper/2])
  control['all_present']=score(allpresent,truth);assert sum(control['all_present']['hallucinated'].values())==sum(v['status']!='observed' for v in targets.values())
  allnull=copy.deepcopy(answer)
  for v in allnull['landmarks'].values():v.update(status='uncertain',ijk=None)
  control['all_uncertain']=score(allnull,truth);assert control['all_uncertain']['missed_visible']==control['oracle']['counts']['observed'] and control['all_uncertain']['hallucination_rate']==0
  wrong=copy.deepcopy(answer);wrong['space']='RAS_mm';control['wrong_space']=score(wrong,truth)
  extra=copy.deepcopy(answer)
  for k,v in targets.items():
   if v['status']=='out_of_fov':extra['landmarks'][k]['ijk']=v['ijk']
  control['explicit_extrapolation']=score(extra,truth);assert control['explicit_extrapolation']['reward']==1 and all(e==0 for e in control['explicit_extrapolation']['extrapolation_errors_mm'].values())
  for axis in range(3):
   delta=copy.deepcopy(answer);key=next(k for k,v in targets.items() if v['status']=='observed');delta['landmarks'][key]['ijk'][axis]+=1
   assert abs(score(delta,truth)['errors_mm'][key]-spacing[axis])<1e-9
  assert control['oracle']['reward']==1 and control['nop']['reward']==0 and control['wrong_space']['reward']==0
  (env/'SOURCE_NOTICE.md').write_text('Source: VerSe, Sekuboyina et al. and Liebl et al., 2021. CT data licensed CC BY-SA 4.0, https://creativecommons.org/licenses/by-sa/4.0/ . Dataset information: https://github.com/anjany/verse . This task supplies the scan intensities and geometry only; source-specific annotation retrieval is prohibited. A partial field of view may have been derived without resampling. No patient identifier or GT supplied.\n')
  (task/'instruction.md').write_text(f'''Localize the 26 requested vertebral landmarks from the supplied CT volume and identify targets that cannot be localized. Use this patient's anatomy, not an assumed fixed count. Some requests may be outside the field of view or represent a genuinely absent extra vertebra. A missing annotation is not proof of absence. Do not force a coordinate for every requested name.

Input `/app/volume.npy` is the entire supplied 3D CT array, shape {a.shape}, access volume[i,j,k]. `/app/volume.nii.gz` contains identical intensities and spatial metadata. This {'complete source CT' if case=='ct-full' else 'partial CT volume'} can be inspected at any slice and zoom. `/app/landmarks.json` gives the requested semantic definitions. You are not given reference segmentations or coordinates. Standard nomenclature: C1-C7; thoracic levels are rib-bearing; lumbar levels precede the sacrum. T13/L6 are possible additional levels, not required placeholders.

Write `/app/answer/landmarks.json` exactly as:
{{"space":"voxel_ijk_zero_based","landmarks":{{"<each requested key>":{{"status":"observed|out_of_fov|absent|uncertain","ijk":[i,j,k] or null}}}}}}
- observed: target exists and its centre is within the supplied scan; provide a native zero-based voxel triple.
- out_of_fov: target's centre lies outside this scan; use null, or optionally give an explicitly extrapolated out-of-bounds voxel triple. Such an estimate is not an observed detection.
- absent: evidence supports that this patient does not have that anatomical level; use null. Do not equate outside coverage with absence.
- uncertain: insufficient evidence to decide/localize; use null.
All keys are required. Fractional indices are allowed. Coordinates are array ijk, NOT screenshot pixels, NOT RAS/LPS millimetres. Do not reorder or flip indices. The scanner origin is not an anatomical anchor.

Run `python /app/volume_tools.py check`. View with `python /app/volume_tools.py view 256 220 {upper//2} --out /app/overview.png` and inspect the resulting image using your image tool. Change the centre to explore the volume; add `--radius-mm 40` to zoom. Axis ticks show native voxel indices. Cyan crosshairs indicate only your chosen inspection centre. Geometry and nonanatomical conversion examples are in `/app/geometry.json`. You may build other views or image-processing tools.

Localization is measured in physical millimetres from native voxel coordinates at 5/10/20 mm thresholds. False observed detections on unavailable requests, missed visible points, correct visibility/absence classification, and uncertain abstentions are measured separately. General anatomy references and software are allowed; case-specific source annotations, prior answers, or reference masks must not be retrieved. Briefly document image evidence and your identification method.\n''')
  toml=(task/'task.toml').read_text().replace('volume-landmarks-ct-full',f'expanded-landmarks-{case}');(task/'task.toml').write_text(toml)
  subprocess.run([str(ROOT/'.venv-br033/bin/python'),str(env/'volume_tools.py'),'check'],check=True)
  tasks.append({'task':case,'task_path':str(task.relative_to(ROOT)),'files':{str(f.relative_to(task)):sha(f) for f in sorted(task.rglob('*')) if f.is_file()}})
  checks.append({'case':case,'shape':list(a.shape),'controls':control,'source_native_array_exact':True,'lossless_dtype_conversion':'float64 to int16; every intensity equal; geometry unchanged','source_centroids_axis_match':True,'source_mask_membership':'C2-L5 all match; C1 centre is atlas-ring centre and not inside bone','sitk_nibabel_world_agreement':True})
 write(B/'validation.json',{'checks':checks,'renderer_asymmetric_ramp':'PASS','source_ct_receipt':json.loads((B/'source/verse/receipt.json').read_text())})
 write(B/'freeze.json',{'round':'BR-039','tasks':tasks,'validation_sha256':sha(B/'validation.json')})
 for nm in ['validation','freeze']:shutil.copy2(B/f'{nm}.json',ROOT/'docs/evidence'/f'br039-{nm}.json')
 print('Frozen two tasks',[(r['case'],r['controls']['oracle']['counts']) for r in checks])
if __name__=='__main__':main()
