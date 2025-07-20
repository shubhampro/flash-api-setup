#!/bin/bash

# FastAPI Multi-Database Project Quick Start Script
# This script sets up everything and runs the application

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

# Check if virtual environment exists
check_venv() {
    if [ ! -d "venv" ]; then
        print_warning "Virtual environment not found. Setting up now..."
        if [ -f "setup_venv.sh" ]; then
            ./setup_venv.sh
        else
            print_error "setup_venv.sh not found!"
            exit 1
        fi
    fi
}

# Activate virtual environment
activate_venv() {
    print_status "Activating virtual environment..."
    source venv/bin/activate
    
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        print_error "Failed to activate virtual environment."
        exit 1
    fi
    
    print_success "Virtual environment activated!"
}

# Check if .env file exists and has MySQL credentials
check_env() {
    if [ ! -f ".env" ]; then
        print_warning ".env file not found. Creating from template..."
        if [ -f "env.example" ]; then
            cp env.example .env
            print_success ".env file created from template"
            print_warning "Please edit .env file with your MySQL credentials before continuing!"
            echo
            echo "Press Enter to open .env file for editing, or Ctrl+C to cancel..."
            read
            if command -v nano &> /dev/null; then
                nano .env
            elif command -v vim &> /dev/null; then
                vim .env
            else
                print_warning "No text editor found. Please edit .env file manually."
            fi
        else
            print_error "env.example not found!"
            exit 1
        fi
    fi
}

# Test database connections
test_connections() {
    print_status "Testing database connections..."
    if python test_connections.py; then
        print_success "Database connections successful!"
    else
        print_error "Database connection test failed!"
        print_warning "Please check your MySQL setup and .env configuration."
        exit 1
    fi
}

# Initialize databases
init_databases() {
    print_status "Initializing databases..."
    if python -m app.db.init_db; then
        print_success "Databases initialized successfully!"
    else
        print_error "Database initialization failed!"
        exit 1
    fi
}

# Run the application
run_app() {
    print_success "🚀 Starting FastAPI application..."
    echo
    echo "=========================================="
    echo "🌐 API Documentation: http://localhost:8000/api/v1/docs"
    echo "📖 ReDoc Documentation: http://localhost:8000/api/v1/redoc"
    echo "🏥 Health Check: http://localhost:8000/health"
    echo "=========================================="
    echo
    print_status "Press Ctrl+C to stop the server"
    echo
    
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
}

# Main execution
main() {
    echo "🚀 FastAPI Multi-Database Project Quick Start"
    echo "============================================="
    echo
    
    # Check and setup virtual environment
    check_venv
    activate_venv
    
    # Check environment configuration
    check_env
    
    # Test database connections
    test_connections
    
    # Initialize databases
    init_databases
    
    # Run the application
    run_app
}

# Run main function
main "$@" 