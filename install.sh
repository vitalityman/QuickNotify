#!/bin/bash

# QuickNotify Installation Script for Linux/macOS

set -e

echo "=========================================="
echo "QuickNotify Installation Script"
echo "=========================================="

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

cd backend
pip install -r requirements.txt
cd ..

# Create required directories
echo "Creating required directories..."
mkdir -p logs data backend/logs

# Create .env file if it doesn't exist
if [ ! -f backend/.env ]; then
    cp .env.example backend/.env 2>/dev/null || true
    echo "Created backend/.env from template"
fi

echo "=========================================="
echo "Installation completed successfully!"
echo "=========================================="
echo ""
echo "To start the application:"
echo "  source venv/bin/activate"
echo "  cd backend"
echo "  python app.py"
echo ""
echo "Then open your browser to http://localhost:5000"
echo "Default credentials: admin / 123456"