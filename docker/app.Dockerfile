# App under test: stripe-samples/accept-a-payment (custom-payment-flow, Python server).
# Stripe keys are runtime-only env vars — never bake them into the image.
FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN git clone --depth 1 https://github.com/stripe-samples/accept-a-payment.git /app

WORKDIR /app/custom-payment-flow/server/python
RUN pip install --no-cache-dir -r requirements.txt

ENV FLASK_APP=server.py
# server.py resolves STATIC_DIR relative to its own file; ../../client/html serves card.html.
ENV STATIC_DIR=../../client/html

EXPOSE 4242

HEALTHCHECK --interval=2s --timeout=5s --retries=30 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:4242/card.html')"

CMD ["python", "-m", "flask", "run", "--host", "0.0.0.0", "--port", "4242"]
