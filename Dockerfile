FROM python:3.12-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl gnupg lsb-release apt-transport-https ca-certificates unzip \
    && rm -rf /var/lib/apt/lists/*

# Install gcloud CLI
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" \
    | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list \
    && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg \
    && apt-get update && apt-get install -y google-cloud-cli \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml uv.lock ./
RUN pip install --upgrade pip \
    && pip install poetry uv \
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi \
    && pip install fastapi uvicorn

# Set uvloop as default
RUN python -c "import asyncio, uvloop; asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())"

# Volumes for code and outputs
VOLUME ["/app/code", "/app/output"]

# Google Cloud credentials
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/service-account.json

EXPOSE 8080

# Run uvicorn server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]
