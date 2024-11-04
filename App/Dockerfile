FROM --platform=linux/arm64 python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    chromium \
    chromium-driver \
    chromium-sandbox \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m myuser && \
    chown -R myuser:myuser /app


ENV CHROME_BIN=/usr/bin/chromium \
    CHROMEDRIVER_PATH=/usr/bin/chromedriver \
    DISPLAY=:99


RUN mkdir templates && \
    chown -R myuser:myuser /app/templates

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY *.py .
COPY templates/* templates/

RUN chown -R myuser:myuser /app


USER myuser


ENV MINIO_ENDPOINT=localhost:9000 \
    MINIO_BUCKET_NAME=screenshots \
    MONGO_URI=mongodb://localhost:27017/


EXPOSE 80


RUN echo '#!/bin/bash\nXvfb :99 -screen 0 1920x1080x16 &\npython main.py' > /app/start.sh && \
    chmod +x /app/start.sh


CMD ["/app/start.sh"]