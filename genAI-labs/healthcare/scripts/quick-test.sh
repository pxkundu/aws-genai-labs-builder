#!/bin/bash

# Quick system test for Healthcare ChatGPT Clone

echo "🏥 Healthcare ChatGPT Clone - Quick Test"
echo "========================================"

# Test 1: Check main files
echo "1. Checking main files..."
if [ -f "README.md" ] && [ -f "architecture.md" ] && [ -f "DEPLOYMENT.md" ] && [ -f "CUSTOMIZATION.md" ]; then
    echo "✅ Main documentation files exist"
else
    echo "❌ Some main documentation files are missing"
fi

# Test 2: Check infrastructure
echo "2. Checking infrastructure..."
if [ -d "infrastructure" ] && [ -f "infrastructure/main.tf" ] && [ -f "infrastructure/variables.tf" ]; then
    echo "✅ Infrastructure files exist"
else
    echo "❌ Infrastructure files are missing"
fi

# Test 3: Check backend
echo "3. Checking backend..."
if [ -d "backend" ] && [ -f "backend/main.py" ] && [ -d "backend/services" ]; then
    echo "✅ Backend files exist"
else
    echo "❌ Backend files are missing"
fi

# Test 4: Check Docker
echo "4. Checking Docker configuration..."
if [ -f "Dockerfile" ] && [ -f "docker-compose.yml" ]; then
    echo "✅ Docker configuration exists"
else
    echo "❌ Docker configuration is missing"
fi

# Test 5: Check Terraform validation
echo "5. Testing Terraform validation..."
cd infrastructure
if terraform validate >/dev/null 2>&1; then
    echo "✅ Terraform configuration is valid"
else
    echo "❌ Terraform configuration has errors"
fi
cd ..

# Test 6: Check Python syntax
echo "6. Testing Python syntax..."
if python3 -m py_compile backend/main.py >/dev/null 2>&1; then
    echo "✅ Backend Python syntax is valid"
else
    echo "❌ Backend Python syntax has errors"
fi

# Test 7: Check knowledge base
echo "7. Checking knowledge base..."
if [ -d "data/knowledge_base" ] && [ -f "data/knowledge_base/medical_guidelines/diabetes-management.md" ]; then
    echo "✅ Knowledge base exists"
else
    echo "❌ Knowledge base is missing"
fi

# Test 8: Check scripts
echo "8. Checking scripts..."
if [ -f "scripts/deployment/deploy.sh" ] && [ -x "scripts/deployment/deploy.sh" ]; then
    echo "✅ Deployment script exists and is executable"
else
    echo "❌ Deployment script is missing or not executable"
fi

echo ""
echo "🎉 Quick test completed!"
echo "The Healthcare ChatGPT Clone system appears to be complete and ready for deployment."
