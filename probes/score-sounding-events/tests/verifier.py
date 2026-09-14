"""Exact multiset event F1; no execution of the submitted JSON artifact."""
from collections import Counter
from fractions import Fraction
import json
from pathlib import Path
import sys


def events(items):
    assert isinstance(items,list),'events must be a list'
    result=Counter()
    for e in items:
        p=e['midi_pitch'];assert isinstance(p,int) and not isinstance(p,bool) and 0<=p<=127
        a=Fraction(e['onset_quarters']);d=Fraction(e['duration_quarters'])
        assert a>=0 and d>0,'invalid onset/duration'
        result[(p,a,d)]+=1
    return result


def compare(gold,answer):
    assert isinstance(answer,list) and len(answer)==len(gold),'one record per excerpt'
    ids=[x['excerpt_id'] for x in answer];assert len(set(ids))==len(ids),'duplicate excerpt'
    assert set(ids)=={x['excerpt_id'] for x in gold},'excerpt IDs'
    by_id={x['excerpt_id']:x for x in answer};scores={};tp=ng=npred=0
    for x in gold:
        g=events(x['events']);p=events(by_id[x['excerpt_id']]['events'])
        hits=sum((g&p).values());gn=sum(g.values());pn=sum(p.values())
        scores[x['excerpt_id']]=dict(f1=2*hits/(gn+pn) if gn+pn else 1,matched=hits,gold=gn,predicted=pn)
        tp+=hits;ng+=gn;npred+=pn
    micro=2*tp/(ng+npred) if ng+npred else 1
    return dict(aggregate_f1=micro,excerpts=scores,accepted=micro>=.98 and all(x['f1']>=.95 for x in scores.values()))


def main():
    try:
        gold=json.loads(Path('/verifier/golden.json').read_text())
        answer=json.loads(Path('/app/answer/events.json').read_text())
        r=compare(gold,answer)
        passed=[k for k,v in r['excerpts'].items() if v['f1']>=.95]
        failures=[f'{k}: F1 {v["f1"]}' for k,v in r['excerpts'].items() if v['f1']<.95]
        if r['aggregate_f1']>=.98:passed.append('aggregate_f1')
        else:failures.append(f'aggregate_f1: {r["aggregate_f1"]}')
        print(json.dumps(dict(passed=passed,failures=failures,metrics=r)))
        return not r['accepted']
    except Exception as e:
        print(json.dumps(dict(passed=[],failures=[f'artifact_schema: {type(e).__name__}: {e}'])))
        return 1


if __name__=='__main__':sys.exit(main())
