# F002 annotated-example comparison

Both fresh Astra/medium attempts completed with valid masks, no terminal exception,
unchanged frozen bytes and exact scoring replay. With the F008 example, recorded
macro Dice was 0.50117 versus 0.45423 without it. Tooth identity and canals improved;
pulp declined and whole-tooth geometry changed only slightly. One target and one
attempt each support an exploratory observation, not a causal/population claim.

User authorization and F002 selection:
codex://threads/01a0c3e5-6fb0-7321-a930-a7251047e7ad.
The [fixed protocol](../methods/dental-reference-ablation/README.md) implements
versioned native-axis naming, general annotation/uncertainty rules and separate
geometry/identity/pulp/canal evaluation. Tools and input target are unchanged.

| Measure | No example | F008 example | Difference |
|---|---:|---:|---:|
| Recorded all-label macro Dice | 0.454 | 0.501 | +0.047 |
| Whole-tooth geometry Dice | 0.778 | 0.789 | +0.010 |
| Correctly identified GT-tooth recall | 0.773 | 0.864 | +0.091 |
| FDI correct among detected teeth | 0.895 | 0.950 | +0.055 |
| Tooth-tissue macro Dice | 0.605 | 0.716 | +0.110 |
| Pulp macro Dice | 0.338 | 0.315 | -0.023 |
| Main-canal macro Dice | 0.112 | 0.196 | +0.085 |
| Small-canal macro Dice | 0.001 | 0.127 | +0.126 |
| Jawbone macro Dice | 0.810 | 0.836 | +0.026 |
| Sinus macro Dice | 0.906 | 0.936 | +0.030 |
| Pharynx Dice | 0.950 | 0.961 | +0.011 |
| Restoration pooled Dice | 0.544 | 0.576 | +0.032 |
| Restoration subtype macro Dice (under review) | 0.153 | 0.199 | +0.046 |


Detected objects 19/22→20/22; correctly identified GT teeth 17/22→19/22. Upper-left
GT 26/27 shifted from predicted 27/28 to matching identities. GT 37 remained predicted 38.
Active labels differ 61→59; a post-hoc common 61-label diagnostic is 0.45423→0.48474,
retained separately from recorded scores. No L/R permutation or output editing.

The reference agent fitted affine and smooth CT registration plus separate jaw
shape alignment, transferred label priors, calibrated pulp rules on the example,
and applied target-specific corrections. Eleven completed commands read the
supplied example. Both agents wrote conventional image-processing programs with
agent-selected coordinates; no pretrained segmentation model ran. A SimpleITK
installation attempt was denied by the proxy and failed, leaving tools unchanged.

Main-canal pooled recall 8.0%→14.4%; small-canal recall remained 8.5% with the example.
Pulp pooled Dice 0.47005→0.36423, precision 39.5%→32.1%, recall 57.9%→42.0%.
Its decline is not simply a numbering effect. Normal-example calibration on true
example tooth masks did not transfer reliably to estimated target masks and
artifact-affected anatomy; no component ablation proves a unique mechanism.

Agent elapsed 22m55s→49m04s; output tokens 33,743→67,173. Raw input tokens include
substantial cache reuse; the evidence record preserves input/cache/uncached totals.
There is no measured dollar cost. Both client transport fallbacks stayed within the
same attempt; no operator inference retry, continuation, extra tool or feedback.

F008 source/QC, input/image hashes, controls, methods, pseudocode, native-coordinate
figures and limitations are retained in the
[full local report](../../../.local/dental-reference-ablation-20260921/comparison/report.md) and
[compact evidence](evidence/dental-reference-example-comparison.json).
[Reproduction code](../methods/dental-reference-ablation/render_comparison.py)
reads saved outputs only. Raw data and generated figures remain local.

F008 has complete 32-tooth/pulp and five-canal label inventory with apparently
uncomplicated sampled views, not clinical certification or exhaustive adjudication.
It has no restoration labels. Acquisition laterality and restoration subtype
consistency remain under review. Results do not prove impossible anatomy, fully
correct GT, or general reference-example effectiveness. Original experiments and
scores remain intact. No more model attempts are authorized by this record.


Follow-up: the [fine-structure mechanism audit](dental-fine-structure-failure-analysis.md)
identifies failed intensity transfer, misplaced canal paths, and harmful prior
clipping. It also adds a specific unresolved occupied-pulp annotation convention;
the earlier general rule clarification does not adjudicate that edge case.
All original measurements above remain unchanged.
