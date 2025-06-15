#!/usr/bin/env bash

# Exit on error
set -o errexit


# Install the full dependencies 
# On the deployed side, we are running from the bihance directory!!
pip install -r ".requirements/requirements.txt"

# Convert static asset files
python manage.py collectstatic --no-input

# Apply any outstanding database migrations
python manage.py migrate
