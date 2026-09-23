# Writing style for summaries and reports

Use this guide for Codex replies, research summaries, findings and other
reader-facing prose in this repository. The aim is a fast first read with enough
source detail to inspect the claim. Task contracts, record schemas and scientific
evidence rules still govern their own content.

## Lead with the answer

- Start with the result or main development in one or two sentences. Name the
  subject, action and consequence; skip a lead-in about what this report will do.
- Organize the rest by reader question or topic, with short, informative headings.
  Put the most consequential section first.
- Give each section a brief takeaway, then the supporting points. Use paragraphs
  for a connected explanation; use bullets for distinct facts, changes or reasons.

## Make points easy to scan

- Begin a bullet with a **specific label.** Follow it with the fact or conclusion.
  Examples: **Result.** **Cost.** **Reference limit.** **Next step.**
- Keep one main point per bullet. Nest details such as component measures or
  affected groups under the point they explain.
- Prefer direct verbs and concrete nouns. Cut repeated setup, throat-clearing,
  stock transitions and sentences that restate the heading.
- Use a small table when readers need to compare the same fields across options,
  conditions or runs. Keep cells short; explain the important difference below.
- Highlight decisive numbers, statuses and contrasts, not whole sentences. A
  reader skimming only headings and labels should still get the story.

## Keep precision while shortening

- Link a source beside the claim it supports. Attribute company, author or model
  claims as claims; distinguish them from independent observations.
- State the denominator, condition and unit with a number when they change its
  meaning. Do not merge different cost, score or timing definitions into one value.
- Separate **Observed**, **Interpretation** and **Unknown** when the boundary
  matters. Put a specific caveat next to its claim; state a shared limitation once.
- Include a consequential counterexample or unresolved alternative, but give it
  its own labeled point instead of burying it in a long paragraph.
- Shorten wording, not evidence. Preserve task inputs, reference boundaries,
  provenance and uncertainty required to support a medical or technical claim.

## Example shape

*Illustrative wording, not a workbench result:*

> **Result.** Run A produced 8 valid outputs from 10 inputs. Run B stopped before
> scoring, so its result is unresolved.
>
> ### What the evidence shows
>
> - **Run A.** 8/10 outputs met the declared format; two failed validation.
> - **Run B.** The runtime timed out before the scorer ran.
> - **Limit.** These conditions do not establish a model-quality comparison.

Before sending, skim the headings and bold labels alone. If they do not convey
the answer, rewrite them. Then remove repeated facts and check that every
material number and qualification remains attached to its evidence.
