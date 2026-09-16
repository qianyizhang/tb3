"""Retain trace-derived tool provenance without exporting raw commands or secrets."""
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'runs/br026-vessel-repair'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    results=json.loads((BASE/'results.json').read_text());audits=[]
    review_path=ROOT/'docs/evidence/br026-trace-review.json'
    reviews=json.loads(review_path.read_text())['reviews'] if review_path.exists() else []
    for row in results['rows']:
        if row['phase']!='terra-high' or row['execution']!='completed':continue
        calls=[]
        for meta in row['session_files']:
            path=ROOT/meta['path'];assert sha(path)==meta['sha256']
            for line in path.read_text().splitlines():
                try:e=json.loads(line)
                except ValueError:continue
                p=e.get('payload') or {}
                if e.get('type')=='response_item' and p.get('type')=='custom_tool_call':
                    source=p.get('input','')
                    calls.append({'call_id':p.get('call_id'),
                        'input_sha256':hashlib.sha256(source.encode()).hexdigest(),
                        'tools':sorted(set(re.findall(r'tools\.([A-Za-z_0-9]+)',source))),
                        'external_or_private_reference_flag':bool(re.search(r'https?://|/verifier\b|/solution\b|\b(?:curl|wget|urllib|requests)\b',source))})
        flags=[x['call_id'] for x in calls if x['external_or_private_reference_flag']]
        audit={'task':row['task'],'session_files':row['session_files'],'calls':calls,
               'shell_command_batches':sum('exec_command' in x['tools'] for x in calls),
               'image_viewing_batches':sum('view_image' in x['tools'] for x in calls),
               'external_or_private_reference_flags':flags,
               'manual_review_status':'pending',
               'limits':'Tool-call evidence and manual review can establish observed behavior, not prove provider-side identity or exclude unobservable prior knowledge.'}
        matches=[x for x in reviews if x['task']==row['task']]
        assert len(matches)<=1
        if matches:
            review=matches[0]
            assert review['session_sha256s']==[x['sha256'] for x in row['session_files']]
            audit['manual_review_status']='completed'
            audit['manual_review']=review
        audits.append(audit)
    out={'round':'BR-026','audits':audits}
    for p in [BASE/'trace-audit.json',ROOT/'docs/evidence/br026-trace-audit.json']:
        p.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps([{k:v for k,v in a.items() if k not in ['calls','session_files']} for a in audits],indent=2))

if __name__=='__main__':main()
