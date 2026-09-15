#!/usr/bin/env python3
import argparse,json,urllib.request
from pathlib import Path

def query(commands):
    req=urllib.request.Request('http://instrument:8000/probe',data=json.dumps(dict(commands=commands)).encode(),headers={'Content-Type':'application/json'})
    with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(req,timeout=10) as response:r=json.load(response)
    with Path('/app/answer/measurements.jsonl').open('a') as f:f.write(json.dumps(r)+'\n')
    return r['outputs']

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['probe']);p.add_argument('--commands',required=True);a=p.parse_args()
    print(json.dumps(dict(outputs=query(json.loads(a.commands)))))
