FROM python:3.12-slim-bookworm
RUN pip install --no-cache-dir numpy==2.2.6 scipy==1.15.3 pillow==11.3.0 opencv-python-headless==4.12.0.88 meshio==5.3.5 scikit-image==0.25.2
COPY . /verifier/
RUN mkdir -p /app/answer /tests && cp /verifier/test.sh /tests/test.sh && chmod 755 /tests/test.sh
WORKDIR /app
CMD ["/tests/test.sh"]
