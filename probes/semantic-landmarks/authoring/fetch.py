"""Fetch selected public assets; verify pinned hashes, never overwrite data."""
from pathlib import Path
import hashlib,json,urllib.request
ROOT=Path(__file__).resolve().parents[3];B=ROOT/'runs/br036-semantic-landmarks/source'
BASE='https://s3.amazonaws.com/openneuro.org/ds004470/'
SUB='sub-C001_acq-MP2RAGE_run-01'
URLS={
 'PDDCA-1.4.1_part1.zip':'https://www.imagenglab.com/data/pddca/PDDCA-1.4.1_part1.zip',
 'pddca.odt':'https://www.imagenglab.com/data/pddca/pddca.odt',
 'mri-C001.nii.gz':BASE+f'sub-C001/anat/{SUB}_T1w.nii.gz',
 'mri-C001.fcsv':BASE+f'derivatives/afids_groundtruth/sub-C001/anat/{SUB}_space-T1w_desc-groundtruth_afids.fcsv',
 **{f'mri-rater{i}.fcsv':BASE+f'derivatives/afids_rater/sub-C001/anat/{SUB}_space-T1w_desc-rater0{i}_afids.fcsv' for i in range(1,4)}
}
def main():
 pins=json.loads((ROOT/'docs/evidence/br036-curation.json').read_text())['source_sha256'];B.mkdir(parents=True,exist_ok=True)
 for name,url in URLS.items():
  target=B/name
  if not target.exists():
   temporary=B/(name+'.partial');assert not temporary.exists(),'Preserve partial download for review'
   urllib.request.urlretrieve(url,temporary)
   assert hashlib.sha256(temporary.read_bytes()).hexdigest()==pins[name],f'Source drift: {name}'
   temporary.rename(target)
  assert hashlib.sha256(target.read_bytes()).hexdigest()==pins[name],f'Existing source mismatch: {name}'
  print(name,'verified',flush=True)
if __name__=='__main__':main()
