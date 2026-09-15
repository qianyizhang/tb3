"""Single controlled vocabulary change to an existing frozen identity task."""
import gzip
import json
import shutil
import tarfile
from common import ROOT,OUT,sha,write,freeze_task

def main():
    old=ROOT/'runs/br013-abdomen/tasks/abdomen-a02';task=OUT/'tasks/abdomen-i01'
    assert not task.exists()
    source_freeze=json.loads((ROOT/'docs/evidence/br013-freeze.json').read_text())
    source=next(t for t in source_freeze['tasks'] if t['task']=='abdomen-a02')
    assert all(sha(old/p)==h for p,h in source['files'].items())
    shutil.copytree(old,task)
    data=OUT/'build/abdomen-i01'
    shutil.copytree(ROOT/'runs/br013-abdomen/build/abdomen-a02',data)
    key=json.loads((task/'tests/expected.json').read_text())
    write(data/'vocabulary.json',sorted(key['truth'].values()))
    instruction=(task/'instruction.md').read_text()
    before='Each label may be used at most once; some vocabulary labels may have no supplied object. Missing vocabulary labels do not imply a missing annotation or disease.'
    after='The vocabulary lists exactly the anatomical classes represented by the supplied objects. Use each label exactly once.'
    assert before in instruction
    (task/'instruction.md').write_text(instruction.replace(before,after))
    cfg=(task/'task.toml').read_text().replace('terminal-bench/abdomen-a02','terminal-bench/abdomen-i01')
    (task/'task.toml').write_text(cfg)
    with (task/'environment/data.tar.gz').open('wb') as f:
        with gzip.GzipFile(fileobj=f,mode='wb',filename='',mtime=0) as gz:
            with tarfile.open(fileobj=gz,mode='w') as tar:
                for p in sorted(data.iterdir()):
                    i=tar.gettarinfo(str(p),p.name);i.mtime=0;i.uid=i.gid=0;i.uname=i.gname=''
                    with p.open('rb') as content:tar.addfile(i,content)
    changed=[p for p,h in source['files'].items() if sha(task/p)!=h]
    assert set(changed)=={'task.toml','instruction.md','environment/data.tar.gz'}
    old_data=ROOT/'runs/br013-abdomen/build/abdomen-a02'
    assert all(sha(p)==sha(old_data/p.name) for p in data.iterdir() if p.name!='vocabulary.json')
    freeze_task(task,{'case':83,'mode':'recognition','object_count':11,'source_task':'BR013-A02',
                      'changed_files':changed,'geometry_ids_render_loader_key_unchanged':True,
                      'removed_vocabulary_labels':['gallbladder','spleen'],
                      'source_freeze_sha256':sha(ROOT/'docs/evidence/br013-freeze.json')})
    print('I01 frozen: same geometry/key/renderer, exactly 11 present labels.')

if __name__=='__main__':main()
