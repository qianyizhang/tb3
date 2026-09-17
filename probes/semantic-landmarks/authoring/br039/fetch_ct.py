"""Fetch one CT member, streaming bounded HTTP ranges and checking ZIP CRC."""
import sys,json,hashlib,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'probes/revisions/br012/authoring'))
from fetch_verse import RemoteZip
B=ROOT/'runs/br039-ct-landmarks/source/verse';B.mkdir(exist_ok=True)
url='https://s3.bonescreen.de/public/VerSe-complete/dataset-verse20training.zip'
name='dataset-01training/rawdata/sub-verse823/sub-verse823_dir-iso_ct.nii.gz'
remote=RemoteZip(url,B/'_ranges')
with zipfile.ZipFile(remote) as z:
 with z.open(name) as src,(B/'ct.nii.gz').open('wb') as dst:
  total=0
  while data:=src.read(8*1024*1024):
   dst.write(data);total+=len(data)
   print(total,flush=True)
info={'url':url,'member':name,'archive_etag':remote.etag,'bytes':total,'sha256':hashlib.sha256((B/'ct.nii.gz').read_bytes()).hexdigest(),'zip_crc_verified':True,'license':'CC-BY-SA-4.0'}
(B/'receipt.json').write_text(json.dumps(info,indent=2)+'\n')
