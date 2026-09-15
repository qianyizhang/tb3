# Source attribution

CT and anatomical masks derive from Jakob Wasserthal / University Hospital Basel,
TotalSegmentator small dataset v2.0.1, CC BY 4.0:
https://zenodo.org/records/10047263 . Original paper:
https://doi.org/10.1148/ryai.230024 . See DATA-LICENSE.txt.

This derivative research audit resamples source CT/masks to 3 mm, creates new
DICOM objects with synthetic patient metadata and research UIDs, and includes
reviewed annotations and deliberately altered annotations. It is not an
unmodified clinical scan or endorsed clinical product. Detailed per-source
receipts and transformations are retained in the private authoring record.

The full label vocabulary is from TotalSegmentator map_to_binary.py at commit
a0d35d5996a9c096caed4184cededdbf2ede5268, Apache-2.0. See LABEL-LICENSE.txt.
