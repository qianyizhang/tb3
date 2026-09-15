"""Geometry-only CT/SEG reader. No anatomical rules or clean reference masks.
Arrays use (slice,row,column). Affine maps [column,row,slice,1] to LPS mm.
"""
from pathlib import Path
import numpy as np
import pydicom
import highdicom as hd

def load_case(directory):
    directory=Path(directory)
    source=[pydicom.dcmread(p) for p in (directory/'ct').glob('*.dcm')]
    if not source: raise ValueError('empty CT series')
    orient=np.array(source[0].ImageOrientationPatient,float)
    normal=np.cross(orient[:3],orient[3:])
    source.sort(key=lambda ds:float(np.sum(np.array(ds.ImagePositionPatient,float)*normal)))
    pixels=np.stack([ds.pixel_array.astype(np.float32)*float(ds.RescaleSlope)+float(ds.RescaleIntercept) for ds in source])
    seg=hd.seg.segread(directory/'seg.dcm')
    descriptions={int(s.SegmentNumber):str(s.SegmentLabel) for s in seg.SegmentSequence}
    numbers=sorted(descriptions)
    labelmap=seg.get_pixels_by_source_instance([ds.SOPInstanceUID for ds in source],segment_numbers=numbers,combine_segments=True,relabel=False,assert_missing_frames_are_empty=True)
    spacing=np.array(source[0].PixelSpacing,float)
    affine=np.eye(4)
    affine[:3,0]=orient[:3]*spacing[1]
    affine[:3,1]=orient[3:]*spacing[0]
    affine[:3,2]=np.array(source[1].ImagePositionPatient,float)-np.array(source[0].ImagePositionPatient,float)
    affine[:3,3]=np.array(source[0].ImagePositionPatient,float)
    return {'ct_hu':pixels,'labels':labelmap,'label_names':descriptions,'affine_lps':affine}
