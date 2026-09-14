# Source attribution and transformations

Derived from Jakob Wasserthal / University Hospital Basel, TotalSegmentator
small dataset v2.0.1, subject s1245. Source record:
https://zenodo.org/records/10047263 ; CC BY 4.0 (DATA-LICENSE.txt).
Original paper: https://doi.org/10.1148/ryai.230024 .

The task samples the source at 3 mm, derives new DICOM CT/SEG objects, assigns
new research UIDs and synthetic patient metadata, and permutes representation
ordering. Task-specific controlled changes are described in the authored
research record. This is a derivative research fixture, not an unmodified
clinical scan, medical device, or endorsement by the source authors.

The 117-name vocabulary is extracted from TotalSegmentator map_to_binary.py
at commit a0d35d5996a9c096caed4184cededdbf2ede5268, Apache-2.0
(LABEL-LICENSE.txt). Local DICOM segment numbers are independently assigned.
