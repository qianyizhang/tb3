FROM python:3.12-slim-bookworm
RUN pip install --no-cache-dir numpy==2.2.6 pillow==11.3.0
WORKDIR /app
ADD data.tar.gz /app/data/
COPY answer.json /app/answer/answer.json
COPY inspect_scene.py inspect_ct.py SOURCE_NOTICE.md DATA-LICENSE.txt LABEL-LICENSE.txt /app/
