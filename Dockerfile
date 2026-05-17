FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies needed for pysha3
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Default: run the full pipeline
CMD ["python", "main.py"]
