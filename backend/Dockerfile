FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# Evita prompts interactivos
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Instalar utilidades básicas (curl, build-essential, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["gunicorn", "smartquote.wsgi:application", "--bind", "0.0.0.0:8000"]

