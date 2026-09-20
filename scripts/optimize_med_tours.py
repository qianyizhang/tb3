#!/usr/bin/env python3
"""Create lossless WebP frames and gzip data for the player; preserve authoring files."""
from pathlib import Path
import gzip,hashlib,json
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]/'presentation/tours';OUT=ROOT/'web';OUT.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 manifest={'json':{},'images':{},'files':{},'source_bytes':0,'served_bytes':0,'method':'Lossless WebP pixels; gzip level 9 exact JSON bytes; original authoring data retained.'}
 for p in sorted((ROOT/'data').iterdir()):
  if p.suffix=='.json' and p.name!='provenance.json':
   q=OUT/(p.name+'.gz');q.write_bytes(gzip.compress(p.read_bytes(),compresslevel=9,mtime=0));assert gzip.decompress(q.read_bytes())==p.read_bytes();manifest['json'][p.stem]=q.name
  elif p.suffix=='.png':
   q=OUT/(p.stem+'.webp');im=Image.open(p);im.save(q,format='WEBP',lossless=True,method=6,exact=True)
   assert im.convert('RGBA').tobytes()==Image.open(q).convert('RGBA').tobytes()
   manifest['images'][p.name]=q.name
  else:continue
  manifest['source_bytes']+=p.stat().st_size;manifest['served_bytes']+=q.stat().st_size
  manifest['files'][q.name]={'source':p.name,'source_sha256':sha(p),'sha256':sha(q),'bytes':q.stat().st_size}
 (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(f"Lossless player data: {manifest['source_bytes']/1e6:.2f} -> {manifest['served_bytes']/1e6:.2f} MB ({1-manifest['served_bytes']/manifest['source_bytes']:.1%} reduction)")
if __name__=='__main__':main()
