# Presentation design

This document owns the reader-facing principles for the medical workbench. The
records, task briefs, renderer contracts and CSS/code own their concrete fields and
behavior. When a presentation decision changes, update this page and the affected
implementation together. Do not turn this page into a second component specification.

## Reading order

1. **Question and action:** tell the reader what the task asks and why it matters.
2. **Source image and supplied input:** show what the agent would actually receive.
3. **Work and output:** use a short sequence or concrete example to show the action.
4. **Reference reveal:** make the reader request the answer; label its source and
   valid domain. Never imply that a teaching crop or reference was solver-visible.
5. **Scope and evidence:** state the one or two limitations needed to interpret the
   page, then offer methods, files and provenance on demand.

The first read should be concise. A useful detail stays near the image or action it
explains; background qualifications belong in one short **Reading boundary** near
the page heading. Further technical detail belongs in a disclosure or copyable
metadata, not in repeated small-print paragraphs. A limitation that changes the
meaning of a reference overlay stays beside that reveal.

## Language

- English and Simplified Chinese are first-class reading languages. First visit
  follows the browser language; an explicit choice is stored and appears in a
  shareable `?lang=en` or `?lang=zh-CN` URL. The switch must be visible and keyboard
  accessible. Set the document's `lang` attribute to the displayed language.
- Translate page controls and authored reading copy, not IDs, file names, license
  names, units, citations or frozen evidence. Scientific claims in both languages
  must have the same scope. A translation is reviewed as an explanation, not made
  by word substitution.
- Keep a stable source ID and a locale-specific companion for authored briefs.
  The current WSI briefs have both languages; the remaining catalogue is the
  planned full sweep. If a translation is missing, show the source language
  explicitly instead of silently suggesting that it has been translated.
- Preserve language when moving between the overview, Explorer, dataset pages and
  local teaching tours. Exported metadata retains the original source language.

## Visual hierarchy

- Native or source-derived examples lead when available. Conceptual animation may
  explain an action, but it does not replace a readable source image or imply a
  case-specific result. The WSI viewer starts with the input alone; GT appears only
  after an explicit reveal.
- Task Explorer teaching scenes use the Sculpted Atlas direction: warm neutral
  surroundings, matte anatomy, quiet context and one task-relevant focus. The
  action must be visible in the staged scene. Source input stays above the scene
  in the normal reading path; reference images keep their explicit reveal.
- Make one visual point at a time. Separate dense label layers when they represent
  different questions, as with TIGER tissue compartments and cell boxes. A legend
  must match overlay colors and line styles. Show crop position and scale without
  burying the image in coordinates.
- Use a small type scale: body text at least 15 px on desktop and 14 px on narrow
  screens, secondary reading text at least 14 px, and labels at least 13 px.
  Reserve smaller mono text for optional raw metadata. Use one primary text color,
  one secondary text color and semantic accent colors; do not create hierarchy by
  adding more muted shades.
- Reuse shared tokens and components before adding local styles. Standalone tours
  may inline their assets for portability, but should follow this same system.

## Provenance and caveats

The normal reading path names the source and reference status in plain language.
File hashes, raw paths, internal IDs and byte counts stay in a **Copy full metadata**
action or an export. The page-level Reading boundary summarizes selection,
coverage and study status once. A reference-specific restriction remains at the
reveal if omitting it could cause a wrong reading. No display-only simplification
changes frozen task bytes, original outcomes or evidence hashes.

## Change review

Check both languages, input-first/reference-reveal behavior, keyboard and mobile
reading, and a copy of complete provenance. For a new visual, verify it against the
source image and the task's actual output. The [Task Brief rules](task-explorer/RULEBOOK.md)
own the detailed authoring contract; this page owns the presentation principles.
