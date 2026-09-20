"""Reopen the local CPR review, starting a loopback-only server if needed."""
from pathlib import Path
import subprocess,sys,time,urllib.request,webbrowser
ROOT=Path(__file__).resolve().parents[5];OUT=ROOT/'runs/br041-image-only-centerline/presentation';URL='http://127.0.0.1:8794/'
def healthy():
 try:
  with urllib.request.urlopen(URL,timeout=1) as r:return b'Coronary tracing review' in r.read(1000)
 except OSError:return False
if not (OUT/'index.html').exists():raise SystemExit('Build presentation/build.py first with .venv-br030/bin/python')
if not healthy():
 with (OUT/'server.log').open('a') as log:subprocess.Popen([sys.executable,'-m','http.server','8794','--bind','127.0.0.1','--directory',str(OUT)],stdout=log,stderr=log,start_new_session=True)
 for _ in range(20):
  if healthy():break
  time.sleep(.2)
 else:raise SystemExit('Could not open port 8794; inspect presentation/server.log')
print(URL);webbrowser.open(URL)
