#!/bin/bash

# Infrastructure Destruction Script
# This script destroys AWS infrastructure created by Terraform

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INFRA_DIR="$SCRIPT_DIR/../infrastructure/terraform"

echo "========================================="
echo "Infrastructure Destruction"
echo "========================================="
echo ""
echo "WARNING: This will destroy all infrastructure resources!"
echo "This action cannot be undone."
echo ""

read -p "Are you sure you want to destroy all infrastructure? (type 'yes' to confirm): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Destruction cancelled."
    exit 0
fi

cd "$INFRA_DIR"

echo ""
echo "Planning infrastructure destruction..."
terraform plan -destroy

echo ""
read -p "Proceed with destruction? (yes/no): " FINAL_CONFIRM

if [ "$FINAL_CONFIRM" != "yes" ]; then
    echo "Destruction cancelled."
    exit 0
fi

echo ""
echo "Destroying infrastructure..."
terraform destroy -auto-approve

echo ""
echo "========================================="
echo "Infrastructure destruction complete!"
echo "========================================="

