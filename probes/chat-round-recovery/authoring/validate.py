"""Check hand-authored traces plus plausible incorrect controls without Docker."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'environment'),str(ROOT/'tests')]
from driver import run_trace
from checks import check

def evaluate(path):
    failures=[]
    for case in json.loads((ROOT/'tests/cases.json').read_text()):
        try:check(case,run_trace(case['events'],path))
        except Exception:failures.append(case['name'])
    return failures

def main():
    started=time.monotonic()
    assert (ROOT/'environment/driver.py').read_bytes()==(ROOT/'tests/driver.py').read_bytes()
    assert not evaluate(ROOT/'solution')
    controls={'empty_scaffold':evaluate(ROOT/'environment')}
    source=(ROOT/'solution/coordinator.py').read_text()
    mutations={
        'accept_at_deadline':("s['deadline'] <= t","s['deadline'] < t"),
        'ignore_incarnation':("('attempt', 'worker', 'epoch')","('attempt', 'worker')"),
        'global_message_id':("m['room'] == event.get('room')","True"),
        'restart_reuses_attempt':("attempt=s['attempt']+1","attempt=1"),
        'drop_reply_retransmit':("if m['phase'] == 'reply_pending':\n            effects.append", "if m['phase'] == 'reply_pending' and kind == 'result':\n            effects.append"),
        'skip_room_fifo':("if room in blocked or m['phase']", "if m['phase']"),
    }
    with tempfile.TemporaryDirectory() as tmp:
        for name,(old,new) in mutations.items():
            assert old in source,name
            # Syntax is checked independently: mutation rejection must be behavioral.
            variant=source.replace(old,new)
            compile(variant,name,'exec')
            (Path(tmp)/'coordinator.py').write_text(variant)
            controls[name]=evaluate(Path(tmp))
            assert controls[name],name+' survived'
    result={'oracle':{'cases':22,'passed':22},'incorrect_controls':controls,
            'elapsed_seconds':time.monotonic()-started,
            'runtime':'fresh Python process and JSON state per event',
            'model_trials':0}
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
