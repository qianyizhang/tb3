"""Read-only CONNECT allowlist for the isolated model client's transport."""
import socket,socketserver,select,json,time
ALLOWED={'chatgpt.com','api.openai.com','auth.openai.com'}
UPSTREAM=('192.168.5.2',10808)
class Handler(socketserver.StreamRequestHandler):
 def handle(self):
  line=self.rfile.readline(8193).decode('ascii','replace').strip();bits=line.split()
  while True:
   h=self.rfile.readline(8193)
   if h in (b'\r\n',b'\n',b''):break
  target=bits[1] if len(bits)==3 else ''
  ok=len(bits)==3 and bits[0]=='CONNECT' and target.endswith(':443') and target[:-4] in ALLOWED
  print(json.dumps({'time':time.time(),'target':target,'allowed':ok}),flush=True)
  if not ok:self.wfile.write(b'HTTP/1.1 403 Forbidden\r\nContent-Length: 0\r\n\r\n');return
  try:
   remote=socket.create_connection(UPSTREAM,timeout=15)
   with remote:
    remote.sendall(('CONNECT '+target+' HTTP/1.1\r\nHost: '+target+'\r\n\r\n').encode());header=b''
    while not header.endswith(b'\r\n\r\n') and len(header)<8192:header+=remote.recv(1)
    if not header.startswith(b'HTTP/1.1 200') and not header.startswith(b'HTTP/1.0 200'):
     self.wfile.write(b'HTTP/1.1 502 Bad Gateway\r\nContent-Length: 0\r\n\r\n');return
    self.wfile.write(b'HTTP/1.1 200 Connection Established\r\n\r\n');self.wfile.flush()
    remote.settimeout(None)
    while True:
     ready,_,_=select.select([self.connection,remote],[],[],300)
     if not ready:return
     for s in ready:
      data=s.recv(65536)
      if not data:return
      (remote if s is self.connection else self.connection).sendall(data)
  except (OSError,ValueError) as e:print(json.dumps({'time':time.time(),'error':type(e).__name__}),flush=True)
class Server(socketserver.ThreadingTCPServer):
 allow_reuse_address=True;daemon_threads=True
Server(('0.0.0.0',3128),Handler).serve_forever()
