FROM python:3.12-slim-bookworm
RUN pip install --no-cache-dir numpy==2.2.6 scipy==1.15.3 nibabel==5.3.2 pillow==11.3.0 scikit-image==0.25.2 trimesh==4.11.3
WORKDIR /app
COPY data /app/data
COPY SOURCE_NOTICE.md DATA-LICENSE.txt /app/
RUN mkdir -p /app/answer
