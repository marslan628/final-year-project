#!/bin/bash
set -e

# Apply migrations, collect static, then start gunicorn
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# Start Gunicorn
exec gunicorn eMarket.wsgi:application --bind 0.0.0.0:8000 --workers 3
