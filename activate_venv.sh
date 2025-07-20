#!/bin/bash

# Simple script to activate the virtual environment

if [ -d "venv" ]; then
    echo "🚀 Activating virtual environment..."
    source venv/bin/activate
    echo "✅ Virtual environment activated!"
    echo "📁 Current Python: $(which python)"
    echo "📦 Current pip: $(which pip)"
    echo ""
    echo "💡 To deactivate, run: deactivate"
    echo "💡 To run the app: uvicorn app.main:app --reload"
else
    echo "❌ Virtual environment not found!"
    echo "💡 Run './setup_venv.sh' to create and setup the virtual environment."
fi 