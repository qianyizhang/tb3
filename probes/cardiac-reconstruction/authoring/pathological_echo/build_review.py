"""Build a local review from frozen submitted surfaces and independently intersected references."""
import json,shutil,os
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from score import volumes,score
from validate import section
ROOT=Path(__file__).resolve().parents[4];HERE=Path(__file__).resolve().parent;B=ROOT/'runs/br034-pathological-echo'
def read(p):return json.loads(p.read_text())
def model(path,lo,idx):
    if not path.exists():return None
    z=np.load(path);p=z['points'];f=z['faces'];v=volumes(p,f);planes=[(1,[0,2]),(0,[1,2]),(2,[0,1])]
    sections=[[np.round(section(x,f,axis,lo[axis]+idx[axis],lo,axes),3).tolist() for x in p] for axis,axes in planes]
    return dict(points=np.round(p,4).tolist(),faces=f.tolist(),volumes=v.tolist(),ef=float(100*(1-v.min()/v.max())),sections=sections)
def main():
    trial=next((ROOT/'runs/br034-pathological-echo-sol-xhigh-v1-20260916').glob('*/result.json')).parent
    answer=trial/'artifacts/app/answer';out=B/'review';out.mkdir(exist_ok=True);cases=[]
    definitions=[('primary','Primary patient · Sol development case',B,answer,'The only patient seen by Sol during the coding attempt.'),
                 ('patient','Hidden patient · unchanged executable',B/'curation/ef48',B/'replays/patient/output','Different patient, 35 frames, no model feedback or code changes.'),
                 ('preserved','Preserved-function control · unchanged executable',B/'curation/preserved-v2',B/'replays/preserved/output','Supplementary negative control added before reviewing model output.'),
                 ('static','Still-input control · same executable',B,B/'replays/static/output','Counterfactual repeated volumes: assess input response, not biological diagnosis.'),
                 ('shift','Phase-shift control · same executable',B,B/'replays/shift/output','Same acquired frames, circularly shifted five positions; initialization index updated.')]
    for key,name,src,pred,note in definitions:
        if key!='primary' and not (B/'replays'/key/'receipt.json').exists():continue
        dst=out/key;dst.mkdir(exist_ok=True);(dst/'images').mkdir(exist_ok=True)
        cal=read(src/'input/geometry.json');lo=np.array(cal['origin_xyz_mm']);idx=np.rint(-lo).astype(int);gt=dict(np.load(src/'reference.npz'));T=len(gt['points'])
        if key=='static':gt['points']=np.repeat(gt['points'][:1],T,axis=0)
        if key=='shift':gt['points']=np.roll(gt['points'],5,axis=0)
        reference=dst/'reference.npz';np.savez_compressed(reference,**gt)
        models=[model(pred/'prediction.npz',lo,idx),model(reference,lo,idx)]
        reference.unlink() # Rebuildable visualization intermediate; canonical reference remains untouched.
        ims=B/'replays'/key/'input/previews' if key in ['static','shift'] else src/'input/previews'
        for p in ims.glob('*.png'):shutil.copy2(p,dst/'images'/p.name)
        summary=read(pred/'summary.json') if (pred/'summary.json').exists() else {}
        receipt=read(B/'replays'/key/'receipt.json') if key!='primary' else read(B/'sol-xhigh-receipt.json')
        grade=receipt.get('grade') or {}
        mpts=np.array(models[1]['points']);center=mpts[0].mean(0);extent=float(max(abs(mpts-center).max(),abs(np.array(models[0]['points'])-center).max() if models[0] else 0))
        case=dict(key=key,name=name,note=note,frames=T,dt=float(np.median(np.diff(cal['timestamps_s']))),models=models,center=center.tolist(),extent=extent,
                  summary=summary,grade=grade,receipt=receipt,
                  pre_assessment=read(answer/'pre_model_assessment.json') if key=='primary' and (answer/'pre_model_assessment.json').exists() else None,
                  diagnostic_note='Functional-reference comparison only; no independent disease etiology.' if key in ['primary','patient','preserved'] else 'Counterfactual control; its functional category is not a patient diagnosis.')
        cases.append(case)
        for fn in ['method.md','summary.json','solve.py']:
            if (pred/fn).exists():shutil.copy2(pred/fn,dst/fn)
        # Independent ES overlay review, with physical contours recomputed above.
        t=int(np.argmin(models[1]['volumes']));sheet=Image.new('RGB',(960,340),'#101623');draw=ImageDraw.Draw(sheet)
        for j in range(3):
            im=Image.open(dst/'images'/f'plane{j+1}_{t:03d}.png').convert('RGB');d=ImageDraw.Draw(im)
            for k,col in [(1,'#f4be62'),(0,'#5ce4cb')]:
                if models[k]:
                    for line in models[k]['sections'][j][t]:d.line(tuple(map(tuple,line)),fill=col,width=1)
            sc=min(310/im.width,310/im.height);im=im.resize((round(im.width*sc),round(im.height*sc)));sheet.paste(im,(j*320+(320-im.width)//2,25));draw.text((j*320+5,6),f'{key} / ref ES frame {t+1} / plane {j+1}',fill='white')
        sheet.save(B/f'{key}-comparison.png')
    primary=cases[0]['grade'];headline=f"Primary reference EF {primary.get('reference_ef_pct',float('nan')):.1f}%; Sol {primary.get('ef_pct',float('nan')):.1f}%. "
    headline+='The original pilot gates passed.' if primary.get('reward')==1 else 'The original pilot gates were not all passed.'
    (out/'data.json').write_text(json.dumps(dict(headline=headline,cases=cases),separators=(',',':')))
    shutil.copy2(HERE/'viewer.html',out/'index.html')
    report=ROOT/'docs/research-rounds/BR-034-results.md'
    if report.exists():shutil.copy2(report,out/'report.md')
    # Scientific static comparison for the evidence archive.
    os.environ.setdefault('MPLCONFIGDIR',str(B/'matplotlib-cache'))
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,3,figsize=(13,3.5),layout='constrained')
    for ax,key in zip(axes,['primary','patient','preserved']):
        c=next((c for c in cases if c['key']==key),None)
        if not c:ax.axis('off');continue
        for k,label,col in [(1,'Clinical reference','#bc8018'),(0,'Sol','#118a84')]:
            m=c['models'][k]
            if m:ax.plot(np.linspace(0,100,c['frames']),m['volumes'],label=f'{label}: EF {m["ef"]:.1f}%',color=col)
        ax.set(title={'primary':'Development patient','patient':'Hidden reduced-function patient','preserved':'Hidden preserved-function control'}[key],xlabel='Acquired beat (%)',ylabel='LV volume (mL)');ax.legend(fontsize=8);ax.grid(alpha=.2)
    fig.savefig(B/'function-comparison.png',dpi=180);fig.savefig(B/'function-comparison.pdf');plt.close(fig)
    print(out)
if __name__=='__main__':main()
