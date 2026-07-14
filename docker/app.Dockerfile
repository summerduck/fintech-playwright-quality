# App under test: stripe-samples/accept-a-payment (custom-payment-flow, Python server).
# Stripe keys are runtime-only env vars — never bake them into the image.
FROM python:3.14-slim@sha256:d3400aa122fa42cf0af0dbe8ec3091b047eac5c8f7e3539f7135e86d855dc015

RUN apt-get update \
    && apt-get install -y --no-install-recommends git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Bust the clone layer whenever upstream HEAD moves (we intentionally test live HEAD).
ADD https://api.github.com/repos/stripe-samples/accept-a-payment/git/refs/heads/main /tmp/upstream-ref
RUN git clone --depth 1 https://github.com/stripe-samples/accept-a-payment.git /app

WORKDIR /app/custom-payment-flow/server/python
RUN pip install --no-cache-dir -r requirements.txt

RUN useradd --system --uid 10001 appuser
USER appuser

ENV FLASK_APP=server.py
# server.py resolves STATIC_DIR relative to its own file; ../../client/html serves card.html.
ENV STATIC_DIR=../../client/html

EXPOSE 4242

HEALTHCHECK --interval=5s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:4242/card.html')"

CMD ["python", "-m", "flask", "run", "--host", "0.0.0.0", "--port", "4242"]
