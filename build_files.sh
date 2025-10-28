#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "Building project..."

# Install Python dependencies
python -m pip install -r Requirement.txt

# Run Django collectstatic
python manage.py collectstatic --noinput

echo "Build complete."