from pathlib import Path
import json,hashlib,shutil,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[4];B=ROOT/'runs/br041-image-only-centerline';OLD=ROOT/'runs/br030-vessel-geometry/tasks/coronary-cpr';H=Path(__file__).resolve().parent
sys.path.insert(0,str(H));from score import score
T=B/'tasks/named-rca';assert not T.exists()
for name in ['environment/data','tests','solution']:(T/name).mkdir(parents=True)
for name in ['Dockerfile','DATA-LICENSE.txt']:shutil.copy2(OLD/'environment'/name,T/'environment'/name)
shutil.copy2(OLD/'environment/data/image.nii.gz',T/'environment/data/image.nii.gz')
(T/'environment/SOURCE_NOTICE.md').write_text('CTA from ImageCAS, Xiaowei Xu and collaborators, https://www.kaggle.com/datasets/xiaoweixumedicalai/imagecas . Source listing declares Apache 2.0. This is a coronary-region crop of a public development image. Private reference geometry is derived from corrected ImageCAS-X annotations, CC BY 4.0, Bransby et al. This pilot is not a held-out or clinical validation. Do not retrieve case-specific labels, masks or centerlines.\n')
(T/'instruction.md').write_text('''Trace a named coronary vessel from a CTA image.

Input: `/app/data/image.nii.gz`, a coronary-region CTA crop with native HU intensities. Arrays are XYZ; the NIfTI affine maps zero-based voxel indices to RAS millimeters. No segmentation, route landmarks or centerline is provided.

Trace from the right coronary artery (RCA) ostium through the RCA into the right posterior descending artery (R-PDA), ending at its distal visible terminus. Follow the central contrast-filled lumen continuously, including bends; select R-PDA rather than the right posterolateral branch. Infer location from the image and anatomical name. This is an image geometry task, not diagnosis.

Write `/app/answer/centerline.npy`: finite floating-point N by 3 array in RAS mm, ordered proximal to distal, 100-2000 points, approximately 0.5 mm sampling (each step 0.05-0.75 mm). Also write `method.md` briefly describing your method, uncertainties and any external sources consulted. Optional segmentation and visualizations are welcome but not required. No CPR or mesh is required.

Evaluation uses a private annotation-derived route: 95th-percentile distance <=1 mm, reference coverage >=95% within 1 mm, each endpoint within 5 mm, and length within 15%. Endpoint tolerance accounts for distal extent ambiguity. A plausible rendering alone is insufficient.

NumPy, SciPy, nibabel, Pillow, scikit-image and trimesh are installed. You may inspect native images, write code and use ordinary tools or general methods. Do not obtain this case's reference annotations, masks or centerlines. Report any external assistance. See `/app/SOURCE_NOTICE.md`.
''')
toml=(OLD/'task.toml').read_text().replace('coronary-cpr','named-rca-image-only').replace('1800.0','3600.0').replace('memory_mb = 4096','memory_mb = 8192')
(T/'task.toml').write_text(toml)
ref=np.load(ROOT/'runs/br030-vessel-geometry/geometry/reference.npz')['reference_path'];np.save(T/'tests/reference.npy',ref);np.save(T/'solution/centerline.npy',ref)
shutil.copy2(H/'score.py',T/'tests/score.py')
(T/'tests/test.sh').write_text('#!/bin/sh\nset -eu\npython /verifier/score.py\n')
shutil.copy2(OLD/'tests/Dockerfile',T/'tests/Dockerfile')
(T/'solution/solve.sh').write_text('#!/bin/sh\nset -eu\nmkdir -p /app/answer\ncp /solution/centerline.npy /app/answer/\n')
controls={'oracle':score(T/'solution',T/'tests/reference.npy')}
for label,line in [('reverse',ref[::-1]),('shift',ref+10),('straight',np.linspace(ref[0],ref[-1],len(ref)))]:
    p=B/'controls'/label;p.mkdir(parents=True);np.save(p/'centerline.npy',line);controls[label]=score(p,T/'tests/reference.npy')
assert controls['oracle']['reward']==1 and all(controls[x]['reward']==0 for x in ['reverse','shift','straight'])
(B/'validation.json').write_text(json.dumps(controls,indent=2)+'\n')
files={str(p.relative_to(T)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(T.rglob('*')) if p.is_file()}
freeze={'round':'BR-041','model':'openai/gpt-5.6-terra','effort':'high','timeout_seconds':3600,'attempts':1,'tasks':[{'task':'named-rca','task_path':str(T.relative_to(ROOT)),'files':files}]}
(B/'freeze.json').write_text(json.dumps(freeze,indent=2)+'\n')
(ROOT/'docs/evidence/br041-freeze.json').write_text(json.dumps(freeze,indent=2)+'\n')
print('Prepared frozen image-only task; oracle/reverse/shift/straight controls healthy')
