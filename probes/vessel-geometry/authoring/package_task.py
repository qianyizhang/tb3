"""Freeze a concrete, tested larger task before its first model trial."""
from pathlib import Path
import hashlib,json,shutil

ROOT=Path(__file__).resolve().parents[3];B=ROOT/'runs/br030-vessel-geometry';H=Path(__file__).resolve().parent
PIP='numpy==2.2.6 scipy==1.15.3 nibabel==5.3.2 pillow==11.3.0 scikit-image==0.25.2 trimesh==4.11.3'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    v=json.loads((B/'geometry/validation.json').read_text());assert all(v['analytic_checks'].values()) and v['controls']['oracle']['reward']==1
    task=B/'tasks/coronary-cpr';assert not task.exists(),'Never overwrite a prepared task'
    env=task/'environment';tests=task/'tests';sol=task/'solution'
    for p in [env,tests,sol]:p.mkdir(parents=True)
    shutil.copytree(B/'geometry/input',env/'data');shutil.copy2(H/'instruction.md',task/'instruction.md')
    (env/'SOURCE_NOTICE.md').write_text('CTA: ImageCAS case 1, Xiaowei Xu and collaborators. Official source https://www.kaggle.com/datasets/xiaoweixumedicalai/imagecas (listing declares Apache 2.0). ImageCAS paper https://arxiv.org/abs/2211.01607 .\nPrediction: released ImageCAS-X CAS-Net checkpoint with full-volume published preprocessing, patch inference, X/Y mirroring and component filtering; batch size 1. Code https://github.com/kitbransby/ImageCAS-X at dbc7343187adf45ca9306dc3460eebc70f92b204 . Weights https://zenodo.org/records/21887809 . No artificial gaps or bridges were inserted. This is an unmodified spatial crop of its prediction and image.\nImageCAS-X annotations and derived geometry are evaluator-only, under CC BY 4.0. This case is in the released training split; this local development task is not a held-out segmentation performance estimate or a clinical diagnostic validation.\n')
    (env/'DATA-LICENSE.txt').write_text('Source license declarations, checked 2026-09-16:\nImageCAS CTA Kaggle listing: Apache 2.0, https://www.apache.org/licenses/LICENSE-2.0 .\nImageCAS-X Zenodo record 21887809: CC BY 4.0, https://creativecommons.org/licenses/by/4.0/ . Attribution: Bransby et al., ImageCAS-X, arXiv:2608.30404 (2026).\nImageCAS-X source code: MIT, retained below.\n\n'+(B/'imagecas-x-source/LICENSE').read_text())
    (env/'Dockerfile').write_text(f'FROM python:3.12-slim-bookworm\nRUN pip install --no-cache-dir {PIP}\nWORKDIR /app\nCOPY data /app/data\nCOPY SOURCE_NOTICE.md DATA-LICENSE.txt /app/\nRUN mkdir -p /app/answer\n')
    shutil.copy2(H/'score_geometry.py',tests/'score_geometry.py');shutil.copy2(B/'geometry/reference.npz',tests/'reference.npz')
    (tests/'test.sh').write_text('#!/bin/sh\nset -eu\npython /verifier/score_geometry.py\n')
    (tests/'Dockerfile').write_text(f'FROM python:3.12-slim-bookworm\nRUN pip install --no-cache-dir {PIP}\nCOPY . /verifier/\nRUN mkdir -p /app/answer /tests && cp /verifier/test.sh /tests/test.sh && chmod 755 /tests/test.sh\nWORKDIR /app\nCMD ["/tests/test.sh"]\n')
    for name in ['corrected_mask.nii.gz','centerline.npy','cpr.npz','vessels.ply']:shutil.copy2(B/'geometry/oracle'/name,sol/name)
    (sol/'solve.sh').write_text('#!/bin/sh\nset -eu\nmkdir -p /app/answer\ncp /solution/corrected_mask.nii.gz /solution/centerline.npy /solution/cpr.npz /solution/vessels.ply /app/answer/\n')
    (task/'task.toml').write_text('''artifacts = ["/app/answer"]
[task]
name = "terminal-bench/coronary-cpr"
description = "Repair a natural coronary segmentation gap, trace RCA to R-PDA, and produce rotated CPR and a world-space mesh."
authors = [{name = "Research pilot"}]
[metadata]
author_name = "Research pilot"
author_email = "probe@example.invalid"
category = "Data Science"
tags = ["cta", "coronary", "segmentation", "cpr", "mesh"]
[verifier]
timeout_sec = 180.0
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
    files={str(p.relative_to(task)):sha(p) for p in sorted(task.rglob('*')) if p.is_file()}
    manifest={'round':'BR-030','pretrial':True,'model':'openai/gpt-5.6-terra','reasoning_effort':'high','agent_timeout_sec':1800,
              'tasks':[{'task':'coronary-cpr','task_path':str(task.relative_to(ROOT)),'files':files}],
              'source_prediction_sha256':sha(B/'predictions/coronary-1-casnet.nii.gz'),
              'validation_sha256':sha(B/'geometry/validation.json'),
              'claim_scope':'One development case. Stage feasibility and model diagnostic; no clinical accuracy or held-out model benchmark claim.'}
    (B/'freeze.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'files':len(files),'freeze_sha256':sha(B/'freeze.json'),'public_image_bytes':(env/'data/image.nii.gz').stat().st_size},indent=2))

if __name__=='__main__':main()
