#!/bin/bash

# Exit on error
set -e

echo "Starting build process..."

# Install Python if not already available
if ! command -v python3 &> /dev/null; then
    echo "Python not found. Installing Python..."
    apt-get update
    apt-get install -y python3 python3-pip
fi

# Set Python alias if python command doesn't exist
if ! command -v python &> /dev/null; then
    alias python=python3
    alias pip=pip3
fi

# Install dependencies
echo "Installing Python dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Build completed successfully!"
