# TIGER cell compartment context — Sol 6 xhigh

## Question and method

How does `openai/gpt-6-sol` at xhigh locate immune cells and assign tissue
compartments across the same three fixed `114S` ROIs, with and without the
official tissue masks? The user accepted both conditions and disclosed tissue
semantics on 2026-09-23. Run one 3600-second diagnostic attempt per condition,
sequentially, with no automatic retry. Use 4 CPUs, 12 GiB, no GPU and the pinned
isolated transport route. Each exact task needs oracle pass and no-op contract
failure. This changed contract is separate from the [Astra diagnostic](../wsi-tiger-context-astra-medium/protocol.md).

## Inputs and reference

Both conditions receive the three source ROI PNGs; the paired condition also
receives the official pixel masks. The prompt defines all tissue codes 0–7,
including code 6 as **inflamed tumor-associated stroma with dense lymphocytes**,
which is distinct from a generic inflammatory region. The solver marks merged
lymphocyte/plasma-cell centers and a code at each point. The private evaluator
matches centers one-to-one within 20 ROI pixels, then reports compartment
agreement both at the source-cell center and at the submitted center. It also
reports pairs within 20 pixels of a mask boundary; this boundary stratum is a
diagnostic, not an exclusion from the main source-center measure. See the
[official TIGER data definitions](https://tiger.grand-challenge.org/Data/).

## Findings and limits

Pending model attempts. Fixed ROIs from one public slide do not measure
autonomous WSI search or a clinical sTIL score. One paired run per condition
cannot isolate a causal assistance effect from run variation. The supplied
mask directly carries the reference tissue labels, so its result measures
assisted attribution rather than inference from H&E alone.
