# App under test: stripe-samples/accept-a-payment (custom-payment-flow, Python server).
# Stripe keys are runtime-only env vars — never bake them into the image.
FROM python:3.12-slim@sha256:423ed6ab25b1921a477529254bfeeabf5855151dc2c3141699a1bfc852199fbf

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
