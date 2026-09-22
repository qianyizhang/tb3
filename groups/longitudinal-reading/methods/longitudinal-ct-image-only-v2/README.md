# Revised CT instructions and conditional localized diagnostic

The user authorized one fresh Astra-medium run with generic instance/uncertainty
clarifications and a conditional narrower diagnostic if lesion regions remain
missed. [Protocol](../../experiments/longitudinal-ct-v2-astra-medium/protocol.md).
The original task, prompts, answers, freezes and scores remain unchanged.

`prepare.py` verifies every v1 task file against its retained manifest, copies
into a fresh destination and requires that only `instruction.md` changes. The
same data-only solver image and private evaluator image are reused by exact ID.
`preflight.py whole-volume` rechecks image identity, the two-image solver allowlist,
absence of private paths and blocked external egress. Native `med run` creates
new oracle/no-op controls and freeze records before inference.

`run_condition.py whole-volume` dispatches Astra medium once, with diagnostic
origin, a two-hour cap, no retries, live isolation checks and transport capture.
Fresh ordinary-usage clearance is required; reset credits are not authorized.
`audit.py whole-volume` reads completed artifacts only. The operator refuses to
launch while another task container is active. It never reads another model's
answer into the solver context.

The shared operator also supports a separately authored `localized` task if the
predeclared omission trigger fires. That task intentionally supplies candidate
locations and is reported separately from the image-only task. No localized task
is prepared or launched merely by running the whole-volume operator.

## Completed study and retained analysis

Both selected model attempts and their oracle/no-op controls completed on
2026-09-22. [Results](../../findings/longitudinal-ct-v2-and-localized.md).
Do not rerun dispatch as a maintenance or verification action. Fresh generation
requires a new destination/experiment and an intentionally selected trial.

`prepare_localized.py` scopes a new private reference to the prospectively selected
missed group and generates candidate centers without diagnostic labels. It keeps
the exact v1 scorer as `base_score.py`; `recognition_score.py` adds independent
judgment validation and positive-reference acceptance. Negative candidates are
absent, so specificity is undefined. `check_recognition_score.py` exercises six
meaningful judgment-contract cases against the prepared scorer.

`analyze_attempt.py SETTING` independently invokes the saved frozen scorer,
requires exact equality or at most 1e-12 numeric difference, measures GT coverage
and creates native comparison figures. Both actual replays matched exactly. It
refuses to overwrite an existing analysis directory. Residual low coverage in a
localized analysis does not authorize any further dispatch. Original analyses,
model artifacts and detailed trace audits are under
`.local/longitudinal-ct-image-only-v2/{whole-volume,localized}/`.
The [retained evidence summary](../../findings/evidence/longitudinal-ct-v2-and-localized.json)
records hashes and exact observable localized trace statements.

The analysis environment is the existing `.venv-br037`, with NumPy, SciPy,
nibabel and Matplotlib. No new runtime or pretrained model was installed.
The task freeze, CT inputs, Docker images and `.local` outputs must be retained
to reproduce locally; a Git clone alone does not contain those large artifacts.
The preparation scripts require retained v1 artifacts and pinned local images;
portable recovery on a fresh machine was not established in this study.
