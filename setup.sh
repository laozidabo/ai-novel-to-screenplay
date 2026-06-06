#!/bin/bash
# One-click setup script for AI Novel to Screenplay tool
# Usage: bash setup.sh

set -e

echo "=== AI Novel to Screenplay - Environment Setup ==="

# Check Python version
echo "[1/4] Checking Python..."
python3 --version

# Create virtual environment
echo "[2/4] Creating virtual environment..."
python3 -m venv venv
echo "Virtual environment created: ./venv"

# Activate and install dependencies
echo "[3/4] Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "Dependencies installed successfully"

# Copy .env.example to .env if not exists
echo "[4/4] Setting up environment config..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo ".env file created from .env.example"
    echo "IMPORTANT: Edit .env and add your DeepSeek API key"
else
    echo ".env file already exists, skipping"
fi

echo ""
echo "=== Setup Complete ==="
echo "To activate the virtual environment: source venv/bin/activate"
echo "To start the application: python app.py"
echo ""
