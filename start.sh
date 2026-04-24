#!/bin/bash
# start.sh
# This script starts the Django backend in the background and the Streamlit frontend in the foreground.

# 1. Run database migrations and collect static files
cd /app/backend
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# 2. Start Django Gunicorn server in the background
echo "Starting Django backend..."
gunicorn acroconnect_backend.wsgi:application --bind 127.0.0.1:8000 --workers 3 --daemon

# Wait a moment to ensure backend is up
sleep 3

# 3. Start Streamlit frontend
echo "Starting Streamlit frontend..."
cd /app/frontend
# Render provides the PORT environment variable.
streamlit run app.py --server.port $PORT --server.address 0.0.0.0
