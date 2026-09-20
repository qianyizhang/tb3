"""Compact read-only progress snapshot."""
import json,time
from pathlib import Path
from run_trials import ROOT,B,job_name
events=B/'recovery-events.jsonl' if (B/'recovery-events.jsonl').exists() else B/'events.jsonl'
rows=[json.loads(s) for s in events.read_text().splitlines()]
print(json.dumps([{k:v for k,v in r.items() if k!='exception'} | {'exception_type':(r.get('exception') or {}).get('exception_type') if isinstance(r.get('exception'),dict) else r.get('exception')} for r in rows[-2:]]))
last=rows[-1]
if last['event']=='start':
    phase=last['phase'];print('elapsed_seconds',round(time.time()-last['time']))
    path=next((ROOT/'runs'/last.get('job',job_name(phase))).glob('*/agent/codex.txt'),None)
    if path:
        items=[]
        for s in path.read_text().splitlines():
            try:r=json.loads(s)
            except:continue
            i=r.get('item',{})
            if r.get('type')=='item.completed':items.append({'type':i.get('type'),'text':i.get('text',i.get('command',i.get('message','')))[:450],'output_tail':i.get('aggregated_output','')[-250:]})
            elif r.get('type')=='error':items.append({'type':'transport_error','text':r.get('message','')[:450]})
        print(json.dumps(items[-2:]))
