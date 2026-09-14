# E01: clean pass; retire

One frozen Terra/high diagnostic passed all 36 private inputs. The agent and
verifier completed normally, with reward 1 and no exception. Agent execution
took 150.284386 seconds; total trial time was 206.822559 seconds. Model/CLI:
gpt-5.6-terra / Codex 0.154.0 through Harbor 0.14.0 and Docker.

The submitted solution explicitly reads each frame's actual temporal and echo
values and physical position, sorts the position's projection onto the slice
normal, and assigns each pixel frame into canonical coordinates. It supports
shared/per-frame constant geometry and uses the declared row/column spacing
convention. The trajectory includes public-example tests and a numerical
refinement to group repeated slice positions. Direct metadata reconstruction
is a legitimate solution; following dimension pointers is not itself required.

All 12 ordered encodings and all 24 transformed encodings pass. This does not
support H01's predicted storage-order failure. Do not add private vendor tags,
compression or missing-frame cases to recover difficulty. The result is one
diagnostic, not a claim of universal imaging competence or final qualification.

The model and both v1 controls share checksum
`e660f333099bc0a41fd355f3c48acb5658f7fe9af53fcf39d61d87046ed38f28`.
The full workshop hash still matches the pretrial freeze. Initial pre-freeze
controls used different authored/comment trees and remain separately recorded;
they are not substituted for the matched v1 pair.

Evidence: [freeze](../../docs/evidence/mr-pilot-freeze.json),
[summary](../../docs/evidence/mr-trial-summary.json),
[raw result](../../runs/mr-terra-high-v1-20260914/mr-frame-association__5L3qSjg/result.json),
[submission](../../runs/mr-terra-high-v1-20260914/mr-frame-association__5L3qSjg/artifacts/app/answer/solution.py),
[trajectory](../../runs/mr-terra-high-v1-20260914/mr-frame-association__5L3qSjg/agent/codex.txt).

Python 3.12 `make check`: artifact gate and 61 offline tests pass. Local static
checks: 21/22; the human-authored final submission README is deliberately
missing. No public upload or final Sol/Opus/adversarial trial occurred.
