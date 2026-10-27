# Base image version MUST match the playwright== pin in requirements.txt.
FROM mcr.microsoft.com/playwright/python:v1.64.1-noble

WORKDIR /work

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Args passed to `docker compose run tests <args>` land directly on pytest.
ENTRYPOINT ["pytest"]
