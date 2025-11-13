#!/bin/bash

echo "==================================="
echo "Phone Tracking System - Quick Start"
echo "==================================="
echo ""
echo "⚠️  WARNING: Use only for authorized device tracking"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

echo "✓ Python 3 found"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✓ Dependencies installed"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file..."
    cp .env.example .env
    
    echo "🔑 Generating security keys..."
    python3 scripts/generate_keys.py > temp_keys.txt
    
    # Extract keys and update .env
    SECRET_KEY=$(grep "SECRET_KEY=" temp_keys.txt | head -1)
    JWT_SECRET=$(grep "JWT_SECRET=" temp_keys.txt | head -1)
    ENCRYPTION_KEY=$(grep "ENCRYPTION_KEY=" temp_keys.txt | head-1)
    
    sed -i "s/SECRET_KEY=.*/SECRET_KEY=${SECRET_KEY#*=}/" .env
    sed -i "s/JWT_SECRET=.*/JWT_SECRET=${JWT_SECRET#*=}/" .env
    sed -i "s/ENCRYPTION_KEY=.*/ENCRYPTION_KEY=${ENCRYPTION_KEY#*=}/" .env
    
    rm temp_keys.txt
    echo "✓ .env file created with secure keys"
else
    echo "✓ .env file exists"
fi

# Initialize database
echo "🗄️  Initializing database..."
python3 init_db.py
echo "✓ Database initialized"

echo ""
echo "==================================="
echo "✅ Setup Complete!"
echo "==================================="
echo ""
echo "To start the server:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Run the server: python app.py"
echo ""
echo "The server will be available at: http://localhost:5000"
echo ""
echo "Next steps:"
echo "  - Review and update .env file with your configuration"
echo "  - Get an OpenCellID API key: https://opencellid.org/"
echo "  - Read API_DOCUMENTATION.md for API usage"
echo "  - Build the Android mobile agent (see mobile_agent/README.md)"
echo ""
echo "Important:"
echo "  - Only use for devices with owner consent"
echo "  - Comply with all privacy and tracking laws"
echo "  - Keep security keys confidential"
echo ""
