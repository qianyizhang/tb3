# Dremel assembly feasibility-probe notes

This AI-authored task is a diagnostic feasibility probe, not a human-authored TB3 submission. It tests the internal boundary after Parquet pages have already been decoded into repetition levels, definition levels, and compact leaf values. It deliberately does not ask an agent to parse whole Parquet files or to use a particular Parquet library.

The contract follows the Parquet nested-encoding description: repetition and definition levels identify repeated and optional path state, while null entries carry no physical value. Apache Arrow's encoding walkthrough was used to check the page/level framing. The hand control is literal; seeded controls independently generate source records and one-way encode them into streams before comparing the candidate output to the known source records. The verifier never imports the reference assembler.

- [Apache Arrow: Parquet encoding, part 2](https://arrow.apache.org/blog/2022/10/08/arrow-parquet-encoding-part-2/)
- [Apache Parquet format](https://github.com/apache/parquet-format)
- [fastparquet issue 373](https://github.com/dask/fastparquet/issues/373), a practical example of ambiguity around nested nulls
- [parquet-java issue 3672](https://github.com/apache/parquet-java/issues/3672), a reminder that a generic row representation can reject valid nested structures

The public result canonicalizes an optional JSON `null` and an absent optional field to an omitted key, because their decoded leaf streams are indistinguishable. Empty repeated fields remain meaningful as `[]`.

## Authoring-control findings

- The first reference draft did not retain child nodes on group metadata, so repeated groups were mistakenly treated as scalar list elements. This was an authoring defect, fixed before controls were run.
- The first draft rejected empty leaf streams when `row_count` was zero. The decoder now permits that well-formed zero-row case. This was an authoring defect, not a model failure.
