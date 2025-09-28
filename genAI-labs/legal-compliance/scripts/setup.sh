#!/bin/bash

# Legal Compliance AI Platform - Setup Script
# This script sets up the development environment

set -e

echo "🚀 Setting up Legal Compliance AI Platform..."

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

# Check if running on macOS or Linux
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
else
    print_error "Unsupported operating system: $OSTYPE"
    exit 1
fi

print_status "Detected operating system: $OS"

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if Node.js is installed
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js 18+ first."
        exit 1
    fi
    
    # Check Node.js version
    NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -lt 18 ]; then
        print_error "Node.js version 18+ is required. Current version: $(node -v)"
        exit 1
    fi
    
    # Check if Python is installed
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.9+ first."
        exit 1
    fi
    
    # Check Python version
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
    
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 9 ]); then
        print_error "Python 3.9+ is required. Current version: $PYTHON_VERSION"
        exit 1
    fi
    
    # Check if AWS CLI is installed (optional)
    if ! command -v aws &> /dev/null; then
        print_warning "AWS CLI is not installed. This is optional for local development."
    fi
    
    # Check if Terraform is installed (optional)
    if ! command -v terraform &> /dev/null; then
        print_warning "Terraform is not installed. This is optional for local development."
    fi
    
    print_success "Prerequisites check completed"
}

# Create environment file
create_env_file() {
    print_status "Creating environment configuration..."
    
    if [ ! -f .env ]; then
        cat > .env << EOF
# Legal Compliance AI Platform - Environment Configuration

# Application Configuration
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
SECRET_KEY=your-secret-key-change-in-production

# Database Configuration
DATABASE_URL=postgresql://legal_user:legal_password@localhost:5432/legal_compliance
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=
CACHE_TTL=3600

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080

# LLM API Keys (REQUIRED - Get these from respective providers)
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here
GOOGLE_API_KEY=your-google-api-key-here

# AWS Configuration (Optional for local development)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600

# Legal Knowledge Base (Optional)
LEGAL_KNOWLEDGE_BASE_URL=https://api.legal-knowledge-base.com
LEGAL_KNOWLEDGE_BASE_KEY=

# Monitoring (Optional)
SENTRY_DSN=
PROMETHEUS_ENABLED=true

# File Upload
MAX_FILE_SIZE=10485760
ALLOWED_FILE_TYPES=pdf,docx,txt,md

# Legal Context
DEFAULT_JURISDICTION=US
SUPPORTED_JURISDICTIONS=US,UK,EU,DE,FR,IT,ES,CA,AU

# LLM Configuration
DEFAULT_LLM_MODELS=gpt-4-turbo-preview,claude-3-5-sonnet-20241022,gemini-pro

# Response Configuration
MAX_RESPONSE_TOKENS=4000
RESPONSE_TEMPERATURE=0.1
RESPONSE_TOP_P=0.9
EOF
        
        print_success "Environment file created at .env"
        print_warning "Please edit .env file and add your API keys before running the application"
    else
        print_status "Environment file already exists"
    fi
}

# Install backend dependencies
install_backend_deps() {
    print_status "Installing backend dependencies..."
    
    if [ -f backend/requirements.txt ]; then
        cd backend
        python3 -m pip install --upgrade pip
        python3 -m pip install -r requirements.txt
        cd ..
        print_success "Backend dependencies installed"
    else
        print_warning "Backend requirements.txt not found"
    fi
}

# Install frontend dependencies
install_frontend_deps() {
    print_status "Installing frontend dependencies..."
    
    if [ -f frontend/package.json ]; then
        cd frontend
        npm install
        cd ..
        print_success "Frontend dependencies installed"
    else
        print_warning "Frontend package.json not found"
    fi
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p data/{fixtures,sample,knowledge_base}
    mkdir -p logs
    mkdir -p uploads
    mkdir -p tests/{unit,integration,e2e}
    
    print_success "Directories created"
}

# Initialize database
init_database() {
    print_status "Initializing database..."
    
    # Create database initialization script
    cat > scripts/init-db.sql << EOF
-- Legal Compliance AI Platform - Database Initialization

CREATE DATABASE IF NOT EXISTS legal_compliance;
CREATE USER IF NOT EXISTS legal_user WITH PASSWORD 'legal_password';
GRANT ALL PRIVILEGES ON DATABASE legal_compliance TO legal_user;

-- Connect to the database
\c legal_compliance;

-- Create tables (basic structure)
CREATE TABLE IF NOT EXISTS questions (
    id SERIAL PRIMARY KEY,
    question_id VARCHAR(255) UNIQUE NOT NULL,
    question TEXT NOT NULL,
    jurisdiction VARCHAR(10) NOT NULL,
    practice_area VARCHAR(50) NOT NULL,
    context TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS responses (
    id SERIAL PRIMARY KEY,
    question_id VARCHAR(255) REFERENCES questions(question_id),
    model VARCHAR(100) NOT NULL,
    response TEXT NOT NULL,
    confidence DECIMAL(3,2),
    tokens_used INTEGER,
    processing_time DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS comparisons (
    id SERIAL PRIMARY KEY,
    question_id VARCHAR(255) REFERENCES questions(question_id),
    comparison_data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_questions_jurisdiction ON questions(jurisdiction);
CREATE INDEX IF NOT EXISTS idx_questions_practice_area ON questions(practice_area);
CREATE INDEX IF NOT EXISTS idx_questions_created_at ON questions(created_at);
CREATE INDEX IF NOT EXISTS idx_responses_question_id ON responses(question_id);
CREATE INDEX IF NOT EXISTS idx_responses_model ON responses(model);
EOF
    
    print_success "Database initialization script created"
}

# Create Docker Compose override for development
create_docker_compose_dev() {
    print_status "Creating Docker Compose development override..."
    
    cat > docker-compose.override.yml << EOF
version: '3.8'

services:
  postgres:
    ports:
      - "5432:5432"
    environment:
      POSTGRES_DB: legal_compliance
      POSTGRES_USER: legal_user
      POSTGRES_PASSWORD: legal_password
    volumes:
      - postgres_dev_data:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init-db.sql

  redis:
    ports:
      - "6379:6379"
    volumes:
      - redis_dev_data:/data

  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://legal_user:legal_password@postgres:5432/legal_compliance
      - REDIS_URL=redis://redis:6379/0
      - ENVIRONMENT=development
      - LOG_LEVEL=DEBUG
    volumes:
      - ./backend:/app
      - ./data:/app/data
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
      - NODE_ENV=development
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev

volumes:
  postgres_dev_data:
  redis_dev_data:
EOF
    
    print_success "Docker Compose development override created"
}

# Create development scripts
create_dev_scripts() {
    print_status "Creating development scripts..."
    
    # Start development environment
    cat > scripts/dev-start.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting Legal Compliance AI Platform development environment..."
docker-compose up -d postgres redis
echo "⏳ Waiting for services to start..."
sleep 10
echo "✅ Services started. Access the application at:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
EOF
    
    # Stop development environment
    cat > scripts/dev-stop.sh << 'EOF'
#!/bin/bash
echo "🛑 Stopping Legal Compliance AI Platform development environment..."
docker-compose down
echo "✅ Services stopped"
EOF
    
    # View logs
    cat > scripts/dev-logs.sh << 'EOF'
#!/bin/bash
echo "📋 Showing Legal Compliance AI Platform logs..."
docker-compose logs -f
EOF
    
    # Make scripts executable
    chmod +x scripts/dev-start.sh
    chmod +x scripts/dev-stop.sh
    chmod +x scripts/dev-logs.sh
    
    print_success "Development scripts created"
}

# Run tests
run_tests() {
    print_status "Running tests..."
    
    # Backend tests
    if [ -f backend/requirements.txt ]; then
        cd backend
        python3 -m pytest tests/ -v --tb=short
        cd ..
        print_success "Backend tests completed"
    fi
    
    # Frontend tests
    if [ -f frontend/package.json ]; then
        cd frontend
        npm test -- --passWithNoTests
        cd ..
        print_success "Frontend tests completed"
    fi
}

# Main setup function
main() {
    print_status "Starting Legal Compliance AI Platform setup..."
    
    check_prerequisites
    create_env_file
    install_backend_deps
    install_frontend_deps
    create_directories
    init_database
    create_docker_compose_dev
    create_dev_scripts
    
    print_success "Setup completed successfully! 🎉"
    
    echo ""
    print_status "Next steps:"
    echo "1. Edit .env file and add your API keys:"
    echo "   - OPENAI_API_KEY"
    echo "   - ANTHROPIC_API_KEY"
    echo "   - GOOGLE_API_KEY"
    echo ""
    echo "2. Start the development environment:"
    echo "   ./scripts/dev-start.sh"
    echo ""
    echo "3. Access the application:"
    echo "   Frontend: http://localhost:3000"
    echo "   Backend:  http://localhost:8000"
    echo "   API Docs: http://localhost:8000/docs"
    echo ""
    echo "4. Run tests:"
    echo "   ./scripts/setup.sh --test"
    echo ""
    print_warning "Don't forget to add your API keys to the .env file!"
}

# Handle command line arguments
if [ "$1" = "--test" ]; then
    run_tests
elif [ "$1" = "--help" ]; then
    echo "Legal Compliance AI Platform Setup Script"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --test    Run tests after setup"
    echo "  --help    Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0              # Full setup"
    echo "  $0 --test       # Setup and run tests"
else
    main
fi
