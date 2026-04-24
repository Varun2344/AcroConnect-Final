FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential libpq-dev curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the entire project
COPY . /app

# Install backend dependencies
RUN pip install --no-cache-dir -r backend/requirements.txt

# Install frontend dependencies
RUN pip install --no-cache-dir -r frontend/requirements.txt

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=acroconnect_backend.settings
ENV API_URL="http://127.0.0.1:8000"

# Make the start script executable
RUN chmod +x start.sh

# Render provides the PORT variable. We will expose it.
EXPOSE $PORT

CMD ["./start.sh"]
