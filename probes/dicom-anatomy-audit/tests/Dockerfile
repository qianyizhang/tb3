FROM python:3.12-slim-bookworm
RUN pip install --no-cache-dir numpy==2.2.6
COPY verifier.py scoring.py expected.json regions.npz /verifier/
COPY test.sh /tests/test.sh
RUN chmod 755 /tests/test.sh && mkdir -p /app/answer
WORKDIR /app
CMD ["/tests/test.sh"]
