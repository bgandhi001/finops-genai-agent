#!/bin/bash
# Quick start script for FinOps GenAI Agent

echo "🚀 Starting FinOps GenAI Agent..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Run: python3 -m venv venv"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import streamlit" 2>/dev/null; then
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found"
    echo "Copy .env.example to .env and add your AWS credentials"
    echo ""
fi

# Start the app
echo "✅ Starting Streamlit app..."
echo "🌐 Opening http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop"
echo ""

streamlit run streamlit_app.py
