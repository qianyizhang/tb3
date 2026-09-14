# E05 author record

This is an original physical-label normalization pilot inspired by the
brainstorm's reserve and dpdata task 003. The source Sol/max trace completed
normally but missed three private tests involving stress_sign, force-column
parsing, direct API and writer round trips. It does not establish difficulty
of this compact conversion function. The requested reserve receives one cheap
diagnostic after E04, without claiming inherited model failure.

References: [extxyz](https://github.com/libAtoms/extxyz),
[dpdata issue 973](https://github.com/deepmodeling/dpdata/issues/973),
[QUIP stress convention](https://github.com/libAtoms/QUIP/discussions/272).
All code and fixtures are original. No upstream source fixture is copied.

The public contract fixes Voigt order, virial sign, units, laboratory basis and
cell volume. A working parser and an installed extxyz parser are available.
This deliberately removes schema exploration and data-pipeline bookkeeping.
The deliverable is the physical conversion alone. Libraries, direct formulas
and all equivalent implementations are accepted. A transpose of a symmetric
tensor cannot demonstrate an error and is an accepted control.

Six canonical cells, two physical rotations and three encodings produce 36
cases in one model trial. The tensor and scalar-triple-product volume exist
before serialization. The independent extxyz reader and direct reference must
both recover all canonical tensors. Controls change Voigt order, virial sign,
use edge-length products for skew-cell volume, or retain signed volume for a
left-handed cell. Nonzero unequal shear terms and skew cells distinguish those
physical errors. The task excludes malformed syntax, asymmetric inputs and
conflicting labels; it is not a general extxyz parser compliance test.

H05 needs a normally completed, independently reproduced failure whose
submitted conversion changes physical meaning while preserving shape. A clean
pass retires this task; no additional format or tensor convention is appended.

The initial Linux build could not obtain extxyz 0.3.0. Before any model trial,
both environments were aligned to 0.4.5 and the controls repeated. This is
a pre-freeze packaging issue, not a model attempt or failure.
