"""Freeze one image-only real case; its verifier checks format, not accuracy."""
import hashlib,json,shutil,sys
from pathlib import Path
import numpy as np
from scipy.spatial import ConvexHull
from score import score,volumes

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];B=ROOT/'runs/br032-real-echo'
PIP='numpy==2.2.6 scipy==1.15.3 pillow==11.3.0 opencv-python-headless==4.12.0.88 meshio==5.3.5 scikit-image==0.25.2'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    task=B/'task/cardiac-real';task.mkdir(parents=True,exist_ok=False)
    for d in ['environment','tests','solution']:(task/d).mkdir()
    shutil.copytree(B/'input',task/'environment/data')
    (task/'environment/Dockerfile').write_text(f'FROM python:3.12-slim-bookworm\nRUN pip install --no-cache-dir {PIP}\nWORKDIR /app\nCOPY data /app/data\nRUN mkdir -p /app/answer\n')
    (task/'tests/Dockerfile').write_text(f'FROM python:3.12-slim-bookworm\nRUN pip install --no-cache-dir {PIP}\nCOPY . /verifier/\nRUN mkdir -p /app/answer /tests && cp /verifier/test.sh /tests/test.sh && chmod 755 /tests/test.sh\nWORKDIR /app\nCMD ["/tests/test.sh"]\n')
    (task/'tests/test.sh').write_text('#!/bin/sh\nset -eu\npython /verifier/score.py\n');shutil.copy2(HERE/'score.py',task/'tests/score.py')
    (task/'task.toml').write_text('''artifacts = ["/app/answer"]
[task]
name = "terminal-bench/cardiac-real"
description = "Real ultrasound case study without a reference reconstruction"
authors = [{name = "Research pilot"}]
[metadata]
author_name = "Research pilot"
author_email = "probe@example.invalid"
category = "Data Science"
tags = ["cardiac", "case-study", "no-reference-mesh"]
[verifier]
timeout_sec = 600.0
environment_mode = "separate"
[agent]
timeout_sec = 1800.0
[environment]
build_timeout_sec = 600.0
cpus = 4
memory_mb = 8192
storage_mb = 16384
gpus = 0
network_mode = "public"
''')
    (task/'instruction.md').write_text('''Build a plausible dynamic left-ventricular BLOOD-POOL surface from the real ultrasound videos in /app/data.

You receive four calibrated, synchronized reslices of one real 3D acquisition: two long-axis planes and two transverse planes. There are 18 original volume frames at 161.15 ms intervals (about 6.2 volumes/sec), not necessarily exactly one beat. Inspect actual motion before assigning extrema. geometry.json defines the common mm coordinate system and exact pixel-to-3D mapping. There are no input contours, initial mesh, pretrained cardiac weights, reference anatomy, reference motion or clinical outcomes. Infer the LV location, apex and basal closure from these images. Do not substitute the outer heart or whole myocardial body for the LV cavity.

Write /app/answer/prediction.npz with points (18,N,3), faces (M,3) integer triangle indices, and alternative_points (K,18,N,3) for K=2 to 5 alternative plausible completions using the same connectivity. Use millimetres, at most 10000 vertices/20000 triangles, finite coordinates, a closed consistently outward-oriented surface with a declared basal cap, and shared connectivity across frames. Alternatives should express meaningful uncertainty from depth, contour or basal assumptions; explain them. Persistent vertex indices are geometric correspondence, not established material identities. Do not claim measured myocardial strain from this cavity surface.

Retain an executable /app/answer/solve.py accepting `--input INPUT_DIRECTORY --output OUTPUT_DIRECTORY`, run it on /app/data, and include method.md and summary.json. summary.json must include frame_ids [1,...,18], volume_ml (18 values computed from your closed mesh), inferred extrema frame references, assumptions and uncertainty. Method.md should explain image evidence, segmentation/geometry/deformation, calibration, basal convention, weakly observed regions and what cannot be concluded. Saving inspectable overlays of your mesh sections on input videos is useful. Derive motion from observations; an unsupported decorative pulse is not the requested result.

Use the installed scientific libraries and local inputs. Do not retrieve the source scan, pretrained cardiac models, published reference reconstructions, or previous workbench/solver files. Dataset identifiers are deliberately absent; focus on the supplied measurements. No additional image or metric feedback will be given. Four other image planes are held out for review, and are not supplied to you.

This is a no-reference case study. Automatic checks only validate file schema, manifold edge closure, orientation, finite coordinates and consistent volume calculations; passing those checks does not establish correct anatomy. The author will independently inspect observed/held-out image agreement and sensitivity to assumptions. Do not optimize a mesh merely to pass the format check. Provide an honest best reconstruction and alternatives. No clinical EF accuracy, hemodynamics, active-force equilibrium, tissue-strain accuracy or diagnosis can be established with these inputs. If reporting fractional cavity-volume change, label it as your model's geometric estimate, not a validated clinical measurement.
''')
    # Deliberately image-ignorant shape: a format control, NEVER an anatomical oracle.
    rng=np.random.default_rng(320);unit=rng.normal(size=(300,3));unit/=np.linalg.norm(unit,axis=1,keepdims=True)
    f=ConvexHull(unit).simplices.copy();tri=unit[f];flip=np.einsum('ij,ij->i',np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),tri.mean(1))<0
    f[flip]=f[flip][:,[0,2,1]]
    p=np.repeat((unit*np.array([25,20,40]))[None],18,axis=0)
    alt=np.stack([p*1.1,p*.9]);np.savez_compressed(task/'solution/prediction.npz',points=p,faces=f,alternative_points=alt)
    (task/'solution/summary.json').write_text(json.dumps(dict(frame_ids=list(range(1,19)),volume_ml=volumes(p,f).tolist(),assumptions='format control',uncertainty='not a reconstruction')))
    (task/'solution/solve.py').write_text('# Deliberately static procedural format-control geometry, not an image reconstruction.\n')
    (task/'solution/method.md').write_text('Static ellipsoid format control. No image fit or truth is asserted.\n')
    (task/'solution/solve.sh').write_text('#!/bin/sh\nset -eu\ncp /solution/prediction.npz /solution/summary.json /solution/solve.py /solution/method.md /app/answer/\n')
    good=score(task/'solution');none=score(B/'absent');assert good['reward']==1 and none['reward']==0
    freeze=dict(round='BR-032',task_path=str(task.relative_to(ROOT)),files={str(p.relative_to(task)):sha(p) for p in sorted(task.rglob('*')) if p.is_file()},
                protocol_sha256=sha(ROOT/'docs/research-rounds/BR-032-real-echo-case.md'),source_receipt_sha256=sha(B/'source/source-receipt.json'),
                input_validation_sha256=sha(B/'input-validation.json'),pre_model_controls=dict(format_only=good,nop=none),
                outcome_scope='case study; no accuracy oracle or clinical/mechanics pass/fail')
    (B/'freeze.json').write_text(json.dumps(freeze,indent=2)+'\n');print(json.dumps(dict(files=len(freeze['files']),format_control=good['reward'],nop=none['reward'])))

if __name__=='__main__':main()
