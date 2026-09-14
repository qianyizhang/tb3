# BR-002/D04 raster review

Original MusicXML and Verovio 5.7.0 / resvg-py 0.5.0 renders produce four clean
PNGs. Only PNGs, an empty JSON template and the contract enter the agent image.
Authoring SVG/MusicXML, generated truth and independent raster transcription
remain outside it. No patient data or copyrighted score is used.

There are two original rhythm/relationship patterns, each in treble and bass:
four artifacts but only two pattern families. Every raster was visually reviewed
and transcribed into a separate MIDI/onset/duration table in validate.py. That
table is compared against the notation-derived truth before freezing. A human
music-editor review has not been performed; no such expertise is claimed.

The fixed-artifact baseline is the independent raster transcription. Targeted
controls split ties, serialize voices and forget accidental scope. Exact F1
implements the disclosed metric, not extra feature gates. Pitches are not graded
by spelling. Model image-tool availability and actual image use must be retained
in the trial evidence; lack of image access is an infrastructure issue.

The source conversation's missing GOLD-GLYPHS tail is completed explicitly in
the BR-002 execution plan. It is needed only if the predeclared split rule fires.
These images test ordinary relation reconstruction; the small output may be easy.
