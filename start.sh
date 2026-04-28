#!/bin/bash
# start.sh
# This script starts the Django backend in the background and the Streamlit frontend in the foreground.

# 1. Run database migrations and collect static files
cd /app/backend
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# 2. Automatically create default admin superuser (for Render free tier)
echo "Ensuring default admin user exists..."
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); u = User.objects.filter(username='admin').first(); (u or User.objects.create_superuser('admin', 'admin@example.com', 'adminpassword123')); u = User.objects.get(username='admin'); u.is_tpo = True; u.save()"

# 2.5. Seed demo student data on deploy if requested
if [ "${AUTO_SEED_DEMO:-false}" = "true" ]; then
  DEMO_COUNT=${DEMO_STUDENT_COUNT:-100}
  echo "Attempting to seed demo student data (count=${DEMO_COUNT})..."
  python manage.py generate_students --count="$DEMO_COUNT"
fi

# 3. Start Django Gunicorn server in the background
echo "Starting Django backend..."
gunicorn acroconnect_backend.wsgi:application --bind 127.0.0.1:8000 --workers 3 --daemon

# Wait a moment to ensure backend is up
sleep 3

# 3. Start Streamlit frontend
echo "Starting Streamlit frontend..."
cd /app/frontend
# Render provides the PORT environment variable.
streamlit run app.py --server.port $PORT --server.address 0.0.0.0
