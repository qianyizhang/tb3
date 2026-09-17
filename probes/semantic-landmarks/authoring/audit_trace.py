"""Summarize observable tool calls and source retrieval flags after trials."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
result={}
for p in sorted((ROOT/'runs').glob('br036-*-terra-high-v1-20260917/*/agent/codex.txt')):
 commands=[];messages=[];tools=[]
 for line in p.read_text().splitlines():
  try:e=json.loads(line)
  except ValueError:continue
  if e.get('type')!='item.completed':continue
  i=e.get('item',{});typ=i.get('type')
  if typ=='command_execution':commands.append(i.get('command',''))
  elif typ=='agent_message':messages.append(i.get('text',''))
  elif typ:tools.append(typ)
 flags=[c for c in commands if any(k in c.lower() for k in ['curl ','wget ','http','urllib','requests.','git clone','aws '])]
 result[p.parts[-4]]={'trace':str(p.relative_to(ROOT)),'command_count':len(commands),'tool_types':sorted(set(tools)),'retrieval_commands_to_review':flags,'public_messages':messages,'commands':commands}
(ROOT/'runs/br036-semantic-landmarks/trace-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:{'command_count':v['command_count'],'retrieval_flags':len(v['retrieval_commands_to_review']),'latest_message':v['public_messages'][-1:] } for k,v in result.items()},indent=2))
