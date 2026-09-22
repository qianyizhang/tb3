# Segment and name ten organs from CT

Segment and name ten organs from CT.

## Value

Tests whether an agent can construct organ boundaries and identities from a complete scan.

## Given

### Original data

One full native CT and a finite ten-organ label dictionary.

### Supplied helpers

Baseline has no masks or pretrained segmenter. The LiteMedSAM condition adds a callable tool and generic skill; the agent chooses prompts.

### Callable tools

Each linked protocol specifies the permitted tools and execution environment.

### Reference-only material

References and permitted access follow each frozen contract. A reader-facing source or illustration is not automatically solver-visible.

## Task specification

Produce a native-grid semantic organ label volume. Follow each protocol's coordinate, identifier and access contract.

## Expected output

Produce a native-grid semantic organ label volume.

## Evaluation

Per-organ semantic and matched geometry Dice; the LiteMedSAM packet changes skill and runtime as well as tool access.

## Conditions

| Condition | Supplied help | Work remaining |
| --- | --- | --- |
| CT only | Full CT and target dictionary; ordinary scientific libraries | Discover, delineate and name organs |
| Callable LiteMedSAM | CT, dictionary, generic skill and callable segmenter | Choose prompts and slices, reconstruct volumes and assign identities |

## Difficulty

The label dictionary specifies targets, but supplies neither locations nor contours. A callable segmenter still requires agent-chosen prompts and semantic assignment.

## Coverage

The experiment index preserves case, contract, assistance and execution boundaries.
An experiment record is not an execution count; grouping does not pool scores.

## Sources

- [CT-only ten-organ segmentation — Astra xhigh](../../experiments/ct-organ-segmentation-astra-xhigh/protocol.md)
- [CT-only ten-organ segmentation — Astra medium](../../experiments/ct-organ-segmentation-astra-medium/protocol.md)
- [CT-only ten-organ segmentation — Sol xhigh](../../experiments/ct-organ-segmentation-sol-xhigh/protocol.md)
- [CT organ segmentation — Astra medium with LiteMedSAM](../../experiments/ct-organ-segmentation-astra-medium-litemedsam/protocol.md)
