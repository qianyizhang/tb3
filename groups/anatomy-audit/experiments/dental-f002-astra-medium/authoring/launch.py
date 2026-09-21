"""Single-dispatch local operator; never retries or gives the solver feedback."""
import json
import fcntl
import os
import re
import shutil
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
BASE = ROOT / '.local/dental-f002-astra-medium'
EXP = ROOT / 'groups/anatomy-audit/experiments/dental-f002-astra-medium'


def now():
    return datetime.now(timezone.utc).isoformat()


def save(state):
    p = BASE / 'operator-state.tmp'
    p.write_text(json.dumps(state, indent=2) + '\n')
    p.replace(BASE / 'operator-state.json')


def main():
    # Shared batch lock prevents concurrent solvers on this small Docker VM.
    batch = ROOT / '.local/dental-followups-20260921'
    lease = (batch / 'solver.lock').open('a')
    fcntl.flock(lease, fcntl.LOCK_EX | fcntl.LOCK_NB)
    queue = json.loads((batch / 'queue.json').read_text())
    if queue.get('no_further_dispatch'):
        raise RuntimeError('The operator has stopped further dispatch')
    this = next(i for i, item in enumerate(queue['order']) if item['experiment'] == EXP.name)
    if queue['order'][this]['state'] != 'ready':
        raise RuntimeError('This experiment is not ready for dispatch')
    if any(item['state'] != 'terminal_reviewed' for item in queue['order'][:this]):
        raise RuntimeError('Earlier experiment requires terminal boundary review')
    # Other user tasks can acquire the same four-CPU / 8-GB Docker VM.
    # Refuse before the dispatch marker if any other Harbor solver is active.
    active = subprocess.run(
        ['docker', 'ps', '-q', '--filter', 'label=com.docker.compose.service=main'],
        capture_output=True, text=True, check=True, timeout=15)
    if active.stdout.strip():
        raise RuntimeError('Shared Docker VM is occupied; leave F002 queued')
    # Persistent dispatch marker deliberately prevents accidental replacement.
    with (BASE / 'dispatch-once.json').open('x') as f:
        json.dump({'created_at': now(), 'operator_pid': os.getpid()}, f)
    before = set((EXP / 'attempts').glob('*.json'))
    cmd = [str(ROOT / '.venv/bin/med'), 'run', 'dental-f002-astra-medium',
           '--diagnostic', '--model', 'openai/gpt-6-astra', '--effort', 'medium',
           '--harbor', str(ROOT / '.venv/bin/harbor')]
    # Docker compose cp preserves host uid/mode. With ALL capabilities dropped,
    # container root cannot read a mode-600 file owned by host uid 501. Keep the
    # host temporary directory private (0700), but allow the copied file to be
    # read inside this single-user container. Never print or retain its contents.
    credentials = tempfile.TemporaryDirectory(prefix='tb3-dental-auth-')
    auth = Path(credentials.name) / 'auth.json'
    shutil.copyfile(Path.home() / '.codex/auth.json', auth)
    auth.chmod(0o644)
    env = dict(os.environ, CODEX_AUTH_JSON_PATH=str(auth))
    log = (BASE / 'operator.log').open('x')
    child = subprocess.Popen(cmd, cwd=ROOT, env=env, stdout=log,
                             stderr=subprocess.STDOUT, start_new_session=True)
    state = {'operator_pid': os.getpid(), 'med_pid': child.pid,
             'med_pgid': child.pid, 'command': cmd, 'started_at': now(),
             'state': 'running', 'automatic_retries': 0}
    save(state)
    capture = None
    capture_file = None
    while child.poll() is None:
        if 'attempt_id' not in state:
            for p in set((EXP / 'attempts').glob('*.json')) - before:
                a = json.loads(p.read_text())
                if a['agent'] == 'codex':
                    state['attempt_id'] = a['id']
                    state['task_digest'] = a['task_digest']
                    state['attempt_path'] = str(ROOT / '.local/attempts' / a['id'])
                    save(state)
        if capture is None and 'attempt_path' in state:
            for trial in (Path(state['attempt_path']) / 'job').glob('task__*'):
                project = re.sub('[^a-z0-9_-]', '-', trial.name.lower())
                result = subprocess.run(
                    ['docker', 'ps', '-q', '--filter',
                     'label=com.docker.compose.project=' + project,
                     '--filter', 'label=com.docker.compose.service=transport'],
                    capture_output=True, text=True, timeout=15)
                cid = result.stdout.strip()
                if result.returncode == 0 and cid and '\n' not in cid:
                    capture_file = (BASE / 'model-transport.log').open('x')
                    capture = subprocess.Popen(['docker', 'logs', '--follow', cid],
                                               stdout=capture_file, stderr=subprocess.STDOUT)
                    state.update(trial_path=str(trial), compose_project=project,
                                 transport_container=cid, transport_capture_pid=capture.pid)
                    save(state)
        time.sleep(3)
    state.update(state='terminal', exit_code=child.returncode, finished_at=now())
    save(state)
    if capture is not None:
        try:
            capture.wait(timeout=15)
        except subprocess.TimeoutExpired:
            capture.terminate()
            capture.wait(timeout=10)
        capture_file.close()
    log.close()
    credentials.cleanup()


if __name__ == '__main__':
    main()
