"""Restore an interrupted agent's own state; never upload reviewer feedback or GT."""
from pathlib import Path
import hashlib,json,shlex
from harbor.agents.installed.codex import Codex
ROOT=Path(__file__).resolve().parents[5]
B=ROOT/'runs/br042-all-vessels-v4-6h-resume1'
SESSION='01a0beb5-c558-7ec2-b58b-d92f1e6818f2'
NOTICE='''The prior process was interrupted by a transport failure. Resume the original task from your saved conversation and work. Your /app/answer files are restored unchanged. /app/work/image.npy and vesselness.npz have been regenerated using the original CTA and your saved prepare.py; other temporary caches and review images were not retained and may need regeneration. No evaluation feedback is provided. You have a fresh allowance of up to 21600 seconds for this continuation, including computation, inspection and reporting. Finish and submit when ready; there is no need to consume the allowance. Keep a current valid answer and method/inventory saved as you work.'''
class ResumedCodex(Codex):
 async def setup(self,environment):
  manifest=json.loads((B/'restore-manifest.json').read_text())
  for rel,digest in manifest['restore_files'].items():
   assert hashlib.sha256((B/rel).read_bytes()).hexdigest()==digest
  await super().setup(environment)
  await self.exec_as_agent(environment,'mkdir -p /app/work /app/answer /tmp/codex-home/sessions')
  await environment.upload_dir(B/'restore/answer','/app/answer')
  await environment.upload_dir(B/'restore/sessions','/tmp/codex-home/sessions')
  await self.exec_as_agent(environment,"python -c \"import nibabel as n,numpy as np; np.save('/app/work/image.npy',n.load('/app/data/image.nii.gz').get_fdata(dtype=np.float32))\" && python /app/answer/prepare.py",timeout_sec=1800)
  expected={k.removeprefix('restore/answer/'):v for k,v in manifest['restore_files'].items() if k.startswith('restore/answer/')}
  code="import hashlib,json;from pathlib import Path; expected="+repr(expected)+"; actual={str(p.relative_to('/app/answer')):hashlib.sha256(p.read_bytes()).hexdigest() for p in Path('/app/answer').rglob('*') if p.is_file()};assert actual==expected;print('Restored answer hashes exact')"
  await self.exec_as_agent(environment,'python -c '+shlex.quote(code))
 async def run(self,instruction,environment,context):
  await super().run(NOTICE,environment,context)
 async def exec_as_agent(self,environment,command,env=None,cwd=None,timeout_sec=None):
  if 'codex exec ' in command:
   command=command.replace('codex exec ',f'codex exec resume {SESSION} ',1)
  return await super().exec_as_agent(environment,command,env=env,cwd=cwd,timeout_sec=timeout_sec)
