FROM python:3.12-slim-bookworm
RUN pip install --no-cache-dir numpy==2.2.6 scipy==1.15.3 pillow==11.3.0 SimpleITK==2.5.2
WORKDIR /app
COPY data /app/data
COPY SOURCE_NOTICE.md /app/
RUN mkdir -p /app/answer
