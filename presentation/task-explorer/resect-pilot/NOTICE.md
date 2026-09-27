# Retained RESECT pilot teaching views

Images/landmarks: Xiao et al., RESECT (2017), https://doi.org/10.1002/mp.12268,
CC BY 4.0 (DATA-LICENSE.txt). Archive: https://doi.org/10.11582/2017.00004
(the article also cites 10.11582/2016.00003). Sample: MedOtter/RESECT-SEG
revision e86fb37dd93f7a9c64e48952f71410af59b04b9b,
https://huggingface.co/datasets/MedOtter/RESECT-SEG/tree/e86fb37dd93f7a9c64e48952f71410af59b04b9b.
No tumor-mask imagery is distributed in this pack. Selection used mask centroids
and published tags before inference; these are two selected public training points.

geometry.json: new complete native XY previews through each supplied MRI query;
US RAS sections share that same fixed initial centre, 48 mm field, 0.5 mm pixels,
positive-intensity 1st/99th windows, linear interpolation and transparent outside
source support. Pixel origins/directions are NIfTI RAS+ mm. No registration run.

trace.json: actual delivered agent PNG panels, cropped with retained pixel boxes
and reduced to 161 square pixels using Lanczos. The agent independently centred
MRI on the query and US on the candidate, using positive-intensity 1st/99.5th
windows and +R right / +A up in axial views. The prompt-candidate panels span
30 mm. Five adjacent final-candidate slabs span 20 mm, at z offsets -2..+2 mm;
the animation changes displayed section only, not anatomy or candidate coordinates.
Original gold centre crosses are retained. Crosses on noncentral slabs indicate
the projected centre, not a point on that slice. All displayed originals match
trace-delivered image hashes. Correlation peaks are rounded retained step-21
stdout, not a new search, probability or reference agreement.

output.json is the actual retained world-coordinate answer. reference.json is
reader-only target/error data and labeled post-hoc verifier diagnostics. References
remain embedded in the portable HTML: reveal is a presentation boundary, not a
security guarantee. Frozen prompt supplies B [-30,15,15], 0.505444 mm from the
reference, versus returned error 1.130199 mm. Original scores remain unchanged;
unaided recovery, cue causal necessity, generalization and clinical claims are
unsupported. Original nop missed result.json; artifact reward is not physical
success. No new medical/model trial or optimizer is executed by this builder.
