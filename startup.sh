#!/bin/bash
# Azure App Service startup command: run migrations, collect static files, start gunicorn.
python manage.py migrate --noinput
python manage.py collectstatic --noinput
gunicorn --bind=0.0.0.0:8000 --timeout 600 config.wsgi
