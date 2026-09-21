from pathlib import Path
import json,hashlib,shutil,tarfile,base64
import nibabel as nib,numpy as np
ROOT=Path(__file__).resolve().parents[5];A=Path(__file__).resolve().parent;B=ROOT/'.local/dental-ct-only-astra-medium';T=B/'task';R=ROOT/'runs/toothfairy3-partial-20260921'
for d in ['environment/data','tests','solution']:(T/d).mkdir(parents=True,exist_ok=True)
# Verify official npm integrity and extract only standalone executables.
j=json.loads((B/'runtime/codex-platform.json').read_text());b=(B/'runtime/codex.tgz').read_bytes();assert 'sha512-'+base64.b64encode(hashlib.sha512(b).digest()).decode()==j['dist']['integrity']
with tarfile.open(B/'runtime/codex.tgz') as tar:
 members=[x for x in tar.getmembers() if x.name.startswith('package/vendor/aarch64-unknown-linux-musl/')]
 tar.extractall(B/'runtime/extracted',members=members,filter='data')
src=R/'viewer-f018/imagesTr/ToothFairy3F_018_0000.nii.gz';x=nib.load(src);data=np.asanyarray(x.dataobj);header=x.header.copy();header['descrip']=b'';header['aux_file']=b'';header['intent_name']=b'';header.extensions.clear();dest=T/'environment/data/ct.nii.gz';nib.save(nib.Nifti1Image(data,x.affine,header),dest);y=nib.load(dest);assert np.array_equal(data,np.asanyarray(y.dataobj)) and np.allclose(x.affine,y.affine)
labels={str(v):k for k,v in json.loads((R/'source/dataset.json').read_text())['labels'].items()};(T/'environment/data/labels.json').write_text(json.dumps(labels,indent=2)+'\n')
shutil.copy2(R/'viewer-f018/labelsTr/ToothFairy3F_018.nii.gz',T/'tests/reference.nii.gz');shutil.copy2(T/'tests/reference.nii.gz',T/'solution/reference.nii.gz');shutil.copy2(T/'environment/data/labels.json',T/'tests/labels.json');shutil.copy2(A/'score.py',T/'tests/score.py')
(T/'instruction.md').write_text('''# Segment a dental cone-beam CT

The original CT volume is `/app/data/ct.nii.gz`. The label-ID definitions are in
`/app/data/labels.json`.

Create a three-dimensional segmentation of the visible structures represented by
these labels. Save `/app/answer/segmentation.nii.gz` as an integer-label NIfTI
volume on exactly the input CT voxel grid, preserving its affine and dimensions.
Use background 0 and the supplied IDs. Label structures according to what is
visible in this scan. Also save `/app/answer/method.md` describing your method,
limitations and any uncertainty.

You may inspect the CT and use the installed local tools. External data, model
weights, websites and other cases are unavailable. There is no reference mask or
scoring feedback in this environment. Choose your own method. You have up to two
hours; save your output before finishing.
''')
(T/'task.toml').write_text('''version = "1.0"
artifacts = ["/app/answer", "/app/work"]
[metadata]
category = "medical-imaging"
[agent]
timeout_sec = 7200.0
[verifier]
timeout_sec = 300.0
environment_mode = "separate"
[verifier.environment]
docker_image = "tb3-dental-evaluator:v1"
network_mode = "no-network"
cpus = 2
memory_mb = 8192
[environment]
docker_image = "tb3-dental-solver:v1"
build_timeout_sec = 600.0
cpus = 4
memory_mb = 12288
storage_mb = 16384
gpus = 0
network_mode = "public"
''')
(T/'environment/Dockerfile').write_text('''FROM tb3-dental-runtime:v1
WORKDIR /app
COPY data /app/data
RUN mkdir -p /app/answer /app/work && chmod -R a-w /app/data
''')
(T/'environment/docker-compose.yaml').write_text('''services:
  main:
    networks: [isolated]
    cap_drop: [ALL]
    security_opt: [no-new-privileges:true]
    environment:
      HTTP_PROXY: http://transport:3128
      HTTPS_PROXY: http://transport:3128
      http_proxy: http://transport:3128
      https_proxy: http://transport:3128
      NO_PROXY: localhost,127.0.0.1
    depends_on: [transport]
  transport:
    image: tb3-dental-transport:v1
    networks: [isolated, egress]
    read_only: true
    cap_drop: [ALL]
    security_opt: [no-new-privileges:true]
networks:
  isolated:
    internal: true
  egress: {}
''')
(T/'tests/Dockerfile').write_text('FROM tb3-dental-runtime:v1\nCOPY . /tests\nRUN mkdir -p /app/answer /logs/verifier\n')
(T/'tests/test.sh').write_text('#!/bin/sh\nset -eu\npython /tests/score.py\n')
(T/'solution/solve.sh').write_text('#!/bin/sh\nset -eu\nmkdir -p /app/answer\ncp /solution/reference.nii.gz /app/answer/segmentation.nii.gz\n')
for p in [T/'tests/test.sh',T/'solution/solve.sh']:p.chmod(0o755)
(B/'runtime/Dockerfile').write_text('''FROM tb3-reproduce-tubular-anatomy-br042-all-vessels-v2-solver:e97a43c0d82d AS scientific
FROM python:3.12-slim-bookworm
COPY --from=scientific /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY extracted/package/vendor/aarch64-unknown-linux-musl /opt/codex
COPY codex-wrapper /usr/local/bin/codex
RUN chmod 755 /usr/local/bin/codex && ln -s /opt/codex/codex-path/rg /usr/local/bin/rg
RUN codex --version && python -c "import numpy,scipy,nibabel,skimage,PIL; print('scientific runtime ready')"
''')
shutil.copy2(A/'codex-wrapper',B/'runtime/codex-wrapper')
shutil.copy2(A/'proxy.py',B/'runtime/proxy.py');(B/'runtime/Proxy.Dockerfile').write_text('FROM python:3.12-slim-bookworm\nCOPY proxy.py /proxy.py\nCMD ["python", "-u", "/proxy.py"]\n')
receipt={'original_ct_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'solver_ct_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'voxels_exactly_equal':True,'affine_equal':True,'metadata_fields_removed':['descrip','aux_file','intent_name','extensions'],'solver_files':['data/ct.nii.gz','data/labels.json'],'gt_only_in_evaluator_and_oracle':True,'codex_version':'0.155.1','runtime_npm_integrity_verified':True};(B/'preparation-receipt.json').write_text(json.dumps(receipt,indent=2))
print(json.dumps(receipt,indent=2))
