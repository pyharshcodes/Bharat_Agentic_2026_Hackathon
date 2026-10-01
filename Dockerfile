# Jan-Sahayak AI - Production Container Image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install system dependencies for reportlab font rendering
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libfreetype6-dev \
    libjpeg-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create required directories
RUN mkdir -p /aikart /app/output /app/agent/data /app/static

# Copy project files
COPY . /app

# Ensure output directory has full permissions
RUN chmod -R 777 /app/output /aikart

# Expose port for Hosted API Endpoint (Method 2)
EXPOSE 8000

# Default command for aiKart "Try Me Now" Sandbox (Method 1)
CMD ["python", "run_sandbox.py"]
