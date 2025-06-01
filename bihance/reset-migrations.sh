#!/usr/bin/env bash

# Exit on any error 
set -e

# Remove migrations folder (for OUR apps only)
rm -rf applications/migrations
rm -rf availabilities/migrations  
rm -rf companies/migrations
rm -rf employer/migrations
rm -rf files/migrations
rm -rf jobs/migrations
rm -rf message/migrations
rm -rf reviews/migrations
rm -rf users/migrations

# Recreate migrations
python manage.py makemigrations applications availabilities companies employer files jobs message reviews users
python manage.py migrate

# Load some initial data (using Django fixtures)
# TODO in future
