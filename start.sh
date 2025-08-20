#!/bin/bash

echo "🚀 Starting FastAPI Multi-App Project Setup..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip first."
    exit 1
fi

echo "✅ Python and pip are available"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Copy config file if .env doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Setting up environment configuration..."
    cp config.env .env
    echo "⚠️  Please edit .env file with your configuration before running the app"
fi

# Initialize database
echo "🗄️  Initializing database..."
python init_db.py

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "To run the application:"
echo "  python run.py"
echo ""
echo "Or use uvicorn directly:"
echo "  uvicorn main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "📖 API Documentation will be available at:"
echo "  http://localhost:8000/docs"
echo ""
echo "🔐 Default admin credentials:"
echo "  Email: admin@example.com"
echo "  Password: admin123"
