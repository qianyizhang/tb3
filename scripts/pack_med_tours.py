#!/usr/bin/env python3
"""Package current English compact media, attribution and reproducibility metadata."""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];T=ROOT/'presentation/tours';E=T/'exports'
def main():
 manifest=json.loads((E/'manifest.json').read_text());files=[]
 for item in manifest['videos']:
  p=E/item['file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256'];files.append(p)
 stories=json.loads((T/'storyboards.json').read_text());ext={'jpeg':'jpg','webp':'webp','png':'png'}[manifest['settings']['stills']]
 for name,s in stories.items():
  files += [E/(name+'.vtt'),E/(name+'.srt')]
  for fmt in ['landscape','portrait']:
   files += [E/f'{name}-{fmt}-step{i+1}.{ext}' for i in range(len(s['steps']))]
 files += [E/'manifest.json',E/'resolved-storyboards.json',T/'README.md',T/'TOOL.md',T/'social-copy.md',T/'storyboards.json',T/'validation.json',T/'compression-report.json',T/'data/provenance.json']
 with zipfile.ZipFile(E/'social-pack.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in sorted(set(files)):assert p.is_file(),p;z.write(p,p.relative_to(T))
  z.write(ROOT/'runs/br039-ct-landmarks/tasks/ct-full/environment/SOURCE_NOTICE.md','licenses/VerSe-SOURCE_NOTICE.md')
  z.write(ROOT/'runs/br016-aneurysm/tasks/aneurysm-n02-v2/environment/SOURCE_NOTICE.md','licenses/OpenNeuro-ds003949-SOURCE_NOTICE.md')
 print('Packed',len(set(files))+2,'files;',round((E/'social-pack.zip').stat().st_size/1e6,2),'MB')
if __name__=='__main__':main()
