# Reconstruct canonical MRI frame associations

Reconstruct canonical MRI frame associations.

## Value

Makes equivalent MRI encodings produce the same usable multidimensional acquisition.

## Given

### Original data

Decoded pydicom dataset with shuffled frames and functional-group metadata.

### Supplied helpers

Documented synthetic metadata profile, public examples and adapter; geometry can be oblique.

### Callable tools

Each linked protocol specifies the permitted tools and execution environment.

### Reference-only material

References and permitted access follow each frozen contract. A reader-facing source or illustration is not automatically solver-visible.

## Task specification

Repair reconstruct(ds): return pixels [time, echo, slice, row, column], affine_lps, temporal_indices and echo_ms. Follow each protocol's coordinate, identifier and access contract.

## Expected output

Repair reconstruct(ds): return pixels [time, echo, slice, row, column], affine_lps, temporal_indices and echo_ms.

## Evaluation

Exact samples and dimensions, sorted actual time/echo values and physical landmark tolerance; this is importer correctness.

## Difficulty

Descriptor ordinals are not actual time or echo values. Correct sorting must preserve each pixel sample and its physical geometry.

## Coverage

The experiment index preserves case, contract, assistance and execution boundaries.
An experiment record is not an execution count; grouping does not pool scores.

## Sources

- [MRI frame association](../../experiments/mr-frame-association/protocol.md)
