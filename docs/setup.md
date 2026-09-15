# Historical machine setup

Recorded 2026-09-12. These versions and host settings describe the original
execution environment; they are not current installation recommendations.
Start with the [reproduction guide](reproduce.md) for archive inspection.

This workspace uses Python 3.12, Harbor 0.14.0 for trials and Harbor 0.18.0 for validation/review. Both are isolated from global Python. `configs/harbor-*.lock.txt` records resolved dependencies; `configs/upstream-lock.json` pins the TB3 rules and hashes. `bash scripts/bootstrap.sh` recreates these environments and the sparse public upstream checkout.

## Docker on this Mac

Installed using [Colima's Docker instructions](https://github.com/abiosoft/colima#docker) and [Homebrew Compose guidance](https://formulae.brew.sh/formula/docker-compose):

```bash
HOMEBREW_NO_AUTO_UPDATE=1 brew install colima docker docker-compose docker-buildx
colima start --runtime docker --vm-type vz --cpu 4 --memory 8 --disk 40
docker version
docker compose version
docker run --rm hello-world
```

Docker runs inside Colima's native arm64 Linux VM. Docker CLI 29.8.0 talks to Engine 29.5.2; Compose 5.5.1 and Buildx 0.37.0 are registered via `cliPluginsExtraDirs` in `~/.docker/config.json`, preserving existing keys. This is the Docker engine/CLI, with Colima as VM manager. No Docker Desktop application or login service was installed.

Use `colima stop` when finished, and `colima start` to resume. The VM was allocated 4 CPUs, 8 GiB memory, and a 40 GiB data disk. Start/stop affects this Colima runtime, so check `docker ps` before stopping it. Nothing was configured to start automatically at login.

Codex's restricted shell cannot access the Docker socket and may incorrectly report Colima as stopped. Authorized Docker operations need the app's elevated execution path. This is a sandbox boundary, not evidence that installation failed. Do not chmod the socket or weaken host permissions to work around it.

## Compose network repair

The first Harbor Codex setup failed before any model call: a custom bridge had `127.0.0.11` with `NO EXTERNAL NAMESERVERS DEFINED`. The VM had no `/etc/resolv.conf`; Docker's default bridge still worked by falling back to Google's DNS. A custom-network test with explicit `--dns 8.8.8.8` resolved Debian and fetched HTTPS successfully.

Persisted the same tested resolvers in `~/.colima/default/colima.yaml`, then restarted the idle Colima runtime:

```yaml
docker:
  dns: [8.8.8.8, 8.8.4.4]
```

This is host runtime configuration, not a task-specific network exception. The failed Harbor attempt remains an infrastructure error with no completed model trial.

## Codex and subscription authentication

See [codex-repair.md](archive/operations.md#codex-cli-repair) for the repaired global CLI and verification. Keep login credentials out of this repository, logs, image layers and build contexts.

For an early container trial, the assignment's subscription route is:

```bash
.venv/bin/harbor run -p probes/cache-invalidation \
  --agent codex --model openai/gpt-5.6-terra --env docker \
  --ae CODEX_FORCE_AUTH_JSON=1 \
  --ae http_proxy=http://192.168.5.2:10808 \
  --ae https_proxy=http://192.168.5.2:10808 \
  --ae HTTP_PROXY=http://192.168.5.2:10808 \
  --ae HTTPS_PROXY=http://192.168.5.2:10808 \
  --ae NO_PROXY=localhost,127.0.0.1 \
  --ak reasoning_effort=high \
  --n-concurrent 1 --n-attempts 1 \
  -o runs --job-name terra-cache-pilot
```

On this Mac, direct container requests to ChatGPT timed out; the proxy flags above route through the already configured host proxy. `192.168.5.2` is Colima’s host gateway. These are explicit local connectivity settings, not benchmark requirements; omit or replace them on another machine. The proxy-assisted trial reached the model and executed commands.

The installed Harbor adapter resolves the authenticated host `~/.codex/auth.json` at runtime for this flag. No API purchase is necessary for the Codex subscription route. A successful login check alone does not establish model availability inside Harbor; the actual trial does. Do not substitute Terra for final Sol trials.

## Evidence

The [ledger](ledger.md) owns measured outcomes. The [requirements](requirements.md) document owns the frozen acceptance plan and remaining gates. `runs/` contains local raw checks and trajectories; do not upload them before checking for secrets and author/private data. No automatic Harbor Hub upload is enabled.

The checked-in command plan in `docs/evidence/cache-evaluation-plan.sh` includes this Mac's proxy. Regenerate it with `scripts/tb3.py plan --backend docker --agent-proxy http://192.168.5.2:10808 probes/cache-invalidation`. Proxy injection covers Harbor agent runs and rubric exec; `harbor analyze` runs on the host and uses its existing network environment.
