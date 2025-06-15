#!/usr/bin/env bash

# Exit on error
set -o errexit


# Resolve directories 
SCRIPT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${SCRIPT_DIR}/.." 
REQ_DIR="${PROJECT_ROOT}/.requirements" 


# Install the full dependencies 
pip install -r "../.requirements/requirements.txt"

# Convert static asset files
python manage.py collectstatic --no-input

# Apply any outstanding database migrations
python manage.py migrate
