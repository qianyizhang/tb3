FROM python:3.12-slim-bookworm
COPY . /verifier/
RUN mkdir -p /app/answer /tests && cp /verifier/test.sh /tests/test.sh && chmod 755 /tests/test.sh
WORKDIR /app
CMD ["/tests/test.sh"]
