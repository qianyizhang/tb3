# Diverse, non-security, short-horizon screen

Date: 2026-09-12. User scope: **stay away from security tasks**; seek hard work
with fewer moving parts and a short horizon. No security research or adversarial
trial is authorized by this screen. Existing historical evidence is retained.

Starting denominator: five completed Terra/high passes, no genuine failures,
and two infrastructure-only model attempts. None of the new leads below is a
demonstrated Terra failure. Sources were opened during this survey.

The old HTTP framing/composition lead is explicitly parked in the catalog under
this scope; its provenance and original rationale remain in the historical
record. It is not an active fallback.

## Selection rule

Prefer one small artifact, one conceptual crux, a reference that finishes in
seconds, and an exact or independently justified verifier. Use public semantics
and accept alternative algorithms and equivalent outputs. Do not increase
repository size, dependency friction, random instance size, or hidden edge
cases to force failure. A solver/library that solves the task is a valid pass.

Bound this round to one new ready candidate and one initial Terra/high trial;
repeat once only if a completed failure survives independent reproduction and
fairness review. Keep 1,800 seconds available, Harbor 0.14/Docker for Terra,
Harbor 0.18 for oracle/nop, and the existing explicit subscription proxy. Sol
and Opus remain reserved. Finish and record this slice before selecting another.

## Breadth and ranking

| Rank | Field / task type | Compact task and essential difficulty | Screen decision |
| --- | --- | --- | --- |
| 1 (tested) | Computational topology / constructive certificate | Given two small integer boundary matrices, produce compatible integral bases for their homology quotient. Rational nullspaces can miss primitive cycles; independent diagonalizations lose the shared basis. | **Terra passed all 43 cases; retire snapshot.** Exact verification worked, but this crux did not defeat Terra. |
| 2 | Numerical analysis / focused repair | Stable barycentric interpolation under incremental node insertion. Common weight scale is irrelevant; relative signs and update consistency are essential. | Full historical class API now reproduced with real wheel-provided helpers; design an independent complete oracle next. No numerical model trial yet. |
| 3 | Digital hardware / small RTL construction | A skid buffer must preserve each accepted beat under backpressure and hold stalled output stable. | Good field diversity, but the basic two-entry design is a published short recipe. Park the basic task; a harder version needs an authentic small invariant, not more bus subsystems. |
| 4 | Calendaring / reconstruction | Expand one recurring series across a clock transition and a range exception, preserving original recurrence identifiers. | Narrow candidate; full iCalendar is too broad. Need a precisely delimited RFC subset and independently expected instances before packaging. |
| 5 | Operations research / optimization artifact | Repair a small shift roster with coverage, transitions and boundary-day obligations; accept any schedule meeting a predeclared cost threshold. | Park for now: a standard solver may make the small version routine, while a large optimality search would violate the short-horizon preference. |
| 6 | Astronomy / scientific data reduction | Coadd two overlapping images while preserving coverage, flux convention and background offset. | Park general mosaicking: too many WCS/data-format choices. A small calibrated numerical core may be suitable after checking independent expected output. |
| 7 | Genomics / reconstruction | Phase a short fragment block up to global haplotype exchange, respecting technology-specific evidence. | Park: legitimate biological motivation, but inference ambiguity, stochastic error and input-stack setup need stronger controls than a short pilot. |
| 8 | Geodesy / numerical computation | Compute an ellipsoidal polygon quantity across the antimeridian, respecting orientation and pole enclosure. | Reject plain library-wrapper version as a hardness candidate. GeographicLib already exposes the needed operation; do not prohibit it just to create difficulty. |

## Primary sources and what they support

- [Hatcher, Algebraic Topology, Chapter 2](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf):
  homology as cycles modulo boundaries. The proposed matrix fixture is an
  original algebraic extraction, not a copied benchmark or a reproduced bug.
- [SymPy matrix normal forms](https://docs.sympy.org/latest/modules/matrices/normalforms.html)
  and [1.14.0 implementation](https://raw.githubusercontent.com/sympy/sympy/1.14.0/sympy/polys/matrices/normalforms.py):
  integer normal forms and transformation support exist. Library use is a
  legitimate solution; diagonal entries alone do not certify compatible bases.
- [ZipCPU skid-buffer design](https://zipcpu.com/blog/2019/05/22/skidbuffer.html):
  a small flow-control component with explicit formal properties and a published
  implementation. Supports authenticity but weakens novelty of the basic task.
- [RFC 5545](https://datatracker.ietf.org/doc/html/rfc5545), sections 3.3.10 and
  3.8.4.4: recurrence generation, invalid local times, and recurrence identity
  semantics. A complete calendaring implementation is outside this slice.
- [Nurse rostering benchmark owner](https://www.schedulingbenchmarks.org/nrp/):
  published instances, constraint guidance and verified feasible schedules.
  No benchmark instance or published best solution is copied into this probe.
- [Reproject mosaicking documentation](https://reproject.readthedocs.io/en/stable/mosaicking.html):
  reprojection, coaddition and background matching are distinct operations.
- [HapCUT2 maintained repository](https://github.com/vibansal/HapCUT2):
  fragment-to-haplotype workflow and differing sequencing-technology inputs.
- [GeographicLib documentation](https://geographiclib.sourceforge.io/html/python/):
  ellipsoidal geodesics and polygon-area APIs are available.

The linked sources motivate domains; the hardness rankings are authoring
judgments. No source report is a model outcome. The available pinned checkout
contains review fixtures rather than a complete current task inventory; this
round does not claim complete semantic novelty clearance against current TB3.

## Results

The bounded diagnostic is complete. The task remained unchanged after freeze.

| Attempt | Reward / execution health | Total elapsed | Decision |
| --- | --- | --- | --- |
| Homology oracle, Harbor 0.18 / Docker | 1; no exception, 43/43 cases | 29.951s | Valid reference control |
| Homology nop, Harbor 0.18 / Docker | 0; no exception, 37/43 cases fail | 24.536s | Valid negative control |
| Homology Terra/high, Harbor 0.14 / Docker | **1; no exception, 43/43 cases** | **399.743s** | Retire; no Sol or failure-confirmation run |

All three have the same Harbor task checksum. See the
[freeze](evidence/homology-pilot-freeze.json),
[results](evidence/homology-trial-summary.json),
[commands](evidence/homology-evaluation-plan.sh), and
[trajectory review](../catalog/analyses/homology-calibration.md).
Current denominator is **six valid Terra/high passes, zero genuine failures,
two earlier infrastructure-only attempts**. This survey did not find a
Terra-failed task. Local static sanity is 21/22; the missing human-authored task
README remains deliberate. Repository artifact checks and all 61 offline tests
passed with Python 3.12. Neither result certifies final TB3 readiness.

The homology reference completed all 43 exact certificate cases; the untouched
starter received zero in a matching Docker nop control. Six focused verifier
tests accept equivalent signs and reject nonsaturated cycles, a changed image
lattice, incomplete kernels, incorrect torsion and nondividing factors. This
establishes a usable diagnostic, not model difficulty or final qualification.

The numerical follow-up executed the complete unchanged historical module with
real SciPy helpers and confirmed the same `0.8` versus expected `0.5` error
through construction, incremental insertion, deferred values and a vector axis.
The high-degree constructor fix still works. See the
[full-class result](evidence/barycentric-public-api.json). No numerical model
trial or historical full-package build occurred.

Next recommendation: design the smallest stable interpolation/update oracle,
then decide whether its coupled numerical invariant warrants a diagnostic.
The three-node sign defect by itself is likely too direct; adding a large
SciPy build would not improve the task. Preserve the non-security and
short-horizon selection constraints.

## Subsequent selection decision

The user requested a deeper search for benchmarks containing genuinely hard
problems. The [benchmark-backed survey](research-benchmark-backed.md) supersedes
the interpolation-first recommendation above. This round's inputs, results,
denominators and original recommendation remain historical evidence.
