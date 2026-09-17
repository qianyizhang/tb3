"""Author-only native voxel-axis reference versus prediction review."""
from pathlib import Path
import json,html
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[4];B=ROOT/'runs/br038-volume-landmarks';OUT=B/'review';OUT.mkdir(exist_ok=True)
parts=['<!doctype html><meta charset="utf-8"><title>BR-038 full-volume 3D landmarks</title><style>body{font-family:system-ui;background:#f6f7fa;color:#17212b;max-width:1300px;margin:30px auto;padding:0 20px}img{width:100%}article{background:white;padding:20px;margin:20px 0;border:1px solid #ddd;border-radius:8px}table{border-collapse:collapse}td,th{padding:8px;border:1px solid #ddd}</style><h1>Complete volumes → native 3D voxel landmarks</h1><p>All axes show original zero-based array indices. Green is the reference; orange is the model prediction projected into each reference slice. This is an author review, never an agent input. Each panel is centred on the reference and reports the prediction’s off-plane distance.</p>']
for r in json.loads((B/'results.json').read_text())['trials']:
 if r['phase']!='terra-high' or not r.get('score',{}).get('contract_valid'):continue
 case=r['case'];task=B/'tasks'/case;env=task/'environment';a=np.load(env/'volume.npy',mmap_mode='r');g=json.loads((env/'geometry.json').read_text());truth=json.loads((task/'tests/truth.json').read_text());defs=json.loads((env/'landmarks.json').read_text());trial=(ROOT/r['result_path']).parent;ans=json.loads((trial/'artifacts/app/answer/landmarks.json').read_text())['landmarks'];spacing=np.array(g['spacing_ijk_mm']);low,high=g['display_window']
 parts.append(f'<h2>{case}</h2><p>{r["score"]["accepted_count"]}/{r["score"]["total"]} within tolerance; mean {r["score"]["mean_mm"]:.2f} mm; maximum {r["score"]["max_mm"]:.2f} mm.</p>')
 for key,gt in truth['points_ijk'].items():
  gt=np.array(gt);pr=np.array(ans[key]);fig,axs=plt.subplots(1,3,figsize=(15,5),constrained_layout=True)
  for axno,ax in enumerate(axs):
   axes=[i for i in range(3) if i!=axno];u,v=axes;k=int(round(gt[axno]));sl=np.take(a,k,axis=axno).T
   ax.imshow(sl,cmap='gray',vmin=low,vmax=high,origin='lower',extent=[-.5,a.shape[u]-.5,-.5,a.shape[v]-.5],aspect=spacing[v]/spacing[u],interpolation='nearest')
   ax.scatter([gt[u]],[gt[v]],c='lime',marker='+',s=100,label='reference');ax.scatter([pr[u]],[pr[v]],c='darkorange',marker='x',s=70,label='prediction')
   ax.set_xlim(max(-.5,gt[u]-30/spacing[u]),min(a.shape[u]-.5,gt[u]+30/spacing[u]));ax.set_ylim(max(-.5,gt[v]-30/spacing[v]),min(a.shape[v]-.5,gt[v]+30/spacing[v]));ax.set_xlabel(f'{"ijk"[u]} → {g["positive_array_axes_patient_directions"][u]}');ax.set_ylabel(f'{"ijk"[v]} → {g["positive_array_axes_patient_directions"][v]}');ax.set_title(f'{"ijk"[axno]}={k}; prediction off-plane {(pr[axno]-gt[axno])*spacing[axno]:+.2f} mm');ax.grid(alpha=.2)
  label=defs[key].splitlines()[0];err=r['score']['errors_mm'][key];fig.suptitle(f'{case} / {key}: {label} — error {err:.2f} mm');name=f'{case}-{key}.png';fig.savefig(OUT/name,dpi=110);plt.close(fig)
  parts.append(f'<article><h3>{html.escape(key+": "+label)}</h3><p>GT voxel: {np.round(gt,3).tolist()} · Prediction voxel: {np.round(pr,3).tolist()} · Error {err:.3f} mm</p><img loading="lazy" src="{name}"></article>')
(OUT/'index.html').write_text('\n'.join(parts));print('Review written',OUT/'index.html')
