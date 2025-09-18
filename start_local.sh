#!/bin/bash
# Local development startup script for VAC Assessment API

echo "🚀 Starting VAC Assessment API - Local Development"
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "app_simplified/main.py" ]; then
    echo "❌ Error: Please run this script from the gwsGPT project root directory"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found"
    echo "💡 Copy .env.example to .env and configure your OpenAI API key"
    exit 1
fi

# Check if virtual environment exists, create if needed
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🐍 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run setup validation
echo "🔍 Checking basic setup..."
# Basic validation without test_setup.py
if [ ! -f "app_simplified/main.py" ]; then
    echo "❌ Error: Main application file not found"
    exit 1
fi

if [ ! -f "app_simplified/data/rules/master2019ToD.json" ]; then
    echo "❌ Error: VAC ToD data file not found"
    exit 1
fi

echo "✅ Basic setup validation passed"

echo ""
echo "🌟 Starting VAC Assessment API server..."
echo "📍 API will be available at: http://localhost:8000"
echo "📖 API documentation at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server with hot reload
python -m uvicorn app_simplified.main:app --reload --port 8000 --host 0.0.0.0
