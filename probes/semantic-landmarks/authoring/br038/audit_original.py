"""Independent physical-coordinate and input-volume audit of BR-036."""
import json,hashlib
from pathlib import Path
import numpy as np,nibabel as nib,SimpleITK as sitk
ROOT=Path(__file__).resolve().parents[4];OLD=ROOT/'runs/br036-semantic-landmarks';B=ROOT/'runs/br038-volume-landmarks'
checks=[]
for fn in ['freeze.json','expanded-freeze.json']:
 for t in json.loads((OLD/fn).read_text())['tasks']:
  task=ROOT/t['task_path'];actual={str(f.relative_to(task)):hashlib.sha256(f.read_bytes()).hexdigest() for f in task.rglob('*') if f.is_file()};assert actual==t['files']
  nii=nib.load(task/'environment/volume.nii.gz');itk=sitk.ReadImage(str(task/'environment/volume.nii.gz'));a=np.asarray(nii.dataobj)
  assert np.array_equal(a,sitk.GetArrayFromImage(itk).transpose(2,1,0))
  raw=OLD/'source'/('ct-C001.nii.gz' if t['task'].startswith('ct') else 'mri-C001.nii.gz');src=nib.load(raw);start=68 if t['task']=='ct-crop' else 145 if t['task']=='mri32-crop' else 0
  assert np.array_equal(a,np.asarray(src.dataobj)[:,:,start:])
  truth=json.loads((task/'tests/truth.json').read_text());points=truth.get('points_ras_mm',truth.get('points'));max_roundtrip=0;max_independent=0
  voxel_truth={}
  for key,p in points.items():
   v=nib.affines.apply_affine(np.linalg.inv(nii.affine),p);w=np.array(itk.TransformPhysicalPointToContinuousIndex(tuple(np.array(p)*[-1,-1,1])));voxel_truth[key]=v.tolist()
   max_independent=max(max_independent,float(np.max(np.abs(v-w))))
   max_roundtrip=max(max_roundtrip,float(np.linalg.norm(nib.affines.apply_affine(nii.affine,v)-p)))
  assert max_independent<1e-4 and max_roundtrip<1e-8
  old_results=json.loads((OLD/'results.json').read_text());r=next(r for r in old_results['trials'] if r['case']==t['task'] and r['phase']=='terra-high');ans=json.loads((ROOT/r['answer_path']).read_text());error_delta=0
  for key,p in ans.items():
   if p is None:continue
   v=np.array(itk.TransformPhysicalPointToContinuousIndex(tuple(np.array(p)*[-1,-1,1])));gt=np.array(voxel_truth[key]);err=np.linalg.norm((v-gt)*np.array(itk.GetSpacing()));error_delta=max(error_delta,abs(err-r['score']['errors_mm'][key]))
  assert error_delta<1e-4
  checks.append({'case':t['task'],'input':'3D NIfTI array, not an image patch','shape':list(a.shape),'voxel_spacing_mm':list(itk.GetSpacing()),'orientation_nibabel':list(nib.aff2axcodes(nii.affine)),'crop_start_k':start,'native_intensities_exact':True,'max_itk_vs_nib_voxel_difference':max_independent,'max_world_roundtrip_error_mm':max_roundtrip,'max_independent_score_difference_mm':error_delta,'qform_sform_max_difference':float(np.max(np.abs(nii.get_qform()-nii.get_sform()))),'voxel_reference':voxel_truth})
out={'round':'BR-038','original_checks':checks,'finding':'No array transpose, RAS/LPS, crop-affine or scorer-distance discrepancy found. Original output contract was physical RAS millimetres. Agent-derived screenshots were tools, not supplied task inputs. Published reference correctness beyond technical alignment still needs independent anatomical adjudication.'}
(B/'original-audit.json').write_text(json.dumps(out,indent=2)+'\n');(ROOT/'docs/evidence/br038-original-audit.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps([{k:v for k,v in c.items() if k!='voxel_reference'} for c in checks],indent=2))
