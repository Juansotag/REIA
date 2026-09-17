FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Dependencias de sistema para fuentes, gráficos y compilación
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpango-1.0-0 \
    libharfbuzz0b \
    libpangoft2-1.0-0 \
    libffi-dev \
    libjpeg-dev \
    libcairo2 \
    fonts-liberation \
    fontconfig \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalar requerimientos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar aplicación completa
COPY . .

# Exponer puerto para Railway
EXPOSE 8000

CMD ["uvicorn", "app.main.py:app", "--host", "0.0.0.0", "--port", "8000"]
