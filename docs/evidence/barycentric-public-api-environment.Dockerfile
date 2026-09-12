FROM python:3.12-slim-bookworm
RUN pip install --no-cache-dir numpy==1.26.4 scipy==1.12.0
WORKDIR /reference
COPY parent_polyint.py patch_polyint.py check.py /reference/
CMD ["python", "check.py"]
