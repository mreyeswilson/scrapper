FROM python:slim

ARG TELEGRAM_TOKEN
ARG MONGO_DB_URI

ENV TELEGRAM_TOKEN=${TELEGRAM_TOKEN}
ENV MONGO_DB_URI=${MONGO_DB_URI}

WORKDIR /app

# Actualiza el sistema e instala las dependencias necesarias
RUN apt update && apt install chromium -y

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app/. .
COPY credentials.json .


CMD ["python", "-u", "main.py"]
