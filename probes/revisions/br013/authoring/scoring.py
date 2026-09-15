"""Exact identity/correction grading, independent of image rendering."""
def score(answer,key):
    field='corrections' if key['mode']=='audit' else 'assignments'
    if not isinstance(answer,dict) or set(answer)!={field} or not isinstance(answer[field],list):
        return {'passed':False,'error':'Expected exactly one list named '+field}
    seen={}
    for row in answer[field]:
        if not isinstance(row,dict) or set(row)!={'object_id','label'}:
            return {'passed':False,'error':'Malformed row'}
        oid,label=row['object_id'],row['label']
        if not isinstance(oid,str) or not isinstance(label,str) or oid in seen:
            return {'passed':False,'error':'Non-string field or duplicate object_id'}
        seen[oid]=label
    truth=key['truth'];proposed=key.get('proposed',{})
    wanted=({k:v for k,v in truth.items() if proposed[k]!=v} if field=='corrections' else truth)
    missing=sorted(wanted.keys()-seen.keys());extra=sorted(seen.keys()-wanted.keys())
    wrong=sorted(k for k in wanted.keys() & seen.keys() if wanted[k]!=seen[k])
    final={**proposed,**seen} if field=='corrections' else seen
    correct=sum(final.get(k)==v for k,v in truth.items())
    return {'passed':not(missing or extra or wrong),'missing':missing,'extra':extra,'wrong':wrong,
            'identities_correct':correct,'identities_total':len(truth),
            'missed_corrections':len(missing) if field=='corrections' else None,
            'false_repairs':len(extra) if field=='corrections' else None}

def read_json(path):
    import json
    if path.stat().st_size>200000: raise ValueError('Answer exceeds 200KB')
    def unique(pairs):
        out={}
        for k,v in pairs:
            if k in out:raise ValueError('Duplicate JSON key')
            out[k]=v
        return out
    return json.loads(path.read_text(),object_pairs_hook=unique)
