#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate

# Create initial superuser if it doesn't exist
python manage.py create_superuser

# Setup homepage content
python manage.py setup_homepage

# Setup contact settings
python manage.py setup_contact_settings

# Create sample projects (optional - comment out if you don't want sample data)
python manage.py create_sample_projects