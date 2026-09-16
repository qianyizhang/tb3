"""Derive source-world queries solely from public plane geometry, then match 3D."""
import json
from pathlib import Path
import runpy
import sys
import numpy as np

data=Path('/app/data');dest=Path('/tmp/public-3d');dest.mkdir(exist_ok=False)
q=json.loads((data/'queries.json').read_text());g=json.loads((data/'view.json').read_text())
s=np.array(g['slice_to_world']);positions=s[:3,3]+(np.array(q['pixels_uv'])*np.array(g['spacing_xy_mm']))@s[:3,:2].T
for name in ['reference_volume.npz','volume.npz']:(dest/name).symlink_to(data/name)
(dest/'queries.json').write_text(json.dumps({'query_ids':q['query_ids'],'reference_world_mm':positions.tolist()}))
sys.argv=['/baseline.py','--data',str(dest),'--out','/output/points.json','--kind','3d']
runpy.run_path('/baseline.py',run_name='__main__')
