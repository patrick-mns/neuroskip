# Etapa base (compartilhada)
FROM python:3.10-slim AS base

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependências Python
COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# Copiar o resto da aplicação
COPY . .

# Etapa pra API
FROM base AS api
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# Etapa pra Worker
FROM base AS worker
CMD ["celery", "-A", "celery_app.config:celery_app", "worker", "--loglevel=info"]
