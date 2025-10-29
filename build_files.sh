#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "Building project..."

# Install Python if not already installed
if ! command -v python3 &> /dev/null; then
    echo "Python not found. Installing Python..."
    apt-get update && apt-get install -y python3 python3-pip
fi

# Set Python alias if python command doesn't exist
if ! command -v python &> /dev/null; then
    alias python=python3
fi

# Install Python dependencies
echo "Installing Python dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

# Install Node.js and npm if needed
if [ -f "package.json" ]; then
    echo "Installing Node.js and npm..."
    curl -fsSL https://deb.nodesource.com/setup_16.x | bash -
    apt-get install -y nodejs
    
    echo "Installing Node.js dependencies..."
    npm install
fi

# Run Django collectstatic
echo "Collecting static files..."
python manage.py collectstatic --noinput
python manage.py collectstatic --noinput

echo "Build complete."