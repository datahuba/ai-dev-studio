FROM python:3.11-slim

# Variables de entorno para optimizar Python en Docker
ENV PYTHONDONTWRITEBYTECODE=1
# Desactiva el buffer de salida para que los logs de consola aparezcan de inmediato
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependencias del sistema necesarias para compilar paquetes
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]