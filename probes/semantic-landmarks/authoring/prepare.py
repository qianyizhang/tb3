"""Curate first source-order CT/MRI cases and freeze semantic localization pilot."""
from pathlib import Path
import csv,hashlib,json,shutil,zipfile
import numpy as np
import nibabel as nib
import SimpleITK as sitk
from score import score
ROOT=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent;B=ROOT/'runs/br036-semantic-landmarks';S=B/'source'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(p):return list(csv.reader(x for x in p.read_text().splitlines() if x and not x.startswith('#')))
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2)+'\n')
MRI={
'1':('AC','Centre of the anterior commissure on the midline.'),
'2':('PC','Centre of the posterior commissure on the midline.'),
'3':('infracollicular_sulcus','Midline inferior end of the sulcus between the inferior colliculi.'),
'4':('pontomesencephalic_junction','Midline junction of pons and midbrain; select the ventral/inferior pontine side.'),
'12':('right_mammillary_body','Centre of the right mammillary body.'),
'13':('left_mammillary_body','Centre of the left mammillary body.'),
'19':('genu','Midline most anterior point of the corpus callosum.'),
'20':('splenium','Midline lowest point of the splenium at its CSF boundary.')}
CT={
'chin':'On the most inferior axial slice containing the chin, centre of mandibular bone at the symmetry midline.',
'mand_r':'Centre of the right mandibular condyle on the most superior axial slice where it is fully visible.',
'mand_l':'Centre of the left mandibular condyle on the most superior axial slice where it is fully visible.',
'odont_proc':'Centre of the dens on the most superior axial slice where the odontoid process is fully visible.'}
def main():
 assert not (B/'freeze.json').exists(),'Never overwrite a freeze'
 z=zipfile.ZipFile(S/'PDDCA-1.4.1_part1.zip')
 for name in ['0522c0001/img.nrrd','0522c0001/Landmarks_0001.fcsv']:z.extract(name,S)
 im=sitk.ReadImage(str(S/'0522c0001/img.nrrd'))
 a=sitk.GetArrayFromImage(im).transpose(2,1,0)
 aff=np.eye(4);aff[:3,:3]=np.array(im.GetDirection()).reshape(3,3)@np.diag(im.GetSpacing());aff[:3,3]=im.GetOrigin();aff=np.diag([-1,-1,1,1])@aff
 ct=nib.Nifti1Image(a,aff);nib.save(ct,S/'ct-C001.nii.gz')
 mri=nib.load(S/'mri-C001.nii.gz')
 assert sha(S/'mri-C001.nii.gz')=='4569c5e45fa61362ebde1e214fee1e5385978000d298c8da82f99f10e4b23688'
 assert sha(S/'mri-C001.fcsv')=='d617ebb0ae555772844919b35e4c1fe19e25dbe38b322f13e7b65795bbe958d7'
 mr={MRI[r[11]][0]:list(map(float,r[1:4])) for r in rows(S/'mri-C001.fcsv') if r[11] in MRI}
 cr={r[11]:list(map(float,r[1:4])) for r in rows(S/'0522c0001/Landmarks_0001.fcsv') if r[11] in CT}
 raters=[{r[11]:list(map(float,r[1:4])) for r in rows(S/f'mri-rater{i}.fcsv')} for i in range(1,4)]
 uncertainty={}
 for k,(name,_) in MRI.items():
  coords=np.array([r[k] for r in raters]);assert np.allclose(coords.mean(0),mr[name],atol=1e-5)
  uncertainty[name]={'max_rater_distance_to_mean_mm':float(np.linalg.norm(coords-coords.mean(0),axis=1).max())}
 tasks=[];cases=[]
 for case,ni,points,defs,tol,source in [
 ('ct-C001',ct,cr,CT,5.0,'PDDCA 1.4.1, 0522c0001; https://www.imagenglab.com/newsite/pddca/ ; Sharp et al. Public-domain dataset; retain attribution.'),
 ('mri-C001',mri,mr,{v[0]:v[1] for v in MRI.values()},3.0,'AFIDs SNSX, ds004470 sub-C001; Taha et al. 2023; https://doi.org/10.18112/openneuro.ds004470 ; CC BY 4.0. Source Git revision 53f2c2caecf346b620971a5dd4672ca538441ede.')]:
  vox={k:nib.affines.apply_affine(np.linalg.inv(ni.affine),p).tolist() for k,p in points.items()}
  assert all(np.all(np.array(v)>=0) and np.all(np.array(v)<ni.shape) for v in vox.values())
  truth={'points_ras_mm':points,'tolerance_mm':tol}
  controls={'oracle':score(points,truth),'empty':score({},truth),'shift20mm':score({k:[v[0]+20,*v[1:]] for k,v in points.items()},truth),'nonfinite':score({k:[float('nan'),0,0] for k in points},truth)}
  assert controls['oracle']['reward']==1 and all(v['reward']==0 for k,v in controls.items() if k!='oracle')
  task=B/'tasks'/case;env=task/'environment';tests=task/'tests';sol=task/'solution'
  for p in [env,tests,sol]:p.mkdir(parents=True)
  nib.save(ni,env/'volume.nii.gz');write(env/'landmarks.json',defs);write(tests/'truth.json',truth);write(sol/'landmarks.json',points)
  (env/'SOURCE_NOTICE.md').write_text(source+'\nPublic data may have appeared in training. Case annotations are withheld from the task.\n')
  packages='numpy==2.2.6 scipy==1.15.3 nibabel==5.3.2 pillow==11.3.0 matplotlib==3.10.6'
  (env/'Dockerfile').write_text(f'FROM python:3.12-slim-bookworm\nRUN pip install --no-cache-dir {packages}\nWORKDIR /app\nCOPY volume.nii.gz landmarks.json SOURCE_NOTICE.md /app/\nRUN mkdir -p /app/answer\n')
  shutil.copy2(H/'score.py',tests/'score.py')
  (tests/'test.sh').write_text('#!/bin/sh\nset -eu\npython /verifier/score.py\n')
  (tests/'Dockerfile').write_text('FROM python:3.12-slim-bookworm\nCOPY . /verifier/\nRUN mkdir -p /app/answer /tests && cp /verifier/test.sh /tests/test.sh && chmod 755 /tests/test.sh\nWORKDIR /app\nCMD ["/tests/test.sh"]\n')
  (sol/'solve.sh').write_text('#!/bin/sh\nset -eu\nmkdir -p /app/answer\ncp /solution/landmarks.json /app/answer/landmarks.json\n')
  (task/'instruction.md').write_text(f'''Localize the named anatomical landmarks in the full {'CT' if case.startswith('ct') else 'T1-weighted MRI'} volume `/app/volume.nii.gz`. Definitions are in `/app/landmarks.json`.
Write `/app/answer/landmarks.json` as a JSON object mapping every requested name to a three-number [R,A,S] physical coordinate in millimetres. The NIfTI affine maps zero-based voxel [i,j,k] to these RAS coordinates; use its actual orientation. Anatomical right/left refer to the patient.
Every requested point must be within {tol:g} mm of the manually annotated reference for a pass. Use image inspection and any numerical tools you find useful; installed packages include nibabel, numpy, scipy, pillow, matplotlib. You may render your own views at any resolution and inspect them. Deliver coordinates and briefly describe how you identified each point. Full scan coverage is retained.
General anatomical references and software are allowed. Do not retrieve this subject's landmark annotations or a solution to this case. This is an image-localization test; source-case answer retrieval must be disclosed and will be reported as source-assisted.
''')
  (task/'task.toml').write_text(f'''artifacts = ["/app/answer"]
[task]
name = "terminal-bench/semantic-{case}"
description = "Semantic anatomical landmark localization from a native full volume."
authors = [{{name = "Research pilot"}}]
[metadata]
author_name = "Research pilot"
author_email = "probe@example.invalid"
category = "Data Science"
tags = ["anatomy", "landmarks"]
[verifier]
timeout_sec = 120.0
environment_mode = "separate"
[agent]
timeout_sec = 1800.0
[environment]
build_timeout_sec = 600.0
cpus = 2
memory_mb = 4096
storage_mb = 10240
gpus = 0
network_mode = "public"
''')
  tasks.append({'task':case,'task_path':str(task.relative_to(ROOT)),'files':{str(f.relative_to(task)):sha(f) for f in sorted(task.rglob('*')) if f.is_file()}})
  cases.append({'case':case,'source':source,'shape':ni.shape,'affine':ni.affine.tolist(),'points_ras_mm':points,'points_voxel':vox,'tolerance_mm':tol,'controls':controls})
 write(B/'curation.json',{'cases':cases,'mri_rater_uncertainty':uncertainty,'selection':'First source-order case for each modality; landmark subset fixed by clear textual definitions. Occipital CT landmark excluded because source definition depends on illustration. No outcome-based selection.','source_sha256':{str(p.relative_to(S)):sha(p) for p in S.rglob('*') if p.is_file()}})
 write(B/'freeze.json',{'round':'BR-036','model':'openai/gpt-5.6-terra','effort':'high','tasks':tasks,'curation_sha256':sha(B/'curation.json')})
 print(json.dumps({'cases':[(x['case'],len(x['points_ras_mm'])) for x in cases],'rater_uncertainty':uncertainty},indent=2))
if __name__=='__main__':main()
