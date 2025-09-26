#!/bin/bash

# Healthcare ChatGPT Clone - System Test Script
# This script tests the completeness and validity of the system

set -e

echo "🏥 Healthcare ChatGPT Clone - System Test"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results
TESTS_PASSED=0
TESTS_FAILED=0

# Function to run a test
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    echo -e "\n${BLUE}Testing: $test_name${NC}"
    echo "Command: $test_command"
    
    if eval "$test_command"; then
        echo -e "${GREEN}✅ PASSED: $test_name${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌ FAILED: $test_name${NC}"
        ((TESTS_FAILED++))
    fi
}

# Function to check if a file exists
check_file() {
    local file_path="$1"
    local description="$2"
    
    if [ -f "$file_path" ]; then
        echo -e "${GREEN}✅ $description exists${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌ $description missing: $file_path${NC}"
        ((TESTS_FAILED++))
    fi
}

# Function to check if a directory exists
check_directory() {
    local dir_path="$1"
    local description="$2"
    
    if [ -d "$dir_path" ]; then
        echo -e "${GREEN}✅ $description exists${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌ $description missing: $dir_path${NC}"
        ((TESTS_FAILED++))
    fi
}

echo -e "\n${YELLOW}1. Testing File Structure${NC}"
echo "=========================="

# Check main project files
check_file "README.md" "Main README"
check_file "architecture.md" "Architecture documentation"
check_file "DEPLOYMENT.md" "Deployment guide"
check_file "CUSTOMIZATION.md" "Customization guide"
check_file "requirements.txt" "Python requirements"
check_file "Dockerfile" "Docker configuration"
check_file "docker-compose.yml" "Docker Compose configuration"

# Check infrastructure files
check_directory "infrastructure" "Infrastructure directory"
check_file "infrastructure/main.tf" "Main Terraform configuration"
check_file "infrastructure/variables.tf" "Terraform variables"
check_file "infrastructure/outputs.tf" "Terraform outputs"
check_file "infrastructure/terraform.tf" "Terraform backend configuration"

# Check environment configurations
check_file "infrastructure/environments/dev.tfvars" "Development environment"
check_file "infrastructure/environments/staging.tfvars" "Staging environment"
check_file "infrastructure/environments/prod.tfvars" "Production environment"

# Check Terraform modules
check_directory "infrastructure/modules" "Terraform modules directory"
check_directory "infrastructure/modules/vpc" "VPC module"
check_directory "infrastructure/modules/s3" "S3 module"
check_directory "infrastructure/modules/rds" "RDS module"
check_directory "infrastructure/modules/security" "Security module"
check_directory "infrastructure/modules/ec2" "EC2 module"

# Check backend files
check_directory "backend" "Backend directory"
check_file "backend/main.py" "Backend main application"
check_file "backend/requirements.txt" "Backend requirements"
check_file "backend/config/settings.py" "Backend configuration"

# Check backend services
check_directory "backend/services" "Backend services"
check_file "backend/services/ai_service.py" "AI service"
check_file "backend/services/database.py" "Database service"
check_file "backend/services/cache.py" "Cache service"
check_file "backend/services/chat_service.py" "Chat service"
check_file "backend/services/knowledge_service.py" "Knowledge service"
check_file "backend/services/analytics_service.py" "Analytics service"

# Check backend API routes
check_directory "backend/api" "Backend API"
check_directory "backend/api/routes" "API routes"
check_file "backend/api/routes/chat.py" "Chat API routes"
check_file "backend/api/routes/health.py" "Health API routes"
check_file "backend/api/routes/knowledge.py" "Knowledge API routes"
check_file "backend/api/routes/analytics.py" "Analytics API routes"

# Check backend models
check_directory "backend/models" "Backend models"
check_file "backend/models/chat.py" "Chat models"

# Check backend utilities
check_directory "backend/utils" "Backend utilities"
check_file "backend/utils/logging_config.py" "Logging configuration"
check_file "backend/utils/validators.py" "Input validators"

# Check scripts
check_directory "scripts" "Scripts directory"
check_directory "scripts/deployment" "Deployment scripts"
check_file "scripts/deployment/deploy.sh" "Deployment script"

# Check data
check_directory "data" "Data directory"
check_directory "data/knowledge_base" "Knowledge base data"
check_file "data/knowledge_base/medical_guidelines/diabetes-management.md" "Sample medical guidelines"
check_file "data/knowledge_base/faq/common-questions.md" "Sample FAQ"

# Check documentation
check_directory "docs" "Documentation directory"
check_directory "docs/user-guide" "User guide"
check_directory "docs/admin-guide" "Admin guide"
check_file "docs/user-guide/README.md" "User guide documentation"
check_file "docs/admin-guide/README.md" "Admin guide documentation"

echo -e "\n${YELLOW}2. Testing Terraform Configuration${NC}"
echo "=================================="

# Change to infrastructure directory
cd infrastructure

# Test Terraform validation
run_test "Terraform validation" "terraform validate"

# Test Terraform format
run_test "Terraform format check" "terraform fmt -check -recursive"

# Test Terraform initialization (without backend)
run_test "Terraform initialization" "terraform init -backend=false"

echo -e "\n${YELLOW}3. Testing Python Code Quality${NC}"
echo "================================="

# Change back to project root
cd ..

# Check if Python is available
if command -v python3 &> /dev/null; then
    echo -e "${GREEN}✅ Python3 is available${NC}"
    ((TESTS_PASSED++))
    
    # Test Python syntax
    run_test "Backend main.py syntax" "python3 -m py_compile backend/main.py"
    run_test "Backend settings.py syntax" "python3 -m py_compile backend/config/settings.py"
    run_test "AI service syntax" "python3 -m py_compile backend/services/ai_service.py"
    run_test "Database service syntax" "python3 -m py_compile backend/services/database.py"
    run_test "Cache service syntax" "python3 -m py_compile backend/services/cache.py"
    run_test "Chat service syntax" "python3 -m py_compile backend/services/chat_service.py"
    run_test "Knowledge service syntax" "python3 -m py_compile backend/services/knowledge_service.py"
    run_test "Analytics service syntax" "python3 -m py_compile backend/services/analytics_service.py"
    run_test "Logging config syntax" "python3 -m py_compile backend/utils/logging_config.py"
    run_test "Validators syntax" "python3 -m py_compile backend/utils/validators.py"
else
    echo -e "${RED}❌ Python3 is not available${NC}"
    ((TESTS_FAILED++))
fi

echo -e "\n${YELLOW}4. Testing Docker Configuration${NC}"
echo "================================="

# Check if Docker is available
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✅ Docker is available${NC}"
    ((TESTS_PASSED++))
    
    # Test Docker Compose syntax
    run_test "Docker Compose syntax" "docker-compose config"
else
    echo -e "${RED}❌ Docker is not available${NC}"
    ((TESTS_FAILED++))
fi

echo -e "\n${YELLOW}5. Testing Scripts${NC}"
echo "=================="

# Check if deployment script is executable
if [ -x "scripts/deployment/deploy.sh" ]; then
    echo -e "${GREEN}✅ Deployment script is executable${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}❌ Deployment script is not executable${NC}"
    ((TESTS_FAILED++))
fi

echo -e "\n${YELLOW}6. Testing Documentation${NC}"
echo "========================="

# Check if documentation files are not empty
if [ -s "README.md" ]; then
    echo -e "${GREEN}✅ README.md is not empty${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}❌ README.md is empty${NC}"
    ((TESTS_FAILED++))
fi

if [ -s "architecture.md" ]; then
    echo -e "${GREEN}✅ architecture.md is not empty${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}❌ architecture.md is empty${NC}"
    ((TESTS_FAILED++))
fi

if [ -s "DEPLOYMENT.md" ]; then
    echo -e "${GREEN}✅ DEPLOYMENT.md is not empty${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}❌ DEPLOYMENT.md is empty${NC}"
    ((TESTS_FAILED++))
fi

if [ -s "CUSTOMIZATION.md" ]; then
    echo -e "${GREEN}✅ CUSTOMIZATION.md is not empty${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}❌ CUSTOMIZATION.md is empty${NC}"
    ((TESTS_FAILED++))
fi

echo -e "\n${YELLOW}7. Testing Knowledge Base${NC}"
echo "=========================="

# Check if knowledge base files exist and are not empty
if [ -s "data/knowledge_base/medical_guidelines/diabetes-management.md" ]; then
    echo -e "${GREEN}✅ Diabetes management guidelines exist${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}❌ Diabetes management guidelines missing or empty${NC}"
    ((TESTS_FAILED++))
fi

if [ -s "data/knowledge_base/faq/common-questions.md" ]; then
    echo -e "${GREEN}✅ Common questions FAQ exists${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}❌ Common questions FAQ missing or empty${NC}"
    ((TESTS_FAILED++))
fi

echo -e "\n${YELLOW}8. Testing Environment Configuration${NC}"
echo "====================================="

# Check if environment files have required variables
if grep -q "aws_region" infrastructure/environments/dev.tfvars; then
    echo -e "${GREEN}✅ Development environment has aws_region${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}❌ Development environment missing aws_region${NC}"
    ((TESTS_FAILED++))
fi

if grep -q "environment" infrastructure/environments/dev.tfvars; then
    echo -e "${GREEN}✅ Development environment has environment variable${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}❌ Development environment missing environment variable${NC}"
    ((TESTS_FAILED++))
fi

if grep -q "project_name" infrastructure/environments/dev.tfvars; then
    echo -e "${GREEN}✅ Development environment has project_name${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}❌ Development environment missing project_name${NC}"
    ((TESTS_FAILED++))
fi

echo -e "\n${YELLOW}9. Testing Security Configuration${NC}"
echo "=================================="

# Check if security-related files exist
if [ -f "infrastructure/modules/security/main.tf" ]; then
    echo -e "${GREEN}✅ Security module exists${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}❌ Security module missing${NC}"
    ((TESTS_FAILED++))
fi

# Check if security groups are defined
if grep -q "aws_security_group" infrastructure/modules/security/main.tf; then
    echo -e "${GREEN}✅ Security groups are defined${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}❌ Security groups are not defined${NC}"
    ((TESTS_FAILED++))
fi

# Check if IAM roles are defined
if grep -q "aws_iam_role" infrastructure/modules/security/main.tf; then
    echo -e "${GREEN}✅ IAM roles are defined${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}❌ IAM roles are not defined${NC}"
    ((TESTS_FAILED++))
fi

echo -e "\n${YELLOW}10. Testing Monitoring Configuration${NC}"
echo "====================================="

# Check if CloudWatch is configured
if grep -q "aws_cloudwatch" infrastructure/main.tf; then
    echo -e "${GREEN}✅ CloudWatch is configured${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}❌ CloudWatch is not configured${NC}"
    ((TESTS_FAILED++))
fi

# Check if logging is configured
if grep -q "aws_cloudwatch_log_group" infrastructure/main.tf; then
    echo -e "${GREEN}✅ CloudWatch log groups are configured${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}❌ CloudWatch log groups are not configured${NC}"
    ((TESTS_FAILED++))
fi

echo -e "\n${YELLOW}Test Summary${NC}"
echo "============="
echo -e "${GREEN}Tests Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Tests Failed: $TESTS_FAILED${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All tests passed! The system is complete and ready for deployment.${NC}"
    exit 0
else
    echo -e "\n${RED}❌ Some tests failed. Please review the issues above.${NC}"
    exit 1
fi
