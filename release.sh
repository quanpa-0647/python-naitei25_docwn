#!/bin/bash

# Deployment script for Heroku
echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Deployment preparation complete!"
