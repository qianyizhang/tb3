FROM python:3.12-slim-bookworm
RUN pip install --no-cache-dir numpy==2.2.6 scipy==1.15.3 nibabel==5.3.2 pillow==11.3.0 matplotlib==3.10.6
WORKDIR /app
COPY data /app/data
COPY view.py /app/view.py
RUN mkdir -p /app/answer
