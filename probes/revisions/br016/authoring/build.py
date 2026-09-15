"""Build three immutable imaging-backed calibration tasks; hold tiny multi-lesion case."""
import json,shutil,tarfile,sys,itertools
from pathlib import Path
import numpy as np,nibabel as nib
from PIL import Image
from common import ROOT,OUT,write,sha,freeze_task
from inspect_mra import panel
from scoring import score
HERE=Path(__file__).parent;SRC=OUT/'source';records=[]
for sub,name in [('013','aneurysm-n01'),('022','aneurysm-n02'),('000','aneurysm-n03')]:
 task=OUT/'tasks'/name;assert not task.exists(),'Do not overwrite a built task'
 env=task/'environment';tests=task/'tests';solution=task/'solution';data=OUT/'build'/name
 for p in [env,tests,solution,data]:p.mkdir(parents=True,exist_ok=True)
 bp=next(SRC.glob(f'sub-{sub}*brain_mask.nii.gz'));rp=next(SRC.glob(f'sub-{sub}*angio.nii.gz'));b=nib.load(bp);r=nib.load(rp)
 a=np.asanyarray(b.dataobj);raw=np.asanyarray(r.dataobj);aff=b.affine;spacing=np.linalg.norm(aff[:3,:3],axis=0)
 assert a.shape==raw.shape and np.array_equal(aff,r.affine) and nib.aff2axcodes(aff)==('R','A','S')
 assert np.isfinite(a).all() and np.isfinite(raw).all()
 np.savez_compressed(data/'brain.npz',volume=a,affine=aff);np.savez_compressed(data/'original.npz',volume=raw,affine=aff)
 assert np.array_equal(np.load(data/'brain.npz')['volume'],a) and np.array_equal(np.load(data/'original.npz')['volume'],raw)
 high=float(np.percentile(a[a>0],99.9));bounds=[0,a.shape[0],0,a.shape[1],0,a.shape[2]]
 metadata={'case':name,'shape':list(a.shape),'spacing_mm':spacing.tolist(),'affine_ijk_to_RAS_mm':aff.tolist(),'axes':['R','A','S'],'coordinates':'zero-based voxel-center indices [i,j,k] in both volumes','brain':'source skull-stripped TOF-MRA, original sample values','original':'original unstripped TOF-MRA, same voxel grid','display_high':high}
 write(data/'volume.json',metadata)
 ims=[panel(a,spacing,d,None,bounds,high,600) for d in range(3)];can=Image.new('RGB',(ims[0].width*3,ims[0].height))
 for i,im in enumerate(ims):can.paste(im,(i*im.width,0))
 can.save(data/'overview.png')
 # Twelve fixed equal slabs span the whole volume, identical policy for every case.
 slabs=[]
 for lo,hi in zip(np.linspace(0,a.shape[2],13,dtype=int)[:-1],np.linspace(0,a.shape[2],13,dtype=int)[1:]):
  bd=bounds.copy();bd[4:]=[int(lo),int(hi)];im=panel(a,spacing,2,None,bd,high,400)
  from PIL import ImageDraw
  ImageDraw.Draw(im).text((12,im.height-18),f'k slab [{lo},{hi})',fill='white');slabs.append(im)
 can=Image.new('RGB',(slabs[0].width*3,slabs[0].height*4))
 for i,im in enumerate(slabs):can.paste(im,((i%3)*im.width,(i//3)*im.height))
 can.save(data/'slabs.png')
 regions=[];refs=[]
 for lp in sorted(SRC.glob(f'sub-{sub}*Lesion*nii.gz')):
  li=nib.load(lp);mask=np.asanyarray(li.dataobj)>0;assert mask.shape==a.shape and np.array_equal(li.affine,aff)
  q=np.argwhere(mask);center=q.mean(0);accepted=set(map(tuple,q.tolist()))
  # 1 mm Euclidean tolerance to source labelled voxel centres; no post-trial tuning.
  rr=np.ceil(1/spacing).astype(int)
  for off in itertools.product(*(range(-int(v),int(v)+1) for v in rr)):
   if np.linalg.norm(np.array(off)*spacing)>1+1e-8:continue
   for xyz in q+np.array(off):
    if np.all(xyz>=0) and np.all(xyz<np.array(a.shape)):accepted.add(tuple(map(int,xyz)))
  region={'accepted_voxels':{','.join(map(str,x)):1 for x in sorted(accepted)}};regions.append(region);refs.append(center.tolist())
  assert np.mean(a[mask]>0)>.95,'Source stripping removes labelled evidence'
  records.append({'case':name,'source':lp.name,'center':center.tolist(),'label_voxels':len(q),'label_extent_mm':((q.max(0)-q.min(0)+1)*spacing).tolist(),'accepted_voxels':len(accepted),'source_mask_sha256':sha(lp)})
 key={'shape':list(a.shape),'regions':regions};write(tests/'expected.json',key)
 oracle={'aneurysms':refs};assert score(oracle,key)['passed']
 controls=[]
 def ck(label,ans,want):
  try:got=score(ans,key)['passed']
  except (ValueError,TypeError,KeyError):got=False
  assert got==want,(label,got,want);controls.append({'name':label,'passed':got,'expected':want})
 ck('oracle',oracle,True);ck('invalid_missing_key',{},False);ck('empty',{'aneurysms':[]},not refs)
 ck('false_positive_corner',{'aneurysms':refs+[[0,0,0]]},False);ck('nan',{'aneurysms':[[float('nan'),0,0]]},False)
 ck('out_of_volume',{'aneurysms':[[-1,0,0]]},False);ck('boolean_coordinate',{'aneurysms':[[True,0,0]]},False)
 if refs:
  ck('duplicate_detection',{'aneurysms':refs+refs},False)
  for j,reg in enumerate(regions):
   first=list(map(int,next(iter(reg['accepted_voxels'])).split(',')));test=[p.copy() for p in refs];test[j]=first;ck(f'acceptance_edge_{j}',{'aneurysms':test},True)
 center=(np.array(a.shape)-1)/2;bright=np.array(np.unravel_index(a.argmax(),a.shape))
 baselines={label:score({'aneurysms':[p.tolist()]},key) for label,p in [('volume_center',center),('brightest_voxel',bright)]}
 write(OUT/'author'/f'{name}-controls.json',{'controls':controls,'baselines':baselines})
 for file in ['scoring.py']:shutil.copy2(HERE/file,tests/file)
 (tests/'test.sh').write_text('#!/bin/sh\nset -eu\npython /verifier/verifier.py\n');(tests/'test.sh').chmod(0o755)
 (tests/'verifier.py').write_text("import json,time\nfrom pathlib import Path\nfrom scoring import score,read_json\ns=time.monotonic();out=Path('/logs/verifier');out.mkdir(parents=True,exist_ok=True)\n(out/'reward.txt').write_text('0\\n')\ntry:r=score(read_json(Path('/app/answer/answer.json')),read_json(Path('/verifier/expected.json')))\nexcept Exception as e:r={'passed':False,'error':str(e)}\nr['grading_seconds']=time.monotonic()-s\n(out/'details.json').write_text(json.dumps(r,indent=2)+'\\n')\n(out/'reward.txt').write_text('1\\n' if r['passed'] else '0\\n')\nprint(json.dumps(r))\n")
 (solution/'solve.sh').write_text("#!/bin/sh\nset -eu\nmkdir -p /app/answer\ncat > /app/answer/answer.json <<'ANSWER'\n"+json.dumps(oracle)+"\nANSWER\n");(solution/'solve.sh').chmod(0o755)
 (env/'answer.json').write_text('{}\n');shutil.copy2(HERE/'inspect_mra.py',env/'inspect_mra.py')
 (env/'SOURCE_NOTICE.md').write_text('Data: Lausanne TOF-MRA cohort, OpenNeuro ds003949, CC0. Di Noto et al., Towards Automated Brain Aneurysm Detection in TOF-MRA: Open Data, Weak Labels, and Anatomical Knowledge. https://doi.org/10.1007/s12021-022-09597-0\nSource patient identifiers are omitted from this benchmark input.\n')
 (env/'Dockerfile').write_text('FROM python:3.12-slim-bookworm\nRUN pip install --no-cache-dir numpy==2.2.6 pillow==11.3.0\nWORKDIR /app\nADD data.tar.gz /app/data/\nCOPY answer.json /app/answer/answer.json\nCOPY inspect_mra.py SOURCE_NOTICE.md /app/\n')
 with tarfile.open(env/'data.tar.gz','w:gz') as t:
  for p in sorted(data.iterdir()):t.add(p,arcname=p.name)
 (task/'task.toml').write_text('''artifacts = ["/app/answer"]
[task]
name = "terminal-bench/'''+name+'''"
description = "Localize intracranial aneurysms in a TOF-MRA volume."
authors = [{name = "Interview research pilot"}]
[metadata]
author_name = "Interview research pilot"
author_email = "probe@example.invalid"
category = "Data Science"
tags = ["anatomy", "3d", "localization"]
[verifier]
timeout_sec = 120.0
environment_mode = "separate"
[agent]
timeout_sec = 1800.0
[environment]
build_timeout_sec = 600.0
cpus = 4
memory_mb = 4096
storage_mb = 10240
gpus = 0
network_mode = "public"
''')
 (task/'instruction.md').write_text('''# Locate intracranial aneurysms

Inspect this one TOF-MRA examination and identify every intracranial aneurysm
visible in the supplied volume. There may be zero, one, or multiple aneurysms.
Normal vessel bends and branch points are not aneurysms. No abnormality has been
synthetically injected. You are locating abnormalities, not predicting rupture
risk or drawing precise contours.

Write `/app/answer/answer.json` with exactly this schema:
`{"aneurysms": [[i, j, k], ...]}`. Return an empty list if none is present.
Coordinates are zero-based voxel-centre indices in the original 3-D array, in
**i,j,k order**. Choose a point within each aneurysm sac. Floating-point indices
are accepted; grading rounds to the nearest voxel centre. Coarse expert-labelled
regions plus 1 mm tolerance are used for matching. All lesions must be found and
extra detections count as false positives; duplicate points do not help.

## Inputs and tools

- `/app/data/brain.npz`: skull-stripped TOF-MRA. NumPy keys `volume`, `affine`.
- `/app/data/original.npz`: original unstripped TOF-MRA on the same voxel grid.
- `/app/data/volume.json`: array shape, spacing, RAS affine, display window.
- `/app/data/overview.png`: three full-volume maximum-intensity projections.
- `/app/data/slabs.png`: twelve equal axial-slab projections covering the entire scan.
- `/app/inspect_mra.py`: supplied slice / projection rendering tool, NumPy and Pillow.

Array axes increase towards Right, Anterior, Superior. Display horizontal increases
the first remaining array axis, and vertical increases the second axis upwards;
labels and ticks show these conventions. These are explicit coordinate views,
not the usual radiological left-right display. Array values remain native resolution.
Projections can obscure superimposed vessels: inspect slices / smaller slabs as needed.
The full scan is included; no crop or displayed position indicates a target.

Examples (illustrative arbitrary coordinates, not suggested findings):
```
python /app/inspect_mra.py --axis k --slices 30 40 50 --out /app/slices.png
python /app/inspect_mra.py --axis j --bounds 80 180 100 200 30 90 --out /app/slab.png
python /app/inspect_mra.py --raw --axis i --slices 100 --high 1000 --out /app/raw.png
```
Without `--slices`, the tool makes a maximum-intensity projection through the
selected bounds. Upper bounds are exclusive. `--high` adjusts the display window,
and `--size` adjusts rendering size. You may write your own analysis or rendering
code; the supplied views are starting points. Finish with the answer file.
''')
 freeze_task(task,{'source_subject':sub,'source_image_sha256':sha(rp),'source_brain_sha256':sha(bp),'clinical_review':'pending sampled experienced-user review','matching':'released source mask dilated by 1 mm Euclidean voxel-centre distance, then nearest-voxel membership','controls':controls,'baselines':baselines})
 print(json.dumps({'built':name,'regions':len(regions),'archive_bytes':(env/'data.tar.gz').stat().st_size}),flush=True)
write(OUT/'author/curation.json',{'admitted':records,'negative':'sub-000, cohort group control','held':{'subject':'sub-062','reason':'one released label spans only approximately 2 mm; hold for human evidence-sufficiency review before any model trial'},'review':'author visual cross-plane check only; not independent clinical validation'})
write(ROOT/'docs/evidence/br016-curation.json',json.loads((OUT/'author/curation.json').read_text()))
