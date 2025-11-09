#!/bin/bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")"/../../.. && pwd)"
LAB_DIR="$REPO_ROOT/genAI-labs/observability"

cd "$LAB_DIR"

echo "🔍 Setting up Observability Lab environment"

# Python environment
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt

# Terraform
if ! command -v terraform >/dev/null 2>&1; then
  echo "⚠️  Terraform not found. Install Terraform >= 1.5"
else
  echo "Terraform version: $(terraform version | head -n1)"
fi

# AWS CLI
if ! command -v aws >/dev/null 2>&1; then
  echo "⚠️  AWS CLI not found. Install AWS CLI v2"
else
  aws sts get-caller-identity >/dev/null && echo "✅ AWS credentials verified" || echo "⚠️  Configure AWS credentials"
fi

echo "✅ Environment setup complete"
