"""One fixed play operator. Only the separate instrument service has this file."""
from http.server import BaseHTTPRequestHandler,HTTPServer
import json,math
from pathlib import Path

def measure(commands):
    q=0.;result=[]
    for u in commands:
        q=min(max(q,u-.173),u+.173);result.append(q)
    return result

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def do_GET(self):
        self.send_response(200 if self.path=='/health' else 404);self.end_headers();self.wfile.write(b'ready')
    def do_POST(self):
        if self.path!='/probe':self.send_error(404);return
        try:
            d=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
            c=d['commands'];assert isinstance(c,list) and 1<=len(c)<=200
            c=[float(x) for x in c];assert all(math.isfinite(x) and -1<=x<=1 for x in c)
            result=dict(commands=c,outputs=measure(c))
        except Exception:self.send_error(400,'outside declared command domain');return
        with Path('/data/queries.jsonl').open('a') as f:f.write(json.dumps(result)+'\n')
        print(json.dumps(result),flush=True)
        b=json.dumps(result).encode();self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)

if __name__=='__main__':
    Path('/data').mkdir(exist_ok=True);HTTPServer(('0.0.0.0',8000),Handler).serve_forever()
