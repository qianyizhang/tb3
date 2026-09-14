# E04: clean pass; retire

Terra/high passed all 20 private settings with reward 1, normal completion and
no exception in 48.681578 agent seconds. The model and oracle/nop controls
share Harbor checksum
`3f70b079d68450b56dbda59958cc2a5f39e2b230bbe3b2ddcd28f784ac4a803d`;
the pretrial workshop hash is unchanged.

The 42 server-recorded measurements include passive readings, both individual
clamp directions and simultaneous clamps. At drive zero, changing Y from
zero to two changes X from -0.3 to 2.2, while changing X leaves Y at 0.75.
The delivered predictor uses Y = -1.6 U + 0.75 and X = 0.8 U + 1.25 Y - 0.3,
replacing the corresponding equation when clamped. The trajectory also
checks 24 further random settings. H04 is not supported: the agent directly
tested the proposed causal distinction. Retire without adding noise, query
limits or a changing instrument.

The service implementation stayed outside the agent image, and the verifier
used independently authored equations with no live instrument. The oracle
calibrated from four measurements; nop failed all five Y-only clamp settings.
The counterfactual author control shows two directions fitting the same
passive sweep, so the public observations alone do not identify this family.

Evidence: [freeze](../../docs/evidence/instrument-pilot-freeze.json),
[summary and query counts](../../docs/evidence/instrument-trial-summary.json),
[controls](../../docs/evidence/instrument-author-controls.json).
Raw query logs and submitted code remain local at the summary's trial path.
This is the tenth valid local Terra pass. Final submission gates remain open.
