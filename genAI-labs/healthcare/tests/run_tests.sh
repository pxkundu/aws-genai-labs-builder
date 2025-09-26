#!/bin/bash

# Healthcare ChatGPT Clone - Test Runner Script
# This script runs all tests for the healthcare application

set -e

echo "🏥 Healthcare ChatGPT Clone - Test Suite"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results
TESTS_PASSED=0
TESTS_FAILED=0

# Function to run a test suite
run_test_suite() {
    local test_name="$1"
    local test_command="$2"
    
    echo -e "\n${BLUE}Running: $test_name${NC}"
    echo "Command: $test_command"
    
    if eval "$test_command"; then
        echo -e "${GREEN}✅ PASSED: $test_name${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}❌ FAILED: $test_name${NC}"
        ((TESTS_FAILED++))
    fi
}

# Check if we're in the right directory
if [ ! -f "pytest.ini" ]; then
    echo -e "${RED}Error: Please run this script from the tests directory${NC}"
    exit 1
fi

# Install test dependencies
echo -e "\n${YELLOW}Installing test dependencies...${NC}"
pip install -r requirements.txt

# Run backend unit tests
run_test_suite "Backend Unit Tests" "pytest test_backend/ -m unit -v"

# Run backend integration tests
run_test_suite "Backend Integration Tests" "pytest test_backend/ -m integration -v"

# Run infrastructure tests
run_test_suite "Infrastructure Tests" "pytest test_infrastructure/ -v"

# Run frontend tests (if available)
if [ -d "test_frontend" ]; then
    run_test_suite "Frontend Tests" "pytest test_frontend/ -v"
fi

# Run security tests
run_test_suite "Security Tests" "pytest -m security -v"

# Run performance tests
run_test_suite "Performance Tests" "pytest -m performance -v"

# Run all tests with coverage
echo -e "\n${YELLOW}Running all tests with coverage...${NC}"
run_test_suite "Full Test Suite with Coverage" "pytest --cov=backend --cov-report=html --cov-report=term-missing"

# Run code quality checks
echo -e "\n${YELLOW}Running code quality checks...${NC}"

# Black formatting check
run_test_suite "Code Formatting (Black)" "black --check backend/"

# Import sorting check
run_test_suite "Import Sorting (isort)" "isort --check-only backend/"

# Linting
run_test_suite "Linting (flake8)" "flake8 backend/"

# Type checking
run_test_suite "Type Checking (mypy)" "mypy backend/"

# Security scanning
run_test_suite "Security Scan (bandit)" "bandit -r backend/"

# Terraform validation
echo -e "\n${YELLOW}Running Terraform validation...${NC}"
cd ../infrastructure
run_test_suite "Terraform Validation" "terraform validate"
cd ../tests

# Generate test report
echo -e "\n${YELLOW}Generating test report...${NC}"
if [ -f "htmlcov/index.html" ]; then
    echo -e "${GREEN}Coverage report generated: htmlcov/index.html${NC}"
fi

# Test summary
echo -e "\n${YELLOW}Test Summary${NC}"
echo "============="
echo -e "${GREEN}Tests Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Tests Failed: $TESTS_FAILED${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All tests passed! The system is ready for deployment.${NC}"
    exit 0
else
    echo -e "\n${RED}❌ Some tests failed. Please review the issues above.${NC}"
    exit 1
fi
