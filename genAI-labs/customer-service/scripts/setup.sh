#!/bin/bash

# GenAI Customer Service Setup Script
# This script sets up the development environment for the GenAI Customer Service workshop

set -e

echo "🚀 Setting up GenAI Customer Service Development Environment"
echo "============================================================"

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

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Python
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python $PYTHON_VERSION found"
    else
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    
    # Check Node.js
    if command_exists node; then
        NODE_VERSION=$(node --version)
        print_success "Node.js $NODE_VERSION found"
    else
        print_error "Node.js is required but not installed"
        exit 1
    fi
    
    # Check npm
    if command_exists npm; then
        NPM_VERSION=$(npm --version)
        print_success "npm $NPM_VERSION found"
    else
        print_error "npm is required but not installed"
        exit 1
    fi
    
    # Check AWS CLI
    if command_exists aws; then
        AWS_VERSION=$(aws --version | cut -d' ' -f1)
        print_success "$AWS_VERSION found"
    else
        print_warning "AWS CLI not found. Please install it manually"
    fi
    
    # Check Git
    if command_exists git; then
        GIT_VERSION=$(git --version | cut -d' ' -f3)
        print_success "Git $GIT_VERSION found"
    else
        print_error "Git is required but not installed"
        exit 1
    fi
}

# Setup Python environment
setup_python_env() {
    print_status "Setting up Python environment..."
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install Python dependencies
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_success "Python dependencies installed"
    else
        print_warning "requirements.txt not found"
    fi
}

# Setup Node.js environment
setup_node_env() {
    print_status "Setting up Node.js environment..."
    
    # Setup web dashboard
    if [ -d "frontend/web-dashboard" ]; then
        cd frontend/web-dashboard
        if [ ! -d "node_modules" ]; then
            npm install
            print_success "Web dashboard dependencies installed"
        else
            print_warning "Web dashboard dependencies already installed"
        fi
        cd ../..
    fi
    
    # Setup customer portal
    if [ -d "frontend/customer-portal" ]; then
        cd frontend/customer-portal
        if [ ! -d "node_modules" ]; then
            npm install
            print_success "Customer portal dependencies installed"
        else
            print_warning "Customer portal dependencies already installed"
        fi
        cd ../..
    fi
}

# Setup environment configuration
setup_env_config() {
    print_status "Setting up environment configuration..."
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_success "Environment file created from example"
            print_warning "Please edit .env file with your configuration"
        else
            # Create basic .env file
            cat > .env << EOF
# Application
DEBUG=true
ENVIRONMENT=development
SECRET_KEY=your-secret-key-here

# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key

# AI Services
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
BEDROCK_REGION=us-east-1

# Database
MONGODB_URL=mongodb://localhost:27017
REDIS_URL=redis://localhost:6379

# Storage
S3_BUCKET=your-s3-bucket-name
OPENSEARCH_ENDPOINT=your-opensearch-endpoint

# AI Configuration
MAX_TOKENS=2000
TEMPERATURE=0.7
CONFIDENCE_THRESHOLD=0.8
ESCALATION_THRESHOLD=0.6
EOF
            print_success "Basic environment file created"
            print_warning "Please edit .env file with your configuration"
        fi
    else
        print_warning "Environment file already exists"
    fi
}

# Setup AWS CDK
setup_aws_cdk() {
    print_status "Setting up AWS CDK..."
    
    if [ -d "infrastructure/cdk" ]; then
        cd infrastructure/cdk
        
        # Install CDK dependencies
        if [ ! -d "node_modules" ]; then
            npm install
            print_success "CDK dependencies installed"
        else
            print_warning "CDK dependencies already installed"
        fi
        
        # Install Python dependencies for CDK
        if [ -f "requirements.txt" ]; then
            pip install -r requirements.txt
            print_success "CDK Python dependencies installed"
        fi
        
        cd ../..
    fi
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    # Create logs directory
    mkdir -p logs
    
    # Create data directory
    mkdir -p data/sample
    mkdir -p data/fixtures
    
    # Create config directory
    mkdir -p config/environments
    mkdir -p config/secrets
    
    print_success "Directories created"
}

# Setup Docker (optional)
setup_docker() {
    if command_exists docker; then
        print_status "Setting up Docker services..."
        
        # Create docker-compose.yml for local services
        cat > docker-compose.yml << EOF
version: '3.8'

services:
  mongodb:
    image: mongo:latest
    container_name: genai-cs-mongodb
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: password
    volumes:
      - mongodb_data:/data/db

  redis:
    image: redis:latest
    container_name: genai-cs-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  mongodb_data:
  redis_data:
EOF
        print_success "Docker Compose file created"
        print_warning "Run 'docker-compose up -d' to start local services"
    else
        print_warning "Docker not found. Skipping Docker setup"
    fi
}

# Test setup
test_setup() {
    print_status "Testing setup..."
    
    # Test Python environment
    if [ -d "venv" ]; then
        source venv/bin/activate
        python -c "import fastapi, boto3, pydantic; print('Python dependencies OK')" 2>/dev/null && print_success "Python environment test passed" || print_error "Python environment test failed"
    fi
    
    # Test Node.js environment
    if [ -d "frontend/web-dashboard/node_modules" ]; then
        cd frontend/web-dashboard
        npm run type-check >/dev/null 2>&1 && print_success "Web dashboard test passed" || print_warning "Web dashboard test failed (this is normal if TypeScript files are not complete)"
        cd ../..
    fi
}

# Main setup function
main() {
    echo "Starting setup process..."
    echo ""
    
    check_prerequisites
    echo ""
    
    setup_python_env
    echo ""
    
    setup_node_env
    echo ""
    
    setup_env_config
    echo ""
    
    setup_aws_cdk
    echo ""
    
    create_directories
    echo ""
    
    setup_docker
    echo ""
    
    test_setup
    echo ""
    
    print_success "Setup completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Edit .env file with your AWS credentials and configuration"
    echo "2. Start local services: docker-compose up -d (if using Docker)"
    echo "3. Run backend: cd backend && python main.py"
    echo "4. Run frontend: cd frontend/web-dashboard && npm start"
    echo "5. Follow the workshop guide in docs/workshop/"
    echo ""
    echo "Happy coding! 🚀"
}

# Run main function
main "$@"
