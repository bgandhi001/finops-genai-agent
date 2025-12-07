#!/bin/bash
# Setup script for FinOps GenAI Agent
# This script automates the virtual environment setup

set -e  # Exit on error

echo "🚀 FinOps GenAI Agent - Setup Script"
echo "===================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✅ Found Python $PYTHON_VERSION"
echo ""

# Create virtual environment
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists."
    read -p "Do you want to recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  Removing old virtual environment..."
        rm -rf venv
    else
        echo "ℹ️  Using existing virtual environment."
    fi
fi

if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created!"
fi

echo ""

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt --quiet

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Configure AWS credentials:"
echo "   aws configure"
echo "   OR"
echo "   cp .env.example .env  # and edit with your credentials"
echo ""
echo "3. Setup AWS infrastructure:"
echo "   python setup_aws.py"
echo ""
echo "4. Run the app:"
echo "   streamlit run streamlit_app.py"
echo ""
echo "5. Generate sample data (optional):"
echo "   python generate_sample_data.py"
echo ""
echo "📚 Documentation:"
echo "   - Quick Start: QUICKSTART.md"
echo "   - Virtual Env Guide: VIRTUAL_ENV_GUIDE.md"
echo "   - Full Docs: README_STREAMLIT.md"
echo ""
