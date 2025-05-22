FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY .. /app
WORKDIR /app

# Install Python dependencies (basic)
RUN pip install --no-cache-dir flask

EXPOSE 5000
CMD ["python", "api/rest_api.py"]
