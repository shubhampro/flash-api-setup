#!/bin/bash

# FastAPI Multi-Database Project Virtual Environment Setup Script
# This script creates and activates a virtual environment for the project

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.8+ first."
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_success "Found Python $PYTHON_VERSION"
}

# Check if pip is installed
check_pip() {
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 is not installed. Please install pip first."
        exit 1
    fi
    
    print_success "Found pip3"
}

# Create virtual environment
create_venv() {
    if [ -d "venv" ]; then
        print_warning "Virtual environment 'venv' already exists."
        read -p "Do you want to recreate it? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_status "Removing existing virtual environment..."
            rm -rf venv
        else
            print_status "Using existing virtual environment."
            return
        fi
    fi
    
    print_status "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created successfully!"
}

# Activate virtual environment
activate_venv() {
    print_status "Activating virtual environment..."
    
    # Source the activation script
    source venv/bin/activate
    
    # Verify activation
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        print_success "Virtual environment activated!"
        print_status "Python path: $(which python)"
        print_status "Pip path: $(which pip)"
    else
        print_error "Failed to activate virtual environment."
        exit 1
    fi
}

# Install dependencies
install_dependencies() {
    print_status "Installing project dependencies..."
    
    # Upgrade pip first
    pip install --upgrade pip
    
    # Install requirements
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_success "Dependencies installed successfully!"
    else
        print_error "requirements.txt not found!"
        exit 1
    fi
}

# Create .env file if it doesn't exist
setup_env() {
    if [ ! -f ".env" ]; then
        print_status "Creating .env file from template..."
        if [ -f "env.example" ]; then
            cp env.example .env
            print_success ".env file created from env.example"
            print_warning "Please edit .env file with your MySQL database credentials!"
        else
            print_warning "env.example not found. Please create .env file manually."
        fi
    else
        print_status ".env file already exists."
    fi
}

# Display next steps
show_next_steps() {
    echo
    echo "=========================================="
    print_success "Virtual environment setup completed!"
    echo "=========================================="
    echo
    echo "Next steps:"
    echo "1. Edit .env file with your MySQL credentials:"
    echo "   nano .env"
    echo
    echo "2. Set up MySQL databases:"
    echo "   mysql -u root -p"
    echo "   CREATE DATABASE mono_api_main;"
    echo "   CREATE DATABASE mono_api_analytics;"
    echo "   CREATE DATABASE mono_api_logs;"
    echo
    echo "3. Initialize databases:"
    echo "   python -m app.db.init_db"
    echo
    echo "4. Test database connections:"
    echo "   python test_connections.py"
    echo
    echo "5. Run the application:"
    echo "   uvicorn app.main:app --reload"
    echo
    echo "6. Access the API documentation:"
    echo "   http://localhost:8000/api/v1/docs"
    echo
    print_warning "Remember to activate the virtual environment in new terminals:"
    echo "   source venv/bin/activate"
    echo
}

# Main execution
main() {
    echo "🚀 FastAPI Multi-Database Project Setup"
    echo "======================================"
    echo
    
    # Check prerequisites
    check_python
    check_pip
    
    # Setup virtual environment
    create_venv
    activate_venv
    
    # Install dependencies
    install_dependencies
    
    # Setup environment file
    setup_env
    
    # Show next steps
    show_next_steps
}

# Run main function
main "$@" 