# Local static checks; task + upstream are read-only, raw results go to runs/.
docker run --rm \
  --mount type=bind,src=/Users/zhangqy/pkgs/tb3,dst=/work,readonly \
  --mount type=bind,src=/Users/zhangqy/pkgs/tb3/runs,dst=/evidence \
  -w /work python:3.12-slim-bookworm bash -c \
  'apt-get update -qq && apt-get install -y --no-install-recommends git >/tmp/git-install.log && git config --global --add safe.directory /work/.cache/terminal-bench && python /work/scripts/tb3.py --runs-dir /evidence static /work/probes/cache-invalidation'
