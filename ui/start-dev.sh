#!/bin/bash

# VAC Assessment UI Development Startup Script

echo "🏥 VAC Assessment UI - Starting Development Environment"
echo "======================================================="

# Check if we're in the UI directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: Run this script from the ui/ directory"
    echo "Usage: cd ui && ./start-dev.sh"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js is not installed"
    echo "Please install Node.js 18+ from https://nodejs.org"
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node --version | cut -d 'v' -f 2 | cut -d '.' -f 1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Error: Node.js version 18+ is required (current: $(node --version))"
    echo "Please update Node.js from https://nodejs.org"
    exit 1
fi

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ Error: Failed to install dependencies"
        exit 1
    fi
else
    echo "✅ Dependencies already installed"
fi

# Create .env.local if it doesn't exist
if [ ! -f ".env.local" ]; then
    echo "⚙️  Creating environment configuration..."
    cat > .env.local << EOF
# VAC Assessment UI Environment Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME="VAC Assessment System"
NEXT_PUBLIC_VERSION="1.0.0"
EOF
    echo "✅ Created .env.local with default configuration"
else
    echo "✅ Environment configuration exists"
fi

# Check if API is running
echo "🔍 Checking API connection..."
if curl -s -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ VAC Assessment API is running at http://localhost:8000"
else
    echo "⚠️  Warning: VAC Assessment API is not responding at http://localhost:8000"
    echo "   Make sure to start the backend API first:"
    echo "   cd .. && uvicorn app_simplified.main:app --reload --port 8000"
fi

echo ""
echo "🚀 Starting VAC Assessment UI..."
echo "   Frontend will be available at: http://localhost:3000"
echo "   API should be running at: http://localhost:8000"
echo ""
echo "   Press Ctrl+C to stop the development server"
echo ""

# Start the development server
npm run dev