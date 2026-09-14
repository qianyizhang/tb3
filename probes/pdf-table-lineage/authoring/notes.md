# H01 — PDF logical table lineage

BR-003, original synthetic materials survey. Author-created prose, values and
graphics; no medical guideline content was copied. `build_fixture.py` retains
the PDF source. The task fixture is the resulting PDF; the generator and truth
are absent from the agent image. All five pages were rendered and inspected.
The survey has two table identities, 12 logical rows, 14 physical row fragments,
seven columns, five physical table envelopes, two split ranges, repeated values,
inherited group labels, local footnote namespaces, and one PDF-rotated page.

`transcribe.py` is a separate authored transcription checked against the visible
pages. Content expectations do not import generator row arrays. Crop envelopes
come from generator geometry and were checked on rendered pages. This is
author verification, not independent radiologist/scientist review.
The text stream is written column-major, which PDF permits; visible reading
order remains conventional. Figures contain clearly labeled illustrative values.
Nothing requires OCR; text extraction and manual transcription are allowed.

The historical crop problem was broader than this table-only deliverable.
Do not claim this snapshot reproduces every historical figure-cropping error.
Human-authored submission sections and final benchmark gates are outstanding.
