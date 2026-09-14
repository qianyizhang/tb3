# E04 author record

One fixed, noiseless, acyclic affine instrument is calibrated through a public
measurement client. The instrument image owns the structural equations; the
agent image contains only the client, passive observations, starter predictor
and public batch/check scripts. Compose supports this separation in the
installed Harbor 0.14/0.18 implementations. A logged-measurement artifact is
collected from the instrument service after the agent phase. The verifier has
no instrument service and grades offline predictions only.

Actual equations, fixed for this snapshot: Y=-1.6 U+0.75;
X=0.8 U+1.25 Y-0.3. Clamps replace complete equations. The private oracle is
an independent algebraically reduced expression, checked against the service
implementation. Five settings per mode produce 20 cases. No hidden mechanism
or coefficients change after calibration.

Author-side identifiability witness: an X-to-Y mechanism with X=-1.2 U+0.6375
and Y=(4/3)X-0.1 has identical passive observations but different clamp
responses. A four-measurement systematic identification baseline solves both
mechanisms; only the first is used in this task. The untouched passive
predictor passes 15/20, failing Y-clamp effects on X. Query count is unrestricted.

H04 predicts successful passive fitting without testing interventions. If no
discriminating measurement precedes a clamp failure, inspect experiment
selection/premature stopping. If the right measurement was obtained but ignored,
classify evidence integration separately. Score predictive equivalence only.

The inspiration is [CausaLab](https://arxiv.org/abs/2605.26029); its published
results use different models, mechanisms and intervention semantics. This
two-channel hard-clamp pilot does not inherit their failure rates. All
instrument code and observations are synthetic and authored here.
