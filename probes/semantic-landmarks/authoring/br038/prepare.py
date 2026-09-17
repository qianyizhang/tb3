"""Full native volumes -> explicitly tagged 3D voxel landmarks, BR-038."""
from pathlib import Path
import json,hashlib,shutil,importlib.util,subprocess
import numpy as np,nibabel as nib,SimpleITK as sitk
from score import score
from volume_tools import plane
ROOT=Path(__file__).resolve().parents[4];OLD=ROOT/'runs/br036-semantic-landmarks';B=ROOT/'runs/br038-volume-landmarks';H=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2)+'\n')
def main():
 assert not (B/'freeze.json').exists(),'Never overwrite freeze'
 # Asymmetric ramp tests detect every plane transposition and index swap.
 a=np.indices((7,11,13));a=10000*a[0]+100*a[1]+a[2]
 for axis in range(3):
  sl,axes=plane(a,axis,3)
  for row in range(sl.shape[0]):
   for col in range(sl.shape[1]):
    q=[0,0,0];q[axis]=3;q[axes[0]]=col;q[axes[1]]=row;assert sl[row,col]==a[tuple(q)]
 tasks=[];checks=[]
 for case,old,tol in [('ct-full','ct-C001',5.),('mri32-full','mri-C001',3.)]:
  base=OLD/'tasks'/old;ni=nib.load(base/'environment/volume.nii.gz');itk=sitk.ReadImage(str(base/'environment/volume.nii.gz'));arr=np.asarray(ni.dataobj)
  assert np.array_equal(arr,sitk.GetArrayFromImage(itk).transpose(2,1,0))
  if case.startswith('mri'):
   ref=json.loads((OLD/'all32-reference.json').read_text());ras=ref['points_ras_mm'];defs=ref['definitions']
  else:ras=json.loads((base/'tests/truth.json').read_text())['points_ras_mm'];defs=json.loads((base/'environment/landmarks.json').read_text())
  ijk={k:list(itk.TransformPhysicalPointToContinuousIndex(tuple(np.array(p)*[-1,-1,1]))) for k,p in ras.items()}
  assert all(np.allclose(nib.affines.apply_affine(ni.affine,p),ras[k],atol=1e-5) for k,p in ijk.items())
  assert all(np.all(np.array(p)>=0) and np.all(np.array(p)<arr.shape) for p in ijk.values())
  task=B/'tasks'/case;shutil.copytree(base,task);env=task/'environment';tests=task/'tests';sol=task/'solution'
  np.save(env/'volume.npy',arr);write(env/'landmarks.json',defs);shutil.copy2(H/'volume_tools.py',env/'volume_tools.py')
  spacing=np.linalg.norm(ni.affine[:3,:3],axis=0);examples=[]
  for v in [[17.,29.,11.],[arr.shape[0]*.61,arr.shape[1]*.37,arr.shape[2]*.73]]:
   examples.append({'ijk':v,'ras_mm':nib.affines.apply_affine(ni.affine,v).tolist()})
  g={'shape_ijk':list(arr.shape),'array_access':'volume[i,j,k]','index_base':0,'voxel_to_ras_mm':ni.affine.tolist(),'spacing_ijk_mm':spacing.tolist(),'positive_array_axes_patient_directions':list(nib.aff2axcodes(ni.affine)),'nonanatomical_coordinate_examples':examples,'display_window':[-200,1400] if case.startswith('ct') else np.percentile(arr[arr>0],[2,99]).tolist()};write(env/'geometry.json',g)
  truth={'points_ijk':ijk,'shape_ijk':list(arr.shape),'linear_voxel_to_mm':ni.affine[:3,:3].tolist(),'tolerance_mm':tol};write(tests/'truth.json',truth);shutil.copy2(H/'score.py',tests/'score.py')
  answer={'space':'voxel_ijk_zero_based','landmarks':ijk};write(sol/'landmarks.json',answer)
  controls={'oracle':score(answer,truth),'wrong_space_tag':score({'space':'RAS_mm','landmarks':ras},truth),'world_as_voxels':score({'space':'voxel_ijk_zero_based','landmarks':ras},truth),'empty':score({},truth),'axis_swap':score({'space':'voxel_ijk_zero_based','landmarks':{k:[v[2],v[1],v[0]] for k,v in ijk.items()}},truth)}
  assert controls['oracle']['reward']==1 and all(v['reward']==0 for k,v in controls.items() if k!='oracle')
  # One-voxel displacement must measure exactly that axis's physical spacing.
  for axis in range(3):
   delta=json.loads(json.dumps(answer));key=next(iter(ijk));delta['landmarks'][key][axis]+=1
   assert abs(score(delta,truth)['errors_mm'][key]-spacing[axis])<1e-9
  (env/'Dockerfile').write_text('FROM python:3.12-slim-bookworm\nRUN pip install --no-cache-dir numpy==2.2.6 scipy==1.15.3 nibabel==5.3.2 pillow==11.3.0 matplotlib==3.10.6\nWORKDIR /app\nCOPY volume.nii.gz volume.npy landmarks.json geometry.json volume_tools.py SOURCE_NOTICE.md /app/\nRUN mkdir -p /app/answer\n')
  (task/'instruction.md').write_text(f'''Localize all {len(ijk)} named anatomical points from the COMPLETE {'CT' if case.startswith('ct') else 'T1 MRI'} volume. This task is volume -> 3D landmark coordinates, not screenshot -> image pixels.

Input: `/app/volume.npy` is the full intensity array with shape {arr.shape}; access it as volume[i,j,k]. `/app/volume.nii.gz` is the identical array with spatial metadata. `/app/landmarks.json` defines the target points. All requested reference points are contained in this full volume. MRI numeric keys refer to definitions in that file.

Output `/app/answer/landmarks.json` with exactly this structure:
{{"space":"voxel_ijk_zero_based","landmarks":{{"<each requested key>":[i,j,k]}}}}
Return native array indices, zero-based; fractional values are allowed. They are 3D VOXEL coordinates, NOT screenshot pixels, NOT physical millimetres, NOT MNI or AC-PC coordinates. Do not reorder axes or flip sides. Index [0,0,0] is the array's first voxel, not an anatomical landmark. Patient RAS [0,0,0] is not necessarily AC. The volume has not been registered to an anatomical template for this task.

Run `python /app/volume_tools.py check` to verify the input contract. `/app/geometry.json` supplies shape, axis directions, affine and arbitrary NONANATOMICAL conversion examples. The supplied viewer avoids manual display-coordinate conversion:
`python /app/volume_tools.py view {arr.shape[0]//2} {arr.shape[1]//2} {arr.shape[2]//2} --out /app/overview.png`
Inspect the resulting image with your image tool. To zoom, add `--radius-mm 30`; change any i,j,k centre to inspect other slices. Axis ticks are original voxel indices. Cyan lines only indicate the centre you requested, not a detected point. You can build other views/tools as desired. `convert i j k` reports world RAS for debugging only; submit voxel indices.

The verifier alone converts voxel differences into physical distances, using the image geometry. Acceptance stays <= {tol:g} mm per landmark. No coordinate convention needs to be guessed. Inspect and refine image evidence for the actual subject; do not substitute nominal atlas positions. Record briefly how you identified the points. General anatomical references/software are allowed; source-subject labels, prior solutions and case-specific annotation retrieval are not. No earlier model answers are supplied.\n''')
  (task/'task.toml').write_text((task/'task.toml').read_text().replace(f'semantic-{old}',f'volume-landmarks-{case}').replace('timeout_sec = 1800.0','timeout_sec = 3600.0'))
  subprocess.run([str(ROOT/'.venv-br033/bin/python'),str(env/'volume_tools.py'),'check'],check=True)
  tasks.append({'task':case,'task_path':str(task.relative_to(ROOT)),'files':{str(f.relative_to(task)):sha(f) for f in sorted(task.rglob('*')) if f.is_file()}})
  checks.append({'case':case,'shape':list(arr.shape),'points':len(ijk),'controls':controls,'reference_conversion':'Independent SimpleITK LPS physical -> continuous native voxel index; cross-checked against nibabel RAS affine','input_original_nifti_sha256':sha(env/'volume.nii.gz'),'native_array_exact':True})
 write(B/'validation.json',{'checks':checks,'renderer_asymmetric_ramp_test':'all pixels in all three native planes verified','trial_plan':'Two fresh Terra/high attempts, full CT four points and full MRI 32 points. 3600 seconds each; matched oracle/nop, zero retries. Same 5/3 mm tolerances. Different output representation and viewer scaffolding, so not an isolated ablation.'})
 write(B/'freeze.json',{'round':'BR-038','tasks':tasks,'validation_sha256':sha(B/'validation.json')})
 for name in ['validation','freeze']:shutil.copy2(B/f'{name}.json',ROOT/'docs/evidence'/f'br038-{name}.json')
 print('Frozen two full-volume voxel-output tasks')
if __name__=='__main__':main()
