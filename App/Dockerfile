# Use python slim base image compatible with ARM64
FROM --platform=linux/arm64 python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    chromium \
    chromium-driver \
    chromium-sandbox \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN useradd -m myuser && \
    chown -R myuser:myuser /app

# Set environment variables for Chrome
ENV CHROME_BIN=/usr/bin/chromium \
    CHROMEDRIVER_PATH=/usr/bin/chromedriver \
    DISPLAY=:99

# Create directory for templates
RUN mkdir templates && \
    chown -R myuser:myuser /app/templates

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY *.py .
COPY templates/* templates/

# Set ownership of all files to non-root user
RUN chown -R myuser:myuser /app

# Switch to non-root user
USER myuser

# Environment variables with default values
ENV MINIO_ENDPOINT=localhost:9000 \
    MINIO_BUCKET_NAME=screenshots \
    MONGO_URI=mongodb://localhost:27017/

# Expose port
EXPOSE 80

# Create start script
RUN echo '#!/bin/bash\nXvfb :99 -screen 0 1920x1080x16 &\npython main.py' > /app/start.sh && \
    chmod +x /app/start.sh

# Run the application
CMD ["/app/start.sh"]