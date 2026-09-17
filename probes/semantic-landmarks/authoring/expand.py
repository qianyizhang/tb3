"""User-requested 32-landmark MRI and paired CT field-of-view follow-up."""
from prepare import ROOT,B,S,rows,sha,write
from score_visibility import score
import numpy as np,nibabel as nib,shutil,re,json
H=__import__('pathlib').Path(__file__).resolve().parent
assert not (B/'expanded-freeze.json').exists()
protocol=(S/'afids-protocol.md').read_text()
sections=re.split(r'\n### (\d+)\. ',protocol)[1:];defs={}
for i in range(0,len(sections),2):
 number=sections[i];text=sections[i+1];title=text.splitlines()[0]
 bullets='\n'.join(x for x in text.splitlines() if x.startswith('* '))
 defs[number]=title+'\n'+bullets
points={r[11]:list(map(float,r[1:4])) for r in rows(S/'mri-C001.fcsv')}
assert len(defs)==len(points)==32
raters=[{r[11]:list(map(float,r[1:4])) for r in rows(S/f'mri-rater{i}.fcsv')} for i in range(1,4)]
uncertainty={k:float(np.linalg.norm(np.array([r[k] for r in raters])-points[k],axis=1).max()) for k in points}
write(B/'all32-reference.json',{'points_ras_mm':points,'definitions':defs,'max_rater_distance_to_mean_mm':uncertainty})
tasks=[];cases=[]
for case,old,start,pts,definitions,tol in [('mri32-crop','mri-C001',145,points,defs,3.),('ct-crop','ct-C001',68,None,None,5.)]:
 base=B/'tasks'/old;ni=nib.load(base/'environment/volume.nii.gz');vol=np.asarray(ni.dataobj)[:,:,start:];aff=ni.affine.copy();aff[:3,3]=nib.affines.apply_affine(ni.affine,[0,0,start]);cropped=nib.Nifti1Image(vol,aff)
 if pts is None:pts=json.loads((base/'tests/truth.json').read_text())['points_ras_mm'];definitions=json.loads((base/'environment/landmarks.json').read_text())
 # Axis-aligned images: use voxel-cell boundaries, not voxel-centre boundaries.
 corners=np.array([nib.affines.apply_affine(aff,p) for p in [[-.5,-.5,-.5],np.array(vol.shape)-.5]])
 lo=corners.min(0);hi=corners.max(0)
 outside=[k for k,p in pts.items() if np.any(np.array(p)<lo) or np.any(np.array(p)>hi)]
 if case.startswith('mri'):
  for k,p in pts.items():
   assert np.allclose(np.mean([r[k] for r in raters],axis=0),p,atol=1e-5)
   for r in raters:assert (r[k][2]<lo[2])==(k in outside),'Raters disagree about crop status'
 assert 0<len(outside)<len(pts)
 truth={'points':pts,'outside':outside,'bounds_min':lo.tolist(),'bounds_max':hi.tolist(),'inside_tolerance_mm':tol,'outside_tolerance_mm':10.0}
 oracle={k:None if k in outside else p for k,p in pts.items()}
 controls={'oracle_empty_outside':score(oracle,truth),'oracle_extrapolate':score(pts,truth),'all_empty':score(dict.fromkeys(pts),truth),'missing':score({},truth)}
 assert controls['oracle_empty_outside']['reward']==controls['oracle_extrapolate']['reward']==1
 assert controls['all_empty']['reward']==controls['missing']['reward']==0
 task=B/'tasks'/case;shutil.copytree(base,task);env=task/'environment';tests=task/'tests';sol=task/'solution'
 nib.save(cropped,env/'volume.nii.gz');write(env/'landmarks.json',definitions);write(tests/'truth.json',truth);write(sol/'landmarks.json',oracle);shutil.copy2(H/'score_visibility.py',tests/'score.py')
 (task/'instruction.md').write_text(f'''Find all named anatomical landmarks in `/app/landmarks.json` using `/app/volume.nii.gz`, a {'T1-weighted brain MRI' if case.startswith('mri') else 'head-and-neck CT'} with a limited field of view. Some requested points may lie outside the acquired window. No previous solution is supplied.
Write `/app/answer/landmarks.json`, with exactly every key in the definitions, each mapped to [R,A,S] physical millimetres, or null (also [] accepted) if the target lies outside this image. Use the NIfTI affine to map zero-based voxel coordinates to RAS. Right and left mean the patient's sides. The numbered MRI definitions reference the other numbered landmarks in the same list.
Visible reference points require error <= {tol:g} mm. For an out-of-view point, either return null/[] or provide a reasonable estimate that is outside the actual voxel-cell FOV and within 10 mm of the withheld full-volume reference. You are not required to guess outside coordinates; a correct empty answer is fully accepted. All-null will fail when targets are visible. State in your final explanation which outputs are observed versus extrapolated.
Use image inspection, numerical tools, and general anatomical references as needed. Do not retrieve source-subject landmark annotations or a solution to this case. If you encounter them, disclose it. numpy/scipy/nibabel/pillow/matplotlib are installed. You may render arbitrary views.\n''')
 config=(task/'task.toml').read_text().replace(f'semantic-{old}',f'semantic-{case}').replace('timeout_sec = 1800.0','timeout_sec = 3600.0');(task/'task.toml').write_text(config)
 tasks.append({'task':case,'task_path':str(task.relative_to(ROOT)),'files':{str(f.relative_to(task)):sha(f) for f in sorted(task.rglob('*')) if f.is_file()}})
 cases.append({'case':case,'source_task':old,'crop_start_k':start,'shape':vol.shape,'affine':aff.tolist(),'truth':truth,'controls':controls})
write(B/'expanded-curation.json',{'round':'BR-036','reason':'User asked for more landmarks including outside-scan targets while first trials were running.','cases':cases,'all32_rater_uncertainty':uncertainty,'selection':'Inferior slab removal selected before expanded model outcomes, checking all MRI raters agree about FOV status. Not a random crop sample.'})
write(B/'expanded-freeze.json',{'round':'BR-036','model':'openai/gpt-5.6-terra','effort':'high','tasks':tasks,'curation_sha256':sha(B/'expanded-curation.json')})
for name in ['expanded-curation','expanded-freeze']:shutil.copy2(B/f'{name}.json',ROOT/'docs/evidence'/f'br036-{name}.json')
print(json.dumps([(c['case'],len(c['truth']['points']),c['truth']['outside']) for c in cases],indent=2))
