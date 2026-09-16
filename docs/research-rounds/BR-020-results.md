# BR-020 — reconstruction-kernel registration results

[Protocol and source curation](BR-020-reconstruction-registration.md) ·
[Freeze](../evidence/br020-freeze.json) ·
[Author audit](../evidence/br020-author-audit.json) ·
[Measured results and execution audit](../evidence/br020-results.json)

## Outcome

Terra/high completed normally and passed the frozen different-reconstruction
task. Retire this snapshot as a hard-task candidate. There is no Terra failure
or stronger-model escalation in this round.

| Condition | RMS error | Maximum error | Runtime | Result |
| --- | --- | --- | --- | --- |
| Terra/high, B50f target with B30f CT | 0.035602 mm | 0.049830 mm | 272.42 s agent / 327.97 s trial | Pass |
| Public-input author baseline, same cross-kernel inputs, 512 starts | 0.034306 mm | 0.048141 mm | 26.36 s solver | Pass |
| Author matched B30f target control, 512 starts | 0.000238 mm | 0.000375 mm | 26.26 s solver | Pass |
| Isolated cross-kernel author replay | 0.031113 mm | 0.043968 mm | 24.41 s solver | Pass |

Acceptance remained RMS <=3 mm and maximum <=5 mm on a 7x7 grid including
the observed image corners. Oracle/nop returned 1/0 on the identical frozen
task, with no exceptions or retries. The final matrix is independently
regraded in the measured receipt. Model runtime includes its reasoning and
tool work; author solver runtime excludes method development and curation.

The initial unmodified 64-start author baseline missed both cross-kernel and
same-kernel controls by about 61 mm RMS. Both misses are retained. Raising
only its start count to 512 solved both before the model run. This rules out
treating those initial misses as evidence of a kernel-specific obstacle.

## What the agent did

The 30-step trajectory shows its own Python registration implementation using
the installed NumPy/SciPy stack. It inspected the target and CT, tried 24
cardinal orientations and 600 random orientation/position starts with Powell
optimization, then refined the best candidate with multiscale intensity
correlation. It also tested gradient correlation, ultimately submitting the
intensity-refined rigid slice-to-LPS matrix and rendering B30f to check it.

SciPy supplies general numerical optimizers; the agent assembled the
registration objective and search. The retained trace shows no downloaded
registration engine, pretrained model, new package installation or network
lookup. Its final public image correlation was 0.963504, consistent with
reconstruction mismatch instead of nearly exact pixel recovery.

The independently inspected initial agent image contains only the public HU
volume/geometry, target, image specification, forward renderer, source notice
and license, plus an empty answer directory. The source DICOM, B50f volume,
private pose, oracle, verifier and author baseline are absent. No task-bearing
follow-up or earlier solver was supplied. Runtime contexts identify Terra/high
and contain the frozen instruction. These are trace and image-audit findings,
not proof of provider-side model identity or an unobservable lack of all prior
knowledge.

The trace's `/app/work/gold.json` is the agent's own best candidate, written
from its random-search scores; it is not a supplied answer key. The absence
of observed network use is based on recorded tool calls and shell code, not
network packet capture.

Harness usage is 486,783 input tokens including 455,424 cached, and 8,066
output tokens. Estimated cost is $0.2506; this is a harness estimate, not a
separately measured bill.

## What this establishes

The selected public NLST pair has matching patient, study, frame of reference,
acquisition number, exposure settings and every one of 139 slice coordinates.
The native kernels are genuinely different, B30f and B50f. Acquisition times
were removed, so a common projection acquisition is strongly supported rather
than independently established from raw projections. This is a registration
engineering example with an author-selected cardiac-region section, not an
expert-certified diagnostic cardiac view.

Exact pixel equality is removed: at the reference pose, the two reconstructions
differ by 13.762 gray levels RMS and correlate at 0.963451. Nevertheless,
ordinary image registration recovers the plane with ample margin. Both the
author baseline and fresh agent pass. This one sample therefore does not
support different reconstruction kernels as sufficient difficulty.

It uses a different patient and plane from BR-019, so timing or error differences
across rounds cannot isolate a kernel effect. The tiny geometric errors measure
agreement with a generated transform; they are not clinical localization
precision. Source spacing is 0.695x0.695x2 mm. No success-rate estimate or
cross-acquisition/cross-modality capability claim follows from one trial.

Same-patient scans with anatomical changes, or different modalities, could
remove more correspondence cues. Those remain separate proposed experiments
requiring independently checked correspondence and a transform model that can
actually meet the tolerance. No such trial was launched here.

The local [interactive comparison](../../runs/br020-registration/review/index.html)
shows the B50f target, B30f at the reference pose, and B30f at the actual agent
pose, with an opacity slider. Raw scans, source receipts, configurations and
traces remain ignored under `runs/`; the closed report and submission workspace
are unchanged.
