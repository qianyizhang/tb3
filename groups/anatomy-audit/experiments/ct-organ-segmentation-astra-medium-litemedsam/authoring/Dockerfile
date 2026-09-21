FROM tb3-ct-organ-solver:v1
WORKDIR /app
COPY litemedsam /opt/litemedsam
RUN --mount=type=bind,source=wheelhouse,target=/wheels python3 -m venv --system-site-packages /opt/litemedsam/.venv && /opt/litemedsam/.venv/bin/pip install --no-cache-dir --no-index --find-links=/wheels -r /opt/litemedsam/requirements.txt && /opt/litemedsam/.venv/bin/pip freeze > /opt/litemedsam/requirements-resolved.txt
COPY skills/ /skills/
ENV LITEMEDSAM_ROOT=/opt/litemedsam
RUN chmod -R a-w /opt/litemedsam/vendor /opt/litemedsam/weights /skills
