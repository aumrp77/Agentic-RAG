#!/bin/bash

# Start frontend for The Munger Talks
echo "🚀 Starting The Munger Talks Frontend..."
echo "=========================================="

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "📁 Navigating to frontend directory..."
    cd frontend || { echo "❌ Frontend directory not found!"; exit 1; }
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    echo "✅ Dependencies installed!"
fi

echo ""
echo "🌐 Starting development server..."
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo ""
echo "💡 Make sure the backend is running first!"
echo "   Run: python start_backend.py"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=========================================="

# Start the development server
npm run dev
