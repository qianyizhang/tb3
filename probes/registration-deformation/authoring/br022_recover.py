"""Recover recorded solver text without executing model commands on the host."""
import ast
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'runs/br022-registration-postmortem'
TRACE=ROOT/'runs/br021-deform-2d-terra-high-v1-20260916/deform-2d__YR5xbbH/agent/trajectory.json'


def main():
    dest=OUT/'recovered';assert not dest.exists();dest.mkdir()
    steps={s['step_id']:s for s in json.loads(TRACE.read_text())['steps']}
    def command(n):
        code=steps[n]['tool_calls'][0]['arguments']['input'];start=code.index('tools.exec_command(')+len('tools.exec_command(')
        return json.JSONDecoder().raw_decode(code[start:])[0]['cmd']
    def body(n,filename,append=False):
        marker=f"cat {'>>' if append else '>'} /tmp/{filename} <<'PY'\n"
        cmd=command(n);assert marker in cmd
        return cmd.split(marker,1)[1].split('\nPY',1)[0]+'\n'
    reg=body(12,'reg.py')+body(13,'reg.py',True)
    reg2=body(14,'reg2d.py')
    edits=command(15).split("python - <<'PY'\n",1)[1].split('\nPY',1)[0]
    count=0
    for node in ast.parse(edits).body:
        if isinstance(node,ast.Assign) and isinstance(node.value,ast.Call):
            call=node.value
            if isinstance(call.func,ast.Attribute) and isinstance(call.func.value,ast.Name) and call.func.value.id=='s' and call.func.attr=='replace':
                old,new=[ast.literal_eval(a) for a in call.args];assert old in reg2;reg2=reg2.replace(old,new);count+=1
    assert count==3
    reg2+=body(17,'reg2d.py',True)+body(19,'reg2d.py',True)
    for name,content in [('reg.py',reg),('reg2d.py',reg2)]:
        ast.parse(content);(dest/name).write_text(content)
    receipt={'trajectory_path':str(TRACE.relative_to(ROOT)),'trajectory_sha256':hashlib.sha256(TRACE.read_bytes()).hexdigest(),
        'recovered_through_step':19,'used_steps':[12,13,14,15,17,19],
        'later_steps':'20 and 21 append visualization only; 22 tests other patch radii without replacing the submitted radius-8 coordinates; 23 writes step-19 coordinates.',
        'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in dest.iterdir() if p.is_file()}}
    (OUT/'recovery.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))


if __name__=='__main__':main()
