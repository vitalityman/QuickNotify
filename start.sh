#!/bin/bash

# QuickNotify Start Script

echo "Starting QuickNotify..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Please run install.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Create required directories
mkdir -p logs backend/logs data

# Start the application
cd backend
echo "Starting Flask application on http://localhost:5000..."
python app.py