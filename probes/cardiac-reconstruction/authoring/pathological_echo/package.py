"""Freeze the clinical adaptation task, independent references, and controls."""
import hashlib,json,shutil
from pathlib import Path
import numpy as np
from score import score,volumes,category
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent;B=ROOT/'runs/br034-pathological-echo'
PIP='numpy==2.2.6 scipy==1.15.3 pillow==11.3.0 opencv-python-headless==4.12.0.88 meshio==5.3.5 scikit-image==0.25.2'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    task=B/'task/cardiac-adaptation';task.mkdir(parents=True,exist_ok=False)
    for d in ['environment','tests','solution']:(task/d).mkdir()
    shutil.copytree(B/'input',task/'environment/data')
    (task/'environment/Dockerfile').write_text(f'FROM python:3.12-slim-bookworm\nRUN pip install --no-cache-dir {PIP}\nWORKDIR /app\nCOPY data /app/data\nRUN mkdir -p /app/answer\n')
    (task/'tests/Dockerfile').write_text(f'FROM python:3.12-slim-bookworm\nRUN pip install --no-cache-dir {PIP}\nCOPY . /verifier/\nRUN mkdir -p /app/answer /tests && cp /verifier/test.sh /tests/test.sh && chmod 755 /tests/test.sh\nWORKDIR /app\nCMD ["/tests/test.sh"]\n')
    (task/'tests/test.sh').write_text('#!/bin/sh\nset -eu\npython /verifier/score.py\n')
    shutil.copy2(HERE/'score.py',task/'tests/score.py');shutil.copy2(B/'reference.npz',task/'tests/reference.npz')
    (task/'task.toml').write_text('''artifacts = ["/app/answer"]
[task]
name = "terminal-bench/cardiac-adaptation"
description = "Adapt a dynamic LV reconstruction to a clinical ultrasound and assess function"
authors = [{name = "Research pilot"}]
[metadata]
author_name = "Research pilot"
author_email = "probe@example.invalid"
category = "Data Science"
tags = ["cardiac", "clinical-echo", "adaptation"]
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
    (task/'instruction.md').write_text('''Adapt a dynamic cardiac reconstruction to the clinical ultrasound in /app/data, then assess LV systolic function from your model and the images.

This is a new patient compared with the optional previous-case solver in previous_case_solve.py. That older script used visually estimated fixed dimensions and does not re-estimate geometry from new pixels. You may replace it entirely. Build an executable image-driven pipeline rather than a table of per-frame answers.

Inputs: volumes.npy contains calibrated uint8 3D B-mode frames, one contiguous acquired beat. geometry.json gives timestamps, spatial scale and the [t,z,y,x] array-to-XYZ-mm convention. initial_mesh.npz gives an expert/software-derived LV blood-pool surface at the declared initial_mesh_frame. It includes the basal closure. There are unannotated orthogonal previews for inspection. No other contours, dynamic reference mesh, EF, disease label, Doppler or patient history are supplied. Treat the initial mesh as a helpful initialization and keep that frame close to it; recover the other phases from the ultrasound. Do not infer myocardial material strain from a cavity surface.

First inspect the images and save /app/answer/pre_model_assessment.json with your initial functional impression, uncertainty, and supporting frame references before fitting your dynamic model. Then implement /app/answer/solve.py accepting --input INPUT_DIRECTORY --output OUTPUT_DIRECTORY. It must re-estimate motion/geometry from the supplied image arrays when rerun, use the provided initial-mesh frame, work without external downloads, and finish a rerun in at most five minutes on 4 CPU cores/8GB RAM. We will replay the unchanged executable on the same case, a second real clinical case with the same schema but potentially different frame count/grid shape, a video whose volumes are all repetitions of the initialization frame, and a circularly phase-shifted version with an appropriately updated initialization-frame index. The altered-video controls test executable input response, not biological diagnosis. Generate all derived figures from the current input rather than relying on cached original measurements or preview files. The volumetric image array is authoritative.

Write prediction.npz: points of shape (T,N,3) in mm and faces of shape (M,3) containing integer triangle indices; shared connectivity across time, at most 10000 vertices/20000 faces, finite coordinates, closed consistently oriented surfaces including your declared basal cap. Write summary.json with volume_ml (T values independently calculated from the closed surfaces), ef_pct = 100*(max(volume_ml)-min(volume_ml))/max(volume_ml), ED/ES frame indices (zero based), uncertainty and diagnosis. diagnosis must include functional_class (one of severely_reduced, moderately_reduced, mildly_reduced_or_borderline, preserved), finding, image_and_model_evidence, differential_and_limits, and confidence. For this pilot's broad functional categories use EF <30%, 30-40%, >40 to <54%, and >=54% respectively; these bins simplify sex-dependent normal ranges and do not by themselves diagnose clinical heart failure or disease etiology. State when your estimate is near a boundary. Do not assert infarction, ischemic cause, valve severity, hemodynamics or a tissue-strain diagnosis without relevant evidence.

Retain method.md explaining the actual image computations, basal and tracking assumptions, failure regions, and how modeling changed or confirmed the initial impression. Save inspectable overlays. The goal is accurate patient-specific changing geometry and an evidence-supported functional assessment. A smooth plausible pulse is insufficient. The independent verifier compares dynamic surfaces and volumes against held-out clinical annotations: sampled symmetric surface mean <=3mm, maximum framewise surface-distance p95 <=6mm, EF error <=8 percentage points, EDV/ESV errors <=15%, and the broad functional category. These are exploratory pilot tolerances; clinical annotations themselves have uncertainty. Surface indices represent geometric correspondence, not known myocardial material points. No reviewer feedback is supplied during this attempt.

Use installed scientific libraries and the provided local data. Do not retrieve source scans, published reference reconstructions, pretrained cardiac models, or previous workbench files. No internet/source diagnosis lookup is needed. Be honest about what B-mode and a cavity model cannot establish. This is a research case, not patient care.
''')
    gt=np.load(B/'reference.npz');p=gt['points'];f=gt['faces'];v=volumes(p,f);ef=float(100*(1-min(v)/max(v)))
    shutil.copy2(B/'reference.npz',task/'solution/prediction.npz')
    summary=dict(volume_ml=v.tolist(),ef_pct=ef,diagnosis=dict(functional_class=category(ef)))
    (task/'solution/summary.json').write_text(json.dumps(summary));(task/'solution/solve.py').write_text('# Reference-artifact scoring control; not a reconstruction algorithm.\n')
    (task/'solution/method.md').write_text('Held-out source annotation, scoring control only.\n')
    (task/'solution/solve.sh').write_text('#!/bin/sh\nset -eu\ncp /solution/prediction.npz /solution/summary.json /solution/solve.py /solution/method.md /app/answer/\n')
    good=score(task/'solution',B/'reference.npz');assert good['reward']==1
    control=B/'static-control';control.mkdir();sp=np.repeat(p[:1],len(p),axis=0);sv=volumes(sp,f)
    np.savez_compressed(control/'prediction.npz',points=sp,faces=f)
    (control/'summary.json').write_text(json.dumps(dict(volume_ml=sv.tolist(),ef_pct=0,diagnosis=dict(functional_class='severely_reduced'))))
    (control/'solve.py').write_text('# static initialization control\n');(control/'method.md').write_text('Frozen ED surface throughout the cardiac cycle.\n')
    static=score(control,B/'reference.npz');assert static['reward']==0
    frozen=dict(round='BR-034',task_path=str(task.relative_to(ROOT)),files={str(p.relative_to(task)):sha(p) for p in sorted(task.rglob('*')) if p.is_file()},
        protocol_sha256=sha(ROOT/'docs/research-rounds/BR-034-pathological-echo.md'),preparation_sha256=sha(B/'preparation.json'),controls=dict(reference=good,static_initialization=static,nop=score(B/'absent',B/'reference.npz')))
    (B/'freeze.json').write_text(json.dumps(frozen,indent=2)+'\n');print(json.dumps(dict(files=len(frozen['files']),controls={k:v['reward'] for k,v in frozen['controls'].items()})))
if __name__=='__main__':main()
