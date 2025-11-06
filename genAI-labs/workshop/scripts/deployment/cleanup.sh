#!/bin/bash
# Cleanup script for Claude Code Workshop infrastructure

set -e

echo "🧹 Cleaning up Claude Code Workshop infrastructure..."

# Check which deployment method was used
if [ -d "infrastructure/cdk" ]; then
    echo "📋 Using CDK cleanup..."
    cd infrastructure/cdk
    
    if [ -d "venv" ]; then
        source venv/bin/activate
    else
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
    fi
    
    read -p "Are you sure you want to destroy all resources? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cdk destroy --force
        echo "✅ CDK stack destroyed"
    else
        echo "Cleanup cancelled"
    fi
    
elif [ -d "infrastructure/terraform" ]; then
    echo "📋 Using Terraform cleanup..."
    cd infrastructure/terraform
    
    read -p "Are you sure you want to destroy all resources? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        terraform destroy -auto-approve
        echo "✅ Terraform resources destroyed"
    else
        echo "Cleanup cancelled"
    fi
else
    echo "⚠️  No infrastructure found. Manual cleanup may be required."
fi

echo ""
echo "✅ Cleanup complete!"

