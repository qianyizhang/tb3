FROM python:3.12-slim-bookworm
RUN pip install --no-cache-dir numpy==2.2.6 scipy==1.15.3 nibabel==5.3.2 pillow==11.3.0 scikit-image==0.25.2 trimesh==4.11.3
COPY . /verifier/
RUN mkdir -p /app/answer /tests && cp /verifier/test.sh /tests/test.sh && chmod 755 /tests/test.sh
WORKDIR /app
CMD ["/tests/test.sh"]
